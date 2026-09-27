from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.service import Service
from app.models.service_request import ServiceRequest
from app.schemas.service_request import ServiceRequestCreate
from app.utils.form_validation import validate_form_data
from app.utils.tracking_code import generate_tracking_code
from sqlalchemy import select

from app.models.service_request import ServiceRequest, RequestStatus
from app.models.user import User, UserRole
from app.schemas.service_request import RequestAssign, RequestFeeUpdate, RequestStatusUpdate

MAX_TRACKING_CODE_RETRIES = 5

VALID_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
    RequestStatus.PENDING: {RequestStatus.ASSIGNED, RequestStatus.CANCELLED},
    RequestStatus.ASSIGNED: {RequestStatus.IN_PROGRESS, RequestStatus.CANCELLED},
    RequestStatus.IN_PROGRESS: {RequestStatus.AWAITING_PAYMENT, RequestStatus.CANCELLED},
    RequestStatus.AWAITING_PAYMENT: {RequestStatus.COMPLETED, RequestStatus.CANCELLED},
    RequestStatus.COMPLETED: set(),
    RequestStatus.CANCELLED: set(),
}


def get_all_requests(db: Session) -> list[ServiceRequest]:
    stmt = select(ServiceRequest).order_by(ServiceRequest.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_request_by_id(db: Session, request_id: int) -> ServiceRequest | None:
    return db.get(ServiceRequest, request_id)


def assign_request(
    db: Session, service_request: ServiceRequest, assign_in: RequestAssign, staff_user: User
) -> ServiceRequest | None:
    if staff_user.role not in (UserRole.CASHIER, UserRole.ADMIN):
        return None
    service_request.assigned_staff_id = assign_in.assigned_staff_id
    if service_request.status == RequestStatus.PENDING:
        service_request.status = RequestStatus.ASSIGNED
    db.commit()
    db.refresh(service_request)
    return service_request


def update_request_status(
    db: Session, service_request: ServiceRequest, status_in: RequestStatusUpdate
) -> tuple[ServiceRequest | None, str | None]:
    allowed_next = VALID_TRANSITIONS.get(service_request.status, set())
    if status_in.status not in allowed_next:
        return None, f"Cannot move request from '{service_request.status.value}' to '{status_in.status.value}'"
    service_request.status = status_in.status
    db.commit()
    db.refresh(service_request)
    return service_request, None


def update_request_fees(db: Session, service_request: ServiceRequest, fee_in: RequestFeeUpdate) -> ServiceRequest:
    update_data = fee_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service_request, field, value)
    db.commit()
    db.refresh(service_request)
    return service_request


def create_service_request(
    db: Session, request_in: ServiceRequestCreate
) -> tuple[ServiceRequest | None, str | None]:
    service = db.get(Service, request_in.service_id)
    if service is None or not service.is_active:
        return None, "Service not found"

    validation_error = validate_form_data(service.form_schema, request_in.form_data)
    if validation_error is not None:
        return None, validation_error

    last_error = None
    for _ in range(MAX_TRACKING_CODE_RETRIES):
        code = generate_tracking_code()
        service_request = ServiceRequest(
            tracking_code=code,
            service_id=service.id,
            guest_name=request_in.guest_name,
            guest_phone=request_in.guest_phone,
            guest_email=request_in.guest_email,
            form_data=request_in.form_data,
            government_fee=service.estimated_government_fee,
            service_fee=service.estimated_service_fee,
        )
        db.add(service_request)
        try:
            db.commit()
            db.refresh(service_request)
            return service_request, None
        except IntegrityError:
            db.rollback()
            last_error = "Could not generate a unique tracking code"
            continue

    return None, last_error


def get_request_by_tracking_code(db: Session, tracking_code: str) -> ServiceRequest | None:
    stmt = select(ServiceRequest).where(ServiceRequest.tracking_code == tracking_code)
    return db.execute(stmt).scalar_one_or_none()