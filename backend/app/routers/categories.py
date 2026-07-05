from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import get_current_admin
from ..models import Category, User
from ..schemas import CategoryCreate, CategoryOut, CategoryTreeOut, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


@router.get("/tree", response_model=list[CategoryTreeOut])
def category_tree(db: Session = Depends(get_db)):
    """Top-level sections with their subcategories."""
    return (
        db.query(Category)
        .options(joinedload(Category.children))
        .filter(Category.parent_id.is_(None))
        .order_by(Category.name)
        .all()
    )


def _check_name_free(db: Session, name: str, exclude_id: int | None = None) -> None:
    query = db.query(Category).filter(Category.name.ilike(name))
    if exclude_id is not None:
        query = query.filter(Category.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Категория с таким названием уже существует",
        )


def _get_section(db: Session, parent_id: int) -> Category:
    parent = db.get(Category, parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Родительская категория не найдена")
    if parent.parent_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Подкатегорию можно добавить только в раздел верхнего уровня",
        )
    return parent


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Название категории обязательно")
    _check_name_free(db, name)

    parent_id = None
    if payload.parent_id:
        parent_id = _get_section(db, payload.parent_id).id

    category = Category(name=name, parent_id=parent_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Название категории обязательно")
        _check_name_free(db, name, exclude_id=category.id)
        category.name = name

    if payload.parent_id is not None:
        if payload.parent_id == 0:
            category.parent_id = None
        else:
            if payload.parent_id == category.id:
                raise HTTPException(status_code=400, detail="Категория не может быть родителем самой себя")
            if category.children:
                raise HTTPException(
                    status_code=400,
                    detail="Раздел с подкатегориями нельзя сделать подкатегорией",
                )
            category.parent_id = _get_section(db, payload.parent_id).id

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    # Subcategories are removed by the FK cascade; product links likewise.
    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
