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

class UserStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    resign = "resign"

class UserRole(enum.Enum):
    admin = "admin"
    manager =  "manager"
    waiters = "waiters"
    employee = "employee"
    customer = "customer"

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

    order = relationship("Orders", back_populates="table")


class Category(base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    menus = relationship("Menu", back_populates="category")

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
    category = relationship("Category", back_populates="menus")

class Update_stock(base):
    __tablename__ = "update_stocks"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menu.id"), nullable=False)
    stock_after = Column(Integer, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    users_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    menu = relationship("Menu", back_populates="update")
    user = relationship("Users", back_populates="stock_updates")

class Users(base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)

    user_detail = relationship("UserDetails", back_populates="users", uselist=False)
    staff_detail = relationship("StaffDetails", back_populates="users", uselist=False)
    staff_orders = relationship("Orders", back_populates="staff", foreign_keys="[Orders.staff_id]") 
    customer_orders = relationship("Orders", back_populates="customer", foreign_keys="[Orders.customer_id]") 
    stock_updates = relationship("Update_stock", back_populates="user")

class UserDetails(base):
    __tablename__ = "userDetails"

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(String, nullable=False)

    users = relationship("Users", back_populates="user_detail")

class StaffDetails(base):
    __tablename__ = "staffDetails"

    id = Column(Integer, primary_key=True, index=True)
    users_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(String, nullable=False)

    users = relationship("Users", back_populates="staff_detail")

class DetailedOrder(base):
    __tablename__ = "detailedOrder"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
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
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guest_name = Column(String, nullable=True)
    total_amount = Column(DECIMAL(10,2), nullable=False)
    discount = Column(DECIMAL(10,2), nullable=False, default=0)
    amount_paid = Column(DECIMAL(10,2), nullable=True)
    change_amount = Column(DECIMAL(10,2), nullable=True)
    method = Column(Enum(paymentType), nullable=False, default=paymentType.cash)
    payment_status = Column(Enum(paymentStatus), nullable=False, default=paymentStatus.unpaid)
    order_status = Column(Enum(orderStatus), nullable=False, default=orderStatus.preparing)

    table = relationship("Table", back_populates="order")
    staff = relationship("Users", back_populates="staff_orders", foreign_keys=[staff_id])
    customer = relationship("Users", back_populates="customer_orders", foreign_keys=[customer_id])
    details = relationship("DetailedOrder", back_populates="order")