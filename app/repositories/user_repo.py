from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_all(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)))


def create(db: Session, data: UserCreate) -> User:
    user = User(**data.model_dump())
    db.add(user)
    db.flush()
    return user


def update(db: Session, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump().items():
        setattr(user, field, value)
    db.flush()
    return user
