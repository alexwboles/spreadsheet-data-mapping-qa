# Synthetic service delivery lifecycle

## Plan

Help a prospective buyer understand what a narrowly scoped CSV reconciliation
report provides. Reuse the existing tested local engine. No new dependencies,
API charges, customer data, application release or production deployment.

## Requirements and acceptance

- Invented fixtures demonstrate renamed headings, a duplicate, a missing ID,
  an unexpected ID, swapped fields and a corrected recheck.
- The broken sample must fail with those specific findings; correction must
  pass all agreed mapped fields. Neither run may alter input bytes.
- Save readable JSON with input hashes and verify its content after saving.
- A plain-language summary explains actions, limitations, intake and price.
- Do not imply a passing comparison certifies an entire CRM migration.

## Design

Four static fixture files plus a dependency-free local runner that calls the
existing comparison and atomic persistence modules. Output stays under ignored
build/. The runner only uses its bundled synthetic fixtures, not arbitrary paths.

## Development

Keep this sample in the existing spreadsheet-data-mapping-qa repository and
review branch. Use explicit runtime checks so Python optimization cannot remove
acceptance checks. Avoid modifying existing application or installer behavior.

## Test

Run the sample end to end and the existing 30 engine/persistence/callback tests.
Inspect JSON findings and hashes, and review the written summary against those
results. This does not validate a rebuilt Windows app or clean-machine install.

## Delivery

Commit verified synthetic demo materials to the existing GitHub review branch.
No advertising, client email, main-branch merge or release is part of this task.
Customer deliveries require approved intake, authorized data handling, reviewed
findings and explicit send approval. Payment is tracked separately from leads.

## Maintenance

Re-run the demo and relevant tests after comparison or persistence changes.
Update fixtures and summary together when behavior changes. Customer reports
must name the exact inputs checked and disclose unresolved issues.

## Verification record — November 2, 2026

The synthetic workflow ran successfully: the first audit reported the expected
duplicate 1001, missing 1003, unexpected 1999 and both swapped fields for 1002.
The corrected four-record audit passed. Both saved reports matched the checked
payloads and all input fingerprints remained unchanged. The existing 30
engine, persistence and desktop callback tests passed. No native app or
clean-machine test was performed, and no production release is implied.
