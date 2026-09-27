from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service
from app.models.service_ticket import ServiceTicket, TicketStatus
from app.models.user import User, UserRole
from app.schemas.ticket import TicketAssign, TicketCreate, TicketStatusUpdate
from app.schemas.ticket import TicketFeeUpdate


VALID_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.PENDING: {TicketStatus.ASSIGNED, TicketStatus.CANCELLED},
    TicketStatus.ASSIGNED: {TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED},
    TicketStatus.IN_PROGRESS: {TicketStatus.AWAITING_PAYMENT, TicketStatus.CANCELLED},
    TicketStatus.AWAITING_PAYMENT: {TicketStatus.COMPLETED, TicketStatus.CANCELLED},
    TicketStatus.COMPLETED: set(),
    TicketStatus.CANCELLED: set(),
}


def create_ticket(db: Session, client_id: int, ticket_in: TicketCreate) -> ServiceTicket | None:
    service = db.get(Service, ticket_in.service_id)
    if service is None or not service.is_active:
        return None

    ticket = ServiceTicket(
        client_id=client_id,
        service_id=service.id,
        description=ticket_in.description,
        government_fee=service.estimated_government_fee,
        service_fee=service.estimated_service_fee,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket_by_id(db: Session, ticket_id: int) -> ServiceTicket | None:
    return db.get(ServiceTicket, ticket_id)


def get_tickets_for_client(db: Session, client_id: int) -> list[ServiceTicket]:
    stmt = (
        select(ServiceTicket)
        .where(ServiceTicket.client_id == client_id)
        .order_by(ServiceTicket.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_all_tickets(db: Session) -> list[ServiceTicket]:
    stmt = select(ServiceTicket).order_by(ServiceTicket.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def assign_ticket(
    db: Session, ticket: ServiceTicket, assign_in: TicketAssign, staff_user: User
) -> ServiceTicket | None:
    if staff_user.role not in (UserRole.CASHIER, UserRole.ADMIN):
        return None
    ticket.assigned_staff_id = assign_in.assigned_staff_id
    if ticket.status == TicketStatus.PENDING:
        ticket.status = TicketStatus.ASSIGNED
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(
    db: Session, ticket: ServiceTicket, status_in: TicketStatusUpdate
) -> tuple[ServiceTicket | None, str | None]:
    allowed_next = VALID_TRANSITIONS.get(ticket.status, set())
    if status_in.status not in allowed_next:
        return None, f"Cannot move ticket from '{ticket.status.value}' to '{status_in.status.value}'"
    ticket.status = status_in.status
    db.commit()
    db.refresh(ticket)
    return ticket, None


def update_ticket_fees(db: Session, ticket: ServiceTicket, fee_in: TicketFeeUpdate) -> ServiceTicket:
    update_data = fee_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket