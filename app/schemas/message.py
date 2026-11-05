from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MessageCreate(BaseModel):
    ad_id: int = Field(gt=0)
    sender_id: int = Field(gt=0)
    recipient_id: int = Field(gt=0)
    text: str = Field(min_length=1, max_length=5000)

    @model_validator(mode="after")
    def users_must_differ(self):
        if self.sender_id == self.recipient_id:
            raise ValueError("sender_id and recipient_id must be different")
        return self


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ad_id: int
    sender_id: int
    recipient_id: int
    text: str
    created_at: datetime
    is_read: bool
