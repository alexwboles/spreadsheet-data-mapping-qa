"""Customer report regressions: real findings, untrusted values and safe saving."""
import tempfile
import unittest
from dataclasses import asdict
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from data_mapping_qa import _read_csv, audit_rows, read_field_map
from readable_report import html_report, text_report
from report_io import InputsChangedError, fingerprint_inputs, save_report_atomic


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags, self.text, self.attributes = [], [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attributes.extend(attrs)

    def handle_data(self, data):
        self.text.append(data)


class ReadableReportTests(unittest.TestCase):
    def fixture_payload(self, name="needs-review"):
        fixtures = Path(__file__).resolve().parent / "demo" / "service-workflow"
        audit = audit_rows(_read_csv(fixtures / "source.csv"),
                           _read_csv(fixtures / f"{name}.csv"), id_field="Record ID",
                           notes_field="Activity", field_map=read_field_map(fixtures / "field-map.json"))
        return asdict(audit) | {"passed": audit.passed, "synthetic": True,
                               "id_field": "Record ID", "notes_field": "Activity"}

    def test_real_defects_and_corrected_result_remain_distinct(self):
        broken = self.fixture_payload()
        body = " ".join(Document(html_report(broken)).text)
        for expected in ("Review required", "Duplicate migrated ID", "Missing migrated record",
                         "Unexpected migrated record", "Field mismatch", "1001", "1003", "1999",
                         "Expected:", "Found:", "Human review pending", "Sample using invented records"):
            self.assertIn(expected, body)
        self.assertIn("Record ID column: Record ID", text_report(broken))
        corrected = self.fixture_payload("corrected")
        self.assertIn("Mapped-field checks passed", html_report(corrected))
        self.assertNotIn("Field mismatch", html_report(corrected))
        corrected["checked_field_map"] = {}
        self.assertIn("Field placement was not checked", html_report(corrected))
        self.assertNotIn("Mapped-field checks passed", html_report(corrected))

    def test_source_values_cannot_create_active_html(self):
        payload = self.fixture_payload()
        attack = '<img src="https://example.invalid/pixel" onerror="alert(1)"><script>alert(2)</script>&'
        payload["field_mismatches"] = {attack: [{"source_field": attack,
            "destination_field": attack, "expected": attack, "actual": attack}]}
        payload["input_files"] = [{"role": "source", "name": attack, "sha256": "a" * 64}]
        payload["checked_field_map"] = {attack: attack}
        payload["id_field"] = attack
        doc = Document(html_report(payload))
        self.assertNotIn("img", doc.tags)
        self.assertNotIn("script", doc.tags)
        self.assertFalse(any(key in ("src", "href", "onerror") for key, _ in doc.attributes))
        self.assertTrue(any(key == "content" and "default-src 'none'" in value
                            for key, value in doc.attributes))
        self.assertIn(attack, " ".join(doc.text))

    def test_readable_saves_keep_atomic_input_and_stale_report_protections(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / "source.csv", root / "report.html"
            source.write_text("Record ID,Name\n1,Synthetic\n", encoding="utf-8")
            versions = fingerprint_inputs([source])
            payload = self.fixture_payload()
            save_report_atomic(target, payload, [source], versions, render=html_report)
            saved = target.read_bytes()
            with patch("report_io.os.replace", side_effect=PermissionError("Synthetic lock")):
                with self.assertRaises(PermissionError):
                    save_report_atomic(target, payload, [source], versions, render=html_report)
            self.assertEqual(target.read_bytes(), saved)
            with self.assertRaises(ValueError):
                save_report_atomic(source, payload, [source], versions, render=html_report)
            source.write_text("Record ID,Name\n1,Changed\n", encoding="utf-8")
            with self.assertRaises(InputsChangedError):
                save_report_atomic(target, payload, [source], versions, render=html_report)
            self.assertEqual(target.read_bytes(), saved)
            self.assertFalse(list(root.glob(".spreadsheet-report-*.tmp")))
