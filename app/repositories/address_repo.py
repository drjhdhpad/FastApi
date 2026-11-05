from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address


def get_by_id(db: Session, address_id: int) -> Address | None:
    return db.get(Address, address_id)


def get_all(db: Session) -> list[Address]:
    return list(db.scalars(select(Address).order_by(Address.id)))


def create(db: Session, **values) -> Address:
    address = Address(**values)
    db.add(address)
    db.flush()
    return address
