from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cyber_session import CyberSession
from app.schemas.session import CyberSessionCreate


def create_session(db: Session, cashier_id: int, session_in: CyberSessionCreate) -> CyberSession:
    session = CyberSession(
        client_name=session_in.client_name,
        id_number=session_in.id_number,
        terminal_number=session_in.terminal_number,
        start_time=session_in.start_time,
        logged_by_cashier_id=cashier_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_all_sessions(db: Session) -> list[CyberSession]:
    stmt = select(CyberSession).order_by(CyberSession.start_time.desc())
    return list(db.execute(stmt).scalars().all())


def get_session_by_id(db: Session, session_id: int) -> CyberSession | None:
    return db.get(CyberSession, session_id)


def end_session(db: Session, session: CyberSession, end_time: datetime) -> tuple[CyberSession | None, str | None]:
    if session.end_time is not None:
        return None, "Session has already been ended"
    if end_time < session.start_time:
        return None, "End time cannot be before start time"
    session.end_time = end_time
    db.commit()
    db.refresh(session)
    return session, None