from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate

from app.core.security import verify_password
from app.models.user import UserRole
from app.schemas.user import PasswordChange, StaffCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        hashed_password=hash_password(user_in.password),
        role=UserRole.CLIENT,  # always CLIENT on public registration — never trust client-supplied role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



def create_staff_user(db: Session, staff_in: StaffCreate) -> User:
    user = User(
        full_name=staff_in.full_name,
        email=staff_in.email,
        phone_number=staff_in.phone_number,
        hashed_password=hash_password(staff_in.password),
        role=staff_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_all_staff(db: Session) -> list[User]:
    stmt = select(User).where(User.role.in_([UserRole.CASHIER, UserRole.ADMIN])).order_by(User.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def update_password(db: Session, user: User, change_in: PasswordChange) -> tuple[bool, str | None]:
    if not verify_password(change_in.current_password, user.hashed_password):
        return False, "Current password is incorrect"
    user.hashed_password = hash_password(change_in.new_password)
    db.commit()
    return True, None


def update_profile(db: Session, user: User, update_in: UserUpdate) -> User:
    update_data = update_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user