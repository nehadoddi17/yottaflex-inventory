
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.reconciliation import reconcile_inventory


def make_movement(movement_type, quantity):
    return SimpleNamespace(
        movement_type=movement_type,
        quantity=quantity,
    )


def make_session(on_hand, movements):
    session = MagicMock()

    balance = SimpleNamespace(
        on_hand=on_hand,
        reserved=0,
        blocked=0,
        safety_stock=0,
    )

    session.scalar.return_value = balance
    session.scalars.return_value.all.return_value = movements

    return session


def test_reconciliation_matches_movement_history():
    movements = [
        make_movement("opening_balance", 100),
        make_movement("receipt", 20),
        make_movement("sale", 10),
    ]
    session = make_session(on_hand=110, movements=movements)

    result = reconcile_inventory(session, sku_id=1, location_id=1)

    assert result["status"] == "matched"
    assert result["recorded_on_hand"] == 110
    assert result["expected_on_hand"] == 110
    assert result["discrepancy"] == 0


def test_reconciliation_detects_mismatch():
    movements = [
        make_movement("opening_balance", 100),
        make_movement("receipt", 20),
        make_movement("sale", 10),
    ]
    session = make_session(on_hand=115, movements=movements)

    result = reconcile_inventory(session, sku_id=1, location_id=1)

    assert result["status"] == "mismatch"
    assert result["recorded_on_hand"] == 115
    assert result["expected_on_hand"] == 110
    assert result["discrepancy"] == 5
