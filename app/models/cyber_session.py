from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CyberSession(Base):
    __tablename__ = "cyber_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Deliberately NOT a foreign key to users — walk-in cyber café clients
    # are typically not registered accounts, just logged for CA compliance.
    client_name: Mapped[str] = mapped_column(String(150))
    id_number: Mapped[str] = mapped_column(String(20), index=True)
    terminal_number: Mapped[int] = mapped_column(Integer)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    logged_by_cashier_id: Mapped[int] = mapped_column(ForeignKey("users.id"))