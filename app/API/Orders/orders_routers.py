from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.Orders.orders_schema import OrdersCreate, OrdersResponse, OrdersUpdateStatus, DetailedOrderBase, MonthlyStatsResponse, TopMenuResponse
from app.API.Orders.orders_service import OrdersService
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrdersResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrdersCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Determine staff_id (null if ordered by customer)
    staff_id = current_user["id"] if current_user["role"] != "customer" else None
    return OrdersService.create_order(db=db, order_data=order_data, staff_id=staff_id)

@router.get("/", response_model=List[OrdersResponse])
def get_all_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return OrdersService.get_all_orders(db)

@router.get("/stats/monthly", response_model=MonthlyStatsResponse)
def get_monthly_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Only staff/admin can see stats
    if current_user["role"] not in ["admin", "manager"]:
         raise HTTPException(status_code=403, detail="Not enough permissions to view statistics")
    return OrdersService.get_monthly_stats(db)

@router.get("/stats/top-menus", response_model=List[TopMenuResponse])
def get_top_menus(
    limit: int = 5, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    # Only staff/admin can see stats
    if current_user["role"] not in ["admin", "manager"]:
         raise HTTPException(status_code=403, detail="Not enough permissions to view statistics")
    return OrdersService.get_top_menus(db, limit=limit)

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
    # Match valid roles from ormModels.py
    if current_user["role"] not in ["admin", "manager", "waiters", "employee"]:
         raise HTTPException(status_code=403, detail="Not enough permissions")
    return OrdersService.free_table(db, order_id)
