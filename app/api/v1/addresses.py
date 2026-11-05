from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.address import Address
from app.repositories import address_repo
from app.schemas.address import AddressCreate, AddressRead

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
def create_address(data: AddressCreate, db: Session = Depends(get_db)):
    address = address_repo.create(db, **data.model_dump())
    db.commit()
    db.refresh(address)
    return address


@router.get("", response_model=list[AddressRead])
def get_addresses(db: Session = Depends(get_db)):
    return address_repo.get_all(db)


@router.get("/{address_id}", response_model=AddressRead)
def get_address(address_id: int, db: Session = Depends(get_db)):
    address = address_repo.get_by_id(db, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address
