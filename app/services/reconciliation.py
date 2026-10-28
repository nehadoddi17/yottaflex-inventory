
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import InventoryBalance, InventoryMovement


# Movement types that affect physical on-hand stock.
INCREASE_TYPES = {"opening_balance", "receipt", "return"}
DECREASE_TYPES = {"sale"}


def reconcile_inventory(
    session: Session,
    sku_id: int,
    location_id: int,
) -> dict:
    """Compare recorded on-hand stock with movement-derived stock."""

    balance = session.scalar(
        select(InventoryBalance).where(
            InventoryBalance.sku_id == sku_id,
            InventoryBalance.location_id == location_id,
        )
    )

    if balance is None:
        raise LookupError("Inventory balance not found.")

    movements = session.scalars(
        select(InventoryMovement)
        .where(
            InventoryMovement.sku_id == sku_id,
            InventoryMovement.location_id == location_id,
        )
        .order_by(InventoryMovement.occurred_at, InventoryMovement.id)
    ).all()

    if not movements:
        return {
            "sku_id": sku_id,
            "location_id": location_id,
            "recorded_on_hand": balance.on_hand,
            "expected_on_hand": None,
            "discrepancy": None,
            "status": "insufficient_history",
            "message": "No movement history exists for this inventory.",
        }

    opening_movements = [
        movement
        for movement in movements
        if movement.movement_type == "opening_balance"
    ]

    if len(opening_movements) != 1:
        return {
            "sku_id": sku_id,
            "location_id": location_id,
            "recorded_on_hand": balance.on_hand,
            "expected_on_hand": None,
            "discrepancy": None,
            "status": "invalid_history",
            "message": (
                "Exactly one opening_balance movement is required "
                "to reconcile this inventory."
            ),
        }

    expected_on_hand = 0

    for movement in movements:
        if movement.movement_type in INCREASE_TYPES:
            expected_on_hand += movement.quantity
        elif movement.movement_type in DECREASE_TYPES:
            expected_on_hand -= movement.quantity
        elif movement.movement_type == "transfer_out":
            expected_on_hand -= movement.quantity
        elif movement.movement_type == "transfer_in":
            expected_on_hand += movement.quantity
        elif movement.movement_type == "damage":
            # Damaged units remain physically on hand but become blocked.
            continue
        else:
            return {
                "sku_id": sku_id,
                "location_id": location_id,
                "recorded_on_hand": balance.on_hand,
                "expected_on_hand": None,
                "discrepancy": None,
                "status": "invalid_history",
                "message": (
                    f"Unsupported movement type: {movement.movement_type}"
                ),
            }

    discrepancy = balance.on_hand - expected_on_hand

    return {
        "sku_id": sku_id,
        "location_id": location_id,
        "recorded_on_hand": balance.on_hand,
        "expected_on_hand": expected_on_hand,
        "discrepancy": discrepancy,
        "status": "matched" if discrepancy == 0 else "mismatch",
    }
