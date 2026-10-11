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

Remaining customer-release checks: clean Windows machine, installer wizard,
file-picker workflow, uninstall/reinstall, and full rebuilt pass/save regression.
No public advertising or customer delivery was performed.
