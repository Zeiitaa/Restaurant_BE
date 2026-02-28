from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import getDB
from app.API.Upstock import update_stock_service
from app.models.Update_Stock.upstock_schema import UpstockCreate, UpstockResponse
from ormModels import Users, UserRole
from app.core.auth import get_current_user, require_role

router = APIRouter(prefix="/upstock", tags=["upstock"])

# get all
@router.get("/", response_model=list[UpstockResponse], dependencies=[Depends(require_role(UserRole.admin, UserRole.manager))])
def get_all_upstock(db: Session = Depends(getDB)):
    return update_stock_service.get_all_upstock(db)

# get by id
@router.get("/{id}", response_model=UpstockResponse, dependencies=[Depends(require_role(UserRole.admin, UserRole.manager))])
def get_upstock_by_id(id: int, db: Session = Depends(getDB)):
    return update_stock_service.get_upstock_by_id(db, id)

# create update stock
@router.post("/", response_model=UpstockResponse)
def create_upstock(
    request: UpstockCreate, 
    db: Session = Depends(getDB),
    current_user: Users = Depends(require_role(UserRole.admin, UserRole.manager))
):
    # rekam log user yang melakukan update stock
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is updating stock for Menu ID: {request.menu_id} (+{request.stock_after} qty)")
    
    # pastikan user id nya benar dan tercatat sesuai user yang login
    request.users_id = current_user.id
    
    return update_stock_service.create_upstock_id(db, request)

