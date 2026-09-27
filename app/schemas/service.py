from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.service import ServiceCategory


class ServiceCreate(BaseModel):
    name: str
    category: ServiceCategory
    description: str
    estimated_government_fee: Decimal = Decimal("0")
    estimated_service_fee: Decimal = Decimal("0")
    requires_physical_visit: bool = False


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: ServiceCategory
    description: str
    estimated_government_fee: Decimal
    estimated_service_fee: Decimal
    requires_physical_visit: bool
    is_active: bool


class ServiceUpdate(BaseModel):
    name: str | None = None
    category: ServiceCategory | None = None
    description: str | None = None
    estimated_government_fee: Decimal | None = None
    estimated_service_fee: Decimal | None = None
    requires_physical_visit: bool | None = None
    is_active: bool | None = None