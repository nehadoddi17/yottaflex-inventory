
import csv
from pathlib import Path

DATA_DIR = (
    Path(__file__).resolve().parent / "test_output"
)


def read_csv(filename):
    with (DATA_DIR / filename).open(
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


skus = read_csv("challenge_skus.csv")
locations = read_csv("challenge_locations.csv")
balances = read_csv("challenge_balances.csv")
orders = read_csv("challenge_orders.csv")
order_lines = read_csv("challenge_order_lines.csv")

sku_ids = {row["sku_id"] for row in skus}
location_ids = {row["location_id"] for row in locations}
order_ids = {row["order_id"] for row in orders}

invalid_balances = sum(
    1
    for row in balances
    if row["sku_id"] not in sku_ids
    or row["location_id"] not in location_ids
    or int(row["reserved"])
       + int(row["blocked"])
       + int(row["safety_stock"])
       > int(row["on_hand"])
    or int(row["available_to_promise"])
       != int(row["on_hand"])
       - int(row["reserved"])
       - int(row["blocked"])
       - int(row["safety_stock"])
)

invalid_lines = sum(
    1
    for row in order_lines
    if row["order_id"] not in order_ids
    or row["sku_id"] not in sku_ids
    or int(row["quantity"]) <= 0
)

print("SKU rows:", len(skus))
print("Location rows:", len(locations))
print("Balance rows:", len(balances))
print("Order rows:", len(orders))
print("Order-line rows:", len(order_lines))
print("Invalid balance rows:", invalid_balances)
print("Invalid order lines:", invalid_lines)

if (
    len(balances) == len(skus) * len(locations)
    and invalid_balances == 0
    and invalid_lines == 0
):
    print("CHALLENGE BASE DATA VALIDATION: PASSED")
else:
    print("CHALLENGE BASE DATA VALIDATION: FAILED")
