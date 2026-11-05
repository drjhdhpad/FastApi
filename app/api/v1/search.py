from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ad import AdStatus
from app.schemas.ad import AdRead
from app.services.search_service import search_ads

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/ads", response_model=list[AdRead])
def search_advertisements(
    ad_status: AdStatus | None = Query(default=None, alias="status"),
    title: str | None = Query(default=None, min_length=1),
    price: int | None = Query(default=None, ge=0),
    create_at: date | None = Query(default=None),
    is_adult: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return search_ads(
        db,
        ad_status=ad_status,
        title=title,
        price=price,
        create_at=create_at,
        is_adult=is_adult,
        page=page,
        limit=limit,
    )
