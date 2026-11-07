
import hashlib
import json
from pathlib import Path

MANIFEST_PATH = Path("data/manifest.json")


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024), b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_manifest():
    with open(MANIFEST_PATH) as file:
        manifest = json.load(file)

    errors = []

    for record in manifest["files"]:
        file_path = Path(record["path"])

        if not file_path.is_file():
            errors.append(f"Missing file: {file_path}")
            continue

        actual_size = file_path.stat().st_size
        actual_hash = calculate_sha256(file_path)

        if actual_size != record["size_bytes"]:
            errors.append(f"Size mismatch: {file_path}")

        if actual_hash != record["sha256"]:
            errors.append(f"SHA-256 mismatch: {file_path}")

        if (
            actual_size == record["size_bytes"]
            and actual_hash == record["sha256"]
        ):
            print(f"PASS: {file_path.name}")

    if errors:
        print("\nVerification failed:")
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)

    if len(manifest["files"]) != manifest["file_count"]:
        raise SystemExit("FAIL: Manifest file count mismatch")

    print("\nAll battery files verified successfully!")


if __name__ == "__main__":
    verify_manifest()
