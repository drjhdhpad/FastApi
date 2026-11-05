from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.engagement import StatEvent


class StatEventCreate(BaseModel):
    event: StatEvent


class StatsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ad_id: int
    event_type: StatEvent
    count: int
    date: datetime
