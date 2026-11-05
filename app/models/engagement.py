from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.basemodel import Base


class StatEvent(str, Enum):
    view = "просмотр"
    call = "звонок"
    message = "сообщение"


class PromotionType(str, Enum):
    bump = "поднять"
    highlight = "выделить цветом"


class Stats(Base):
    __tablename__ = "stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ad_id: Mapped[int] = mapped_column(
        ForeignKey("advistiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Promotion(Base):
    __tablename__ = "promotions"
    __table_args__ = (
        CheckConstraint(
            "type IN ('поднять', 'выделить цветом')",
            name="ck_promotions_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ad_id: Mapped[int] = mapped_column(
        ForeignKey("advistiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    start: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="активно")
