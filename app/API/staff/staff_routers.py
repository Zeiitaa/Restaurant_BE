from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.Staff.staff_schema import staffCreate, staffUpdate, staffResponse, staffRegister
from ormModels import staffRole
from app.core.auth import get_current_staff, require_role
from app.API.staff import staff_service
import database

router = APIRouter(
    prefix="/staff",
    tags=["staff"]
)

@router.get("/profile", response_model=staffResponse)
def get_current_staff_profile(current_staff = Depends(get_current_staff)):
    return staffResponse.model_validate(current_staff)

# create
@router.post("/", response_model=staffResponse)
def create_staff(request:staffCreate, db:Session = Depends(database.getDB)):
    return staff_service.create_staff(db, request)

# get all
@router.get("/", response_model=list[staffResponse], dependencies=[Depends(require_role(staffRole.admin, staffRole.manager))])
def get_all_staff(db:Session = Depends(database.getDB)):
    return staff_service.get_all_staff(db)

# get by ID
@router.get("/{id}", response_model=staffResponse, dependencies=[Depends(require_role(staffRole.admin, staffRole.manager))])
def get_staff_by_id(id:int, db:Session = Depends(database.getDB)):
    return staff_service.get_all_staff(id, db)

# deactivate
@router.patch("/deactivate/{id}", response_model=staffResponse, dependencies=[Depends(require_role(staffRole.admin, staffRole.manager))])
def deactivate_staff_by_id(id: int, request:staffUpdate, db:Session = Depends(database.getDB)):
    return staff_service.deactivate_staff(id, request, db)

# register
@router.post("/register", response_model=staffResponse, dependencies=[Depends(require_role(staffRole.admin, staffRole.manager))])
def register_staff(request:staffRegister, db:Session = Depends(database.getDB)):
    return staff_service.register_staff(db, request)

@router.patch("/{id}", response_model=staffResponse, dependencies=[Depends(require_role(staffRole.admin, staffRole.manager))])
def update_user_by_id(id:int, request:staffUpdate, db:Session = Depends(database.getDB)):
    return staff_service.update_staff(id, request, db)