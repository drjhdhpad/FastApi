from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ad import Advertisement
from app.models.category import AdCategory, Category
from app.schemas.ad import AdCreate, AdUpdate


def get_by_id(db: Session, ad_id: int) -> Advertisement | None:
    return db.get(Advertisement, ad_id)


def get_all(
    db: Session,
    *,
    ad_status: str | None,
    category: str | None,
    title: str | None,
    price: int | None,
    create_at: date | None,
    is_adult: bool | None,
    page: int,
    limit: int,
) -> list[Advertisement]:
    query = select(Advertisement)
    if ad_status is not None:
        query = query.where(Advertisement.status == ad_status)
    if title:
        search_text = title.strip()
        if db.bind.dialect.name == "sqlite":
            query = query.where(
                func.casefold(Advertisement.title).like(f"%{search_text.casefold()}%")
            )
        else:
            query = query.where(Advertisement.title.ilike(f"%{search_text}%"))
    if price is not None:
        query = query.where(Advertisement.price == price)
    if create_at is not None:
        query = query.where(func.date(Advertisement.created_at) == create_at.isoformat())
    if is_adult is not None:
        query = query.where(Advertisement.is_adult == is_adult)
    if category is not None:
        matching_ads = (
            select(AdCategory.ad_id)
            .join(Category, Category.id == AdCategory.category_id)
            .where(Category.name == category)
        )
        query = query.where(Advertisement.id.in_(matching_ads))
    query = query.order_by(Advertisement.id).offset((page - 1) * limit).limit(limit)
    return list(db.scalars(query))


def create(db: Session, data: AdCreate) -> Advertisement:
    ad = Advertisement(**data.model_dump())
    db.add(ad)
    db.flush()
    return ad


def update(db: Session, ad: Advertisement, data: AdUpdate) -> Advertisement:
    for field, value in data.model_dump().items():
        setattr(ad, field, value)
    db.flush()
    return ad
