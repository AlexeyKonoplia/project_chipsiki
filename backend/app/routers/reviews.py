from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import get_current_user
from ..models import Product, Review, User
from ..schemas import ReviewCreate, ReviewOut, ReviewWithProduct
from .products import serialize_product, _resolve_categories

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewWithProduct])
def list_reviews(
    product_id: int | None = None,
    author_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Review).options(
        joinedload(Review.author),
        joinedload(Review.product).joinedload(Product.owner),
        joinedload(Review.product).joinedload(Product.categories),
    )
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if author_id:
        query = query.filter(Review.author_id == author_id)
    reviews = query.order_by(Review.created_at.desc()).all()

    result = []
    for r in reviews:
        item = ReviewWithProduct.model_validate(r)
        item.product = serialize_product(db, r.product)
        result.append(item)
    return result


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product: Product | None = None

    if payload.product_id is not None:
        product = db.get(Product, payload.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
    elif payload.new_product_name and payload.new_product_name.strip():
        # Create the product inline (image supplied via URL, if any).
        product = Product(
            name=payload.new_product_name.strip(),
            description=(
                payload.new_product_description.strip()
                if payload.new_product_description
                else None
            ),
            image_url=payload.new_product_image_url or None,
            owner_id=current_user.id,
        )
        product.categories = _resolve_categories(db, payload.new_product_category_ids)
        db.add(product)
        db.flush()  # obtain product.id without committing yet
    else:
        raise HTTPException(
            status_code=400,
            detail="Укажите существующий товар (product_id) или данные нового товара",
        )

    existing = (
        db.query(Review)
        .filter(Review.product_id == product.id, Review.author_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже оставили отзыв на этот товар",
        )

    review = Review(
        rating=payload.rating,
        text=(payload.text.strip() if payload.text else None),
        product_id=product.id,
        author_id=current_user.id,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
