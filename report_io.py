"""Local report persistence: protect inputs, detect stale audits and replace atomically."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path


class InputsChangedError(ValueError):
    """The current files are no longer the versions that produced the audit."""


def fingerprint_inputs(paths: list[Path]) -> dict[str, str]:
    fingerprints = {}
    for path in paths:
        resolved = path.resolve()
        digest = hashlib.sha256()
        with resolved.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        fingerprints[str(resolved)] = digest.hexdigest()
    return fingerprints


def verify_input_versions(paths: list[Path], expected: dict[str, str]) -> None:
    try:
        actual = fingerprint_inputs(paths)
    except OSError as exc:
        raise InputsChangedError("Input files changed or became unavailable. Run the check again before saving.") from exc
    if actual != expected:
        raise InputsChangedError("Input file contents changed. Run the check again before saving.")


def validate_report_target(target: Path, sources: list[Path]) -> Path:
    target = target.resolve()
    for source in sources:
        source = source.resolve()
        if target == source or (target.exists() and target.samefile(source)):
            raise ValueError("Choose a different file; original spreadsheets cannot be overwritten.")
    return target


def save_report_atomic(target: Path, payload: dict, sources: list[Path],
                       expected_fingerprints: dict[str, str]) -> Path:
    """Leave a previous report intact if serialization, writing or replacement fails.

    Checks detect ordinary external edits before and during save. They are not
    an OS-level lock against a hostile concurrent process changing files after
    the last check. Fingerprints identify the exact inputs the reviewer checked.
    """
    target = validate_report_target(target, sources)
    verify_input_versions(sources, expected_fingerprints)
    text = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         prefix=".spreadsheet-report-", suffix=".tmp",
                                         dir=target.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        verify_input_versions(sources, expected_fingerprints)
        validate_report_target(target, sources)
        os.replace(temporary, target)
        temporary = None
        return target
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
