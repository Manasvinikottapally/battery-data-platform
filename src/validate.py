
from pathlib import Path
import pandas as pd

# -------------------------------------
# STEP 1: Load processed Parquet files
# -------------------------------------

DATA_DIR = Path("data/processed")

cycles = pd.read_parquet(
    DATA_DIR / "battery_cycles.parquet"
)

measurements = pd.read_parquet(
    DATA_DIR / "battery_measurements.parquet"
)

print("\nBATTERY DATA QUALITY REPORT")
print("=" * 45)

# -------------------------------------
# STEP 2: Verify record counts
# -------------------------------------

print(f"Total cycle records: {len(cycles):,}")
print(f"Total measurement records: {len(measurements):,}")

# -------------------------------------
# STEP 3: Check missing values
# -------------------------------------

print("\nMissing measurement values:")

required_columns = [
    "battery_id",
    "cycle_id",
    "time_seconds",
    "voltage_v",
    "current_a",
    "temperature_c"
]

missing_values = measurements[
    required_columns
].isna().sum()

print(missing_values)

# -------------------------------------
# STEP 4: Check duplicate cycle IDs
# -------------------------------------

duplicate_cycles = cycles.duplicated(
    subset=["battery_id", "cycle_id"]
).sum()

print(f"\nDuplicate cycle IDs: {duplicate_cycles}")

# -------------------------------------
# STEP 5: Check cycle types
# -------------------------------------

valid_types = {
    "charge",
    "discharge",
    "impedance"
}

invalid_cycle_types = (
    ~cycles["cycle_type"].isin(valid_types)
).sum()

print(f"Invalid cycle types: {invalid_cycle_types}")

# -------------------------------------
# STEP 6: Check discharge capacity
# -------------------------------------

discharge_cycles = cycles[
    cycles["cycle_type"] == "discharge"
]

invalid_capacity = (
    discharge_cycles["capacity_ah"].isna()
    | (discharge_cycles["capacity_ah"] <= 0)
).sum()

print(f"Invalid discharge capacity: {invalid_capacity}")

# -------------------------------------
# STEP 7: Check voltage range
# -------------------------------------

invalid_voltage = (
    (measurements["voltage_v"] < 0)
    | (measurements["voltage_v"] > 6)
).sum()

print(f"Voltage values outside 0-6 V: {invalid_voltage}")

# -------------------------------------
# STEP 8: Verify measurement relationships
# -------------------------------------

cycle_keys = pd.MultiIndex.from_frame(
    cycles[["battery_id", "cycle_id"]]
)

measurement_keys = pd.MultiIndex.from_frame(
    measurements[["battery_id", "cycle_id"]]
)

orphan_measurements = (
    ~measurement_keys.isin(cycle_keys)
).sum()

print(f"Orphan measurements: {orphan_measurements}")

# -------------------------------------
# STEP 9: Display results
# -------------------------------------

print("\n" + "=" * 45)
print("DATA QUALITY CHECKS COMPLETED")
print("=" * 45)
