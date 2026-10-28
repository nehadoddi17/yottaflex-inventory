
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate_consistent_data(
    number_of_skus=10,
    number_of_locations=3,
    movements_per_pair=20,
):
    random.seed(42)

    output_dir = Path(__file__).resolve().parent
    balance_file = output_dir / "consistent_inventory.csv"
    movement_file = output_dir / "consistent_movements.csv"

    now = datetime.now(timezone.utc)
    movement_id = 1

    with (
        balance_file.open("w", newline="", encoding="utf-8") as bf,
        movement_file.open("w", newline="", encoding="utf-8") as mf,
    ):
        balance_writer = csv.writer(bf)
        movement_writer = csv.writer(mf)

        balance_writer.writerow([
            "sku_code",
            "location_code",
            "opening_stock",
            "on_hand",
            "reserved",
            "blocked",
            "safety_stock",
            "available_to_promise",
        ])

        movement_writer.writerow([
            "movement_code",
            "sku_code",
            "location_code",
            "movement_type",
            "quantity",
            "occurred_at",
        ])

        for sku_num in range(1, number_of_skus + 1):
            sku_code = f"SKU-C{sku_num:04d}"

            for location_num in range(1, number_of_locations + 1):
                location_code = f"LOC-C{location_num:03d}"

                opening_stock = random.randint(100, 300)
                on_hand = opening_stock
                blocked = 0

                base_time = now - timedelta(days=30)

                # Record the opening stock as the first movement.
                movement_writer.writerow([
                    f"GEN-MOV-{movement_id:08d}",
                    sku_code,
                    location_code,
                    "opening_balance",
                    opening_stock,
                    base_time.isoformat(),
                ])
                movement_id += 1

                # Generate movements while maintaining valid stock.
                for event_num in range(movements_per_pair):
                    possible_types = ["receipt", "sale", "return", "damage"]

                    if on_hand - blocked <= 1:
                        movement_type = "receipt"
                    else:
                        movement_type = random.choice(possible_types)

                    if movement_type == "receipt":
                        quantity = random.randint(1, 20)
                        on_hand += quantity

                    elif movement_type == "sale":
                        available = on_hand - blocked
                        quantity = random.randint(
                            1, min(10, available)
                        )
                        on_hand -= quantity

                    elif movement_type == "return":
                        quantity = random.randint(1, 10)
                        on_hand += quantity

                    else:  # damage
                        available_to_damage = on_hand - blocked
                        quantity = random.randint(
                            1, min(5, available_to_damage)
                        )
                        blocked += quantity

                    occurred_at = base_time + timedelta(
                        hours=event_num + 1
                    )

                    movement_writer.writerow([
                        f"GEN-MOV-{movement_id:08d}",
                        sku_code,
                        location_code,
                        movement_type,
                        quantity,
                        occurred_at.isoformat(),
                    ])
                    movement_id += 1

                reserved = random.randint(
                    0, max(0, on_hand - blocked)
                )
                safety_stock = random.randint(
                    0, max(0, on_hand - blocked - reserved)
                )

                atp = (
                    on_hand
                    - reserved
                    - blocked
                    - safety_stock
                )

                balance_writer.writerow([
                    sku_code,
                    location_code,
                    opening_stock,
                    on_hand,
                    reserved,
                    blocked,
                    safety_stock,
                    atp,
                ])

    print("Consistent synthetic data generated successfully.")
    print(f"Inventory file: {balance_file}")
    print(f"Movement file: {movement_file}")
    print(f"SKU-location pairs: {number_of_skus * number_of_locations}")
    print(
        "Movement records: "
        f"{number_of_skus * number_of_locations * (movements_per_pair + 1)}"
    )


if __name__ == "__main__":
    generate_consistent_data()
