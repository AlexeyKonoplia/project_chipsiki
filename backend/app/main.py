import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine
from .models import Category
from .routers import admin, auth, categories, products, reviews, users


# Default marketplace-style taxonomy: section -> subcategories.
# Seeded idempotently by name; admins can edit the tree afterwards.
DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Еда": [
        "Пицца",
        "Суши и роллы",
        "Бургеры",
        "Шаурма",
        "Снеки и чипсы",
        "Сладкое",
        "Полуфабрикаты",
    ],
    "Напитки": ["Пиво", "Газировка", "Соки", "Энергетики", "Кофе", "Чай"],
    "Заведения": ["Кафе", "Рестораны", "Доставка", "Бары"],
    "Магазины": ["Продуктовые", "Маркетплейсы", "Одежда и обувь"],
    "Электроника": ["Смартфоны", "Наушники", "Компьютеры", "Гаджеты"],
    "Дом и быт": ["Бытовая техника", "Мебель", "Для кухни"],
    "Красота и здоровье": ["Косметика", "Аптека"],
    "Развлечения": ["Игры", "Кино", "Книги"],
    "Прочее": [],
}


def _wait_for_db(retries: int = 30, delay: float = 2.0) -> None:
    # The DB (or its DNS name) may not be ready the instant the backend starts,
    # especially under Portainer where depends_on ordering isn't guaranteed.
    # Retry instead of crashing the container.
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            last_err = exc
            print(
                f"[startup] database not ready (attempt {attempt}/{retries}), "
                f"retrying in {delay}s...",
                flush=True,
            )
            time.sleep(delay)
    raise RuntimeError("Database is not reachable after waiting") from last_err


def _bootstrap_db() -> None:
    _wait_for_db()

    # Create tables on startup (simple approach; real projects use Alembic).
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        # Lightweight, idempotent migration for the is_admin column so existing
        # databases (persisted volume) pick it up without a full reset.
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin "
                "boolean NOT NULL DEFAULT false"
            )
        )
        # Two-level category tree (sections/subcategories).
        conn.execute(
            text(
                "ALTER TABLE categories ADD COLUMN IF NOT EXISTS parent_id "
                "integer REFERENCES categories(id) ON DELETE CASCADE"
            )
        )
        # Account approval: pre-existing users are backfilled as approved
        # (DEFAULT true); new registrations start unapproved.
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_approved "
                "boolean NOT NULL DEFAULT true"
            )
        )
        conn.execute(text("UPDATE users SET is_approved = true WHERE is_admin = true"))
        # Grant admin to the configured usernames if they already exist.
        if settings.admin_usernames:
            conn.execute(
                text("UPDATE users SET is_admin = true WHERE username = ANY(:names)"),
                {"names": settings.admin_usernames},
            )

    _seed_categories()


def _seed_categories() -> None:
    # Insert any missing default sections/subcategories (matched by name),
    # leaving everything the admins created or renamed untouched.
    with Session(engine) as db:
        for section_name, sub_names in DEFAULT_CATEGORIES.items():
            section = db.query(Category).filter(Category.name == section_name).first()
            if not section:
                section = Category(name=section_name)
                db.add(section)
                db.flush()
            for sub_name in sub_names:
                exists = db.query(Category).filter(Category.name == sub_name).first()
                if not exists:
                    db.add(Category(name=sub_name, parent_id=section.id))
        db.commit()


_bootstrap_db()

os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(title="Chipsiki Reviews API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(admin.router)
app.include_router(users.router)

# Serve uploaded images.
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/api/health")
def health():
    return {"status": "ok"}
