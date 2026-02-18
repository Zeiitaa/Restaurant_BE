from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, func
from fastapi import HTTPException, status
from ormModels import Orders, DetailedOrder, Menu, Table, Users
from app.models.Orders.orders_schema import OrdersCreate, OrdersUpdate, OrdersUpdateStatus, DetailedOrderBase
from app.models.Table.table_schema import TableStatus
from datetime import datetime, timezone, timedelta
from typing import List

class OrdersService:
    @staticmethod
    def create_order(db: Session, order_data: OrdersCreate, staff_id: int = None):
        # 1. Check Table 
        table = db.execute(select(Table).where(Table.id == order_data.table_id)).scalar_one_or_none()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        
        if table.status == TableStatus.booked:
            raise HTTPException(status_code=400, detail="Table is already occupied")

        total_amount = 0
        detailed_orders = []

        # 2. Process Items
        for item in order_data.items:
            # Get Menu with pessimistic locking to ensure stock doesn't change during calculation
            menu_item = db.execute(
                select(Menu).where(Menu.id == item.menu_id).with_for_update()
            ).scalar_one_or_none()

            if not menu_item:
                raise HTTPException(status_code=404, detail=f"Menu item {item.menu_id} not found")
            
            if menu_item.status == "outOfStock":
                raise HTTPException(status_code=400, detail=f"Menu {menu_item.name} is out of stock")

            if menu_item.daily_portion < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough stock for {menu_item.name}. Remaining: {menu_item.daily_portion}"
                )

            # Deduct stock
            menu_item.daily_portion -= item.quantity
            if menu_item.daily_portion == 0:
                menu_item.status = "outOfStock"

            subtotal = menu_item.price * item.quantity
            total_amount += subtotal

            detailed_orders.append(DetailedOrder(
                menu_id=item.menu_id,
                quantity=item.quantity,
                notes=item.notes,
                order_type=item.order_type,
                subtotal=subtotal
            ))

        # 3. Create Order
        new_order = Orders(
            table_id=order_data.table_id,
            customer_id=order_data.customer_id,
            guest_name=order_data.guest_name,
            staff_id=staff_id,
            date=datetime.now(timezone.utc),
            total_amount=total_amount,
            method=order_data.method,
            order_status="preparing",
            payment_status="unpaid"
        )
        
        db.add(new_order)
        db.flush() # Get the new_order.id

        # 4. Link details to order
        for detail in detailed_orders:
            detail.order_id = new_order.id
            db.add(detail)

        # 5. Update Table Status
        table.status = TableStatus.booked

        db.commit()
        db.refresh(new_order)
        
        # Reload with details for response
        return db.execute(
            select(Orders)
            .where(Orders.id == new_order.id)
            .options(joinedload(Orders.details))
        ).unique().scalar_one()

    @staticmethod
    def get_all_orders(db: Session):
        return db.execute(
            select(Orders).options(joinedload(Orders.details))
        ).unique().scalars().all()

    @staticmethod
    def get_order_by_id(db: Session, order_id: int):
        order = db.execute(
            select(Orders)
            .where(Orders.id == order_id)
            .options(joinedload(Orders.details))
        ).unique().scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    @staticmethod
    def update_order_status(db: Session, order_id: int, status_data: OrdersUpdateStatus):
        # Gunakan query dengan join ke Table untuk mempermudah pembebasan meja
        order = db.execute(
            select(Orders).where(Orders.id == order_id)
        ).scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if status_data.order_status:
            order.order_status = status_data.order_status
        
        if status_data.method:
            order.method = status_data.method
        
        if status_data.payment_status:
            # Logika Otomatis: Jika status berubah jadi 'paid', bebaskan meja
            if status_data.payment_status == "paid" and order.payment_status != "paid":
                table = db.execute(select(Table).where(Table.id == order.table_id)).scalar_one_or_none()
                if table:
                    table.status = TableStatus.available
            
            order.payment_status = status_data.payment_status

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def add_items_to_order(db: Session, order_id: int, new_items: List[DetailedOrderBase]):
        # 1. Get existing order with pessimistic lock
        order = db.execute(
            select(Orders).where(Orders.id == order_id).with_for_update()
        ).scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.payment_status == "paid":
            raise HTTPException(status_code=400, detail="Cannot add items to a paid order")

        added_total = 0

        # 2. Process New Items
        for item in new_items:
            menu_item = db.execute(
                select(Menu).where(Menu.id == item.menu_id).with_for_update()
            ).scalar_one_or_none()

            if not menu_item:
                raise HTTPException(status_code=404, detail=f"Menu item {item.menu_id} not found")
            
            if menu_item.status == "outOfStock":
                raise HTTPException(status_code=400, detail=f"Menu {menu_item.name} is out of stock")

            if menu_item.daily_portion < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough stock for {menu_item.name}. Remaining: {menu_item.daily_portion}"
                )

            # Deduct stock
            menu_item.daily_portion -= item.quantity
            if menu_item.daily_portion == 0:
                menu_item.status = "outOfStock"

            subtotal = menu_item.price * item.quantity
            added_total += subtotal

            # Add to DetailedOrder
            db.add(DetailedOrder(
                order_id=order.id,
                menu_id=item.menu_id,
                quantity=item.quantity,
                notes=item.notes,
                order_type=item.order_type,
                subtotal=subtotal
            ))

        # 3. Update Order Total
        order.total_amount += added_total
        
        db.commit()
        db.refresh(order)
        
        # Return complete order with updated details
        return db.execute(
            select(Orders)
            .where(Orders.id == order.id)
            .options(joinedload(Orders.details))
        ).unique().scalar_one()

    @staticmethod
    def free_table(db: Session, order_id: int):
        order = db.execute(select(Orders).where(Orders.id == order_id)).scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        table = db.execute(select(Table).where(Table.id == order.table_id)).scalar_one_or_none()
        if table:
            table.status = TableStatus.available
            db.commit()
        return {"message": f"Table {table.table_code} is now available"}

    @staticmethod
    def get_monthly_stats(db: Session):
        one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Count total orders (all orders in the last 30 days)
        total_orders_query = select(func.count(Orders.id)).where(Orders.date >= one_month_ago)
        total_orders = db.execute(total_orders_query).scalar() or 0
        
        # Total revenue (sum of paid orders in the last 30 days)
        total_revenue_query = select(func.sum(Orders.total_amount)).where(
            Orders.date >= one_month_ago,
            Orders.payment_status == "paid"
        )
        total_revenue = db.execute(total_revenue_query).scalar() or 0
        
        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue)
        }

    @staticmethod
    def get_top_menus(db: Session, limit: int = 5):
        one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        query = (
            select(
                Menu.id,
                Menu.name,
                func.sum(DetailedOrder.quantity).label("total_quantity")
            )
            .join(DetailedOrder, Menu.id == DetailedOrder.menu_id)
            .join(Orders, DetailedOrder.order_id == Orders.id)
            .where(Orders.date >= one_month_ago)
            .group_by(Menu.id, Menu.name)
            .order_by(func.sum(DetailedOrder.quantity).desc())
            .limit(limit)
        )
        
        results = db.execute(query).all()
        
        return [
            {"menu_id": row.id, "name": row.name, "total_quantity": int(row.total_quantity)}
            for row in results
        ]
