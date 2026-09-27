from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    body: str


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    sender_staff_id: int | None
    is_from_guest: bool
    body: str
    created_at: datetime