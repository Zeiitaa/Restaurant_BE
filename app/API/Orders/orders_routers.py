from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.Orders.orders_schema import OrdersCreate, OrdersResponse, OrdersUpdateStatus, DetailedOrderBase, MonthlyStatsResponse, TopMenuResponse
from app.API.Orders.orders_service import OrdersService
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

router = APIRouter(prefix="/orders", tags=["Orders"])

# Manual optional auth dependency to support Guest
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user_optional(token: str = Depends(oauth2_scheme_optional)):
    if not token:
        return None
    try:
        load_dotenv()
        SECRET_KEY = os.getenv("SECRET_KEY")
        ALGORITHM = os.getenv("ALGORITHM")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return {"id": int(user_id), "role": payload.get("role")}
    except JWTError:
        return None  # Invalid token treated as Guest

@router.post("/", response_model=OrdersResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrdersCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    # Determine staff_id or customer_id logic
    staff_id = None
    
    # If user is logged in
    if current_user:
        role = current_user.get("role")
        user_id = current_user.get("id")
        
        if role != "customer":
            # Staff creating order
            staff_id = user_id
        else:
            # Customer creating order, auto-fill customer_id if not provided
            if not order_data.customer_id:
                order_data.customer_id = user_id

    return OrdersService.create_order(db=db, order_data=order_data, staff_id=staff_id)

@router.get("/", response_model=List[OrdersResponse])
def get_all_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return OrdersService.get_all_orders(db)

@router.get("/stats/monthly", response_model=MonthlyStatsResponse)
def get_monthly_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Only staff/admin can see stats
    user_role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if user_role not in ["admin", "manager"]:
         raise HTTPException(status_code=403, detail="Not enough permissions to view statistics")
    return OrdersService.get_monthly_stats(db)

@router.get("/stats/top-menus", response_model=List[TopMenuResponse])
def get_top_menus(
    limit: int = 5, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    # Only staff/admin can see stats
    user_role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if user_role not in ["admin", "manager"]:
         raise HTTPException(status_code=403, detail="Not enough permissions to view statistics")
    return OrdersService.get_top_menus(db, limit=limit)

@router.get("/served", response_model=List[OrdersResponse])
def get_served_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return OrdersService.get_served_orders(db)

@router.get("/{order_id}", response_model=OrdersResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return OrdersService.get_order_by_id(db, order_id)

@router.patch("/{order_id}/status", response_model=OrdersResponse)
def update_order_status(
    order_id: int, 
    status_data: OrdersUpdateStatus, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return OrdersService.update_order_status(db, order_id, status_data)

@router.post("/{order_id}/items", response_model=OrdersResponse)
def add_items_to_order(
    order_id: int,
    new_items: List[DetailedOrderBase],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Staff or Admin can add items to existing order
    user_role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if user_role not in ["admin", "waiters", "manager", "employee"]:
         raise HTTPException(status_code=403, detail="Not enough permissions to add items")
    return OrdersService.add_items_to_order(db, order_id, new_items)

@router.post("/{order_id}/clear-table")
def clear_table(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Match valid roles from ormModels.py
    user_role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if user_role not in ["admin", "manager", "waiters", "employee"]:
         raise HTTPException(status_code=403, detail="Not enough permissions")
    return OrdersService.free_table(db, order_id)
