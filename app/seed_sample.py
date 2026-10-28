
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import SessionLocal
from app.models import (
    Product,
    SKU,
    Location,
    InventoryBalance,
    Order,
    OrderLine,
    InventoryMovement,
)


def seed_sample_data():
    with SessionLocal() as session:
        # 1. Create or retrieve the product
        product = session.scalar(
            select(Product).where(
                Product.name == "Sample Water Bottle"
            )
        )

        if product is None:
            product = Product(
                name="Sample Water Bottle",
                category="Accessories",
            )
            session.add(product)
            session.flush()

        # 2. Create or retrieve the SKU
        sku = session.scalar(
            select(SKU).where(
                SKU.sku_code == "SKU-000001"
            )
        )

        if sku is None:
            sku = SKU(
                sku_code="SKU-000001",
                product_id=product.id,
                unit_price=299.00,
            )
            session.add(sku)
            session.flush()

        # 3. Create or retrieve the location
        location = session.scalar(
            select(Location).where(
                Location.location_code == "LOC-000001"
            )
        )

        if location is None:
            location = Location(
                location_code="LOC-000001",
                name="Hyderabad Main Store",
                location_type="store",
            )
            session.add(location)
            session.flush()

        # 4. Create the initial inventory balance if needed
        balance = session.scalar(
            select(InventoryBalance).where(
                InventoryBalance.sku_id == sku.id,
                InventoryBalance.location_id == location.id,
            )
        )

        if balance is None:
            balance = InventoryBalance(
                sku_id=sku.id,
                location_id=location.id,
                on_hand=100,
                reserved=15,
                blocked=5,
                safety_stock=10,
            )
            session.add(balance)

        # 5. Create or retrieve the sample order
        order = session.scalar(
            select(Order).where(
                Order.order_code == "ORD-2026-000001"
            )
        )

        if order is None:
            order = Order(
                order_code="ORD-2026-000001",
                status="created",
                channel="online",
                fulfillment_location_id=location.id,
                created_at=datetime.now(timezone.utc),
            )
            session.add(order)
            session.flush()

        # 6. Create the order line if needed
        order_line = session.scalar(
            select(OrderLine).where(
                OrderLine.order_id == order.id,
                OrderLine.sku_id == sku.id,
            )
        )

        if order_line is None:
            order_line = OrderLine(
                order_id=order.id,
                sku_id=sku.id,
                quantity=10,
            )
            session.add(order_line)

        # 7. Create the opening inventory movement if needed
        opening_movement = session.scalar(
            select(InventoryMovement).where(
                InventoryMovement.movement_code
                == "MOV-2026-OPEN-000001"
            )
        )

        if opening_movement is None:
            opening_movement = InventoryMovement(
                movement_code="MOV-2026-OPEN-000001",
                sku_id=sku.id,
                location_id=location.id,
                movement_type="opening_balance",
                quantity=100,
                occurred_at=datetime(
                    2026, 10, 27, tzinfo=timezone.utc
                ),
            )
            session.add(opening_movement)

        # 8. Save all changes
        session.commit()

        print(
            f"Sample data ready: {sku.sku_code}, "
            f"{location.location_code}"
        )


if __name__ == "__main__":
    seed_sample_data()

