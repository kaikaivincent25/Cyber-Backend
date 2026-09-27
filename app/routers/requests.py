from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.service_request import create_service_request
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestSubmitted
from app.crud.service_request import get_request_by_tracking_code
from app.schemas.service_request import ServiceRequestRead
from app.crud.service_request import (
    assign_request,
    get_all_requests,
    get_request_by_id,
    update_request_fees,
    update_request_status,
)
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_roles
from app.models.user import User, UserRole
from app.schemas.service_request import RequestAssign, RequestFeeUpdate, RequestStatusUpdate

STAFF_ROLES = (UserRole.CASHIER, UserRole.ADMIN)


router = APIRouter(prefix="/api/requests", tags=["requests"])


@router.post("", response_model=ServiceRequestSubmitted, status_code=201)
def submit_request(request_in: ServiceRequestCreate, db: Session = Depends(get_db)):
    service_request, error = create_service_request(db, request_in)

    if error == "Service not found":
        raise HTTPException(status_code=404, detail=error)
    if error is not None:
        raise HTTPException(status_code=400, detail=error)

    return ServiceRequestSubmitted(
        tracking_code=service_request.tracking_code,
        status=service_request.status,
        message="Your request has been submitted. Save this tracking code to check your status later.",
    )

@router.get("/track/{tracking_code}", response_model=ServiceRequestRead)
def track_request(tracking_code: str, db: Session = Depends(get_db)):
    service_request = get_request_by_tracking_code(db, tracking_code)
    if service_request is None:
        raise HTTPException(status_code=404, detail="No request found with that tracking code")
    return service_request



@router.get("", response_model=list[ServiceRequestRead], dependencies=[Depends(require_roles(*STAFF_ROLES))])
def list_all_requests(db: Session = Depends(get_db)):
    return get_all_requests(db)


@router.get("/{request_id}", response_model=ServiceRequestRead, dependencies=[Depends(require_roles(*STAFF_ROLES))])
def get_request(request_id: int, db: Session = Depends(get_db)):
    service_request = get_request_by_id(db, request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return service_request


@router.patch(
    "/{request_id}/assign",
    response_model=ServiceRequestRead,
    dependencies=[Depends(require_roles(*STAFF_ROLES))],
)
def assign_request_endpoint(
    request_id: int,
    assign_in: RequestAssign,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service_request = get_request_by_id(db, request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    updated = assign_request(db, service_request, assign_in, staff_user=current_user)
    if updated is None:
        raise HTTPException(status_code=403, detail="Not authorized to assign requests")
    return updated


@router.patch(
    "/{request_id}/status",
    response_model=ServiceRequestRead,
    dependencies=[Depends(require_roles(*STAFF_ROLES))],
)
def update_request_status_endpoint(
    request_id: int,
    status_in: RequestStatusUpdate,
    db: Session = Depends(get_db),
):
    service_request = get_request_by_id(db, request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    updated, error = update_request_status(db, service_request, status_in)
    if error is not None:
        raise HTTPException(status_code=400, detail=error)
    return updated


@router.patch(
    "/{request_id}/fees",
    response_model=ServiceRequestRead,
    dependencies=[Depends(require_roles(*STAFF_ROLES))],
)
def update_request_fees_endpoint(
    request_id: int,
    fee_in: RequestFeeUpdate,
    db: Session = Depends(get_db),
):
    service_request = get_request_by_id(db, request_id)
    if service_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return update_request_fees(db, service_request, fee_in)