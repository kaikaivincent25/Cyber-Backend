from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CyberSessionCreate(BaseModel):
    client_name: str
    id_number: str
    terminal_number: int
    start_time: datetime
    # No logged_by_cashier_id here — derived from the authenticated
    # cashier's own user id server-side (Step 6's pattern), never
    # accepted as client input.


class CyberSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_name: str
    id_number: str
    terminal_number: int
    start_time: datetime
    end_time: datetime | None
    logged_by_cashier_id: int


class CyberSessionEnd(BaseModel):
    end_time: datetime