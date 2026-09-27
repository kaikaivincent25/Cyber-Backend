from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.service_request import RequestStatus
from decimal import Decimal
from pydantic import Field

from app.models.service_request import RequestStatus



class ServiceRequestCreate(BaseModel):
    service_id: int
    guest_name: str
    guest_phone: str
    guest_email: EmailStr | None = None
    form_data: dict[str, Any] = {}
    # No tracking_code, status, fees, assigned_staff_id — every one of
    # those is server-derived, same non-negotiable rule as every other
    # resource in this project.


class ServiceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tracking_code: str
    service_id: int
    assigned_staff_id: int | None
    guest_name: str
    guest_phone: str
    guest_email: str | None
    form_data: dict[str, Any]
    status: RequestStatus
    government_fee: Decimal
    service_fee: Decimal
    created_at: datetime
    updated_at: datetime


class ServiceRequestSubmitted(BaseModel):
    """What we hand back to the guest right after submission — deliberately
    smaller than ServiceRequestRead, built around the one thing that matters
    to them at this moment: their tracking code."""

    tracking_code: str
    status: RequestStatus
    message: str

class RequestAssign(BaseModel):
    assigned_staff_id: int


class RequestStatusUpdate(BaseModel):
    status: RequestStatus


class RequestFeeUpdate(BaseModel):
    government_fee: Decimal | None = Field(default=None, ge=0)
    service_fee: Decimal | None = Field(default=None, ge=0)