from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.service_request import get_request_by_id, get_request_by_tracking_code
from app.dependencies.auth import get_current_user_optional
from app.models.service_request import ServiceRequest
from app.models.user import User, UserRole


class RequestAccess:
    """Represents whoever is allowed into this request's thread — either a
    guest (via tracking code) or a staff member (via role), never both."""

    def __init__(self, service_request: ServiceRequest, staff_user: User | None):
        self.service_request = service_request
        self.staff_user = staff_user

    @property
    def is_guest(self) -> bool:
        return self.staff_user is None


def get_request_access(
    request_id: int,
    x_tracking_code: str | None = Header(default=None),
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> RequestAccess:
    service_request = get_request_by_id(db, request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    # Staff path: a valid, role-appropriate logged-in user is always allowed in.
    if current_user is not None and current_user.role in (UserRole.CASHIER, UserRole.ADMIN):
        return RequestAccess(service_request, staff_user=current_user)

    # Guest path: the tracking code sent must match *this specific* request.
    if x_tracking_code is not None:
        matched = get_request_by_tracking_code(db, x_tracking_code)
        if matched is not None and matched.id == service_request.id:
            return RequestAccess(service_request, staff_user=None)

    # Neither path succeeded — same 404 used everywhere else for "you don't get to know this exists."
    raise HTTPException(status_code=404, detail="Request not found")