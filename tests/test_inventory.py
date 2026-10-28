
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.inventory import calculate_atp
from app.services.movements import record_movement


def test_basic_atp_calculation():
    result = calculate_atp(
        on_hand=100,
        reserved=15,
        blocked=5,
        safety_stock=10,
        approved_inbound=20,
    )

    assert result == 90


def test_atp_without_inbound_stock():
    result = calculate_atp(
        on_hand=50,
        reserved=10,
        blocked=5,
        safety_stock=5,
    )

    assert result == 30


def test_invalid_negative_stock():
    with pytest.raises(ValueError):
        calculate_atp(
            on_hand=100,
            reserved=-5,
            blocked=0,
            safety_stock=0,
        )


def test_impossible_stock_allocation():
    with pytest.raises(ValueError):
        calculate_atp(
            on_hand=10,
            reserved=8,
            blocked=2,
            safety_stock=1,
        )


def test_sale_cannot_use_blocked_stock():
    session = MagicMock()

    balance = SimpleNamespace(
        sku_id=1,
        location_id=1,
        on_hand=10,
        reserved=0,
        blocked=6,
        safety_stock=0,
    )

    session.scalar.return_value = balance

    with pytest.raises(ValueError, match="Sale exceeds available stock"):
        record_movement(
            session=session,
            sku_id=1,
            location_id=1,
            movement_type="sale",
            quantity=5,
        )

    assert balance.on_hand == 10
    assert balance.blocked == 6
    session.rollback.assert_called_once()
    session.commit.assert_not_called()
