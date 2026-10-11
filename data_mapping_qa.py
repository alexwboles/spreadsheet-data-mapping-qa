"""Quality-control helpers for human-reviewed spreadsheet mapping work.

The checks are intentionally conservative: they flag records for review rather
than guessing where ambiguous free text belongs.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


def normalize(value: object) -> str:
    """Normalize text for loss-detection comparisons."""

    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip().casefold()


def flatten_notes(value: object) -> str:
    """Put separate note lines on one line without dropping their content."""

    parts = [part.strip() for part in re.split(r"[\r\n]+", str(value or ""))]
    return " / ".join(part for part in parts if part)


@dataclass(frozen=True)
class MappingAudit:
    source_count: int
    destination_count: int
    duplicate_source_ids: list[str]
    duplicate_destination_ids: list[str]
    missing_destination_ids: list[str]
    unexpected_destination_ids: list[str]
    notes_with_line_breaks: list[str]
    potentially_lost_values: dict[str, list[str]]
    checked_field_map: dict[str, str] = field(default_factory=dict)
    field_mismatches: dict[str, list[dict[str, str]]] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not any(
            (
                self.duplicate_source_ids,
                self.duplicate_destination_ids,
                self.missing_destination_ids,
                self.unexpected_destination_ids,
                self.notes_with_line_breaks,
                self.potentially_lost_values,
                self.field_mismatches,
            )
        )


def _ids(rows: Iterable[dict[str, str]], id_field: str) -> list[str]:
    return [normalize(row.get(id_field)) for row in rows]


def audit_rows(
    source_rows: list[dict[str, str]],
    destination_rows: list[dict[str, str]],
    *,
    id_field: str,
    notes_field: str = "Notes",
    field_map: dict[str, str] | None = None,
) -> MappingAudit:
    """Compare source and destination records and return a review-ready audit."""

    if not id_field.strip():
        raise ValueError("Choose a record ID column.")
    for label, rows in (("Source", source_rows), ("Destination", destination_rows)):
        if not rows:
            raise ValueError(f"{label} has no records; an empty file cannot pass validation.")
        for number, row in enumerate(rows, start=2):
            if id_field not in row or not normalize(row[id_field]):
                raise ValueError(f"{label} row {number}: missing record ID in '{id_field}'.")

    if field_map is not None:
        if not isinstance(field_map, dict) or not field_map:
            raise ValueError("Field map must be a nonempty JSON object of source and destination headings.")
        if any(not isinstance(name, str) or not name.strip()
               for pair in field_map.items() for name in pair):
            raise ValueError("Field map headings must be nonempty strings.")
        if id_field in field_map or id_field in field_map.values():
            raise ValueError("Do not map the record ID as a value field.")
        if len(set(field_map.values())) != len(field_map):
            raise ValueError("Each mapped destination heading must be unique.")
        for label, rows, headings in (
            ("Source", source_rows, field_map.keys()),
            ("Destination", destination_rows, field_map.values()),
        ):
            for number, row in enumerate(rows, start=2):
                for heading in headings:
                    if heading not in row:
                        raise ValueError(f"{label} row {number}: missing mapped heading '{heading}'.")
    checked_map = dict(field_map or {})

    source_ids = _ids(source_rows, id_field)
    destination_ids = _ids(destination_rows, id_field)
    source_counts = Counter(source_ids)
    destination_counts = Counter(destination_ids)

    source_by_id = {normalize(row.get(id_field)): row for row in source_rows}
    destination_by_id = {
        normalize(row.get(id_field)): row for row in destination_rows
    }

    potential_loss: dict[str, list[str]] = {}
    field_mismatches: dict[str, list[dict[str, str]]] = {}
    for record_id in sorted(set(source_by_id) & set(destination_by_id)):
        source = source_by_id[record_id]
        destination = destination_by_id[record_id]
        mismatches = [
            {"source_field": source_field, "destination_field": destination_field,
             "expected": source[source_field], "actual": destination[destination_field]}
            for source_field, destination_field in checked_map.items()
            if source[source_field] != destination[destination_field]
        ]
        if mismatches:
            field_mismatches[record_id] = mismatches
        destination_text = " | ".join(
            normalize(value) for value in destination_by_id[record_id].values()
        )
        missing_values = []
        for field, raw_value in source.items():
            value = normalize(raw_value)
            if field == id_field or field in checked_map or not value:
                continue
            if not re.search(r"(?<!\w)" + re.escape(value) + r"(?!\w)", destination_text):
                missing_values.append(f"{field}: {str(raw_value).strip()}")
        if missing_values:
            potential_loss[record_id] = missing_values

    notes_with_breaks = sorted(
        record_id
        for record_id, row in destination_by_id.items()
        if "\n" in str(row.get(notes_field, ""))
        or "\r" in str(row.get(notes_field, ""))
    )

    return MappingAudit(
        source_count=len(source_rows),
        destination_count=len(destination_rows),
        duplicate_source_ids=sorted(
            record_id for record_id, count in source_counts.items() if count > 1
        ),
        duplicate_destination_ids=sorted(
            record_id for record_id, count in destination_counts.items() if count > 1
        ),
        missing_destination_ids=sorted(set(source_ids) - set(destination_ids)),
        unexpected_destination_ids=sorted(set(destination_ids) - set(source_ids)),
        notes_with_line_breaks=notes_with_breaks,
        potentially_lost_values=potential_loss,
        checked_field_map=checked_map,
        field_mismatches=field_mismatches,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        headers = reader.fieldnames
        if not headers or any(not name.strip() for name in headers):
            raise ValueError("CSV must contain nonempty column headings.")
        if len(set(headers)) != len(headers):
            raise ValueError("CSV contains duplicate column headings.")
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"CSV line {reader.line_num}: wrong number of columns.")
            rows.append(row)
        return rows


def read_field_map(path: Path) -> dict[str, str]:
    def unique_headings(pairs):
        result = {}
        for heading, destination in pairs:
            if heading in result:
                raise ValueError(f"Field map repeats source heading '{heading}'.")
            result[heading] = destination
        return result
    mapping = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_headings)
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("Field map must be a nonempty JSON object of source and destination headings.")
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a mapped CSV against its source")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--id-field", required=True)
    parser.add_argument("--notes-field", default="Notes")
    parser.add_argument("--field-map", type=Path,
                        help="JSON object mapping source headings to destination headings; values are compared exactly")
    args = parser.parse_args()

    try:
        audit = audit_rows(
            _read_csv(args.source),
            _read_csv(args.destination),
            id_field=args.id_field,
            notes_field=args.notes_field,
            field_map=read_field_map(args.field_map) if args.field_map else None,
        )
    except (ValueError, OSError, UnicodeError, csv.Error) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    payload = asdict(audit) | {"passed": audit.passed}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if audit.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
