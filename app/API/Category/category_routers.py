from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import getDB
from app.API.Category import category_service
from app.models.Category.category_schema import CategoryCreate, CategoryResponse, CategoryUpdate
from ormModels import Users, UserRole
from app.core.auth import get_current_user, require_role

router = APIRouter(prefix="/category", tags=["category"])

# get all
@router.get("/", response_model=list[CategoryResponse])
def get_all_category(db: Session = Depends(getDB)):
    return category_service.get_all_category(db)

# get by id
@router.get("/{id}", response_model=CategoryResponse)
def get_category_by_id(id: int, db: Session = Depends(getDB)):
    return category_service.get_category_by_id(db, id)

# create
@router.post("/", response_model=CategoryResponse)
def create_category(
    request: CategoryCreate, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin, UserRole.manager))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is creating a new category: {request.name}")
    return category_service.create_category(db, request)

# update
@router.patch("/{id}", response_model=CategoryResponse)
def update_category(
    id: int, 
    request: CategoryUpdate, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin, UserRole.manager))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is updating category ID: {id}")
    return category_service.update_category(db, id, request)

# delete
@router.delete("/{id}")
def delete_category(
    id: int, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is deleting category ID: {id}")
    category_service.delete_category(db, id)
    return {"detail": "Category successfully deleted"}