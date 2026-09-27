from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.ticket import create_ticket, get_ticket_by_id, get_tickets_for_client
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.ticket import TicketCreate, TicketRead
from app.crud.ticket import (
    assign_ticket,
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    get_tickets_for_client,
    update_ticket_status,
)
from app.dependencies.permissions import require_roles
from app.schemas.ticket import TicketAssign, TicketCreate, TicketRead, TicketStatusUpdate
from app.crud.ticket import update_ticket_fees
from app.schemas.ticket import TicketFeeUpdate



router = APIRouter(prefix="/api/tickets", tags=["tickets"])

STAFF_ROLES = (UserRole.CASHIER, UserRole.ADMIN)


@router.post("", response_model=TicketRead, status_code=201)
def submit_ticket(
    ticket_in: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = create_ticket(db, client_id=current_user.id, ticket_in=ticket_in)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return ticket


@router.get("/me", response_model=list[TicketRead])
def list_my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_tickets_for_client(db, client_id=current_user.id)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = get_ticket_by_id(db, ticket_id)

    is_owner = ticket is not None and ticket.client_id == current_user.id
    is_staff = current_user.role in STAFF_ROLES

    if ticket is None or not (is_owner or is_staff):
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket

@router.get("", response_model=list[TicketRead], dependencies=[Depends(require_roles(UserRole.CASHIER, UserRole.ADMIN))])
def list_all_tickets(db: Session = Depends(get_db)):
    return get_all_tickets(db)


@router.patch(
    "/{ticket_id}/assign",
    response_model=TicketRead,
    dependencies=[Depends(require_roles(UserRole.CASHIER, UserRole.ADMIN))],
)
def assign_ticket_endpoint(
    ticket_id: int,
    assign_in: TicketAssign,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    updated = assign_ticket(db, ticket, assign_in, staff_user=current_user)
    if updated is None:
        raise HTTPException(status_code=403, detail="Not authorized to assign tickets")
    return updated


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketRead,
    dependencies=[Depends(require_roles(UserRole.CASHIER, UserRole.ADMIN))],
)
def update_ticket_status_endpoint(
    ticket_id: int,
    status_in: TicketStatusUpdate,
    db: Session = Depends(get_db),
):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    updated, error = update_ticket_status(db, ticket, status_in)
    if error is not None:
        raise HTTPException(status_code=400, detail=error)
    return updated


@router.patch(
    "/{ticket_id}/fees",
    response_model=TicketRead,
    dependencies=[Depends(require_roles(UserRole.CASHIER, UserRole.ADMIN))],
)
def update_ticket_fees_endpoint(
    ticket_id: int,
    fee_in: TicketFeeUpdate,
    db: Session = Depends(get_db),
):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return update_ticket_fees(db, ticket, fee_in)