from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ad import AdStatus


class AdCreate(BaseModel):
    owner_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    price: int = Field(ge=0)
    status: AdStatus = AdStatus.active
    isActive: bool = True
    is_favorite: bool = False
    is_adult: bool = False
    address_id: int | None = Field(default=None, gt=0)


class AdUpdate(AdCreate):
    pass


class AdRead(AdCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime
    created_at: datetime
    view_count: int


class AdPurchase(BaseModel):
    buyer_id: int = Field(gt=0)


class AdPurchaseRead(BaseModel):
    ad_id: int
    status: AdStatus
    price: int
    buyer_id: int
    buyer_balance: int
    seller_id: int
    seller_balance: int
