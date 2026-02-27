from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, func
from fastapi import HTTPException, status
from ormModels import Orders, DetailedOrder, Menu, Table, Users, paymentStatus, orderStatus, menuStatus
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
            
            # Use value if it's an enum
            menu_item_status = menu_item.status.value if hasattr(menu_item.status, "value") else menu_item.status
            if menu_item_status == "outOfStock":
                raise HTTPException(status_code=400, detail=f"Menu {menu_item.name} is out of stock")

            if float(menu_item.daily_portion) < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough stock for {menu_item.name}. Remaining: {menu_item.daily_portion}"
                )

            # Deduct stock
            menu_item.daily_portion -= item.quantity
            if float(menu_item.daily_portion) <= 0:
                menu_item.status = menuStatus.outofstock

            subtotal = float(menu_item.price) * item.quantity
            total_amount += subtotal

            detailed_orders.append(DetailedOrder(
                menu_id=item.menu_id,
                quantity=item.quantity,
                notes=item.notes,
                order_type=item.order_type,
                subtotal=subtotal
            ))

        # 3. Create Order
        discount_percent = float(order_data.discount or 0)
        # Hitung diskon dulu baru pajak 10%: (Subtotal * (1 - Discount%)) * 1.1
        subtotal = float(total_amount)
        discounted_amount = subtotal * (1 - (discount_percent / 100))
        final_total = round(discounted_amount * 1.1, 2)
        
        new_order = Orders(
            table_id=order_data.table_id,
            customer_id=order_data.customer_id,
            guest_name=order_data.guest_name,
            staff_id=staff_id,
            date=datetime.now(timezone.utc),
            total_amount=final_total,
            discount=discount_percent,
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
            .options(
                joinedload(Orders.details).joinedload(DetailedOrder.menu),
                joinedload(Orders.staff),
                joinedload(Orders.customer)
            )
        ).unique().scalar_one()

    @staticmethod
    def get_all_orders(db: Session):
        return db.execute(
            select(Orders).options(
                joinedload(Orders.details).joinedload(DetailedOrder.menu),
                joinedload(Orders.staff),
                joinedload(Orders.customer)
            )
        ).unique().scalars().all()

    @staticmethod
    def get_preparing_orders(db: Session):
        """Returns orders that are preparing but not yet served."""
        return db.execute(
            select(Orders)
            .where(
                Orders.order_status == orderStatus.preparing,
                Orders.payment_status == paymentStatus.unpaid
            )
            .options(
                joinedload(Orders.details).joinedload(DetailedOrder.menu),
                joinedload(Orders.staff),
                joinedload(Orders.customer)
            )
        ).unique().scalars().all()

    @staticmethod
    def get_served_orders(db: Session):
        """Returns orders that are served but not yet paid (ready for payment processing)."""
        return db.execute(
            select(Orders)
            .where(
                Orders.order_status == orderStatus.served,
                Orders.payment_status == paymentStatus.unpaid
            )
            .options(
                joinedload(Orders.details).joinedload(DetailedOrder.menu),
                joinedload(Orders.staff),
                joinedload(Orders.customer)
            )
        ).unique().scalars().all()

    @staticmethod
    def get_order_by_id(db: Session, order_id: int):
        order = db.execute(
            select(Orders)
            .where(Orders.id == order_id)
            .options(
                joinedload(Orders.details).joinedload(DetailedOrder.menu),
                joinedload(Orders.staff),
                joinedload(Orders.customer)
            )
        ).unique().scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    @staticmethod
    def update_order_status(db: Session, order_id: int, status_data: OrdersUpdateStatus, current_staff_id: int = None):
        # Gunakan query dengan join ke Table untuk mempermudah pembebasan meja
        order = db.execute(
            select(Orders).where(Orders.id == order_id).options(
                joinedload(Orders.details),
                joinedload(Orders.staff),
                joinedload(Orders.customer)
            )
        ).unique().scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Jika staff melakukan update (terutama saat bayar), catat staff_id nya
        if current_staff_id:
            order.staff_id = current_staff_id

        if status_data.order_status:
            order.order_status = status_data.order_status
        
        if status_data.method:
            order.method = status_data.method

        if status_data.discount is not None:
            # Jika ada update diskon, kita hitung ulang total_amount yang disimpan
            order.discount = status_data.discount
            # Hitung subtotal kotor dari item-item (tanpa pajak/diskon)
            gross_subtotal = sum(float(detail.subtotal) for detail in order.details)
            # Terapkan diskon (%) baru baru pajak (%) 10
            new_final = round((gross_subtotal * (1 - (float(order.discount) / 100))) * 1.1, 2)
            order.total_amount = new_final
        
        if status_data.amount_paid is not None:
            # total_amount di DB sekarang sudah absolute final (udah kena diskon % dan pajak 10)
            final_amount = round(float(order.total_amount), 2)
            if status_data.amount_paid < final_amount:
                raise HTTPException(
                    status_code=400,
                    detail=f"Amount paid ({status_data.amount_paid}) is less than the bill ({final_amount})"
                )
            order.amount_paid = status_data.amount_paid
            order.change_amount = round(status_data.amount_paid - final_amount, 2)

        if status_data.payment_status:
            # Logika Otomatis: Jika status berubah jadi 'paid', bebaskan meja
            if status_data.payment_status == "paid" and order.payment_status != "paid":
                # Validasi amount_paid sudah diisi sebelum mark paid
                if order.amount_paid is None and status_data.amount_paid is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Please provide amount_paid before marking order as paid"
                    )
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
            
            # Use value if it's an enum
            menu_item_status = menu_item.status.value if hasattr(menu_item.status, "value") else menu_item.status
            if menu_item_status == "outOfStock":
                raise HTTPException(status_code=400, detail=f"Menu {menu_item.name} is out of stock")

            if float(menu_item.daily_portion) < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough stock for {menu_item.name}. Remaining: {menu_item.daily_portion}"
                )

            # Deduct stock
            menu_item.daily_portion -= item.quantity
            if float(menu_item.daily_portion) <= 0:
                menu_item.status = menuStatus.outofstock

            subtotal = float(menu_item.price) * item.quantity
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

        # 3. Update Order Total (diskon % dulu baru tambah pajak 10%)
        discount_multiplier = 1 - (float(order.discount or 0) / 100.0)
        added_after_discount_tax = round((float(added_total) * discount_multiplier) * 1.1, 2)
        order.total_amount = float(order.total_amount) + added_after_discount_tax
        
        db.commit()
        db.refresh(order)
        
        # Return complete order with updated details
        return db.execute(
            select(Orders)
            .where(Orders.id == order.id)
            .options(
                joinedload(Orders.details).joinedload(DetailedOrder.menu),
                joinedload(Orders.staff),
                joinedload(Orders.customer)
            )
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
        now = datetime.now(timezone.utc)
        one_month_ago = now - timedelta(days=30)
        two_months_ago = now - timedelta(days=60)
        
        # --- Current Period (Last 30 days) ---
        # Count total orders (all orders in the last 30 days)
        total_orders_query = select(func.count(Orders.id)).where(Orders.date >= one_month_ago)
        total_orders = db.execute(total_orders_query).scalar() or 0
        
        # Total revenue (sum of paid orders in the last 30 days)
        # di database, total_amount sudah absolute final (sudah dipotong diskon & tambah pajak)
        total_revenue_query = select(func.sum(Orders.total_amount)).where(
            Orders.date >= one_month_ago,
            Orders.payment_status == paymentStatus.paid
        )
        total_revenue = db.execute(total_revenue_query).scalar() or 0
        
        # --- Previous Period (30-60 days ago) ---
        prev_orders_query = select(func.count(Orders.id)).where(
            Orders.date >= two_months_ago,
            Orders.date < one_month_ago
        )
        prev_orders = db.execute(prev_orders_query).scalar() or 0
        
        prev_revenue_query = select(func.sum(Orders.total_amount)).where(
            Orders.date >= two_months_ago,
            Orders.date < one_month_ago,
            Orders.payment_status == paymentStatus.paid
        )
        prev_revenue = db.execute(prev_revenue_query).scalar() or 0

        # --- Percentage Calculation ---
        def calculate_percentage_change(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            diff = current - previous
            return (diff / previous) * 100

        orders_change = calculate_percentage_change(total_orders, prev_orders)
        revenue_change = calculate_percentage_change(float(total_revenue), float(prev_revenue))
        
        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "total_orders_change": orders_change,
            "total_revenue_change": revenue_change
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
