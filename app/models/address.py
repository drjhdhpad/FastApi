from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.basemodel import Base


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    street: Mapped[str] = mapped_column(String(200), nullable=False)
    house: Mapped[str] = mapped_column(String(30), nullable=False)
