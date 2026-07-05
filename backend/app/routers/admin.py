from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin
from ..models import User
from ..schemas import UserOut, AdminUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    return db.query(User).order_by(User.username).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: AdminUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if payload.is_admin is not None:
        if user.id == current_admin.id and not payload.is_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя снять права администратора с самого себя",
            )
        user.is_admin = payload.is_admin
        if payload.is_admin:
            user.is_approved = True

    if payload.is_approved is not None:
        user.is_approved = payload.is_approved

    if payload.username is not None:
        new_username = payload.username.strip()
        if len(new_username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя должно быть не короче 3 символов",
            )
        clash = (
            db.query(User)
            .filter(User.username == new_username, User.id != user.id)
            .first()
        )
        if clash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Имя пользователя уже занято",
            )
        user.username = new_username

    db.commit()
    db.refresh(user)
    return user
