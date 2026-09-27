from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.session import create_session, end_session, get_all_sessions, get_session_by_id
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_roles
from app.models.user import User, UserRole
from app.schemas.session import CyberSessionCreate, CyberSessionEnd, CyberSessionRead

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

STAFF_ROLES = (UserRole.CASHIER, UserRole.ADMIN)


@router.post(
    "",
    response_model=CyberSessionRead,
    status_code=201,
    dependencies=[Depends(require_roles(*STAFF_ROLES))],
)
def create_session_endpoint(
    session_in: CyberSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_session(db, cashier_id=current_user.id, session_in=session_in)


@router.get("", response_model=list[CyberSessionRead], dependencies=[Depends(require_roles(*STAFF_ROLES))])
def list_sessions(db: Session = Depends(get_db)):
    return get_all_sessions(db)


@router.patch(
    "/{session_id}/end",
    response_model=CyberSessionRead,
    dependencies=[Depends(require_roles(*STAFF_ROLES))],
)
def end_session_endpoint(
    session_id: int,
    end_in: CyberSessionEnd,
    db: Session = Depends(get_db),
):
    session = get_session_by_id(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    updated, error = end_session(db, session, end_in.end_time)
    if error is not None:
        raise HTTPException(status_code=400, detail=error)
    return updated