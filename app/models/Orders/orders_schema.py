from pydantic import BaseModel, Field, ConfigDict

from typing import Optional

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

# base
class OrdersBase(BaseModel):
    # date, staff, total amount, status itu dari service
    table_id: int = Field(..., description="Please input Table ID", examples=[1])
    customer_id: Optional[int] = Field(None, description="Please input customer ID", examples=[1])
    guest_name: Optional[str] = Field(None, description="Please input the guest name")
    method: paymentType = paymentType.cash

class OrdersCreate(OrdersBase):
    pass

# update Order
class OrdersUpdate(BaseModel):
    table_id: Optional[int] = None
    customer_id: Optional[int] = None
    guest_name: Optional[str] = None
    method: Optional[paymentType] = None

# update status order
class OrdersUpdateStatus(BaseModel):
    order_status: orderStatus

# response
class OrdersResponse(OrdersBase):
    id: int
    date: datetime
    staff_id: int
    order_type: orderType
    order_status: orderStatus
    payment_status: paymentStatus
    total_amount: float

    model_config = ConfigDict(from_attributes=True)

#  delete (soft)
class OrdersDelete(BaseModel):
    id: int
    orderStatus: orderStatus.cancelled



    
