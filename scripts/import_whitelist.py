#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import DATA_DIR  # noqa: E402
from app.validation import is_valid_github_username, normalize_username  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import approved GitHub usernames from a CSV file."
    )
    parser.add_argument("csv_path", help="Path to a CSV file with GitHub usernames.")
    parser.add_argument(
        "--column",
        default="github_username",
        help=(
            "Header name containing GitHub usernames. If the CSV has no matching "
            "header, the first column is used."
        ),
    )
    return parser.parse_args()


KNOWN_USERNAME_HEADERS = {
    "github_username",
    "github username",
    "github",
    "username",
    "user",
    "login",
}


def _looks_like_header(row: list[str], requested_column: str) -> bool:
    normalized_cells = {cell.strip().lower() for cell in row}
    return (
        requested_column.strip().lower() in normalized_cells
        or bool(normalized_cells & KNOWN_USERNAME_HEADERS)
    )


def extract_usernames(csv_path: Path, column: str) -> tuple[list[str], list[str]]:
    valid_usernames: set[str] = set()
    rejected: list[str] = []

    with csv_path.open(newline="") as csv_file:
        reader = csv.reader(csv_file)
        rows = list(reader)

        if not rows:
            return [], []

        first_row = rows[0]
        if _looks_like_header(first_row, column):
            header = [cell.strip() for cell in first_row]
            lowercase_header = [cell.lower() for cell in header]
            requested_column = column.strip().lower()
            selected_index = (
                lowercase_header.index(requested_column)
                if requested_column in lowercase_header
                else 0
            )
            username_values = (
                row[selected_index] if len(row) > selected_index else ""
                for row in rows[1:]
            )
        else:
            username_values = (row[0] if row else "" for row in rows)

        for raw_username in username_values:
            username = normalize_username(raw_username)
            if is_valid_github_username(username):
                valid_usernames.add(username)
            elif username:
                rejected.append(username)

    return sorted(valid_usernames), rejected


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

    usernames, rejected = extract_usernames(csv_path, args.column)
    save_whitelist(usernames)

    print(f"Saved {len(usernames)} usernames to data/whitelist.json.")
    if rejected:
        print(f"Skipped {len(rejected)} invalid username(s).", file=sys.stderr)


if __name__ == "__main__":
    main()
