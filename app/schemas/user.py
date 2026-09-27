from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole
from pydantic import BaseModel, Field
from app.models.user import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    password: str
    # Note: no `role` field here — every self-registered user becomes
    # UserRole.CLIENT by default, set server-side. Staff accounts are
    # created differently (Step 8's admin-only user creation), never
    # via public self-signup accepting an arbitrary role.


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone_number: str
    role: UserRole
    is_active: bool


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None





class StaffCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    password: str
    role: UserRole  # constrained to CASHIER/ADMIN at the router level, not here — see note below


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)