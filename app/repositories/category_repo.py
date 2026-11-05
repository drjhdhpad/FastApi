from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def get_all(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)))


def create(db: Session, name: str) -> Category:
    category = Category(name=name)
    db.add(category)
    db.flush()
    return category
