import unittest
import tempfile
from pathlib import Path

from data_mapping_qa import audit_rows, flatten_notes, normalize, _read_csv


class MappingQATests(unittest.TestCase):
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
