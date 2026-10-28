
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import InventoryBalance, Reservation, OrderLine


def create_reservation(
    session: Session,
    order_line_id: int,
    location_id: int,
    quantity: int,
    expires_at: datetime,
) -> Reservation:
    """Reserve available stock for an order line."""

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be an integer.")

    if quantity <= 0:
        raise ValueError("Reservation quantity must be positive.")

    if expires_at.tzinfo is None or expires_at.utcoffset() is None:
        raise ValueError("Expiry time must include a timezone.")

    if expires_at <= datetime.now(timezone.utc):
        raise ValueError("Expiry time must be in the future.")

    try:
        order_line = session.get(OrderLine, order_line_id)

        if order_line is None:
            raise LookupError("Order line not found.")

        if quantity > order_line.quantity:
            raise ValueError("Reservation exceeds the order-line quantity.")

        balance = session.scalar(
            select(InventoryBalance)
            .where(
                InventoryBalance.sku_id == order_line.sku_id,
                InventoryBalance.location_id == location_id,
            )
            .with_for_update()
        )

        if balance is None:
            raise LookupError("Inventory balance not found.")

        available = (
            balance.on_hand
            - balance.reserved
            - balance.blocked
            - balance.safety_stock
        )

        if quantity > available:
            raise ValueError("Insufficient available stock to reserve.")

        reservation = Reservation(
            reservation_code=(
                f"RES-LINE-{order_line_id}-"
                f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
            ),
            order_line_id=order_line.id,
            sku_id=order_line.sku_id,
            location_id=location_id,
            quantity=quantity,
            status="active",
            expires_at=expires_at,
        )

        balance.reserved += quantity
        session.add(reservation)
        session.commit()
        session.refresh(reservation)

        return reservation

    except Exception:
        session.rollback()
        raise


def expire_reservations(session: Session) -> int:
    """Release active reservations whose expiry time has passed."""

    now = datetime.now(timezone.utc)
    expired_count = 0

    try:
        reservations = session.scalars(
            select(Reservation)
            .where(
                Reservation.status == "active",
                Reservation.expires_at <= now,
            )
            .with_for_update()
        ).all()

        for reservation in reservations:
            balance = session.scalar(
                select(InventoryBalance)
                .where(
                    InventoryBalance.sku_id == reservation.sku_id,
                    InventoryBalance.location_id == reservation.location_id,
                )
                .with_for_update()
            )

            if balance is None:
                raise LookupError(
                    f"Balance missing for reservation {reservation.reservation_code}"
                )

            if balance.reserved < reservation.quantity:
                raise ValueError(
                    f"Reserved balance is inconsistent for "
                    f"{reservation.reservation_code}"
                )

            balance.reserved -= reservation.quantity
            reservation.status = "expired"
            expired_count += 1

        session.commit()
        return expired_count

    except Exception:
        session.rollback()
        raise
