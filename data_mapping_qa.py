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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


def normalize(value: object) -> str:
    """Normalize text for loss-detection comparisons."""

    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


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
) -> MappingAudit:
    """Compare source and destination records and return a review-ready audit."""

    source_ids = _ids(source_rows, id_field)
    destination_ids = _ids(destination_rows, id_field)
    source_counts = Counter(source_ids)
    destination_counts = Counter(destination_ids)

    source_by_id = {normalize(row.get(id_field)): row for row in source_rows}
    destination_by_id = {
        normalize(row.get(id_field)): row for row in destination_rows
    }

    potential_loss: dict[str, list[str]] = {}
    for record_id in sorted(set(source_by_id) & set(destination_by_id)):
        source = source_by_id[record_id]
        destination_text = " | ".join(
            normalize(value) for value in destination_by_id[record_id].values()
        )
        missing_values = []
        for field, raw_value in source.items():
            value = normalize(raw_value)
            if field == id_field or not value:
                continue
            if value not in destination_text:
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
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a mapped CSV against its source")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--id-field", required=True)
    parser.add_argument("--notes-field", default="Notes")
    args = parser.parse_args()

    audit = audit_rows(
        _read_csv(args.source),
        _read_csv(args.destination),
        id_field=args.id_field,
        notes_field=args.notes_field,
    )
    payload = asdict(audit) | {"passed": audit.passed}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if audit.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
