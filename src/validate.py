
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/processed")

cycles = pd.read_parquet(
    DATA_DIR / "battery_cycles.parquet"
)

measurements = pd.read_parquet(
    DATA_DIR / "battery_measurements.parquet"
)

print("\nBATTERY DATA QUALITY REPORT")
print("=" * 45)

# 1. Record counts
print(f"Total cycles: {len(cycles):,}")
print(f"Total measurements: {len(measurements):,}")

# 2. Missing values
print("\nMissing measurement values:")
print(
    measurements[
        ["time_seconds", "voltage_v",
         "current_a", "temperature_c"]
    ].isna().sum()
)

# 3. Duplicate cycle identifiers
duplicate_cycles = cycles.duplicated(
    subset=["battery_id", "cycle_id"]
).sum()

print(f"\nDuplicate cycle IDs: {duplicate_cycles}")

# 4. Check allowed operation types
valid_types = {"charge", "discharge", "impedance"}

invalid_types = (
    ~cycles["cycle_type"].isin(valid_types)
).sum()

print(f"Invalid cycle types: {invalid_types}")

# 5. Check measurement-to-cycle relationships
cycle_keys = pd.MultiIndex.from_frame(
    cycles[["battery_id", "cycle_id"]]
)

measurement_keys = pd.MultiIndex.from_frame(
    measurements[["battery_id", "cycle_id"]]
)

orphan_records = (
    ~measurement_keys.isin(cycle_keys)
).sum()

print(f"Orphan measurements: {orphan_records}")

# 6. Validate discharge capacity
discharge = cycles[
    cycles["cycle_type"] == "discharge"
]

invalid_capacity = (
    discharge["capacity_ah"].isna()
    | (discharge["capacity_ah"] <= 0)
).sum()

print(f"Invalid discharge capacities: {invalid_capacity}")

# 7. Basic voltage screening
invalid_voltage = (
    (measurements["voltage_v"] < 0)
    | (measurements["voltage_v"] > 6)
).sum()

print(f"Voltage readings outside 0-6 V: {invalid_voltage}")

print("\nValidation checks completed.")
