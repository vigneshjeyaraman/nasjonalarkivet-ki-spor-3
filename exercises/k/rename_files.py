"""Rename dated inbox files to YYYY-MM-DD_description.ext."""

import argparse
import re
from datetime import date
from pathlib import Path


DATE_PATTERNS = (
    re.compile(r"(?<!\d)(\d{4})[-_](\d{2})[-_](\d{2})(?!\d)"),
    re.compile(r"(?<!\d)(\d{2})\.(\d{2})\.(\d{4})(?!\d)"),
)
NORWEGIAN_LETTERS = str.maketrans({"æ": "ae", "ø": "o", "å": "a"})
INBOX = Path(__file__).resolve().parent / "inbox"


def target_name(filename):
    """Return the new name, or None when the name has no valid date."""
    path = Path(filename)
    stem = path.stem
    for index, pattern in enumerate(DATE_PATTERNS):
        match = pattern.search(stem)
        if not match:
            continue
        parts = match.groups()
        year, month, day = parts if index == 0 else (parts[2], parts[1], parts[0])
        try:
            parsed = date(int(year), int(month), int(day))
        except ValueError:
            continue
        description = stem[: match.start()] + stem[match.end() :]
        description = re.sub(r"\s*\(\d+\)", "", description)
        description = description.lower().translate(NORWEGIAN_LETTERS)
        description = re.sub(r"[^a-z0-9]+", "-", description).strip("-")
        if not description:
            return None
        return f"{parsed.isoformat()}_{description}{path.suffix.lower()}"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Rename files after checking for collisions")
    args = parser.parse_args()

    files = sorted(path for path in INBOX.iterdir() if path.is_file())
    planned = [(path, path.with_name(new_name)) for path in files
               if (new_name := target_name(path.name)) and new_name != path.name]
    targets = {}
    collisions = []
    for source, target in planned:
        if target in targets:
            collisions.append(f"{source.name} and {targets[target].name} -> {target.name}")
        elif target.exists():
            collisions.append(f"{source.name} -> existing {target.name}")
        targets[target] = source

    print("Mode: APPLY" if args.apply else "Mode: DRY RUN")
    for source, target in planned:
        print(f"Rename: {source.name} -> {target.name}")
    for path in files:
        if target_name(path.name) is None:
            print(f"No date, left alone: {path.name}")
    if collisions:
        for collision in collisions:
            print(f"Collision: {collision}")
        print("No files changed; resolve the collisions before applying.")
        return 1

    if args.apply:
        for source, target in planned:
            source.rename(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
