"""Local-only file picker for the spreadsheet migration checker."""
import csv
import json
import tkinter as tk
from dataclasses import asdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from data_mapping_qa import _read_csv, audit_rows


def main():
    root = tk.Tk()
    root.title("TechPartner Spreadsheet Check")
    root.geometry("850x620")
    root.minsize(650, 450)
    panel = ttk.Frame(root, padding=20)
    panel.pack(fill="both", expand=True)
    ttk.Label(panel, text="Check a spreadsheet migration", font=("Segoe UI", 18)).pack(anchor="w")
    ttk.Label(panel, text="Choose two UTF-8 CSV exports. Files stay on this computer and are never modified.", wraplength=700).pack(anchor="w", pady=8)
    paths = []
    for label in ("Original CSV", "Migrated CSV"):
        row = ttk.Frame(panel)
        row.pack(fill="x", pady=5)
        value = tk.StringVar()
        paths.append(value)
        ttk.Label(row, text=label, width=18).pack(side="left")
        ttk.Entry(row, textvariable=value).pack(side="left", fill="x", expand=True)
        def choose(target=value):
            filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if filename:
                target.set(filename)
        ttk.Button(row, text="Browse…", command=choose).pack(side="right", padx=5)
    id_field = tk.StringVar(value="Record ID")
    notes_field = tk.StringVar(value="Notes")
    for label, variable in (("Record ID column (exact heading)", id_field), ("Notes column (optional)", notes_field)):
        ttk.Label(panel, text=label).pack(anchor="w", pady=(8, 0))
        ttk.Entry(panel, textvariable=variable).pack(fill="x")
    status = tk.StringVar(value="No check performed yet.")
    ttk.Label(panel, textvariable=status, wraplength=700).pack(anchor="w", pady=10)
    output = tk.Text(panel, wrap="word", height=12, state="disabled")
    output.pack(fill="both", expand=True)
    result = None

    def invalidate(*_):
        nonlocal result
        result = None
        status.set("Inputs changed. Run the check again before saving.")
    for variable in [*paths, id_field, notes_field]:
        variable.trace_add("write", invalidate)

    def check():
        nonlocal result
        result = None
        try:
            if not all(path.get().strip() for path in paths):
                raise ValueError("Choose both CSV files first.")
            audit = audit_rows(*[_read_csv(Path(path.get())) for path in paths], id_field=id_field.get(), notes_field=notes_field.get())
            result = asdict(audit) | {"passed": audit.passed}
            status.set("Checks passed — human review is still required." if audit.passed else "Review required — see findings below.")
            text = json.dumps(result, indent=2, ensure_ascii=False)
        except (ValueError, OSError, UnicodeError, csv.Error) as exc:
            status.set("Check could not complete. No files changed.")
            text = str(exc)
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.insert("1.0", text)
        output.configure(state="disabled")

    def save():
        if result is None:
            messagebox.showinfo("Run a check", "Complete a check before saving a report.")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON report", "*.json")])
        if filename:
            try:
                target = Path(filename).resolve()
                if target in [Path(path.get()).resolve() for path in paths]:
                    raise ValueError("Choose a different file; original spreadsheets cannot be overwritten.")
                target.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                messagebox.showinfo("Report saved", "The report can contain source data. Share it only with authorized recipients.")
            except (OSError, ValueError) as exc:
                messagebox.showerror("Report not saved", str(exc))

    buttons = ttk.Frame(panel)
    buttons.pack(fill="x", pady=12)
    ttk.Button(buttons, text="Check files", command=check).pack(side="left")
    ttk.Button(buttons, text="Save report…", command=save).pack(side="left", padx=10)
    ttk.Label(panel, text="This checks data preservation, not whether information was assigned to the correct business field.", wraplength=700).pack(anchor="w")
    root.mainloop()


if __name__ == "__main__":
    main()
