import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import Category, Product, Review, User
from ..schemas import ProductOut
from fastapi import Response

router = APIRouter(prefix="/api/products", tags=["products"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


def _save_image(image: UploadFile) -> str:
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый формат изображения (разрешены jpeg, png, webp, gif)",
        )
    data = image.file.read()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Изображение слишком большое (максимум 5 МБ)",
        )
    ext = os.path.splitext(image.filename or "")[1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    os.makedirs(settings.upload_dir, exist_ok=True)
    path = os.path.join(settings.upload_dir, filename)
    with open(path, "wb") as f:
        f.write(data)
    return f"/uploads/{filename}"


def _resolve_categories(db: Session, category_ids: list[int]) -> list[Category]:
    if not category_ids:
        return []
    cats = db.query(Category).filter(Category.id.in_(category_ids)).all()
    return cats


def serialize_product(db: Session, product: Product) -> ProductOut:
    stats = (
        db.query(func.count(Review.id), func.avg(Review.rating))
        .filter(Review.product_id == product.id)
        .one()
    )
    count, avg = stats
    out = ProductOut.model_validate(product)
    out.review_count = int(count or 0)
    out.average_rating = round(float(avg), 2) if avg is not None else None
    return out


@router.get("", response_model=list[ProductOut])
def list_products(
    q: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product).options(
        joinedload(Product.owner), joinedload(Product.categories)
    )
    if q:
        query = query.filter(Product.name.ilike(f"%{q.strip()}%"))
    if category_id:
        query = query.filter(Product.categories.any(Category.id == category_id))
    products = query.order_by(Product.created_at.desc()).all()
    return [serialize_product(db, p) for p in products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return serialize_product(db, product)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(...),
    description: str | None = Form(None),
    # Categories arrive as repeated form fields: category_ids=1&category_ids=2
    category_ids: list[int] = Form(default=[]),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Название товара обязательно")

    image_url = _save_image(image) if image is not None else None

    product = Product(
        name=name,
        description=(description.strip() if description else None),
        image_url=image_url,
        owner_id=current_user.id,
    )
    product.categories = _resolve_categories(db, category_ids)
    db.add(product)
    db.commit()
    db.refresh(product)
    return serialize_product(db, product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    # Admins can delete any product; regular users only their own.
    if not current_user.is_admin and product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления товара")
    db.delete(product)  # cascades to reviews and category links
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
