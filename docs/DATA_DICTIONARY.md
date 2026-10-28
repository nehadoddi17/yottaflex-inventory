# YottaFlex Inventory — Data Dictionary

## Overview

The challenge dataset consists of synthetic inventory master data, stock balances, movement history, orders, reservations, shipments, replenishment rules, and labelled anomaly scenarios.

All identifiers refer to synthetic records.

## Dataset Files

| File | Purpose |
|---|---|
| `challenge_products.csv` | Product master records |
| `challenge_skus.csv` | Stock-keeping units associated with products |
| `challenge_locations.csv` | Warehouses, stores, and inventory locations |
| `challenge_balances.csv` | Recorded inventory quantities per SKU and location |
| `challenge_movements.csv` | Inventory movement history |
| `challenge_orders.csv` | Order headers and lifecycle information |
| `challenge_order_lines.csv` | SKU-level quantities belonging to orders |
| `challenge_reservations.csv` | Stock reservation records |
| `challenge_shipments.csv` | Shipment and transfer records |
| `challenge_replenishment_rules.csv` | Replenishment policies |
| `anomaly_cases.csv` | Explicit anomaly test fixtures |
| `ground_truth.csv` | Expected anomaly labels and test conditions |

## Entity Definitions

### Product

Represents a product family or catalog item.

- `product_id`: Unique product identifier.
- Additional descriptive fields: Product name and catalog attributes, as defined in the generated CSV header.

### SKU

Represents a specific stock-keeping unit.

- `sku_id`: Unique SKU identifier.
- `product_id`: Reference to its product.
- `sku_code`: Business identifier, following the configured SKU naming convention.

### Location

Represents a physical or logical inventory location.

- `location_id`: Unique location identifier.
- `location_code`: Business identifier for the location.
- Additional descriptive fields: Location attributes defined by the generator.

### Inventory Balance

Represents the recorded stock position for a SKU at a location.

- SKU and location identifiers identify the inventory position.
- `on_hand`: Recorded physical stock quantity.
- `reserved`: Quantity committed to reservations.
- `blocked`: Quantity unavailable for allocation.
- `safety_stock`: Quantity protected by the replenishment policy.
- `available_to_promise`: Calculated available quantity.

### Inventory Movement

Represents a stock-changing event.

- `movement_id`: Unique movement record identifier.
- `movement_code`: Business identifier, following the configured MOV naming convention.
- SKU and location identifiers identify the affected inventory position.
- `movement_type`: Event category such as opening, receipt, sale, return, damage, or transfer.
- `quantity`: Positive movement quantity.
- `occurred_at`: Event timestamp.
- Reference fields associate a movement with a source operation when available.

### Order and Order Line

An order is the header record for a customer or channel request. Order lines specify the SKU and quantity requested.

- `order_id`: Unique order identifier.
- `order_code`: Business identifier, following the configured ORD naming convention.
- `order_line_id`: Unique order-line identifier.
- SKU and order identifiers link each line to the relevant records.
- Quantities represent requested or processed units, according to the field definition.

### Reservation

Represents stock held for an order line.

- `reservation_id`: Unique reservation record identifier.
- `reservation_code`: Business identifier following the configured reservation naming convention.
- `order_line_id`: Reference to an order line.
- `location_id`: Location holding the reserved stock.
- `quantity`: Reserved quantity.
- `expires_at`: Reservation expiry timestamp.
- `status`: Reservation lifecycle state.

### Shipment

Represents a shipment or stock transfer between locations.

- `shipment_id`: Unique shipment record identifier.
- `shipment_code`: Business identifier, following the configured SHP naming convention.
- Origin and destination location identifiers describe the route.
- `status`: Shipment lifecycle state.
- Dispatch and receipt timestamps describe the transfer timeline when provided.

### Replenishment Rule

Defines replenishment settings for a SKU and location, including threshold and target quantities where configured.

### Anomaly Cases and Ground Truth

Anomaly fixtures describe test conditions and expected labels.

- `scenario_id`: Scenario identifier, such as GT-001.
- `anomaly_type`: Category of the anomaly.
- Source identifiers locate relevant records.
- `expected_label`: Expected classification label.
- `test_condition`: Human-readable description of the condition being tested.

These fixtures are not necessarily persisted operational events. See the project README for known limitations.

## Available-to-Promise Formula

```text
ATP = on_hand - reserved - blocked - safety_stock + approved_inbound
```

The application validates quantity constraints before calculating ATP. Approved inbound should only include quantities eligible under the inventory policy.

## Validation

Run the validator against a generated dataset:

```powershell
python generator/validate_challenge_dataset.py generator/gt_test
```

For the full-scale dataset, substitute its output directory.

## Schema Accuracy Note

This document describes the logical entities and common fields. For the exact column names, types, enumerated values, nullability, primary keys, foreign keys, and effective-date constraints, consult the CSV headers, SQLAlchemy models in `app/models.py`, and the generator implementation. Do not infer unspecified columns or lifecycle constraints from this summary.
