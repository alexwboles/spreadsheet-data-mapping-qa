# TechPartner CSV migration review - synthetic sample

This illustrates the proposed service deliverable. All names and records are
fictional. It is not a customer result or testimonial.

## Inputs and agreed comparison

Original: original.csv. Migrated: missing-record.csv.
Record identifier: Record ID. Fields: Name and Notes.
Expected transformation: none. Each ID should keep its name and notes.

## Findings

| Check | Finding | Proposed action |
| --- | --- | --- |
| Record count | Original has 2 records; migrated has 1 | Restore the omitted record |
| Missing ID | Record ID 2 is absent | Restore Sample Contact and its note |
| Duplicate IDs | None in either file | No action |
| Preserved values | ID 1 retains Demo Customer and Follow up on Friday | No action |
| Field placement | Manually checked Name and Notes for the surviving record | No correction needed for ID 1 |

Decision: review required. Do not replace the original with this migrated file.

## Recheck illustration

The matching migrated.csv includes both records. The tool produced the saved
qa-rebuilt-report.json with counts 2 and 2 and `passed: true`.
Manual comparison of both names and notes matches the original.

The automated check ignores case and repeated whitespace and searches across
destination fields. It does not independently prove correct field placement,
case-sensitive identifiers, date conversions, or business meaning. Those require
an agreed mapping and human review. The report records that scope explicitly.

## Delivery contents

A real accepted engagement would deliver a findings summary, the machine-readable
audit, agreed mapping and exceptions, and one recheck. Original exports stay
unchanged. Any corrected data file would require separate agreed scope.
