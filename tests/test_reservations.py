
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.reservations import expire_reservations


def test_expired_reservation_releases_reserved_stock():
    session = MagicMock()

    reservation = SimpleNamespace(
        reservation_code="RES-ORD-2026-000001-01",
        sku_id=1,
        location_id=1,
        quantity=5,
        status="active",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )

    balance = SimpleNamespace(
        sku_id=1,
        location_id=1,
        on_hand=20,
        reserved=5,
        blocked=2,
        safety_stock=3,
    )

    session.scalars.return_value.all.return_value = [reservation]
    session.scalar.return_value = balance

    expired_count = expire_reservations(session)

    assert expired_count == 1
    assert reservation.status == "expired"
    assert balance.reserved == 0

    # ATP before expiry: 20 - 5 - 2 - 3 = 10
    # ATP after expiry: 20 - 0 - 2 - 3 = 15
    atp_before = 20 - 5 - 2 - 3
    atp_after = 20 - balance.reserved - 2 - 3

    assert atp_before == 10
    assert atp_after == 15
    session.commit.assert_called_once()