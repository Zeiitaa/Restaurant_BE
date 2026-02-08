from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import getDB
from app.API.Menu import menu_service
from app.models.Menu.menu_schema import MenuCreate, MenuResponse, MenuUpdate
from ormModels import Users, UserRole
from app.core.auth import get_current_user, require_role

router = APIRouter(prefix="/menu", tags=["menu"])

# get all
@router.get("/", response_model=list[MenuResponse])
def get_all_menu(db: Session = Depends(getDB)):
    return menu_service.get_all_menu(db)

# get by id
@router.get("/{id}", response_model=MenuResponse)
def get_menu_by_id(id: int, db: Session = Depends(getDB)):
    return menu_service.get_menu_by_id(db, id)

# create
@router.post("/", response_model=MenuResponse)
def create_menu(
    request: MenuCreate, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin, UserRole.manager))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is creating a new menu: {request.name}")
    return menu_service.create_menu(db, request)

# update
@router.patch("/{id}", response_model=MenuResponse)
def update_menu(
    id: int, 
    request: MenuUpdate, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin, UserRole.manager))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is updating menu ID: {id}")
    return menu_service.update_menu(db, request, id)

# soft delete (change status to outofstock)
@router.delete("/{id}", response_model=MenuResponse)
def delete_menu_status(
    id: int, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin, UserRole.manager))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is changing menu ID: {id} status to outOfStock")
    return menu_service.delete_menu(db, id)