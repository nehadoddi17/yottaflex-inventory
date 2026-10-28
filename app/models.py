
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)


class SKU(Base):
    __tablename__ = "skus"
    __table_args__ = (
        UniqueConstraint("sku_code", name="uq_skus_sku_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku_code: Mapped[str] = mapped_column(String(30), nullable=False)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    unit_price: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )


class InventoryBalance(Base):
    __tablename__ = "inventory_balances"
    __table_args__ = (
        UniqueConstraint(
            "sku_id", "location_id",
            name="uq_balance_sku_location",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    on_hand: Mapped[int] = mapped_column(Integer, default=0)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    blocked: Mapped[int] = mapped_column(Integer, default=0)
    safety_stock: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    movement_code: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False
    )
    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    movement_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_code: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="created"
    )
    channel: Mapped[str] = mapped_column(
        String(30), nullable=False, default="online"
    )
    fulfillment_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class OrderLine(Base):
    __tablename__ = "order_lines"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_line_quantity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), nullable=False
    )
    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_reservation_quantity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_code: Mapped[str] = mapped_column(
        String(60), unique=True, nullable=False
    )
    order_line_id: Mapped[int] = mapped_column(
        ForeignKey("order_lines.id"), nullable=False
    )
    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="active"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    shipment_code: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id"), nullable=True
    )
    source_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )
    destination_location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="in_transit"
    )
    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ReplenishmentRule(Base):
    __tablename__ = "replenishment_rules"
    __table_args__ = (
        UniqueConstraint(
            "sku_id", "location_id",
            name="uq_replenishment_sku_location",
        ),
        CheckConstraint(
            "reorder_point >= 0",
            name="ck_reorder_point_nonnegative",
        ),
        CheckConstraint(
            "target_stock >= reorder_point",
            name="ck_target_stock_gte_reorder_point",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False)
    target_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=7
    )
