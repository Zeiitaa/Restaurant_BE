# IMPORT
from sqlalchemy import String, Integer, ForeignKey, Date, DateTime, Column, Enum, DECIMAL
from sqlalchemy.orm import relationship

from database import base

import enum

from datetime import datetime, timezone

# Declare Enum
class tableStatus(enum.Enum):
    available = "available"
    booked = "booked"

class staffStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    resign = "resign"

class staffPosition(enum.Enum):
    admin = "admin"
    manager =  "manager"
    waiters = "waiters"
    employee = "employee"

class menuStatus(enum.Enum):    
    available = "available"   
    outofstock = "outOfStock"

class orderType(enum.Enum):
    dinein = "dinein"
    takeaway = "takeaway"

class orderStatus(enum.Enum):
    preparing = "preparing"
    served = "served"
    cancelled = "cancelled"

class paymentStatus(enum.Enum):
    unpaid = "unpaid"
    paid = "paid"

class paymentType(enum.Enum):
    cash = "cash"
    qris = "qris"


# Declare table

class Table(base):
    __tablename__ = "tables"

    # ISI Table
    id = Column(Integer, primary_key=True, index=True)
    table_code = Column(Integer, nullable=False, unique=True)
    status = Column(Enum(tableStatus), nullable=False, default=tableStatus.available) 
    capacity = Column(Integer, nullable=False)

    tables = relationship("Orders", back_populates="table")


class Category(base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    category = relationship("Menu", back_populates="menu")

class Menu(base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    daily_portion = Column(Integer, nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    status = Column(Enum(menuStatus), nullable=False, default=menuStatus.available)
    category_id = Column(Integer, ForeignKey("categories.id"),nullable=False)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)

    menus = relationship("DetailedOrder", back_populates="menu")
    update = relationship("Update_stock", back_populates="menu")
    menu = relationship("Category", back_populates="category")

class Update_stock(base):
    __tablename__ = "update_stocks"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menu.id"), nullable=False)
    stock_after = Column(Integer, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    menu = relationship("Menu", back_populates="update")

class Staff(base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    status = Column(Enum(staffStatus), nullable=False, default=staffStatus.inactive)
    position = Column(Enum(staffPosition), nullable=False, default=staffPosition.employee)

    orders = relationship("Orders", back_populates="staff")

class DetailedOrder(base):
    __tablename__ = "detailedOrder"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id") )
    menu_id = Column(Integer, ForeignKey("menu.id"), nullable=False)
    notes = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    order_type = Column(Enum(orderType), nullable=False, default=orderType.dinein)
    subtotal = Column(DECIMAL(10,2), nullable=False)


    order = relationship("Orders", back_populates="details")
    menu = relationship("Menu", back_populates="menus")

class Orders(base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    total_amount = Column(DECIMAL(10,2), nullable=False)
    method = Column(Enum(paymentType), nullable=False, default=paymentType.cash)
    payment_status = Column(Enum(paymentStatus), nullable=False, default=paymentStatus.unpaid)
    order_status = Column(Enum(orderStatus), nullable=False, default=orderStatus.preparing)

    table = relationship("Table", back_populates="tables")
    staff = relationship("Staff", back_populates="orders")
    details = relationship("DetailedOrder", back_populates="order")