from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.user import (
    create_staff_user,
    get_all_staff,
    get_user_by_email,
    update_password,
    update_profile,
)
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_roles
from app.models.user import User, UserRole
from app.schemas.user import PasswordChange, StaffCreate, UserRead, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
def update_my_profile(
    update_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_profile(db, current_user, update_in)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_my_password(
    change_in: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success, error = update_password(db, current_user, change_in)
    if not success:
        raise HTTPException(status_code=400, detail=error)


@router.get("/staff", response_model=list[UserRead], dependencies=[Depends(require_roles(UserRole.ADMIN))])
def list_staff(db: Session = Depends(get_db)):
    return get_all_staff(db)


@router.post(
    "/staff",
    response_model=UserRead,
    status_code=201,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def create_staff(staff_in: StaffCreate, db: Session = Depends(get_db)):
    if staff_in.role not in (UserRole.CASHIER, UserRole.ADMIN):
        raise HTTPException(status_code=400, detail="Staff accounts must be role 'cashier' or 'admin'")

    existing = get_user_by_email(db, staff_in.email)
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    return create_staff_user(db, staff_in)