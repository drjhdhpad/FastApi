from datetime import date

from sqlalchemy.orm import Session

from app.models.ad import AdStatus
from app.repositories import ad_repo


def search_ads(
    db: Session,
    *,
    ad_status: AdStatus | None = None,
    category: str | None = None,
    title: str | None = None,
    price: int | None = None,
    create_at: date | None = None,
    is_adult: bool | None = None,
    page: int = 1,
    limit: int = 20,
):
    return ad_repo.get_all(
        db,
        ad_status=ad_status.value if ad_status else None,
        category=category,
        title=title,
        price=price,
        create_at=create_at,
        is_adult=is_adult,
        page=page,
        limit=limit,
    )
