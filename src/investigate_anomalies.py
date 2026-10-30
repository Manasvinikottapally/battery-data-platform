
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/processed")

measurements = pd.read_parquet(
    DATA_DIR / "battery_measurements.parquet"
)

# Show complete columns in terminal
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)

# ------------------------------------------
# 1. Find rows containing missing values
# ------------------------------------------

missing_rows = measurements[
    measurements[
        ["voltage_v", "current_a", "temperature_c"]
    ].isna().any(axis=1)
]

print("\nROWS WITH MISSING MEASUREMENTS")
print("=" * 60)
print(missing_rows.to_string(index=False))

# ------------------------------------------
# 2. Find voltage readings outside 0-6 V
# ------------------------------------------

invalid_voltage = measurements[
    (measurements["voltage_v"] < 0)
    | (measurements["voltage_v"] > 6)
]

print("\nVOLTAGE READINGS OUTSIDE 0-6 V")
print("=" * 60)
print(invalid_voltage.to_string(index=False))

# ------------------------------------------
# 3. Count anomalies per battery
# ------------------------------------------

print("\nMISSING ROWS BY BATTERY")
print(missing_rows.groupby("battery_id").size())

print("\nOUT-OF-RANGE VOLTAGE BY BATTERY")
print(invalid_voltage.groupby("battery_id").size())

# ------------------------------------------
# 4. Inspect voltage statistics
# ------------------------------------------

print("\nVOLTAGE STATISTICS")
print(
    measurements.groupby("battery_id")["voltage_v"]
    .agg(["min", "max", "mean"])
)

# ------------------------------------------
# 5. Check if missing rows overlap with
#    out-of-range voltage rows
# ------------------------------------------

overlap = missing_rows.index.intersection(
    invalid_voltage.index
)

print("\nAnomaly overlap count:", len(overlap))
