#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import DATA_DIR  # noqa: E402
from app.validation import is_valid_github_username, normalize_username  # noqa: E402

DEFAULT_ROSTER_PATH = DATA_DIR / "classroom_roster.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import approved GitHub usernames from a GitHub Classroom roster CSV."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=str(DEFAULT_ROSTER_PATH),
        help="Path to a GitHub Classroom roster CSV file. Defaults to data/classroom_roster.csv.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print usernames and summary without writing data/whitelist.json.",
    )
    return parser.parse_args()


@dataclass(frozen=True)
class ImportResult:
    usernames: list[str]
    total_rows: int
    skipped_rows: int
    duplicates_removed: int


def extract_usernames(csv_path: Path) -> ImportResult:
    raw_valid_usernames: list[str] = []
    skipped_rows = 0
    total_rows = 0

    with csv_path.open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []
        if "github_username" not in fieldnames:
            raise ValueError(
                "Missing required CSV column: github_username. Expected columns "
                "include identifier, github_username, github_id, name."
            )

        for row in reader:
            total_rows += 1
            username = normalize_username(row.get("github_username", ""))
            if not username:
                skipped_rows += 1
                continue

            if is_valid_github_username(username):
                raw_valid_usernames.append(username)
            else:
                skipped_rows += 1

    usernames = sorted(set(raw_valid_usernames))
    duplicates_removed = len(raw_valid_usernames) - len(usernames)
    return ImportResult(
        usernames=usernames,
        total_rows=total_rows,
        skipped_rows=skipped_rows,
        duplicates_removed=duplicates_removed,
    )


def save_whitelist(usernames: list[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "whitelist.json"
    path.write_text(json.dumps(usernames, indent=2) + "\n")


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}", file=sys.stderr)
        raise SystemExit(1)

    try:
        result = extract_usernames(csv_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Total rows: {result.total_rows}")
    print(f"Valid usernames: {len(result.usernames)}")
    print(f"Skipped rows: {result.skipped_rows}")
    print(f"Duplicates removed: {result.duplicates_removed}")

    if args.dry_run:
        print(json.dumps(result.usernames, indent=2) + "\n")
        print("Dry run: no files written.")
        return

    save_whitelist(result.usernames)
    print("Saved usernames to data/whitelist.json.")


if __name__ == "__main__":
    main()
