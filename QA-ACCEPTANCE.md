# Windows acceptance checks - October 10, 2026

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
