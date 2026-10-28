from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    InventoryBalance,
    InventoryMovement,
    Shipment,
    ShipmentLine,
)


def dispatch_transfer(
    session: Session,
    shipment_code: str,
    sku_id: int,
    source_location_id: int,
    destination_location_id: int,
    quantity: int,
) -> Shipment:
    """Dispatch stock from a source location into transit."""

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be an integer.")

    if quantity <= 0:
        raise ValueError("Transfer quantity must be positive.")

    if source_location_id == destination_location_id:
        raise ValueError("Source and destination must be different.")

    try:
        existing = session.scalar(
            select(Shipment).where(
                Shipment.shipment_code == shipment_code
            )
        )
        if existing is not None:
            raise ValueError("Shipment code already exists.")

        source = session.scalar(
            select(InventoryBalance)
            .where(
                InventoryBalance.sku_id == sku_id,
                InventoryBalance.location_id == source_location_id,
            )
            .with_for_update()
        )

        if source is None:
            raise LookupError("Source inventory balance not found.")

        available = (
            source.on_hand
            - source.reserved
            - source.blocked
            - source.safety_stock
        )

        if quantity > available:
            raise ValueError("Insufficient available stock for transfer.")

        now = datetime.now(timezone.utc)

        source.on_hand -= quantity

        shipment = Shipment(
            shipment_code=shipment_code,
            order_id=None,
            source_location_id=source_location_id,
            destination_location_id=destination_location_id,
            status="in_transit",
            shipped_at=now,
        )
        session.add(shipment)
        session.flush()

        line = ShipmentLine(
            shipment_id=shipment.id,
            sku_id=sku_id,
            quantity=quantity,
        )
        session.add(line)

        movement = InventoryMovement(
            movement_code=_next_movement_code(session, now),
            sku_id=sku_id,
            location_id=source_location_id,
            movement_type="transfer_out",
            quantity=quantity,
            occurred_at=now,
        )
        session.add(movement)

        session.commit()
        session.refresh(shipment)
        return shipment

    except Exception:
        session.rollback()
        raise


def receive_transfer(
    session: Session,
    shipment_code: str,
) -> Shipment:
    """Receive an in-transit shipment into its destination inventory."""

    try:
        shipment = session.scalar(
            select(Shipment)
            .where(Shipment.shipment_code == shipment_code)
            .with_for_update()
        )

        if shipment is None:
            raise LookupError("Shipment not found.")

        if shipment.status != "in_transit":
            raise ValueError("Only in-transit shipments can be received.")

        lines = session.scalars(
            select(ShipmentLine).where(
                ShipmentLine.shipment_id == shipment.id
            )
        ).all()

        if not lines:
            raise ValueError("Shipment has no transfer lines.")

        now = datetime.now(timezone.utc)

        for line in lines:
            destination = session.scalar(
                select(InventoryBalance)
                .where(
                    InventoryBalance.sku_id == line.sku_id,
                    InventoryBalance.location_id
                    == shipment.destination_location_id,
                )
                .with_for_update()
            )

            if destination is None:
                raise LookupError(
                    "Destination inventory balance not found."
                )

            destination.on_hand += line.quantity

            movement = InventoryMovement(
                movement_code=_next_movement_code(session, now),
                sku_id=line.sku_id,
                location_id=shipment.destination_location_id,
                movement_type="transfer_in",
                quantity=line.quantity,
                occurred_at=now,
            )
            session.add(movement)

        shipment.status = "received"
        shipment.received_at = now

        session.commit()
        session.refresh(shipment)
        return shipment

    except Exception:
        session.rollback()
        raise


def _next_movement_code(session: Session, now: datetime) -> str:
    latest_id = session.scalar(
        select(InventoryMovement.id)
        .order_by(InventoryMovement.id.desc())
        .limit(1)
    ) or 0

    return f"MOV-{now.year}-{latest_id + 1:08d}"