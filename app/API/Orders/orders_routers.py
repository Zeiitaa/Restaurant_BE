from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.Orders.orders_schema import OrdersCreate, OrdersResponse, OrdersUpdateStatus, DetailedOrderBase
from app.API.Orders.orders_service import OrdersService
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrdersResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrdersCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Only staff/admin can create orders (or mobile client with token)
    return OrdersService.create_order(db=db, order_data=order_data, staff_id=current_user["id"])

@router.get("/", response_model=List[OrdersResponse])
def get_all_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return OrdersService.get_all_orders(db)

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
    if current_user["role"] not in ["admin", "waiters", "manager", "employee"]:
         raise HTTPException(status_code=403, detail="Not enough permissions to add items")
    return OrdersService.add_items_to_order(db, order_id, new_items)

@router.post("/{order_id}/clear-table")
def clear_table(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # This might be restricted to staff
    if current_user["role"] not in ["admin", "staff"]:
         raise HTTPException(status_code=403, detail="Not enough permissions")
    return OrdersService.free_table(db, order_id)
