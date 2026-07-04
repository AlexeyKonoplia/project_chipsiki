import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from .config import settings
from .database import Base, engine
from .routers import admin, auth, categories, products, reviews


def _bootstrap_db() -> None:
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
        # Grant admin to the configured usernames if they already exist.
        if settings.admin_usernames:
            conn.execute(
                text("UPDATE users SET is_admin = true WHERE username = ANY(:names)"),
                {"names": settings.admin_usernames},
            )


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

# Serve uploaded images.
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/api/health")
def health():
    return {"status": "ok"}
