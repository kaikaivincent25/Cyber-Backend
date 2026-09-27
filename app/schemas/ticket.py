from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.service_ticket import TicketStatus
from decimal import Decimal

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    service_id: int
    description: str
    # No client_id, status, assigned_staff_id, or fees here.
    # client_id comes from the authenticated user (Step 4+).
    # status always starts at PENDING server-side.
    # fees are copied from the Service's estimates server-side at creation.


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    assigned_staff_id: int | None
    service_id: int
    description: str
    status: TicketStatus
    government_fee: Decimal
    service_fee: Decimal
    created_at: datetime
    updated_at: datetime


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketFeeUpdate(BaseModel):
    government_fee: Decimal | None = None
    service_fee: Decimal | None = None


class TicketAssign(BaseModel):
    assigned_staff_id: int


class TicketFeeUpdate(BaseModel):
    government_fee: Decimal | None = Field(default=None, ge=0)
    service_fee: Decimal | None = Field(default=None, ge=0)
