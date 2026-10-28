
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

balances = pd.read_csv(BASE_DIR / "inventory_data.csv")
movements = pd.read_csv(BASE_DIR / "inventory_movements.csv")

print("Inventory balance rows:", len(balances))
print("Movement rows:", len(movements))

# Check for duplicate movement codes
duplicate_codes = movements["movement_code"].duplicated().sum()
print("Duplicate movement codes:", duplicate_codes)

# Check movement types
valid_types = {"receipt", "sale", "return", "damage"}
invalid_types = (
    ~movements["movement_type"].isin(valid_types)
).sum()
print("Invalid movement types:", invalid_types)

# Check quantities
invalid_quantities = (
    movements["quantity"].isna()
    | (movements["quantity"] <= 0)
).sum()
print("Invalid movement quantities:", invalid_quantities)

# Check that movement SKUs and locations exist in the balance data
valid_pairs = balances[["sku_code", "location_code"]].drop_duplicates()

checked = movements.merge(
    valid_pairs,
    on=["sku_code", "location_code"],
    how="left",
    indicator=True,
)

unknown_pairs = (checked["_merge"] == "left_only").sum()
print("Movements with unknown SKU/location pairs:", unknown_pairs)

if (
    duplicate_codes == 0
    and invalid_types == 0
    and invalid_quantities == 0
    and unknown_pairs == 0
):
    print("Basic movement validation: PASSED")
else:
    print("Basic movement validation: FAILED")
