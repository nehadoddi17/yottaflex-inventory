
import csv
import random
from pathlib import Path


def generate_inventory_data(
    number_of_skus=100,
    number_of_locations=10,
    output_file="inventory_data.csv",
):
    random.seed(42)

    output_path = Path(__file__).resolve().parent / output_file

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow([
            "sku_code",
            "location_code",
            "on_hand",
            "reserved",
            "blocked",
            "safety_stock",
            "available_to_promise",
        ])

        for sku_number in range(1, number_of_skus + 1):
            sku_code = f"SKU-{sku_number:06d}"

            for location_number in range(
                1, number_of_locations + 1
            ):
                location_code = (
                    f"LOC-{location_number:04d}"
                )

                on_hand = random.randint(50, 500)
                reserved = random.randint(
                    0, min(20, on_hand // 4)
                )
                blocked = random.randint(
                    0, min(10, on_hand // 4)
                )
                safety_stock = random.randint(
                    0,
                    max(
                        0,
                        on_hand - reserved - blocked,
                    ),
                )

                available_to_promise = (
                    on_hand
                    - reserved
                    - blocked
                    - safety_stock
                )

                writer.writerow([
                    sku_code,
                    location_code,
                    on_hand,
                    reserved,
                    blocked,
                    safety_stock,
                    available_to_promise,
                ])

    print(f"Inventory data generated: {output_path}")
    print(f"SKUs: {number_of_skus}")
    print(f"Locations: {number_of_locations}")
    print(
        "Inventory balance rows: "
        f"{number_of_skus * number_of_locations}"
    )


if __name__ == "__main__":
    generate_inventory_data()
