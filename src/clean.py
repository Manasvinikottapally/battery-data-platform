
from pathlib import Path

import pandas as pd

INPUT_PATH = Path("data/processed/battery_measurements.parquet")
OUTPUT_DIR = Path("data/curated")

MIN_VOLTAGE = 0.0
MAX_VOLTAGE = 6.0

REQUIRED_COLUMNS = [
    "battery_id",
    "cycle_id",
    "voltage_v",
    "current_a",
    "temperature_c",
]


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Processed measurements not found: {INPUT_PATH}"
        )

    df = pd.read_parquet(INPUT_PATH)

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    missing_mask = df[
        ["voltage_v", "current_a", "temperature_c"]
    ].isna().any(axis=1)

    voltage_mask = (
        (df["voltage_v"] < MIN_VOLTAGE)
        | (df["voltage_v"] > MAX_VOLTAGE)
    )

    flagged_mask = missing_mask | voltage_mask

    clean_df = df.loc[~flagged_mask].copy()
    flagged_df = df.loc[flagged_mask].copy()

    flagged_df["quality_issue"] = ""

    flagged_df.loc[
        missing_mask.loc[flagged_df.index],
        "quality_issue"
    ] = "missing_measurement"

    flagged_df.loc[
        voltage_mask.loc[flagged_df.index],
        "quality_issue"
    ] += "|voltage_out_of_range"

    flagged_df["quality_issue"] = (
        flagged_df["quality_issue"].str.strip("|")
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    clean_df.to_parquet(
        OUTPUT_DIR / "battery_measurements_clean.parquet",
        index=False
    )

    flagged_df.to_parquet(
        OUTPUT_DIR / "battery_measurements_flagged.parquet",
        index=False
    )

    print("Battery data curation completed!")
    print(f"Total measurements: {len(df):,}")
    print(f"Clean measurements: {len(clean_df):,}")
    print(f"Flagged measurements: {len(flagged_df):,}")

    assert len(clean_df) + len(flagged_df) == len(df)


if __name__ == "__main__":
    main()
