"""Local-only file picker for the spreadsheet migration checker."""
import csv
import json
import tkinter as tk
from dataclasses import asdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from data_mapping_qa import _read_csv, audit_rows, read_field_map


def validate_report_target(target: Path, sources: list[Path]) -> Path:
    target = target.resolve()
    for source in sources:
        source = source.resolve()
        if target == source or (target.exists() and target.samefile(source)):
            raise ValueError("Choose a different file; original spreadsheets cannot be overwritten.")
    return target


def main():
    root = tk.Tk()
    root.title("TechPartner Spreadsheet Check")
    root.geometry("850x700")
    root.minsize(650, 530)
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
    map_path = tk.StringVar()
    ttk.Label(panel, text="Field map (optional JSON: source heading → destination heading)").pack(anchor="w", pady=(8, 0))
    map_row = ttk.Frame(panel)
    map_row.pack(fill="x")
    ttk.Entry(map_row, textvariable=map_path).pack(side="left", fill="x", expand=True)
    def choose_map():
        filename = filedialog.askopenfilename(filetypes=[("JSON field map", "*.json")])
        if filename:
            map_path.set(filename)
    ttk.Button(map_row, text="Browse…", command=choose_map).pack(side="right", padx=5)
    status = tk.StringVar(value="No check performed yet.")
    ttk.Label(panel, textvariable=status, wraplength=700).pack(anchor="w", pady=10)
    output = tk.Text(panel, wrap="word", height=12, state="disabled")
    output.pack(fill="both", expand=True)
    result = None

    def invalidate(*_):
        nonlocal result
        result = None
        status.set("Inputs changed. Run the check again before saving.")
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.configure(state="disabled")
    for variable in [*paths, id_field, notes_field, map_path]:
        variable.trace_add("write", invalidate)

    def check():
        nonlocal result
        result = None
        try:
            if not all(path.get().strip() for path in paths):
                raise ValueError("Choose both CSV files first.")
            mapping = read_field_map(Path(map_path.get())) if map_path.get().strip() else None
            audit = audit_rows(*[_read_csv(Path(path.get())) for path in paths], id_field=id_field.get(), notes_field=notes_field.get(), field_map=mapping)
            result = asdict(audit) | {"passed": audit.passed}
            status.set(("Mapped-field checks passed — human review is still required." if mapping else "Preservation scan passed — field placement was not checked.") if audit.passed else "Review required — see findings below.")
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
                protected_paths = [Path(path.get()) for path in paths]
                if map_path.get().strip():
                    protected_paths.append(Path(map_path.get()))
                target = validate_report_target(Path(filename), protected_paths)
                target.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                messagebox.showinfo("Report saved", "The report can contain source data. Share it only with authorized recipients.")
            except (OSError, ValueError) as exc:
                messagebox.showerror("Report not saved", str(exc))

    buttons = ttk.Frame(panel)
    buttons.pack(fill="x", pady=12)
    ttk.Button(buttons, text="Check files", command=check).pack(side="left")
    ttk.Button(buttons, text="Save report…", command=save).pack(side="left", padx=10)
    ttk.Label(panel, text="With a field map, exact values are checked in the agreed columns. Other transformations and business meaning require review.", wraplength=700).pack(anchor="w")
    root.mainloop()


if __name__ == "__main__":
    main()
