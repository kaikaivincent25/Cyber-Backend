import enum
from datetime import datetime

from sqlalchemy import String, Text, Enum as SAEnum, Numeric, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from sqlalchemy.dialects.postgresql import JSONB

    

class ServiceCategory(str, enum.Enum):
    PASSPORT_AID = "passport_aid"
    ECITIZEN_SERVICE = "ecitizen_service"
    SOFTWARE_DEV = "software_dev"
    OTHER = "other"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[ServiceCategory] = mapped_column(SAEnum(ServiceCategory))
    description: Mapped[str] = mapped_column(Text)

    # Estimated fees shown on the public catalog/landing page
    estimated_government_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    estimated_service_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    requires_physical_visit: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    form_schema: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)