from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, Product, Review, User
from ..schemas import LeaderboardEntry, UserPublic

router = APIRouter(prefix="/api/users", tags=["users"])


# Declared before "/{user_id}" so the literal path wins the route match.
@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(
    q: str | None = None,
    category_id: int | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Users ranked by how many reviews they've written.

    Optionally restricted to reviews on products in a given category
    (its subcategories included) and/or filtered by a username substring.
    Only users with at least one matching review appear.
    """
    query = (
        db.query(
            User.id,
            User.username,
            User.is_admin,
            func.count(Review.id).label("review_count"),
            func.avg(Review.rating).label("average_rating"),
        )
        .join(Review, Review.author_id == User.id)
    )

    if category_id:
        # Filtering by a top-level section also counts its subcategories.
        child_ids = [
            row.id
            for row in db.query(Category.id).filter(Category.parent_id == category_id)
        ]
        cat_ids = [category_id, *child_ids]
        query = query.filter(
            Review.product.has(Product.categories.any(Category.id.in_(cat_ids)))
        )

    if q and q.strip():
        query = query.filter(User.username.ilike(f"%{q.strip()}%"))

    rows = (
        query.group_by(User.id, User.username, User.is_admin)
        .order_by(func.count(Review.id).desc(), User.username)
        .limit(max(1, min(limit, 500)))
        .all()
    )

    return [
        LeaderboardEntry(
            id=r.id,
            username=r.username,
            is_admin=r.is_admin,
            review_count=int(r.review_count or 0),
            average_rating=round(float(r.average_rating), 2)
            if r.average_rating is not None
            else None,
        )
        for r in rows
    ]


@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
