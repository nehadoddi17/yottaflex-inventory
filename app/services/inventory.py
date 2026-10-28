
def calculate_atp(
    on_hand: int,
    reserved: int,
    blocked: int,
    safety_stock: int,
    approved_inbound: int = 0,
) -> int:
    """Calculate available-to-promise inventory."""

    quantities = {
        "on_hand": on_hand,
        "reserved": reserved,
        "blocked": blocked,
        "safety_stock": safety_stock,
        "approved_inbound": approved_inbound,
    }

    for name, quantity in quantities.items():
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise ValueError(f"{name} must be an integer.")

        if quantity < 0:
            raise ValueError(f"{name} cannot be negative.")

    if reserved + blocked + safety_stock > on_hand:
        raise ValueError(
            "Reserved, blocked, and safety stock cannot exceed on-hand stock."
        )

    return on_hand - reserved - blocked - safety_stock + approved_inbound
