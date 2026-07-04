from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Category, User
from ..schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    name = payload.name.strip()
    existing = db.query(Category).filter(Category.name.ilike(name)).first()
    if existing:
        # Idempotent-ish: return the existing category instead of erroring.
        return existing
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
