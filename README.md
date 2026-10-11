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
share them only with authorized recipients. This tool flags possible data loss,
not correct semantic field placement. Human review remains required.

A small, dependency-free Python utility for checking a human-reviewed
spreadsheet migration before delivery. It does not guess where ambiguous text
belongs. Instead, it creates a focused review queue for:

- missing or unexpected record IDs;
- duplicate source or destination IDs;
- source values that may have been lost during mapping;
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
