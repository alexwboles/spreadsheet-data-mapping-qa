"""Exercise actual desktop callbacks with test widgets, not native-window QA."""
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import desktop


class DesktopCallbackTests(unittest.TestCase):
    def build_test_ui(self, source, destination, report):
        variables, commands, messages, output = [], {}, [], []

        class Variable:
            def __init__(self, value=""):
                self.value, self.callbacks = value, []
                variables.append(self)

            def get(self):
                return self.value

            def set(self, value):
                self.value = value
                for callback in self.callbacks:
                    callback()

            def trace_add(self, _, callback):
                self.callbacks.append(callback)

        class Widget:
            def __init__(self, *args, **kwargs):
                pass

            def pack(self, **kwargs):
                pass

        class Root(Widget):
            def title(self, _): pass
            def geometry(self, _): pass
            def minsize(self, *_): pass
            def mainloop(self): pass

        class Text(Widget):
            def __init__(self, *args, **kwargs):
                self.text = ""
                output.append(self)

            def configure(self, **kwargs): pass
            def delete(self, *_): self.text = ""
            def insert(self, _, value): self.text = value

        class Button(Widget):
            def __init__(self, *args, **kwargs):
                commands[kwargs["text"]] = kwargs["command"]

        tk = types.SimpleNamespace(Tk=Root, StringVar=Variable, Text=Text)
        ttk = types.SimpleNamespace(Frame=Widget, Label=Widget, Entry=Widget, Button=Button)
        picker = types.SimpleNamespace(asksaveasfilename=lambda **kwargs: str(report))
        alerts = types.SimpleNamespace(showinfo=lambda *args: messages.append(args), showerror=lambda *args: messages.append(args))
        with patch.multiple(desktop, tk=tk, ttk=ttk, filedialog=picker, messagebox=alerts):
            desktop.main()
        variables[0].set(str(source))
        variables[1].set(str(destination))
        return variables, commands, messages, output[0], picker, alerts

    def test_save_records_versions_and_external_edit_clears_stale_result(self):
        with tempfile.TemporaryDirectory(prefix="spreadsheet-callback-qa-") as directory:
            root = Path(directory)
            source, destination, report = [root / name for name in ("source.csv", "destination.csv", "report.json")]
            for file in (source, destination):
                file.write_text("Record ID,Name\n1,Synthetic\n", encoding="utf-8")
            variables, commands, messages, output, picker, alerts = self.build_test_ui(source, destination, report)
            with patch.multiple(desktop, filedialog=picker, messagebox=alerts):
                commands["Check files"]()
                commands["Save report…"]()
                saved = report.read_bytes()
                payload = json.loads(saved)
                self.assertTrue(payload["passed"])
                self.assertEqual([entry["role"] for entry in payload["input_files"]], ["source", "destination"])
                self.assertTrue(all(len(entry["sha256"]) == 64 and "\\" not in entry["name"] for entry in payload["input_files"]))
                self.assertIn("Report saved", messages[-1])
                destination.write_text("Record ID,Name\n1,Changed after audit\n", encoding="utf-8")
                commands["Save report…"]()
                self.assertEqual(report.read_bytes(), saved)
                self.assertEqual(output.text, "")
                self.assertIn("contents changed", variables[-1].get())
                self.assertIn("Report not saved", messages[-1])
                commands["Save report…"]()
                self.assertIn("Run a check", messages[-1])

    def test_failed_save_never_shows_success_or_damages_previous_report(self):
        with tempfile.TemporaryDirectory(prefix="spreadsheet-callback-qa-") as directory:
            root = Path(directory)
            source, destination, report = [root / name for name in ("source.csv", "destination.csv", "report.json")]
            for file in (source, destination):
                file.write_text("Record ID,Name\n1,Synthetic\n", encoding="utf-8")
            report.write_bytes(b'{"previous":"retain"}')
            _, commands, messages, _, picker, alerts = self.build_test_ui(source, destination, report)
            with patch.multiple(desktop, filedialog=picker, messagebox=alerts):
                commands["Check files"]()
                with patch("report_io.os.replace", side_effect=PermissionError("Synthetic report lock")):
                    commands["Save report…"]()
                self.assertEqual(report.read_bytes(), b'{"previous":"retain"}')
                self.assertIn("Report not saved", messages[-1])
                self.assertFalse(any(message[0] == "Report saved" for message in messages))


if __name__ == "__main__":
    unittest.main()
