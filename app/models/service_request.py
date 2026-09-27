import enum
from datetime import datetime

from sqlalchemy import String, Text, Enum as SAEnum, DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    AWAITING_PAYMENT = "awaiting_payment"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    tracking_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)

    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    assigned_staff_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Guest contact — no account, no FK to users. Phone-primary per our locked-in default.
    guest_name: Mapped[str] = mapped_column(String(150))
    guest_phone: Mapped[str] = mapped_column(String(20))
    guest_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # The guest's actual answers, shaped by that Service's form_schema at submission time.
    form_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    status: Mapped[RequestStatus] = mapped_column(SAEnum(RequestStatus), default=RequestStatus.PENDING)

    government_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    service_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())