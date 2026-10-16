# Windows acceptance checks - October 10, 2026

## October 16 report-persistence source review

Source review found direct destination truncation during report saving and no
check for files edited externally at the same selected path after an audit.
Added same-directory temporary write/flush/atomic replace, input version checks,
and input SHA256/basename evidence in desktop reports. Stale results are cleared
and cannot be saved after an ordinary input/map edit or removal.

All 30 source tests pass: the previous 19 mapping/input-protection tests plus
9 report persistence tests and 2 actual callback tests using controlled widget
substitutes. Fault injection covers blocked replacement, failed flush, invalid
JSON payload, changes before/during saving, removed inputs and changed maps.
Previous reports and protected inputs remain unchanged; temporary files are
cleaned in the exercised failure cases. Callback tests verify honest failure
messages and clearing stale output. No native window was opened in these tests.

These changes are on a separate GitHub review branch and have not been merged,
rebuilt into the existing installer/executable or installed. Earlier native
acceptance evidence below applies to the older build, not these new callbacks.
Native/rebuilt-package, clean-machine and distribution checks remain pending.
No advertising, client messages, customer records, paid calls or spending were
used in this source QA. No sale or payment is verified.

## Historical native checks for earlier builds

Synthetic data only. Tested on Alex's existing Windows PC, not a clean machine.

- Installer exited 0; installed executable, guide, uninstaller, desktop shortcut,
  and Windows uninstall registration were verified.
- Installed executable launched and rendered its complete interface.
- Matching two-record CSVs displayed `passed: true` with both counts equal to 2.
- Save report created valid JSON with the expected counts and result.
- A migrated CSV missing record 2 displayed `passed: false` and missing ID 2.
- Changing inputs invalidated saving but initially left old results visible.
  Fixed and rebuilt with Python 3.11.9/PyInstaller 6.22.3 and NSIS 3.13.
- Rebuilt installation exited 0; installed and built executable SHA256 hashes
  matched: 9230705B047F55684D509D4D0B1487DE26DDAC571C3A1C85F043267E198F0AC1.
- Rebuilt installed app displayed a missing-file error, then cleared that old
  result immediately when the original-file input changed.
- All 12 validation tests passed after the source change.

Additional acceptance checks completed in the next goal turn:

- Migrated-file Browse opened the Windows picker; double-clicking migrated.csv
  selected it and the rebuilt app displayed the expected passing two-record audit.
- Rebuilt Save report wrote demo/qa-rebuilt-report.json with `passed: true` and
  both counts equal to 2. Original and migrated CSV SHA256 hashes stayed unchanged.
- Silent uninstall exited 0 and removed the app, desktop shortcut, and uninstall
  registration. Source CSVs and saved reports remained present.
- Visible installer welcome, installation, and completion screens worked;
  reinstall restored the app, shortcut, and registration. Installed executable
  hash matched the build again.
- A synthetic in-memory 5,000-row, 30-column audit passed in 10.125 seconds on
  this development PC. This is one measured workload, not a speed guarantee.

Remaining downloadable-app release checks: clean Windows machine acceptance and
review of bundled dependency notices before distribution. No clean Windows VM
or Windows Sandbox executable was found in the available environment.

The proposed reviewed CSV reconciliation service uses the locally installed
tool and supplies a reviewed report, not a customer software installation.
No public advertising or customer delivery was performed.

## Release candidate 0.3.0 - mapped-field checks

- Added explicit source/destination column maps with exact-value comparisons.
  Swapped values are flagged even when all original words remain in the record.
- Invalid/empty maps, duplicate JSON source keys, absent mapped headings,
  repeated destination headings and mappings of the ID field are rejected.
- Report target checks also protect source/map files through hard-link aliases.
- All 19 tests passed, including subprocess CLI pass/failure and input preservation.
- A 5,000-row, 29-mapped-field comparison passed in 0.716 seconds on this PC.
- Final executable and installer rebuilt successfully. Installation exited 0,
  registered version 0.3.0 and matched build/installed executable SHA256:
  3A9CC54E4118C7892D02FB40CF5FDE888F4EB516306DD9E15A8DBDA7E1308BF2.
- Installed app loaded field-map.json through its Browse picker and reported
  two field mismatches for swapped-fields.csv. Save report generated
  demo/qa-mapped-report.json with `passed: false`, counts 2/2 and both mismatches.
- Selecting corrected migrated.csv cleared the stale report; Check files then
  displayed mapped-field checks passed, no mismatches, and `passed: true`.

Clean-machine and bundled-notice review remain pending for software distribution.
