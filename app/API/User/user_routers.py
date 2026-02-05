from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.User.user_schema import UserCreate, UserUpdate, UserResponse, UserRegister, UserDeact
from ormModels import UserRole
from app.core.auth import get_current_user, require_position
from app.API.User import user_service
import database

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.get("/profile", response_model=UserResponse)
def get_current_user_profile(current_user = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

# create
@router.post("/", response_model=UserResponse)
def create_user(request:UserCreate, db:Session = Depends(database.getDB)):
    return user_service.create_user(db, request)

# get all
@router.get("/", response_model=list[UserResponse], dependencies=[Depends(require_position(UserRole.admin, UserRole.manager))])
def get_all_user(db:Session = Depends(database.getDB)):
    return user_service.get_all_user(db)

# get by ID
@router.get("/{id}", response_model=UserResponse, dependencies=[Depends(require_position(UserRole.admin, UserRole.manager))])
def get_user_by_id(id:int, db:Session = Depends(database.getDB)):
    return user_service.get_all_user(id, db)

# deactivate
@router.patch("/deactivate/{id}", response_model=UserResponse, dependencies=[Depends(require_position(UserRole.admin))])
def deactivate_user_by_id(id: int, request:UserDeact, db:Session = Depends(database.getDB)):
    return user_service.deactivate_user(id, request, db)

@router.patch("/{id}", response_model=UserResponse, dependencies=[Depends(require_position(UserRole.admin, UserRole.manager))])
def update_user_by_id(id:int, request:UserUpdate, db:Session = Depends(database.getDB)):
    return user_service.update_user(id, request, db)