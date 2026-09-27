from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.service import create_service, update_service
from app.dependencies.permissions import require_roles
from app.models.service import Service
from app.models.user import UserRole
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from app.crud.service import get_all_services_admin


router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db)):
    stmt = select(Service).where(Service.is_active == True)  # noqa: E712
    return db.execute(stmt).scalars().all()


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None or not service.is_active:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("", response_model=ServiceRead, status_code=201, dependencies=[Depends(require_roles(UserRole.ADMIN))])
def create_service_endpoint(service_in: ServiceCreate, db: Session = Depends(get_db)):
    return create_service(db, service_in)


@router.patch("/{service_id}", response_model=ServiceRead, dependencies=[Depends(require_roles(UserRole.ADMIN))])
def update_service_endpoint(service_id: int, service_in: ServiceUpdate, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return update_service(db, service, service_in)



@router.get(
    "/admin/all",
    response_model=list[ServiceRead],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def list_all_services_admin(db: Session = Depends(get_db)):
    return get_all_services_admin(db)