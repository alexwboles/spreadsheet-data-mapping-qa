# A CSV migration review, from findings to recheck

All records are invented. This is a reproducible sample, not customer work,
a testimonial, a full migration certification or evidence of a sale.

## What the buyer receives

A human-reviewed findings summary, machine-readable audit, the agreed field
map and exceptions, and one recheck after corrections supplied by the customer.
The customer does not need to install software for this service.

## Agreed comparison

Compare source.csv with needs-review.csv using Record ID. Map Name to Contact,
Notes to Activity, and Status to Stage, with exact values and no transformations.
Identifiers in this tool are case-insensitive and whitespace-normalized. A
case-sensitive identifier requirement is outside this service's accepted scope.

| Finding | Evidence | Action for the migration owner |
| --- | --- | --- |
| Record counts differ | 4 source rows; 5 destination rows | Resolve the specific issues below; equal counts alone do not prove correctness |
| Duplicate | ID 1001 appears twice in the destination | Confirm the intended record and remove the extra copy |
| Missing record | ID 1003 absent from the destination | Restore the record and its mapped fields |
| Unexpected record | ID 1999 absent from the source | Confirm origin and whether it belongs in this migration |
| Swapped fields | ID 1002 has the note in Contact and name in Activity | Correct both fields using the agreed map |

**Initial decision: review required.** Do not approve the migration based on this
export. Duplicate IDs also make the corresponding value comparisons ambiguous;
the duplicate must be resolved before accepting a recheck.

## Recheck

The illustrative corrected.csv has all four original IDs exactly once and all
three mapped fields match. Its automated checks pass. A human still confirms
mapping completeness, intended transformations, exclusions and business meaning.
The fixture is supplied only to demonstrate a recheck; fixing customer exports
is not included in the proposed review price.

## Reproduce locally

From this repository root, with Python 3.10 or later:

```powershell
python demo/service-workflow/run_demo.py
```

No packages, API keys, network calls or customer files are needed. The runner
verifies expected defects, corrected results, saved JSON and unchanged input
hashes. Reports go to ignored build/synthetic-service-delivery. Reruns replace
only those two named synthetic reports using the tested atomic report writer.
Each report records the checked input basenames and SHA256 hashes.

For a real engagement, obtain approved scope, mapping, transfer channel and
retention terms before receiving records. Reports can contain input values;
share only with authorized recipients after Alex reviews the findings.

## Proposed commercial scope

$125 USD: one accepted UTF-8 CSV pair, up to 5,000 rows per file and 30 columns,
stable IDs, agreed field checks, findings and one recheck. Two business days
after accepting the files and mapping. Excludes attachments, relationships,
automations and transformations requiring interpretation. Payment arrangements
must be agreed before accepting an order. No paid engagement is established.
