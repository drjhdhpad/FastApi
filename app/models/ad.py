from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, synonym

from app.models.basemodel import Base


class AdStatus(str, Enum):
    active = "активно"
    sold = "продано"
    withdrawn = "снято"


class Advertisement(Base):
    __tablename__ = "advistiments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('активно', 'продано', 'снято')",
            name="ck_advistiments_status",
        ),
        CheckConstraint("price >= 0", name="ck_advistiments_price_nonnegative"),
        CheckConstraint("isActive IN (0, 1)", name="ck_advistiments_is_active_boolean"),
        CheckConstraint("is_adult IN (0, 1)", name="ck_advistiments_is_adult_boolean"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column("text", String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=AdStatus.active.value)
    isActive: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("1")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    date = synonym("created_at")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    is_favorite: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )
    is_adult: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )
    address_id: Mapped[int | None] = mapped_column(
        ForeignKey("address.id"), nullable=True, index=True
    )


advistiments = Advertisement
