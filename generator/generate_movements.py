
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate_movements(
    number_of_skus=100,
    number_of_locations=10,
    movements_per_location=20,
):
    random.seed(42)

    output_path = (
        Path(__file__).resolve().parent
        / "inventory_movements.csv"
    )

    movement_types = ["receipt", "sale", "return", "damage"]
    weights = [35, 40, 15, 10]

    now = datetime.now(timezone.utc)
    movement_id = 1

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow([
            "movement_code",
            "sku_code",
            "location_code",
            "movement_type",
            "quantity",
            "occurred_at",
        ])

        for sku_number in range(1, number_of_skus + 1):
            sku_code = f"SKU-{sku_number:06d}"

            for location_number in range(
                1, number_of_locations + 1
            ):
                location_code = f"LOC-{location_number:04d}"

                for _ in range(movements_per_location):
                    movement_type = random.choices(
                        movement_types,
                        weights=weights,
                        k=1,
                    )[0]

                    quantity = random.randint(1, 10)

                    occurred_at = now - timedelta(
                        days=random.randint(0, 90),
                        minutes=random.randint(0, 1440),
                    )

                    writer.writerow([
                        f"GEN-MOV-{movement_id:08d}",
                        sku_code,
                        location_code,
                        movement_type,
                        quantity,
                        occurred_at.isoformat(),
                    ])

                    movement_id += 1

    print(f"Movement data generated: {output_path}")
    print(f"Movement records: {movement_id - 1}")


if __name__ == "__main__":
    generate_movements()
