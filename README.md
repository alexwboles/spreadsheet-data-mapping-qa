# Spreadsheet Data-Mapping QA

## Desktop interface (development version)

`python desktop.py` opens a local file picker, exact column-name inputs,
clear check status and a saveable JSON report. No network services are used.
The bundled Windows installer and installed core workflow have been checked
on the development PC. See QA-ACCEPTANCE.md for evidence and remaining release
checks. Clean-machine acceptance is pending; this is not yet cleared for sale.

Input must be UTF-8 CSV with unique, nonempty headings and consistent row
widths. Both files must contain records and a nonblank ID on every row.
Invalid input cannot produce a passing audit. Reports can contain source data;
share them only with authorized recipients. An optional field map checks exact
values in agreed destination columns. Without one, the preservation scan does
not check field placement. Human review remains required.

A small, dependency-free Python utility for checking a human-reviewed
spreadsheet migration before delivery. It does not guess where ambiguous text
belongs. Instead, it creates a focused review queue for:

- missing or unexpected record IDs;
- duplicate source or destination IDs;
- source values that may have been lost during mapping;
- exact-value mismatches in explicitly mapped columns, including renamed headings;
- remaining multiline Notes cells that should be flattened; and
- source/destination record-count differences.

## Run the tests

```powershell
python -m unittest -v
```

## Audit exported CSV files

```powershell
python data_mapping_qa.py source.csv destination.csv --id-field "Record ID" --notes-field Notes
```

The command returns exit code `0` only when all checks pass. Potentially lost
values are warnings for human review; the tool never moves ambiguous content
automatically.

## Check agreed field placement

Create a JSON map such as `{"Name": "Full Name", "Notes": "Comments"}` and
choose it with the desktop app's Field map Browse button, or use:

```powershell
python data_mapping_qa.py source.csv destination.csv --id-field "Record ID" --field-map mapping.json
```

Mapped values are compared exactly, including case, whitespace and empty values.
Expected formatting changes can be reported as mismatches; the tool does not
guess conversions or business meaning. Partial maps check only their listed
columns; remaining values receive the original preservation scan. Record IDs
still use case-insensitive, whitespace-normalized matching. Nonempty unique
headings are required and merged/split field mappings are not supported.

The report records `checked_field_map` and `field_mismatches` so reviewers can
see which fields were checked. Invalid maps cannot silently fall back to a pass.
Report saving rejects input aliases, including hard links, as overwrite targets.

## Review-branch report safety

The desktop source now fingerprints source, destination and optional map files
before/after checking, and verifies those versions again before replacing a
report. Saved desktop reports include input basenames and SHA256 fingerprints
(not full local paths) to identify the versions reviewed. An ordinary external
edit at the same path invalidates saving, clears the stale display and requires
a new check. This is change detection, not a filesystem lock against hostile
concurrent edits.

Saving writes and flushes a temporary file in the report's directory, then
atomically replaces the destination. Serialization, flush and replacement
failure tests preserve the previous report and clean the temporary file. Input
and map overwrite protections still apply. Reports may contain source data;
they must remain restricted to authorized recipients.

All 30 source tests pass, including the actual desktop callbacks exercised with
controlled test widgets (not a native window/picker test). These fixes are on a
separate review branch; the existing Windows executable/installer has NOT been
rebuilt or installed with them. Native GUI, rebuilt-package and clean-machine
acceptance remain pending. No commercial readiness or payment is established.
