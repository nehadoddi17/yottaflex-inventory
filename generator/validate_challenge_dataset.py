
import csv
import sys
from pathlib import Path
from collections import Counter


def read_csv(folder, filename):
    path = folder / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def duplicates(values):
    counts = Counter(values)
    return [value for value, count in counts.items() if count > 1]


def validate(folder):
    errors = []
    warnings = []

    products = read_csv(folder, "challenge_products.csv")
    skus = read_csv(folder, "challenge_skus.csv")
    locations = read_csv(folder, "challenge_locations.csv")
    balances = read_csv(folder, "challenge_balances.csv")
    movements = read_csv(folder, "challenge_movements.csv")
    orders = read_csv(folder, "challenge_orders.csv")
    lines = read_csv(folder, "challenge_order_lines.csv")
    reservations = read_csv(folder, "challenge_reservations.csv")
    shipments = read_csv(folder, "challenge_shipments.csv")
    rules = read_csv(folder, "challenge_replenishment_rules.csv")
    ground_truth = read_csv(folder, "ground_truth.csv")
    anomaly_cases = read_csv(folder, "anomaly_cases.csv")

    # 1. Primary-key uniqueness.
    primary_keys = [
        (products, "product_id", "products"),
        (skus, "sku_id", "SKUs"),
        (locations, "location_id", "locations"),
        (orders, "order_id", "orders"),
        (lines, "order_line_id", "order lines"),
        (reservations, "reservation_id", "reservations"),
        (shipments, "shipment_id", "shipments"),
        (rules, "rule_id", "replenishment rules"),
        (movements, "movement_code", "movement codes"),
    ]

    for rows, field, label in primary_keys:
        dups = duplicates(row[field] for row in rows)
        if dups:
            errors.append(f"{label}: duplicate {field} values: {dups[:3]}")

    # 2. Foreign-key integrity.
    product_ids = {r["product_id"] for r in products}
    sku_ids = {r["sku_id"] for r in skus}
    location_ids = {r["location_id"] for r in locations}
    order_ids = {r["order_id"] for r in orders}

    for sku in skus:
        if sku["product_id"] not in product_ids:
            errors.append(f"SKU {sku['sku_id']} references unknown product")

    for balance in balances:
        if balance["sku_id"] not in sku_ids:
            errors.append("Balance references unknown SKU")
        if balance["location_id"] not in location_ids:
            errors.append("Balance references unknown location")

    for movement in movements:
        if movement["sku_id"] not in sku_ids:
            errors.append(f"Movement {movement['movement_code']} has unknown SKU")
        if movement["location_id"] not in location_ids:
            errors.append(f"Movement {movement['movement_code']} has unknown location")
        if int(movement["quantity"]) <= 0:
            errors.append(f"Movement {movement['movement_code']} has nonpositive quantity")

    for order in orders:
        if order["location_id"] not in location_ids:
            errors.append(f"Order {order['order_id']} has unknown location")

    for line in lines:
        if line["order_id"] not in order_ids:
            errors.append(f"Order line {line['order_line_id']} has unknown order")
        if line["sku_id"] not in sku_ids:
            errors.append(f"Order line {line['order_line_id']} has unknown SKU")
        if int(line["quantity"]) <= 0:
            errors.append(f"Order line {line['order_line_id']} has nonpositive quantity")

    for reservation in reservations:
        if reservation["order_id"] not in order_ids:
            errors.append(f"Reservation {reservation['reservation_id']} has unknown order")
        if reservation["sku_id"] not in sku_ids:
            errors.append(f"Reservation {reservation['reservation_id']} has unknown SKU")
        if reservation["location_id"] not in location_ids:
            errors.append(f"Reservation {reservation['reservation_id']} has unknown location")
        if int(reservation["quantity"]) <= 0:
            errors.append(f"Reservation {reservation['reservation_id']} has nonpositive quantity")

    for shipment in shipments:
        if shipment["order_id"] not in order_ids:
            errors.append(f"Shipment {shipment['shipment_id']} has unknown order")
        if shipment["origin_location_id"] not in location_ids:
            errors.append(f"Shipment {shipment['shipment_id']} has unknown origin")

    for rule in rules:
        if rule["sku_id"] not in sku_ids:
            errors.append(f"Rule {rule['rule_id']} has unknown SKU")
        if rule["location_id"] not in location_ids:
            errors.append(f"Rule {rule['rule_id']} has unknown location")

    # 3. Balance arithmetic.
    for balance in balances:
        on_hand = int(balance["on_hand"])
        reserved = int(balance["reserved"])
        blocked = int(balance["blocked"])
        safety = int(balance["safety_stock"])
        atp = int(balance["available_to_promise"])

        if min(on_hand, reserved, blocked, safety) < 0:
            errors.append(
                f"Negative balance quantity for SKU {balance['sku_id']}, "
                f"location {balance['location_id']}"
            )

        if reserved + blocked + safety > on_hand:
            errors.append(
                f"Reserved + blocked + safety exceeds on-hand for "
                f"SKU {balance['sku_id']}, location {balance['location_id']}"
            )

        if atp != on_hand - reserved - blocked - safety:
            errors.append(
                f"ATP formula mismatch for SKU {balance['sku_id']}, "
                f"location {balance['location_id']}"
            )

    # 4. Movement history reconciliation.
    history = {}
    opening_count = Counter()

    for movement in movements:
        key = (movement["sku_id"], movement["location_id"])
        kind = movement["movement_type"]
        quantity = int(movement["quantity"])

        if kind == "opening_balance":
            opening_count[key] += 1
            if key in history:
                errors.append(f"Opening movement is not first for pair {key}")
            history[key] = {"on_hand": quantity, "blocked": 0}
        elif key not in history:
            errors.append(f"Movement has no opening balance: {key}")
        elif kind in ("receipt", "return"):
            history[key]["on_hand"] += quantity
        elif kind == "sale":
            history[key]["on_hand"] -= quantity
            if history[key]["on_hand"] < history[key]["blocked"]:
                errors.append(f"Sale causes negative unblocked stock for {key}")
        elif kind == "damage":
            history[key]["blocked"] += quantity
            if history[key]["blocked"] > history[key]["on_hand"]:
                errors.append(f"Blocked stock exceeds on-hand for {key}")
        else:
            errors.append(f"Unknown movement type: {kind}")

    for balance in balances:
        key = (balance["sku_id"], balance["location_id"])
        expected = history.get(key)
        if expected is None:
            errors.append(f"No movement history for balance {key}")
            continue

        if opening_count[key] != 1:
            errors.append(f"Expected exactly one opening movement for {key}")

        if expected["on_hand"] != int(balance["on_hand"]):
            errors.append(f"On-hand reconciliation mismatch for {key}")

        if expected["blocked"] != int(balance["blocked"]):
            errors.append(f"Blocked reconciliation mismatch for {key}")

    # 5. Ground-truth completeness.
    required_types = {
        "balance_mismatch",
        "reservation_exceeds_atp",
        "fulfilled_from_blocked_stock",
        "premature_transfer_receipt",
    }
    present_types = {row["anomaly_type"] for row in ground_truth}

    if present_types != required_types:
        errors.append(
            f"Ground-truth types mismatch. Expected {required_types}; "
            f"found {present_types}"
        )

    if len(ground_truth) != len(anomaly_cases):
        errors.append("Ground-truth and anomaly-case row counts differ")

    if any(row["expected_label"] != "1" for row in ground_truth):
        errors.append("Ground-truth contains an unexpected label")

    # Summary.
    print(f"Products: {len(products)}")
    print(f"SKUs: {len(skus)}")
    print(f"Locations: {len(locations)}")
    print(f"Balances: {len(balances)}")
    print(f"Movements: {len(movements)}")
    print(f"Orders / lines: {len(orders)} / {len(lines)}")
    print(f"Reservations: {len(reservations)}")
    print(f"Shipments: {len(shipments)}")
    print(f"Replenishment rules: {len(rules)}")
    print(f"Ground-truth cases: {len(ground_truth)}")
    print(f"Errors: {len(errors)}")

    for error in errors[:50]:
        print("ERROR:", error)

    if len(errors) > 50:
        print(f"... and {len(errors) - 50} more errors")

    return errors


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "generator/test_output_v3"
    )

    try:
        errors = validate(folder)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print("VALIDATION COULD NOT COMPLETE:", exc)
        sys.exit(2)

    if errors:
        print("VALIDATION FAILED")
        sys.exit(1)

    print("VALIDATION PASSED")
