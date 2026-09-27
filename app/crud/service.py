from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate
from sqlalchemy import select
from app.models.service import Service

def create_service(db: Session, service_in: ServiceCreate) -> Service:
    service = Service(**service_in.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def update_service(db: Session, service: Service, service_in: ServiceUpdate) -> Service:
    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service



def get_all_services_admin(db: Session) -> list[Service]:
    stmt = select(Service).order_by(Service.created_at.desc())
    return list(db.execute(stmt).scalars().all())