import unittest

from data_mapping_qa import audit_rows, flatten_notes, normalize


class MappingQATests(unittest.TestCase):
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
