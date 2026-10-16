import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from report_io import (InputsChangedError, fingerprint_inputs, save_report_atomic,
                       verify_input_versions)


class ReportPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="spreadsheet-qa-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "source.csv"
        self.source.write_text("ID,Name\n1,Synthetic\n", encoding="utf-8")
        self.target = self.root / "report.json"
        self.target.write_bytes(b'{"previous":"keep me"}')
        self.expected = fingerprint_inputs([self.source])

    def assert_previous_preserved(self):
        self.assertEqual(self.target.read_bytes(), b'{"previous":"keep me"}')
        self.assertEqual(list(self.root.glob(".spreadsheet-report-*.tmp")), [])

    def test_atomic_success_is_valid_json_and_preserves_input(self):
        before = self.source.read_bytes()
        payload = {"passed": True, "name": "Synthetic é", "input_files": [{"sha256": self.expected[str(self.source.resolve())]}]}
        self.assertEqual(save_report_atomic(self.target, payload, [self.source], self.expected), self.target)
        self.assertEqual(json.loads(self.target.read_text(encoding="utf-8")), payload)
        self.assertEqual(self.source.read_bytes(), before)

    def test_replacement_failure_preserves_old_report_and_cleans_temp(self):
        with patch("report_io.os.replace", side_effect=PermissionError("Synthetic locked report")):
            with self.assertRaises(PermissionError):
                save_report_atomic(self.target, {"passed": True}, [self.source], self.expected)
        self.assert_previous_preserved()

    def test_flush_failure_preserves_old_report_and_cleans_temp(self):
        with patch("report_io.os.fsync", side_effect=OSError("Synthetic full device")):
            with self.assertRaises(OSError):
                save_report_atomic(self.target, {"passed": True}, [self.source], self.expected)
        self.assert_previous_preserved()

    def test_invalid_json_payload_preserves_old_report(self):
        for payload in ({"value": object()}, {"value": float("nan")}):
            with self.subTest(payload=payload), self.assertRaises((ValueError, TypeError)):
                save_report_atomic(self.target, payload, [self.source], self.expected)
        self.assert_previous_preserved()

    def test_changed_source_at_same_path_invalidates_saved_result(self):
        self.source.write_text("ID,Name\n1,Changed\n", encoding="utf-8")
        with self.assertRaises(InputsChangedError):
            save_report_atomic(self.target, {"passed": True}, [self.source], self.expected)
        self.assert_previous_preserved()

    def test_changed_input_during_write_cannot_replace_report(self):
        def change_input(_):
            self.source.write_text("ID,Name\n1,Changed during save\n", encoding="utf-8")
        with patch("report_io.os.fsync", side_effect=change_input):
            with self.assertRaises(InputsChangedError):
                save_report_atomic(self.target, {"passed": True}, [self.source], self.expected)
        self.assert_previous_preserved()

    def test_removed_input_is_stale_not_a_success(self):
        self.source.unlink()
        with self.assertRaises(InputsChangedError):
            verify_input_versions([self.source], self.expected)
        self.assert_previous_preserved()

    def test_map_changes_are_also_detected(self):
        mapping = self.root / "map.json"
        mapping.write_text('{"Name":"Name"}', encoding="utf-8")
        expected = fingerprint_inputs([self.source, mapping])
        mapping.write_text('{"Name":"Other"}', encoding="utf-8")
        with self.assertRaises(InputsChangedError):
            save_report_atomic(self.target, {"passed": True}, [self.source, mapping], expected)
        self.assert_previous_preserved()

    def test_direct_and_hardlink_input_targets_are_rejected(self):
        alias = self.root / "source-alias.json"
        os.link(self.source, alias)
        before = self.source.read_bytes()
        for target in (self.source, alias):
            with self.subTest(target=target), self.assertRaises(ValueError):
                save_report_atomic(target, {"passed": True}, [self.source], self.expected)
        self.assertEqual(before, self.source.read_bytes())
        self.assert_previous_preserved()


if __name__ == "__main__":
    unittest.main()
