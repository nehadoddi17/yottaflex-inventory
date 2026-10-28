
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

balances = pd.read_csv(BASE_DIR / "consistent_inventory.csv")
movements = pd.read_csv(BASE_DIR / "consistent_movements.csv")

results = []

for _, balance in balances.iterrows():
    sku = balance["sku_code"]
    location = balance["location_code"]

    history = movements[
        (movements["sku_code"] == sku)
        & (movements["location_code"] == location)
    ].sort_values("occurred_at")

    expected_on_hand = 0
    expected_blocked = 0
    opening_count = 0

    for _, movement in history.iterrows():
        movement_type = movement["movement_type"]
        quantity = int(movement["quantity"])

        if movement_type == "opening_balance":
            opening_count += 1
            expected_on_hand += quantity

        elif movement_type in ("receipt", "return"):
            expected_on_hand += quantity

        elif movement_type == "sale":
            expected_on_hand -= quantity

        elif movement_type == "damage":
            expected_blocked += quantity

    on_hand_matches = expected_on_hand == int(balance["on_hand"])
    blocked_matches = expected_blocked == int(balance["blocked"])

    results.append({
        "sku_code": sku,
        "location_code": location,
        "opening_count": opening_count,
        "expected_on_hand": expected_on_hand,
        "recorded_on_hand": int(balance["on_hand"]),
        "expected_blocked": expected_blocked,
        "recorded_blocked": int(balance["blocked"]),
        "on_hand_matches": on_hand_matches,
        "blocked_matches": blocked_matches,
    })

result_df = pd.DataFrame(results)

print("SKU-location pairs checked:", len(result_df))
print(
    "Pairs with exactly one opening balance:",
    (result_df["opening_count"] == 1).sum(),
)
print(
    "On-hand mismatches:",
    (~result_df["on_hand_matches"]).sum(),
)
print(
    "Blocked-stock mismatches:",
    (~result_df["blocked_matches"]).sum(),
)

if (
    (result_df["opening_count"] == 1).all()
    and result_df["on_hand_matches"].all()
    and result_df["blocked_matches"].all()
):
    print("CONSISTENT DATA VALIDATION: PASSED")
else:
    print("CONSISTENT DATA VALIDATION: FAILED")

result_df.to_csv(
    BASE_DIR / "reconciliation_validation.csv",
    index=False,
)
print("Detailed results saved to reconciliation_validation.csv")
