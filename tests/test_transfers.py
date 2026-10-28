
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.transfers import dispatch_transfer, receive_transfer


def test_dispatch_reduces_source_stock():
    session = MagicMock()

    source = SimpleNamespace(
        on_hand=20,
        reserved=2,
        blocked=3,
        safety_stock=5,
    )

    # First query: shipment does not exist.
    # Second query: return the source inventory balance.
    session.scalar.side_effect = [None, source, 0]

    shipment = dispatch_transfer(
        session=session,
        shipment_code="SHP-2026-000001",
        sku_id=1,
        source_location_id=1,
        destination_location_id=2,
        quantity=5,
    )

    assert source.on_hand == 15
    session.add.assert_called()
    session.commit.assert_called_once()
    assert shipment.status == "in_transit"


def test_dispatch_rejects_insufficient_available_stock():
    session = MagicMock()

    source = SimpleNamespace(
        on_hand=20,
        reserved=5,
        blocked=5,
        safety_stock=5,
    )

    # Shipment does not exist; then return the source balance.
    session.scalar.side_effect = [None, source]

    with pytest.raises(ValueError, match="Insufficient available stock"):
        dispatch_transfer(
            session=session,
            shipment_code="SHP-2026-000002",
            sku_id=1,
            source_location_id=1,
            destination_location_id=2,
            quantity=6,
        )

    assert source.on_hand == 20
    session.rollback.assert_called_once()
    session.commit.assert_not_called()


def test_receive_adds_stock_only_at_destination():
    session = MagicMock()

    shipment = SimpleNamespace(
        id=1,
        shipment_code="SHP-2026-000003",
        source_location_id=1,
        destination_location_id=2,
        status="in_transit",
        received_at=None,
    )

    line = SimpleNamespace(sku_id=1, quantity=5)

    destination = SimpleNamespace(
        on_hand=10,
        reserved=0,
        blocked=0,
        safety_stock=0,
    )

    # Shipment lookup, destination lookup, and movement ID lookup.
    session.scalar.side_effect = [shipment, destination, 0]
    session.scalars.return_value.all.return_value = [line]

    result = receive_transfer(
        session=session,
        shipment_code="SHP-2026-000003",
    )

    assert destination.on_hand == 15
    assert result.status == "received"
    assert result.received_at is not None
    session.commit.assert_called_once()


def test_receive_rejects_already_received_shipment():
    session = MagicMock()

    shipment = SimpleNamespace(
        id=1,
        shipment_code="SHP-2026-000004",
        status="received",
    )
    session.scalar.return_value = shipment

    with pytest.raises(ValueError, match="Only in-transit shipments"):
        receive_transfer(
            session=session,
            shipment_code="SHP-2026-000004",
        )

    session.rollback.assert_called_once()
    session.commit.assert_not_called()