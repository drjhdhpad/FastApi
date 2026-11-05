from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ad import Advertisement
from app.models.message import Message
from app.models.user import User
from app.repositories import message_repo
from app.schemas.message import MessageCreate, MessageRead

router = APIRouter(prefix="/api", tags=["messages"])


@router.post("/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def send_message(data: MessageCreate, db: Session = Depends(get_db)):
    ad = db.get(Advertisement, data.ad_id)
    if ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if ad.owner_id not in (data.sender_id, data.recipient_id):
        raise HTTPException(
            status_code=400,
            detail="A message participant must be the advertisement owner",
        )
    if db.get(User, data.sender_id) is None or db.get(User, data.recipient_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    message = message_repo.create(
        db,
        ad_id=data.ad_id,
        sender_id=data.sender_id,
        recipient_id=data.recipient_id,
        text=data.text.strip(),
    )
    if not message.text:
        db.rollback()
        raise HTTPException(status_code=422, detail="Message text cannot be blank")
    db.commit()
    db.refresh(message)
    return message


@router.get("/users/{user_id}/messages", response_model=list[MessageRead])
def get_user_messages(
    user_id: int,
    ad_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return message_repo.get_for_user(db, user_id, ad_id=ad_id)


@router.patch("/messages/{message_id}/read", response_model=MessageRead)
def mark_message_read(message_id: int, recipient_id: int = Query(gt=0), db: Session = Depends(get_db)):
    message = db.get(Message, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.recipient_id != recipient_id:
        raise HTTPException(status_code=403, detail="Only the recipient can mark a message as read")
    message.is_read = True
    db.commit()
    db.refresh(message)
    return message
