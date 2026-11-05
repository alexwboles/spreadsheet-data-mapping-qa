"""Reproduce a synthetic review and recheck; never processes customer files."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from data_mapping_qa import _read_csv, audit_rows, read_field_map
from report_io import fingerprint_inputs, save_report_atomic, verify_input_versions
from readable_report import html_report


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    fixtures = Path(__file__).resolve().parent
    output = ROOT / "build" / "synthetic-service-delivery"
    output.mkdir(parents=True, exist_ok=True)
    all_inputs = [fixtures / name for name in
                  ("source.csv", "needs-review.csv", "corrected.csv", "field-map.json")]
    original_versions = fingerprint_inputs(all_inputs)
    for name, expected_pass in (("needs-review", False), ("corrected", True)):
        paths = [fixtures / "source.csv", fixtures / f"{name}.csv", fixtures / "field-map.json"]
        versions = fingerprint_inputs(paths)
        audit = audit_rows(_read_csv(paths[0]), _read_csv(paths[1]),
                           id_field="Record ID", notes_field="Activity",
                           field_map=read_field_map(paths[2]))
        verify_input_versions(paths, versions)
        require(audit.passed == expected_pass, f"Unexpected decision for {name}")
        require(audit.source_count == 4, "Source fixture count changed")
        if not expected_pass:
            require(audit.destination_count == 5, "Broken fixture count changed")
            require(audit.duplicate_destination_ids == ["1001"], "Duplicate not detected")
            require(audit.missing_destination_ids == ["1003"], "Missing record not detected")
            require(audit.unexpected_destination_ids == ["1999"], "Unexpected record not detected")
            require(set(audit.field_mismatches) == {"1002"}, "Unexpected mismatch IDs")
            require({item["source_field"] for item in audit.field_mismatches["1002"]}
                    == {"Name", "Notes"}, "Swapped fields not detected")
        else:
            require(audit.destination_count == 4, "Corrected fixture count changed")
        payload = asdict(audit) | {"passed": audit.passed, "synthetic": True,
                    "id_field": "Record ID", "notes_field": "Activity",
                    "input_files": [{"role": role, "name": path.name,
                                     "sha256": versions[str(path.resolve())]}
                                    for role, path in zip(("source", "destination", "field_map"), paths)]}
        target = output / f"{name}-report.json"
        save_report_atomic(target, payload, paths, versions)
        require(json.loads(target.read_text(encoding="utf-8")) == payload,
                "Saved report differs from checked results")
        readable_target = output / f"{name}-report.html"
        save_report_atomic(readable_target, payload, paths, versions, render=html_report)
        require(readable_target.read_text(encoding="utf-8") == html_report(payload),
                "Readable report differs from checked results")
        print(f"{name}: {'PASS' if audit.passed else 'REVIEW REQUIRED'}; "
              f"source={audit.source_count}, destination={audit.destination_count}; {target.name}")
    verify_input_versions(all_inputs, original_versions)
    print("Original fixtures unchanged; both saved reports verified.")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
