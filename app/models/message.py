from datetime import datetime

from sqlalchemy import Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("service_requests.id"), index=True)

    # Exactly one of these two identifies the sender — never both, never neither.
    sender_staff_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_from_guest: Mapped[bool] = mapped_column(Boolean, default=False)

    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())