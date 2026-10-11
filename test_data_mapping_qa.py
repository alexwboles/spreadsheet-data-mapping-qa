import unittest
import tempfile
import json
import subprocess
import sys
from pathlib import Path

from data_mapping_qa import audit_rows, flatten_notes, normalize, _read_csv, read_field_map
from desktop import validate_report_target


class MappingQATests(unittest.TestCase):
    def test_cli_reports_mapped_pass_and_swapped_failure(self):
        project = Path(__file__).resolve().parent
        source = project / "demo" / "original.csv"
        before = source.read_bytes()
        for filename, expected_exit in (("migrated.csv", 0), ("swapped-fields.csv", 1)):
            run = subprocess.run([sys.executable, str(project / "data_mapping_qa.py"),
                                  str(source), str(project / "demo" / filename),
                                  "--id-field", "Record ID", "--field-map",
                                  str(project / "demo" / "field-map.json")],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, expected_exit, run.stderr)
            payload = json.loads(run.stdout)
            self.assertEqual(payload["passed"], expected_exit == 0)
            self.assertEqual(payload["checked_field_map"], {"Name": "Name", "Notes": "Notes"})
        self.assertEqual(before, source.read_bytes())

    def test_explicit_map_file_cannot_silently_disable_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.json"
            for value in ("null", "{}", "[]", '"Name"', "bad json", '{"Name":"Name","Name":"Notes"}'):
                path.write_text(value, encoding="utf-8")
                with self.subTest(value=value), self.assertRaises(ValueError):
                    read_field_map(path)

    def test_report_cannot_overwrite_source_via_hard_link(self):
        import os
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            source.write_text("ID,Name\n1,Demo\n", encoding="utf-8")
            alias = Path(directory) / "alias.json"
            os.link(source, alias)
            before = source.read_bytes()
            for target in (source, alias):
                with self.assertRaisesRegex(ValueError, "cannot be overwritten"):
                    validate_report_target(target, [source])
            self.assertEqual(before, source.read_bytes())
            self.assertEqual(validate_report_target(Path(directory) / "report.json", [source]),
                             Path(directory) / "report.json")

    def test_mapped_fields_catch_swapped_values(self):
        source = [{"ID": "1", "Name": "Demo", "Notes": "Call Friday"}]
        destination = [{"ID": "1", "Name": "Call Friday", "Notes": "Demo"}]
        audit = audit_rows(source, destination, id_field="ID",
                           field_map={"Name": "Name", "Notes": "Notes"})
        self.assertFalse(audit.passed)
        self.assertEqual(len(audit.field_mismatches["1"]), 2)
        self.assertEqual(audit.checked_field_map, {"Name": "Name", "Notes": "Notes"})

    def test_mapped_fields_support_renamed_headers(self):
        audit = audit_rows([{"ID": "1", "Name": "Demo"}],
                           [{"ID": "1", "Full Name": "Demo"}], id_field="ID",
                           field_map={"Name": "Full Name"})
        self.assertTrue(audit.passed)

    def test_mapped_fields_compare_exact_values_including_empty(self):
        for expected, actual in (("", "new"), ("Demo", "demo"), ("0", ""), ("Ann", " Ann ")):
            with self.subTest(expected=expected, actual=actual):
                audit = audit_rows([{"ID": "1", "Name": expected}],
                                   [{"ID": "1", "Name": actual}], id_field="ID",
                                   field_map={"Name": "Name"})
                self.assertFalse(audit.passed)

    def test_invalid_maps_fail_before_comparison(self):
        rows = [{"ID": "1", "Name": "Demo", "Notes": "Call"}]
        for mapping in ({}, [], {"Name": 3}, {"": "Name"}, {"Absent": "Name"},
                        {"Name": "Absent"}, {"Name": "Notes", "Notes": "Notes"},
                        {"ID": "Name"}, {"Name": "ID"}):
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                audit_rows(rows, rows, id_field="ID", field_map=mapping)

    def test_empty_files_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "no records"):
            audit_rows([], [], id_field="ID")

    def test_missing_or_blank_ids_cannot_pass(self):
        for row in ({"Name": "X"}, {"ID": " "}):
            with self.assertRaisesRegex(ValueError, "missing record ID"):
                audit_rows([row], [row], id_field="ID")

    def test_zero_is_not_discarded(self):
        self.assertEqual(normalize(0), "0")

    def test_substring_is_not_preservation(self):
        for source, destination in (("12", "123"), ("Ann", "Joanne")):
            audit = audit_rows([{"ID": "1", "Name": source}], [{"ID": "1", "Name": destination}], id_field="ID")
            self.assertFalse(audit.passed)

    def test_malformed_csv_is_rejected(self):
        for text in ("ID,ID\n1,2\n", "ID,Name\n1\n", "ID,Name\n1,A,extra\n", "ID,\n1,A\n"):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "input.csv"
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    _read_csv(path)

    def test_normalize_collapses_whitespace_and_case(self):
        self.assertEqual(normalize("  Hello\nWORLD "), "hello world")

    def test_flatten_notes_preserves_each_line(self):
        self.assertEqual(flatten_notes("XYZ\nZYX\r\nABC"), "XYZ / ZYX / ABC")

    def test_clean_transfer_passes(self):
        source = [{"ID": "1", "Name": "Acme", "Notes": "Call Tuesday"}]
        destination = [
            {"ID": "1", "Company": "Acme", "Notes": "Call Tuesday"}
        ]
        self.assertTrue(audit_rows(source, destination, id_field="ID").passed)

    def test_missing_record_is_flagged(self):
        audit = audit_rows(
            [{"ID": "1"}, {"ID": "2"}], [{"ID": "1"}], id_field="ID"
        )
        self.assertEqual(audit.missing_destination_ids, ["2"])

    def test_duplicate_destination_id_is_flagged(self):
        audit = audit_rows(
            [{"ID": "1"}], [{"ID": "1"}, {"ID": "1"}], id_field="ID"
        )
        self.assertEqual(audit.duplicate_destination_ids, ["1"])

    def test_multiline_notes_are_flagged(self):
        audit = audit_rows(
            [{"ID": "1", "Notes": "A\nB"}],
            [{"ID": "1", "Notes": "A\nB"}],
            id_field="ID",
        )
        self.assertEqual(audit.notes_with_line_breaks, ["1"])

    def test_potentially_lost_value_is_flagged(self):
        audit = audit_rows(
            [{"ID": "1", "Email": "person@example.com", "Notes": "Keep me"}],
            [{"ID": "1", "Email": "person@example.com", "Notes": ""}],
            id_field="ID",
        )
        self.assertEqual(audit.potentially_lost_values, {"1": ["Notes: Keep me"]})


if __name__ == "__main__":
    unittest.main()
