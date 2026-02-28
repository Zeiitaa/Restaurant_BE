from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.Orders.orders_schema import OrdersCreate, OrdersResponse, OrdersUpdateStatus, DetailedOrderBase, MonthlyStatsResponse, TopMenuResponse
from app.API.Orders.orders_service import OrdersService
from ormModels import Orders, paymentStatus
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
import midtransclient
import time

load_dotenv()

# --- SETUP MIDTRANS CORE API ---

server_key = os.getenv("MIDTRANS_SERVER_KEY", "").strip()
client_key = os.getenv("MIDTRANS_CLIENT_KEY", "").strip()

core_api = midtransclient.CoreApi(
    is_production=False,
    server_key=server_key, 
    client_key=client_key  
)


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

@router.get("/preparing", response_model=List[OrdersResponse])
def get_preparing_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return OrdersService.get_preparing_orders(db)

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
    # Catat ID staff/kasir yang melakukan update
    current_staff_id = current_user.id if hasattr(current_user, "id") else None
    return OrdersService.update_order_status(
        db=db, 
        order_id=order_id, 
        status_data=status_data, 
        current_staff_id=current_staff_id
    )

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

@router.post("/{order_id}/generate-qris")
def generate_qris(
    order_id: int,
    db: Session = Depends(get_db),
):
    try:
        # 1. Query Order
        order = db.query(Orders).filter(Orders.id == order_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # 2. Check Payment Status
        if order.payment_status == paymentStatus.paid or str(order.payment_status) == "paid":
             raise HTTPException(status_code=400, detail="Order is already paid")
             
        # 3. Generate Unique Midtrans Order ID
        timestamp = int(time.time())
        midtrans_order_id = f"ORDER-{order_id}-{timestamp}"
        
        # 4. Prepare Payload
        customer_name = order.guest_name if order.guest_name else "Guest"
        
        # Ensure gross_amount is int and > 0
        gross_amount = int(order.total_amount)
        if gross_amount <= 0:
            raise HTTPException(status_code=400, detail="Total amount must be greater than 0")

        payload = {
            "payment_type": "gopay",
            "transaction_details": {
                "order_id": midtrans_order_id,
                "gross_amount": gross_amount
            },
            "customer_details": {
                "first_name": customer_name
            }
        }
        
        # 5. Execute Charge
        charge_response = core_api.charge(payload)
        
        # 6. Parse Response for QR Code URL
        qr_image_url = None
        actions = charge_response.get("actions", [])
        for action in actions:
            if action.get("name") == "generate-qr-code":
                qr_image_url = action.get("url")
                break
                
        if not qr_image_url:
            raise HTTPException(
                status_code=500, 
                detail="Gagal mendapatkan URL QRIS dari respon Midtrans. Pastikan metode pembayaran aktif."
            )

        # 7. Return JSON Response
        return {
            "message": "QRIS generated successfully",
            "original_order_id": order_id,
            "midtrans_order_id": midtrans_order_id,
            "total_amount": int(order.total_amount),
            "qr_image_url": qr_image_url,
            "midtrans_response": charge_response 
        }

    except midtransclient.error_midtrans.MidtransAPIError as e:
        raise HTTPException(status_code=500, detail=f"Midtrans API Error: {e.message}")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
