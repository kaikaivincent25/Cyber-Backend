from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.message import create_message, get_messages_for_request
from app.dependencies.request_access import RequestAccess, get_request_access
from app.schemas.message import MessageCreate, MessageRead

router = APIRouter(prefix="/api/requests/{request_id}/messages", tags=["messages"])


@router.get("", response_model=list[MessageRead])
def list_messages(
    access: RequestAccess = Depends(get_request_access),
    db: Session = Depends(get_db),
):
    return get_messages_for_request(db, access.service_request.id)


@router.post("", response_model=MessageRead, status_code=201)
def post_message(
    message_in: MessageCreate,
    access: RequestAccess = Depends(get_request_access),
    db: Session = Depends(get_db),
):
    sender_staff_id = access.staff_user.id if not access.is_guest else None
    return create_message(db, access.service_request.id, message_in.body, sender_staff_id)