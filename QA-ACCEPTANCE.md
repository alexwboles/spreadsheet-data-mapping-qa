# Windows acceptance checks - October 10, 2026

## November 5 readable findings and export

Requirements: make the current audit understandable without reading JSON,
provide an offline report suitable for human review, preserve JSON consumers
and the existing atomic-save/input-protection behavior. Render the existing
audit rather than recalculate or infer results. Escape every spreadsheet value
in the HTML and load no scripts or external resources. This change adds no
external services or application dependencies.

Desktop results now show a plain-language findings list. Save readable report
exports HTML with the exact field map, counts, specific findings, next actions,
ID/notes settings and input basenames/SHA256 values. Reports say human review
pending. Malformed map JSON now identifies the line/column and gives a valid
mapping example and recovery instruction.

`py -3.11 -m unittest -v` ran 35 tests: 34 passed and one optional NSIS test was
skipped because NSIS_COMPILER was not supplied. New regressions exercise actual
desktop callbacks for invalid-map recovery, readable export and stale refusal;
HTML injection through IDs, headings, values and filenames; distinct defective,
corrected and unmapped decisions; and atomic HTML saving with replacement
failure, input-overwrite refusal and changed input. Earlier JSON tests passed.

`py -3.11 demo/service-workflow/run_demo.py` verified defective and corrected
JSON/HTML reports and unchanged synthetic inputs. The isolated local HTTP
preview returned 200. Browser control and its connection check timed out, so
rendered desktop/mobile, print and native Save As acceptance remain unverified
for this change. A browser reconnection request is pending. No customer data,
installer publication, message or paid service was used.

Existing CPython/PyInstaller tools also built an isolated unsigned review
executable at build/isolated-review-jnlilean/package. SHA256:
97efcc8252757391353d32de640417dccce2eb220f94d2f1b281fef48aee5985.
The builder accepted all 13 binary origins and five embedded dependency
notices. This is build evidence only. The new executable has not been launched,
installed, visually accepted or distributed.

## November 3 actual-payload installation review

Built normal-target and QA_ROOT installers from source
490afe621bbd0a8dba1cf51bbc7d6f836984bf09 with existing NSIS 3.13 and the
verified isolated application. Normal-target artifact SHA256:
9ba9a8b27aaa01a0d06bd3a2393e1a387ee8ba05c66b10eaafb96f9275800d21.
The normal-target installer was not run or distributed.

Only the separate QA_ROOT installer was executed in a fresh ignored build
directory. Setup returned zero; installed executable and seven notice files
matched expected hashes. The exact installed QA executable opened its native
interface and closed. Uninstall returned zero and removed known owned files
while preserving the synthetic report and unrelated note. This adds actual-
payload lifecycle evidence to the earlier synthetic-payload ownership tests.
It is still a test on the development PC with an explicit QA target, not
default-target or clean-machine acceptance. No existing app was replaced and
no real desktop shortcuts, Start Menu entries or uninstall registry entries
were written by the QA installer.

## November 3 isolated executable follow-through

Tested the isolated build with SHA256
943b394b95419a0d236e2528e8d80ecf38828e3872508e9d94b368d058b41285,
not the earlier November 2 binary. Native comparison passed four synthetic
records and Save As wrote native-pass-isolated-20261103.json. Parsed report
counts were 4/4 with passed:true and no field mismatches; all three saved input
SHA256 values matched the selected fixtures.

A controlled external edit to the selected migrated fixture then triggered
Report not saved, cleared the previous output and left the designated stale
report target absent. A malformed JSON mapping could not complete a new check
and Save report refused it. Restoring the mapping and rerunning the check
produced a valid passing result. All input fixtures were restored byte-for-byte
and verified. Only the isolated review window was closed.

This supplements the earlier observed defective-file audit/save on this same
binary. It is not a clean-machine test, application installer acceptance, or
proof of every possible error path. Native screenshots and parsed reports are
retained locally; no customer data, distribution or installed app was involved.

## November 3 installer notice inventory

Installer source now explicitly includes the five dependency notices, their
provenance manifest and README beside the installed application. The existing
NSIS 3.13 compiler built a QA-only installer using a non-executable synthetic
payload. A fresh install reproduced all seven files byte-for-byte; the five
license SHA256 values matched the reviewed manifest. An owned upgrade retained
an unrelated note in the notices folder. Uninstall removed only known notice
files and retained the unrelated note and report. Ownership-marker and path
override checks continued to pass. All 31 source/installer tests passed.

