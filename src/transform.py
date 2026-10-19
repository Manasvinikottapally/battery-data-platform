
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat


# ==========================================
# STEP 1: Define input and output directories
# ==========================================

RAW_DIR = Path("data/raw/nasa/batteries")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# STEP 2: Helper function
# ==========================================

def scalar(value):
    """
    Convert a nested MATLAB numeric value
    into a Python float.
    """
    array = np.asarray(value).squeeze()

    if array.size != 1:
        raise ValueError(
            "Expected exactly one numeric value"
        )

    return float(array.item())


# ==========================================
# STEP 3: Automatically discover battery files
# ==========================================

battery_files = sorted(RAW_DIR.glob("B*.mat"))

if not battery_files:
    raise FileNotFoundError(
        f"No battery files found in {RAW_DIR}"
    )

print(f"Discovered {len(battery_files)} battery files")


# ==========================================
# STEP 4: Initialize record collections
# ==========================================

cycle_records = []
measurement_records = []


# ==========================================
# STEP 5: Process each battery file
# ==========================================

for file_path in battery_files:

    battery_id = file_path.stem

    print(f"Processing battery: {battery_id}")

    mat = loadmat(file_path)

    if battery_id not in mat:
        raise ValueError(
            f"{battery_id} not found inside {file_path}"
        )

    # Read the battery cycles
    cycles = mat[battery_id][0, 0]["cycle"][0]

    # ==========================================
    # STEP 6: Process each cycle
    # ==========================================

    for cycle_id, cycle in enumerate(cycles, start=1):

        cycle_type = str(cycle["type"][0])

        ambient_temp = scalar(
            cycle["ambient_temperature"]
        )

        measurements = cycle["data"][0, 0]

        capacity = None

        if cycle_type == "discharge":
            capacity = scalar(
                measurements["Capacity"]
            )

        # Save cycle-level record
        cycle_records.append({
            "battery_id": battery_id,
            "cycle_id": cycle_id,
            "cycle_type": cycle_type,
            "ambient_temperature_c": ambient_temp,
            "capacity_ah": capacity
        })

        # Impedance cycles have different measurements
        if cycle_type not in ("charge", "discharge"):
            continue

        # ==========================================
        # STEP 7: Extract time-series measurements
        # ==========================================

        time = np.asarray(
            measurements["Time"]
        ).flatten()

        voltage = np.asarray(
            measurements["Voltage_measured"]
        ).flatten()

        current = np.asarray(
            measurements["Current_measured"]
        ).flatten()

        temperature = np.asarray(
            measurements["Temperature_measured"]
        ).flatten()

        # ==========================================
        # STEP 8: Validate measurement lengths
        # ==========================================

        lengths = {
            len(time),
            len(voltage),
            len(current),
            len(temperature)
        }

        if len(lengths) != 1:
            raise ValueError(
                f"Measurement length mismatch: "
                f"{battery_id}, cycle {cycle_id}"
            )

        # ==========================================
        # STEP 9: Create measurement records
        # ==========================================

        for t, v, i, temp in zip(
            time,
            voltage,
            current,
            temperature
        ):

            measurement_records.append({
                "battery_id": battery_id,
                "cycle_id": cycle_id,
                "cycle_type": cycle_type,
                "time_seconds": float(t),
                "voltage_v": float(v),
                "current_a": float(i),
                "temperature_c": float(temp)
            })


# ==========================================
# STEP 10: Convert records into DataFrames
# ==========================================

cycles_df = pd.DataFrame(cycle_records)

measurements_df = pd.DataFrame(
    measurement_records
)


# ==========================================
# STEP 11: Save processed data in Parquet
# ==========================================

cycles_path = (
    OUTPUT_DIR / "battery_cycles.parquet"
)

measurements_path = (
    OUTPUT_DIR / "battery_measurements.parquet"
)

cycles_df.to_parquet(
    cycles_path,
    index=False
)

measurements_df.to_parquet(
    measurements_path,
    index=False
)


# ==========================================
# STEP 12: Display processing summary
# ==========================================

print("\n" + "=" * 45)
print("BATTERY ETL TRANSFORMATION COMPLETED")
print("=" * 45)

print(f"Battery files processed: {len(battery_files)}")
print(f"Total cycle records: {len(cycles_df):,}")
print(f"Total measurement records: {len(measurements_df):,}")

print("\nCycle type distribution:")
print(cycles_df["cycle_type"].value_counts())

print("\nCycle preview:")
print(cycles_df.head())

print("\nOutput files:")
print(cycles_path)
print(measurements_path)
