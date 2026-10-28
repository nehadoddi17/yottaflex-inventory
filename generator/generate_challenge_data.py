
import argparse
import csv
import random
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

DEFAULT_SEED = 20261022


def write_csv(path, columns, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def generate_data(output_dir, num_skus=5000, num_locations=100,
                  num_orders=50000, num_movements=1000000,
                  seed=DEFAULT_SEED):
    if min(num_skus, num_locations, num_orders, num_movements) < 1:
        raise ValueError("All counts must be positive.")

    pair_count = num_skus * num_locations
    if num_movements < pair_count:
        raise ValueError(
            f"--movements must be at least {pair_count} because "
            "each SKU-location pair needs an opening movement."
        )

    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Master data
    products, skus, locations = [], [], []
    for i in range(1, num_skus + 1):
        products.append({
            "product_id": i,
            "product_code": f"PRD-{i:06d}",
            "product_name": f"Synthetic Product {i}",
            "category": rng.choice(["general", "electronics", "home", "apparel"]),
            "active": True,
        })
        skus.append({
            "sku_id": i,
            "sku_code": f"SKU-{i:06d}",
            "product_id": i,
            "unit_price": f"{rng.uniform(5, 500):.2f}",
            "active": True,
        })

    location_types = ["warehouse", "store", "distribution_center"]
    for i in range(1, num_locations + 1):
        locations.append({
            "location_id": i,
            "location_code": f"LOC-{i:06d}",
            "location_name": f"Synthetic Location {i}",
            "location_type": location_types[(i - 1) % 3],
            "parent_location_id": "",
            "active": True,
        })

    write_csv(output_dir / "challenge_products.csv",
              ["product_id", "product_code", "product_name", "category", "active"],
              products)
    write_csv(output_dir / "challenge_skus.csv",
              ["sku_id", "sku_code", "product_id", "unit_price", "active"], skus)
    write_csv(output_dir / "challenge_locations.csv",
              ["location_id", "location_code", "location_name",
               "location_type", "parent_location_id", "active"], locations)

    # 2. Opening movements, then valid subsequent movements.
    # State is updated from every movement; balances are derived afterward.
    states = []
    for sku_id in range(1, num_skus + 1):
        for location_id in range(1, num_locations + 1):
            opening = rng.randint(50, 500)
            states.append({
                "sku_id": sku_id,
                "location_id": location_id,
                "on_hand": opening,
                "blocked": 0,
                "opening": opening,
            })

    movement_path = output_dir / "challenge_movements.csv"
    event_count = num_movements - pair_count
    movement_rng = random.Random(seed + 1)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    with movement_path.open("w", newline="", encoding="utf-8") as f:
        cols = ["movement_id", "movement_code", "sku_id", "location_id",
                "movement_type", "quantity", "occurred_at",
                "reference_type", "reference_id"]
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        movement_id = 0

        # Exactly one opening movement per SKU-location pair.
        for state in states:
            movement_id += 1
            writer.writerow({
                "movement_id": movement_id,
                "movement_code": f"MOV-2026-{movement_id:08d}",
                "sku_id": state["sku_id"],
                "location_id": state["location_id"],
                "movement_type": "opening_balance",
                "quantity": state["opening"],
                "occurred_at": start.isoformat(),
                "reference_type": "opening",
                "reference_id": "",
            })
                
        # Each event is applied to the state before it is written.
        if event_count < 1:
            raise ValueError(
                "At least one non-opening movement is required."
            )

        for offset in range(event_count):
            if offset == 0:
                # Guarantee one blocked-stock balance through a real
                # damage movement, keeping movement history consistent.
                state = states[0]
                kind = "damage"
                qty = 1
                state["blocked"] += qty
            else:
                state = movement_rng.choice(states)
                available = state["on_hand"] - state["blocked"]

                choices = ["receipt", "return", "sale", "damage"]
                weights = [35, 15, 40, 10]
                if available < 1:
                    choices, weights = ["receipt", "return"], [70, 30]

                kind = movement_rng.choices(
                    choices, weights=weights, k=1
                )[0]
                qty = movement_rng.randint(1, 10)

                if kind == "sale":
                    qty = min(qty, available)
                    if qty < 1:
                        kind = "receipt"
                    else:
                        state["on_hand"] -= qty
                elif kind in ("receipt", "return"):
                    state["on_hand"] += qty
                elif kind == "damage":
                    qty = min(qty, max(1, available))
                    state["blocked"] += qty

            movement_id += 1
            writer.writerow({
                "movement_id": movement_id,
                "movement_code": f"MOV-2026-{movement_id:08d}",
                "sku_id": state["sku_id"],
                "location_id": state["location_id"],
                "movement_type": kind,
                "quantity": qty,
                "occurred_at": (
                    start + timedelta(seconds=movement_id)
                ).isoformat(),
                "reference_type": "synthetic_event",
                "reference_id": "",
            })


    # 3. Balances derived from opening stock and movement history.
    balances = []
    for state in states:
        on_hand = state["on_hand"]
        blocked = state["blocked"]
        safety = min(on_hand - blocked, max(0, int(on_hand * 0.05)))
        balances.append({
            "sku_id": state["sku_id"],
            "location_id": state["location_id"],
            "on_hand": on_hand,
            "reserved": 0,
            "blocked": blocked,
            "safety_stock": safety,
            "available_to_promise": on_hand - blocked - safety,
        })

    write_csv(output_dir / "challenge_balances.csv",
              ["sku_id", "location_id", "on_hand", "reserved", "blocked",
               "safety_stock", "available_to_promise"], balances)

    # 4. Orders and order lines.
    orders, lines = [], []
    for i in range(1, num_orders + 1):
        location_id = rng.randint(1, num_locations)
        sku_id = rng.randint(1, num_skus)
        quantity = rng.randint(1, 5)
        status = rng.choice(["created", "confirmed", "fulfilled", "cancelled"])
        orders.append({
            "order_id": i,
            "order_code": f"ORD-2026-{i:06d}",
            "location_id": location_id,
            "status": status,
            "channel": rng.choice(["online", "store", "marketplace"]),
            "created_at": (start + timedelta(seconds=i)).isoformat(),
        })
        lines.append({
            "order_line_id": i,
            "order_id": i,
            "sku_id": sku_id,
            "quantity": quantity,
        })

    write_csv(output_dir / "challenge_orders.csv",
              ["order_id", "order_code", "location_id", "status", "channel", "created_at"],
              orders)
    write_csv(output_dir / "challenge_order_lines.csv",
              ["order_line_id", "order_id", "sku_id", "quantity"], lines)

    # 5. Supporting entities. Reservations are synthetic examples;
    # they are not included in the balances above.
    reservations, shipments, rules = [], [], []
    for i in range(1, min(num_orders, 1000) + 1):
        order = orders[i - 1]
        reservations.append({
            "reservation_id": i,
            "reservation_code": f"RES-{order['order_code']}-01",
            "order_id": order["order_id"],
            "sku_id": lines[i - 1]["sku_id"],
            "location_id": order["location_id"],
            "quantity": lines[i - 1]["quantity"],
            "status": rng.choice(["active", "expired", "released"]),
            "expires_at": (start + timedelta(days=1)).isoformat(),
        })
        shipments.append({
    "shipment_id": i,
    "shipment_code": f"SHP-2026-{i:06d}",
    "order_id": order["order_id"],
    "origin_location_id": order["location_id"],
    "destination_location_id": "",
    "status": rng.choice(["created", "in_transit", "delivered"]),
    "dispatch_time": (
        start + timedelta(days=2)
    ).isoformat() if i == 1 else "",
    "receipt_time": (
        start + timedelta(days=1)
    ).isoformat() if i == 1 else "",
})

    for i in range(1, num_skus + 1):
        rules.append({
            "rule_id": i,
            "sku_id": i,
            "location_id": rng.randint(1, num_locations),
            "reorder_point": rng.randint(10, 50),
            "reorder_quantity": rng.randint(20, 100),
            "active": True,
        })

    write_csv(output_dir / "challenge_reservations.csv",
              ["reservation_id", "reservation_code", "order_id", "sku_id",
               "location_id", "quantity", "status", "expires_at"], reservations)
    write_csv(output_dir / "challenge_shipments.csv",
              ["shipment_id", "shipment_code", "order_id", "origin_location_id",
 "destination_location_id", "status", "dispatch_time", "receipt_time"], shipments)
    write_csv(output_dir / "challenge_replenishment_rules.csv",
              ["rule_id", "sku_id", "location_id", "reorder_point",
               "reorder_quantity", "active"], rules)

   
   
    # 6. Ground truth and concrete anomaly test fixtures.
    # These fixtures intentionally describe invalid scenarios without
    # corrupting the clean inventory balances or movement history.

    balance_lookup = {
        (int(b["sku_id"]), int(b["location_id"])): b
        for b in balances
    }

    anomaly_cases = []

    # GT-001: Deliberately report one extra unit compared with replayed stock.
    b = balances[0]
    anomaly_cases.append({
        "scenario_id": "GT-001",
        "anomaly_type": "balance_mismatch",
        "source_sku_id": b["sku_id"],
        "source_location_id": b["location_id"],
        "source_order_id": "",
        "source_shipment_id": "",
        "expected_on_hand": b["on_hand"],
        "test_on_hand": b["on_hand"] + 1,
        "test_quantity": "",
        "available_to_promise": b["available_to_promise"],
        "blocked_quantity": b["blocked"],
        "event_time": "",
        "expected_label": 1,
        "test_condition": "test_on_hand != expected_on_hand",
    })

    # GT-002: Create a reservation request one unit above ATP.
    reservation = reservations[0]
    rb = balance_lookup.get(
        (int(reservation["sku_id"]), int(reservation["location_id"]))
    )
    if rb is not None:
        atp = int(rb["available_to_promise"])
        anomaly_cases.append({
            "scenario_id": "GT-002",
            "anomaly_type": "reservation_exceeds_atp",
            "source_sku_id": reservation["sku_id"],
            "source_location_id": reservation["location_id"],
            "source_order_id": reservation["order_id"],
            "source_shipment_id": "",
            "expected_on_hand": rb["on_hand"],
            "test_on_hand": rb["on_hand"],
            "test_quantity": atp + 1,
            "available_to_promise": atp,
            "blocked_quantity": rb["blocked"],
            "event_time": "",
            "expected_label": 1,
            "test_condition": "test_quantity > available_to_promise",
        })

    # GT-003: Attempt to allocate blocked units to an order.
    blocked_balances = [x for x in balances if int(x["blocked"]) > 0]
    if blocked_balances:
        b = blocked_balances[0]
        anomaly_cases.append({
            "scenario_id": "GT-003",
            "anomaly_type": "fulfilled_from_blocked_stock",
            "source_sku_id": b["sku_id"],
            "source_location_id": b["location_id"],
            "source_order_id": orders[0]["order_id"],
            "source_shipment_id": "",
            "expected_on_hand": b["on_hand"],
            "test_on_hand": b["on_hand"],
            "test_quantity": 1,
            "available_to_promise": b["available_to_promise"],
            "blocked_quantity": b["blocked"],
            "event_time": "",
            "expected_label": 1,
            "test_condition": "allocation_source_is_blocked_stock",
        })

    # GT-004: Receipt time occurs before the transfer dispatch time.
    shipment = shipments[0]
    dispatch_time = start + timedelta(days=2)
    receipt_time = start + timedelta(days=1)
    anomaly_cases.append({
        "scenario_id": "GT-004",
        "anomaly_type": "premature_transfer_receipt",
        "source_sku_id": "",
        "source_location_id": shipment["origin_location_id"],
        "source_order_id": shipment["order_id"],
        "source_shipment_id": shipment["shipment_code"],
        "expected_on_hand": "",
        "test_on_hand": "",
        "test_quantity": 1,
        "available_to_promise": "",
        "blocked_quantity": "",
        "event_time": receipt_time.isoformat(),
        "expected_label": 1,
        "test_condition": (
            f"receipt_time {receipt_time.isoformat()} precedes "
            f"dispatch_time {dispatch_time.isoformat()}"
        ),
    })

    case_columns = [
        "scenario_id", "anomaly_type", "source_sku_id",
        "source_location_id", "source_order_id", "source_shipment_id",
        "expected_on_hand", "test_on_hand", "test_quantity",
        "available_to_promise", "blocked_quantity", "event_time",
        "expected_label", "test_condition",
    ]
    write_csv(output_dir / "anomaly_cases.csv", case_columns, anomaly_cases)

    # Ground-truth labels refer to the corresponding concrete test cases.
    ground_truth = [
        {
            "scenario_id": case["scenario_id"],
            "anomaly_type": case["anomaly_type"],
            "related_file": "anomaly_cases.csv",
            "entity_id": case["source_shipment_id"]
            or case["source_order_id"]
            or (
                f"SKU-{int(case['source_sku_id']):06d}|"
                f"LOC-{int(case['source_location_id']):06d}"
            ),
            "expected_label": case["expected_label"],
            "test_condition": case["test_condition"],
        }
        for case in anomaly_cases
    ]

    write_csv(
        output_dir / "ground_truth.csv",
        [
            "scenario_id", "anomaly_type", "related_file",
            "entity_id", "expected_label", "test_condition",
        ],
        ground_truth,
    )


    # 7. Data dictionary, reproducibility manifest and checksums.
    dictionary = {
        "seed": seed,
        "movement_count_includes_opening_movements": True,
        "balance_formula": "ATP = on_hand - reserved - blocked - safety_stock",
        "movement_types": ["opening_balance", "receipt", "return", "sale", "damage"],
        "notes": [
            "All data is synthetic.",
            "Ground truth lists anomaly scenarios; the anomalies are not injected into clean data.",
            "Reservation examples are not deducted from generated balances.",
            "Order fulfillment and shipment lifecycle are illustrative and require further validation.",
        ],
    }
    (output_dir / "data_dictionary.json").write_text(
        json.dumps(dictionary, indent=2), encoding="utf-8"
    )

    manifest = {
        "seed": seed,
        "skus": num_skus,
        "locations": num_locations,
        "orders": num_orders,
        "movements": num_movements,
        "balance_rows": len(balances),
        "generated_at": "fixed synthetic dataset; timestamps are deterministic",
        "files": {},
    }
    for path in sorted(output_dir.glob("*.csv")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest["files"][path.name] = {
            "sha256": digest,
            "bytes": path.stat().st_size,
        }
    (output_dir / "source_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print("Generated synthetic challenge data.")
    print(f"SKUs: {num_skus}; locations: {num_locations}")
    print(f"Balances: {len(balances)}; movements: {num_movements}")
    print(f"Orders: {num_orders}; seed: {seed}")
    print(f"Output: {output_dir.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic inventory challenge data.")
    parser.add_argument("--skus", type=int, default=5000)
    parser.add_argument("--locations", type=int, default=100)
    parser.add_argument("--orders", type=int, default=50000)
    parser.add_argument("--movements", type=int, default=1000000)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "challenge_output",
    )
    args = parser.parse_args()
    generate_data(args.output, args.skus, args.locations, args.orders,
                  args.movements, args.seed)


if __name__ == "__main__":
    main()