This test ran only in ignored build/installer-qa, with QA-local shortcuts and
no actual Desktop/Start Menu or uninstall-registry writes. It did not build,
install or publish a customer application installer. Later actual-payload QA
is recorded above; clean-machine and normal-target acceptance remain open.

## November 2 isolated native rebuild

Built the review-branch desktop app with the already installed Python 3.11.9
and PyInstaller 6.22.3, without downloading dependencies or replacing the
installed product. Candidate:
`build/native-review-20261102/artifacts/TechPartner-Spreadsheet-Check-Review.exe`.
SHA256: `D90622B404D7CBBD918AB76B30F7CC0DF680126C26027B1E2FB0F55D0E415BE8`.
The build includes the fingerprinted/atomic report-saving source. All 30
core, persistence and controlled desktop-callback tests pass under this exact
Python interpreter. The native build process completed normally.

The compiled executable launched its own window. Using copied synthetic CSVs
and the exact field map, the native Check files button correctly displayed
Review required, source/destination counts 4/5, duplicate 1001, missing 1003
and unexpected 1999. The native Save report button opened the expected Windows
Save As dialog. No customer files were selected or modified.

Report saving, complete native mismatch evidence, corrected recheck and stale
input refusal were NOT verified: the Windows automation helper could see but
could not activate the Save As dialog. A refreshed exact-window recovery also
failed, so native input stopped. Only the exact-path isolated review processes
were closed afterward; the preexisting installed application was not targeted.
No success is inferred from opening the dialog or from callback unit tests.

Observed usability follow-up: Save As starts in the launcher's current folder,
which may be an application/runtime folder. A future change should offer the
selected CSV's directory and a sensible report name, then verify that behavior
in the actual dialog. The app has not been changed for that follow-up yet.

The candidate remains local and unsigned. It has not been installed, published,
emailed or cleared for sale. Full native saving/recovery, clean-recipient setup,
bundled dependency notices and commercial-delivery acceptance remain open.
No spending, paid API calls, client records or verified sale resulted from QA.

## October 18 installer ownership review

The previous installer copied its named files into an existing directory without
checking ownership. The review-branch installer now rejects unmarked target
folders, fixes its target despite `/D` overrides, and verifies both directory
and product marker before uninstalling. Older unmarked installed versions are
not overwritten; backing up reports and using their existing uninstaller is
required before a future approved upgrade.

Native NSIS QA uses a non-executable synthetic payload in a fresh directory
under ignored `build/installer-qa`, with local QA-only shortcuts and no real
Desktop/Start Menu or uninstall-registry writes. It verifies unowned-folder
refusal with byte-for-byte preservation, a marked upgrade, missing/wrong marker
uninstall refusal, foreign-directory uninstall refusal, ignored install-directory
override, and preservation of an unrelated synthetic report on uninstall.
This is installer-control-flow QA only, not a rebuilt-application acceptance
test or a clean-machine test. No existing installed app was changed and no
artifact was delivered or advertised. Full release checks remain pending.

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

## November 3 isolated native report verification

Tested the November 2 unsigned review executable, SHA256
D90622B404D7CBBD918AB76B30F7CC0DF680126C26027B1E2FB0F55D0E415BE8,
on the existing development Windows PC. No installed product was replaced.

- Synthetic source (4 rows) / defective destination (5 rows) plus explicit map
  produced Review required. Native Save As completed and created parseable JSON.
- Saved report contained duplicate ID 1001, missing ID 1003, unexpected ID 1999
  and both swapped Name/Notes field mismatches for 1002; passed:false.
- Changing to the corrected destination immediately cleared old output. Running
  again displayed mapped-field checks passed; native Save As created a second
  report with passed:true, counts 4/4 and no field mismatches.
- Saved input basenames and SHA256 fingerprints matched the actual three files.
- After the passing check, a controlled edit to the ignored corrected fixture
  at the same path caused Report not saved / Input file contents changed.
  Stale output was cleared and the proposed stale report did not exist.
- Restored that synthetic fixture byte-for-byte from a test-only backup, then
  verified all three input fingerprints matched the passing report again.

The prior automation activation blocker is resolved for this workflow. File
picker accessibility actions were incomplete, but visible-coordinate entry and
keyboard confirmation worked. No client records, emails, payments or network
services were used. This does not establish clean-machine acceptance, rebuilt
installer readiness, signed binaries or completed dependency-notice review.
Software distribution is still not approved as sale-ready. The separately
reviewed export-report service does not require distributing this executable.
