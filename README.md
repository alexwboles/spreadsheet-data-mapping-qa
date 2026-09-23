# Spreadsheet Data-Mapping QA

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
