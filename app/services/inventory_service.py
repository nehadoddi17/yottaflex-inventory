
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import InventoryBalance
from app.services.inventory import calculate_atp


def get_inventory_atp(
    session: Session,
    sku_id: int,
    location_id: int,
) -> dict:
    statement = select(InventoryBalance).where(
        InventoryBalance.sku_id == sku_id,
        InventoryBalance.location_id == location_id,
    )

    balance = session.scalar(statement)

    if balance is None:
        raise LookupError("No inventory balance found for this SKU and location.")

    atp = calculate_atp(
        on_hand=balance.on_hand,
        reserved=balance.reserved,
        blocked=balance.blocked,
        safety_stock=balance.safety_stock,
        approved_inbound=0,
    )

    return {
        "sku_id": balance.sku_id,
        "location_id": balance.location_id,
        "on_hand": balance.on_hand,
        "reserved": balance.reserved,
        "blocked": balance.blocked,
        "safety_stock": balance.safety_stock,
        "approved_inbound": 0,
        "available_to_promise": atp,
    }
