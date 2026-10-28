
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import InventoryBalance, InventoryMovement


def record_movement(
    session: Session,
    sku_id: int,
    location_id: int,
    movement_type: str,
    quantity: int,
) -> InventoryMovement:
    """Record a stock change and update its balance atomically."""

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be an integer.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    allowed_types = {"receipt", "sale", "return", "damage"}

    if movement_type not in allowed_types:
        raise ValueError("Unsupported movement type.")

    try:
        balance = session.scalar(
            select(InventoryBalance)
            .where(
                InventoryBalance.sku_id == sku_id,
                InventoryBalance.location_id == location_id,
            )
            .with_for_update()
        )

        if balance is None:
            raise LookupError("Inventory balance not found.")

        if movement_type == "receipt":
            balance.on_hand += quantity

        elif movement_type == "sale":
            available = (
                balance.on_hand
                - balance.reserved
                - balance.blocked
                - balance.safety_stock
            )

            if quantity > available:
                raise ValueError("Sale exceeds available stock.")

            balance.on_hand -= quantity

        elif movement_type == "return":
            balance.on_hand += quantity

        elif movement_type == "damage":
            if quantity > balance.on_hand - balance.blocked:
                raise ValueError("Damage quantity exceeds unblocked stock.")

            balance.blocked += quantity

        movement_count = session.scalar(
            select(InventoryMovement.id)
            .order_by(InventoryMovement.id.desc())
            .limit(1)
        )

        next_id = (movement_count or 0) + 1
        movement_code = f"MOV-{datetime.now(timezone.utc).year}-{next_id:08d}"

        movement = InventoryMovement(
            movement_code=movement_code,
            sku_id=sku_id,
            location_id=location_id,
            movement_type=movement_type,
            quantity=quantity,
            occurred_at=datetime.now(timezone.utc),
        )

        session.add(movement)
        session.flush()
        session.commit()
        session.refresh(movement)

        return movement

    except Exception:
        session.rollback()
        raise
