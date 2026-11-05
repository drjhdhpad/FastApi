from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.message import Message


def create(db: Session, **values) -> Message:
    message = Message(**values)
    db.add(message)
    db.flush()
    return message


def get_for_user(db: Session, user_id: int, *, ad_id: int | None = None) -> list[Message]:
    query = select(Message).where(
        or_(Message.sender_id == user_id, Message.recipient_id == user_id)
    )
    if ad_id is not None:
        query = query.where(Message.ad_id == ad_id)
    return list(db.scalars(query.order_by(Message.created_at, Message.id)))
