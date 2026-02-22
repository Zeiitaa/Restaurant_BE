from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime

# ENUM
class orderType(str, Enum):
    dinein = "dinein"
    takeaway = "takeaway"

class orderStatus(str, Enum):
    preparing = "preparing"
    served = "served"
    cancelled = "cancelled"

class paymentStatus(str, Enum):
    unpaid = "unpaid"
    paid = "paid"

class paymentType(str, Enum):
    cash  = "cash"
    qris = "qris"

# Simplified Menu Schema for Order Response
class MenuSimpleResponse(BaseModel):
    id: int
    name: str
    price: float
    image: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Detailed Order Schema
class DetailedOrderBase(BaseModel):
    menu_id: int
    quantity: int = Field(..., gt=0)
    notes: Optional[str] = None
    order_type: orderType = orderType.dinein

class DetailedOrderResponse(DetailedOrderBase):
    id: int
    subtotal: float
    menu: Optional[MenuSimpleResponse] = None
    model_config = ConfigDict(from_attributes=True)

# base
class OrdersBase(BaseModel):
    table_id: int = Field(..., description="Please input Table ID", examples=[1])
    customer_id: Optional[int] = Field(None, description="Please input customer ID", examples=[1])
    staff_id: Optional[int] = Field(None, description="Please input staff ID", examples=[1])
    guest_name: Optional[str] = Field(None, description="Please input the guest name")
    method: paymentType = paymentType.cash

class OrdersCreate(OrdersBase):
    items: List[DetailedOrderBase]
    discount: Optional[float] = Field(0.0, ge=0, description="Discount amount (not percentage)")

# update Order
class OrdersUpdate(BaseModel):
    table_id: Optional[int] = None
    customer_id: Optional[int] = None
    staff_id: Optional[int] = None
    guest_name: Optional[str] = None
    method: Optional[paymentType] = None

# update status order
class OrdersUpdateStatus(BaseModel):
    order_status: Optional[orderStatus] = None
    payment_status: Optional[paymentStatus] = None
    method: Optional[paymentType] = None
    amount_paid: Optional[float] = Field(None, ge=0, description="Amount paid by the customer")

# response
class OrdersResponse(OrdersBase):
    id: int
    date: datetime
    staff_id: Optional[int] = None
    order_status: orderStatus
    payment_status: paymentStatus
    total_amount: float
    discount: float = 0.0
    amount_paid: Optional[float] = None
    change_amount: Optional[float] = None
    details: List[DetailedOrderResponse]

    model_config = ConfigDict(from_attributes=True)

class MonthlyStatsResponse(BaseModel):
    total_orders: int
    total_revenue: float
    total_orders_change: float
    total_revenue_change: float

class TopMenuResponse(BaseModel):
    menu_id: int
    name: str
    total_quantity: int



    
