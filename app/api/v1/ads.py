from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ad import AdStatus, Advertisement
from app.models.address import Address
from app.models.category import AdCategory, Category
from app.models.engagement import StatEvent, Stats, Promotion
from app.models.message import Message
from app.models.user import User
from app.repositories import ad_repo
from app.schemas.ad import AdCreate, AdPurchase, AdPurchaseRead, AdRead, AdUpdate
from app.schemas.engagement import StatEventCreate, StatsRead
from app.services import ad_service, search_service

router = APIRouter(prefix="/api/ads", tags=["advertisements"])
legacy_stats_router = APIRouter(prefix="/ads", tags=["advertisement statistics"])


@router.post("", response_model=AdRead, status_code=status.HTTP_201_CREATED)
def create_ad(data: AdCreate, db: Session = Depends(get_db)):
    if db.get(User, data.owner_id) is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    if data.address_id is not None and db.get(Address, data.address_id) is None:
        raise HTTPException(status_code=404, detail="Address not found")
    ad = ad_repo.create(db, data)
    db.commit()
    db.refresh(ad)
    return ad


@router.get("", response_model=list[AdRead])
def get_ads(
    ad_status: AdStatus | None = Query(default=None, alias="status"),
    category: str | None = None,
    title: str | None = Query(default=None, min_length=1),
    price: int | None = Query(default=None, ge=0),
    create_at: date | None = Query(default=None),
    is_adult: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return search_service.search_ads(
        db,
        ad_status=ad_status,
        category=category,
        title=title,
        price=price,
        create_at=create_at,
        is_adult=is_adult,
        page=page,
        limit=limit,
    )


@router.get("/{ad_id}", response_model=AdRead)
def get_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = ad_service.get_ad(db, ad_id)
    ad.view_count += 1
    db.commit()
    db.refresh(ad)
    return ad


@router.put("/{ad_id}", response_model=AdRead)
def update_ad(ad_id: int, data: AdUpdate, db: Session = Depends(get_db)):
    return ad_service.update_ad(db, ad_id, data)


@router.post("/{ad_id}/buy", response_model=AdPurchaseRead)
def buy_ad(ad_id: int, data: AdPurchase, db: Session = Depends(get_db)):
    return ad_service.buy_ad(db, ad_id, data)


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = ad_service.get_ad(db, ad_id)
    for model in (AdCategory, Promotion, Stats, Message):
        db.execute(delete(model).where(model.ad_id == ad_id))
    db.delete(ad)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{ad_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_category(ad_id: int, category_id: int, db: Session = Depends(get_db)):
    ad_service.get_ad(db, ad_id)
    if db.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if db.get(AdCategory, (ad_id, category_id)) is None:
        db.add(AdCategory(ad_id=ad_id, category_id=category_id))
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@legacy_stats_router.post("/{ad_id}/stats/events", response_model=StatsRead)
@router.post("/{ad_id}/stats/events", response_model=StatsRead)
def record_ad_event(ad_id: int, data: StatEventCreate, db: Session = Depends(get_db)):
    ad_service.get_ad(db, ad_id)
    stats = db.scalar(
        select(Stats).where(Stats.ad_id == ad_id, Stats.event_type == data.event.value)
    )
    if stats is None:
        stats = Stats(ad_id=ad_id, event_type=data.event.value, count=0)
        db.add(stats)
    stats.count += 1
    stats.date = datetime.utcnow()
    db.commit()
    db.refresh(stats)
    return stats


@legacy_stats_router.get("/{ad_id}/stats", response_model=list[StatsRead])
@router.get("/{ad_id}/stats", response_model=list[StatsRead])
def get_ad_stats(ad_id: int, db: Session = Depends(get_db)):
    ad_service.get_ad(db, ad_id)
    return list(db.scalars(select(Stats).where(Stats.ad_id == ad_id).order_by(Stats.id)))
