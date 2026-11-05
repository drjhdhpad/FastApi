from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import user_repo
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, data: UserCreate):
    user = user_repo.create(db, data)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from exc
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = user_repo.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_repo.update(db, user, data)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from exc
    db.refresh(user)
    return user
