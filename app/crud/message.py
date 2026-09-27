from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.message import Message


def create_message(db: Session, request_id: int, body: str, sender_staff_id: int | None) -> Message:
    message = Message(
        request_id=request_id,
        sender_staff_id=sender_staff_id,
        is_from_guest=sender_staff_id is None,
        body=body,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages_for_request(db: Session, request_id: int) -> list[Message]:
    stmt = select(Message).where(Message.request_id == request_id).order_by(Message.created_at.asc())
    return list(db.execute(stmt).scalars().all())