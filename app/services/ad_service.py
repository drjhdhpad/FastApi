from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.ad import AdStatus, Advertisement
from app.models.address import Address
from app.models.user import User
from app.schemas.ad import AdPurchase, AdPurchaseRead, AdUpdate
from app.repositories import ad_repo


def get_ad(db: Session, ad_id: int) -> Advertisement:
    ad = ad_repo.get_by_id(db, ad_id)
    if ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


def update_ad(db: Session, ad_id: int, data: AdUpdate) -> Advertisement:
    ad = get_ad(db, ad_id)
    if db.get(User, data.owner_id) is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    if data.address_id is not None and db.get(Address, data.address_id) is None:
        raise HTTPException(status_code=404, detail="Address not found")
    ad_repo.update(db, ad, data)
    db.commit()
    db.refresh(ad)
    return ad


def buy_ad(db: Session, ad_id: int, data: AdPurchase) -> AdPurchaseRead:
    ad = get_ad(db, ad_id)
    if ad.status != AdStatus.active.value:
        raise HTTPException(status_code=409, detail="Advertisement is not available")

    buyer = db.get(User, data.buyer_id)
    if buyer is None:
        raise HTTPException(status_code=404, detail="Buyer not found")
    if buyer.id == ad.owner_id:
        raise HTTPException(status_code=400, detail="Seller cannot buy their own advertisement")

    seller_id, price = ad.owner_id, ad.price
    sold = db.execute(
        update(Advertisement)
        .where(Advertisement.id == ad_id, Advertisement.status == AdStatus.active.value)
        .values(status=AdStatus.sold.value, isActive=False)
    )
    if sold.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="Advertisement is no longer available")

    debited = db.execute(
        update(User)
        .where(User.id == buyer.id, User.balance >= price)
        .values(balance=User.balance - price)
    )
    if debited.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=400, detail="Insufficient funds")

    credited = db.execute(
        update(User)
        .where(User.id == seller_id)
        .values(balance=User.balance + price)
    )
    if credited.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="Seller no longer exists")
    db.commit()

    db.refresh(buyer)
    seller = db.get(User, seller_id)
    return AdPurchaseRead(
        ad_id=ad_id,
        status=AdStatus.sold,
        price=price,
        buyer_id=buyer.id,
        buyer_balance=buyer.balance,
        seller_id=seller_id,
        seller_balance=seller.balance,
    )
