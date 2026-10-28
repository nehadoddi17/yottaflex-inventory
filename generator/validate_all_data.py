
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

balances = pd.read_csv(BASE_DIR / "consistent_inventory.csv")
movements = pd.read_csv(BASE_DIR / "consistent_movements.csv")

# Check 1: ATP formula
expected_atp = (
    balances["on_hand"]
    - balances["reserved"]
    - balances["blocked"]
    - balances["safety_stock"]
)
incorrect_atp = (
    balances["available_to_promise"] != expected_atp
).sum()

# Check 2: Stock allocation must not exceed on-hand
invalid_allocation = (
    balances["reserved"]
    + balances["blocked"]
    + balances["safety_stock"]
    > balances["on_hand"]
).sum()

# Check 3: Movement codes must be unique
duplicate_codes = movements["movement_code"].duplicated().sum()

# Check 4: Movement types must be valid
valid_types = {
    "opening_balance",
    "receipt",
    "sale",
    "return",
    "damage",
}
invalid_types = (
    ~movements["movement_type"].isin(valid_types)
).sum()

# Check 5: Movement quantities must be positive
invalid_quantities = (
    movements["quantity"].isna()
    | (movements["quantity"] <= 0)
).sum()

print("Inventory rows:", len(balances))
print("Movement rows:", len(movements))
print("Incorrect ATP rows:", incorrect_atp)
print("Invalid stock allocations:", invalid_allocation)
print("Duplicate movement codes:", duplicate_codes)
print("Invalid movement types:", invalid_types)
print("Invalid movement quantities:", invalid_quantities)

checks_passed = all([
    incorrect_atp == 0,
    invalid_allocation == 0,
    duplicate_codes == 0,
    invalid_types == 0,
    invalid_quantities == 0,
])

if checks_passed:
    print("ALL DATA QUALITY CHECKS: PASSED")
else:
    print("ALL DATA QUALITY CHECKS: FAILED")
