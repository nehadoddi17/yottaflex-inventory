
import pytest

from app.services.inventory import calculate_atp


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
