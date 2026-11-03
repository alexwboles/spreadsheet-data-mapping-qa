"""Opt-in native installer tests with a non-executable synthetic payload.

Set NSIS_COMPILER to an existing makensis.exe. No dependencies are downloaded.
All installation targets and artifacts stay in build/installer-qa. QA builds
omit real Desktop/Start Menu shortcuts and Windows uninstall registry writes.
The synthetic .exe is only compared as bytes, never launched. Artifacts remain
for inspection; there is no recursive cleanup.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
COMPILER = os.environ.get("NSIS_COMPILER", "")


@unittest.skipUnless(os.name == "nt" and COMPILER and Path(COMPILER).is_file(),
                     "requires Windows and explicit NSIS_COMPILER")
class InstallerSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / "build" / "installer-qa"
        base.mkdir(parents=True, exist_ok=True)
        cls.work = Path(tempfile.mkdtemp(prefix="ownership-", dir=base)).resolve()
        if not cls.work.is_relative_to(base.resolve()):
            raise RuntimeError("QA target escaped build/installer-qa")
        cls.target = cls.work / "installed"
        cls.package = cls.work / "Synthetic-Installer-Safety-QA.exe"
        cls.payload = cls.work / "synthetic-payload.txt"
        cls.payload.write_bytes(b"SYNTHETIC INSTALLER TEST ONLY - NOT AN APPLICATION\n")
        result = subprocess.run([
            COMPILER, "/V2", f"/DQA_ROOT={cls.target}",
            f"/DPACKAGE_OUT={cls.package}", f"/DPAYLOAD_EXE={cls.payload}",
            str(ROOT / "installer.nsi"),
        ], cwd=ROOT, capture_output=True, text=True, timeout=90)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def run_setup(self):
        return subprocess.run([str(self.package), "/S"], timeout=30).returncode

    def run_uninstall(self):
        # _?= keeps NSIS in this explicit QA directory and waits for completion.
        return subprocess.run([str(self.target / "Uninstall.exe"), "/S",
                               f"_?={self.target}"], timeout=30).returncode

    def test_owned_install_and_uninstall_protect_unrelated_files(self):
        self.target.mkdir()
        app = self.target / "TechPartner-Spreadsheet-Check.exe"
        app.write_bytes(b"UNRELATED EXISTING FILE")
        sentinel = self.target / "user-report.json"
        sentinel.write_bytes(b'{"synthetic":true}')
        before = {p.name: p.read_bytes() for p in self.target.iterdir()}
        self.assertEqual(self.run_setup(), 2)
        self.assertEqual({p.name: p.read_bytes() for p in self.target.iterdir()}, before)

        # Only our exact synthetic fixtures are removed to test fresh install.
        app.unlink()
        sentinel.unlink()
        self.target.rmdir()  # empty QA directory only; no recursive deletion
        self.assertEqual(self.run_setup(), 0)
        self.assertEqual(app.read_bytes(), self.payload.read_bytes())
        notices = self.target / "third-party"
        expected_notices = {
            "README.txt", "notice-sources.json", "PYTHON-LICENSE.txt",
            "TCL-LICENSE.txt", "TK-LICENSE.txt", "OPENSSL-LICENSE.txt",
            "PYINSTALLER-COPYING.txt",
        }
        self.assertEqual({p.name for p in notices.iterdir()}, expected_notices)
        for name in expected_notices:
            self.assertEqual((notices / name).read_bytes(),
                             (ROOT / "third-party" / name).read_bytes())
        notice_manifest = json.loads((notices / "notice-sources.json").read_text())
        for entry in notice_manifest["notices"]:
            self.assertEqual(hashlib.sha256(
                (notices / entry["file"]).read_bytes()).hexdigest(), entry["sha256"])
        unrelated_notice = notices / "customer-note.txt"
        unrelated_notice.write_bytes(b"SYNTHETIC CUSTOMER NOTE - KEEP")
        self.assertTrue((self.target / "qa-shortcuts" /
                         "TechPartner Spreadsheet Check.lnk").is_file())
        marker = self.target / "install-marker.ini"
        correct_marker = marker.read_bytes()
        sentinel.write_bytes(b'{"synthetic":true}')

        foreign = self.work / "unrelated-target"
        foreign.mkdir()
        foreign_report = foreign / "keep.json"
        foreign_report.write_bytes(b"SYNTHETIC FOREIGN DATA")
        (foreign / "install-marker.ini").write_bytes(correct_marker)
        result = subprocess.run([str(self.target / "Uninstall.exe"), "/S",
                                 f"_?={foreign}"], timeout=30)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(foreign_report.read_bytes(), b"SYNTHETIC FOREIGN DATA")
        result = subprocess.run([str(self.package), "/S", f"/D={foreign}"],
                                timeout=30)
        self.assertEqual(result.returncode, 0)
        self.assertFalse((foreign / "TechPartner-Spreadsheet-Check.exe").exists())
        self.assertEqual(foreign_report.read_bytes(), b"SYNTHETIC FOREIGN DATA")

        marker.unlink()
        self.assertEqual(self.run_uninstall(), 3)
        self.assertTrue(app.exists())
        marker.write_bytes(b"[Install]\r\nProduct=Unrelated.Product\r\n")
        self.assertEqual(self.run_uninstall(), 3)
        self.assertTrue(app.exists())
        marker.write_bytes(correct_marker)

        self.assertEqual(self.run_setup(), 0)  # owned upgrade
        self.assertEqual(sentinel.read_bytes(), b'{"synthetic":true}')
        self.assertEqual(unrelated_notice.read_bytes(), b"SYNTHETIC CUSTOMER NOTE - KEEP")
        self.assertEqual(self.run_uninstall(), 0)
        self.assertFalse(app.exists())
        self.assertFalse(marker.exists())
        self.assertEqual(sentinel.read_bytes(), b'{"synthetic":true}')
        self.assertEqual(unrelated_notice.read_bytes(), b"SYNTHETIC CUSTOMER NOTE - KEEP")
        self.assertEqual({p.name for p in notices.iterdir()}, {"customer-note.txt"})
        self.assertFalse((self.target / "qa-shortcuts").exists())


if __name__ == "__main__":
    unittest.main()
