
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

RAW_DIR = Path("data/raw/nasa/batteries")
MANIFEST_PATH = Path("data/manifest.json")

SOURCE_URL = (
    "https://phm-datasets.s3.amazonaws.com/"
    "NASA/5.+Battery+Data+Set.zip"
)


def calculate_sha256(file_path):
    """Calculate the SHA-256 checksum without loading the entire file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def create_manifest():
    battery_files = sorted(RAW_DIR.glob("B*.mat"))

    if not battery_files:
        raise FileNotFoundError(
            f"No battery files found in {RAW_DIR}"
        )

    records = []

    for file_path in battery_files:
        record = {
            "battery_id": file_path.stem,
            "path": file_path.as_posix(),
            "size_bytes": file_path.stat().st_size,
            "sha256": calculate_sha256(file_path)
        }

        records.append(record)
        print(f"Verified metadata: {file_path.name}")

    manifest = {
        "dataset": "NASA Li-ion Battery Aging Dataset",
        "source_url": SOURCE_URL,
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "file_count": len(records),
        "files": records
    }

    MANIFEST_PATH.parent.mkdir(
        parents=True, exist_ok=True
    )

    with open(MANIFEST_PATH, "w") as file:
        json.dump(manifest, file, indent=2)

    print(f"\nManifest saved to: {MANIFEST_PATH}")
    print(f"Total files: {len(records)}")


if __name__ == "__main__":
    create_manifest()
