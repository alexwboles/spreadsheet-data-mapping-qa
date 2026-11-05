"""Readable, offline findings from the same audit used by the JSON report."""
from html import escape


def report_title(payload: dict) -> str:
    if not payload["passed"]:
        return "Review required"
    if payload["checked_field_map"]:
        return "Mapped-field checks passed"
    return "Preservation scan passed"


def findings(payload: dict) -> list[tuple[str, str, str]]:
    rows = []
    for key, label, action in (
        ("duplicate_source_ids", "Duplicate original ID", "Confirm one intended original record before comparing values."),
        ("duplicate_destination_ids", "Duplicate migrated ID", "Confirm the intended migrated row and resolve the extra copies."),
        ("missing_destination_ids", "Missing migrated record", "Restore the record from the agreed original export."),
        ("unexpected_destination_ids", "Unexpected migrated record", "Confirm its origin and whether it belongs in this export."),
        ("notes_with_line_breaks", "Multiline note", "Review the note formatting required by the destination system."),
    ):
        for record_id in payload[key]:
            rows.append((label, record_id, action))
    for record_id, values in payload["potentially_lost_values"].items():
        for value in values:
            rows.append(("Potential value loss", record_id, value))
    for record_id, mismatches in payload["field_mismatches"].items():
        for item in mismatches:
            rows.append(("Field mismatch", record_id,
                         f"{item['source_field']} → {item['destination_field']}\n"
                         f"Expected: {item['expected']}\nFound: {item['actual']}"))
    return rows


def text_report(payload: dict) -> str:
    lines = [report_title(payload), "Human review pending", "",
             f"Original rows: {payload['source_count']}  |  Migrated rows: {payload['destination_count']}",
             f"Record ID column: {payload.get('id_field', 'not recorded in this report')}", ""]
    mapping = payload["checked_field_map"]
    if mapping:
        lines.append("Exact field checks")
        lines.extend(f"  {source} → {destination}" for source, destination in mapping.items())
    else:
        lines.append("Field placement was not checked. Choose a field map to check agreed columns.")
    lines += ["", "Findings"]
    rows = findings(payload)
    for label, record_id, detail in rows:
        lines += [f"• {label} · ID {record_id}", f"  {detail}"]
    if not rows:
        lines.append("No issues flagged by the selected automated checks.")
    lines += ["", "Resolve duplicate IDs before relying on their value comparisons.",
              "Confirm the agreed mapping, intentional conversions and business meaning before sign-off."]
    return "\n".join(lines)


def html_report(payload: dict) -> str:
    """Escape every input value and load no scripts, fonts or network assets."""
    def safe(value):
        return escape(str(value), quote=True)

    rows = findings(payload)
    finding_rows = "".join(
        f"<tr><th scope='row'>{safe(label)}</th><td class='record'>{safe(record_id)}</td>"
        f"<td class='value'>{safe(detail)}</td></tr>"
        for label, record_id, detail in rows
    )
    mapping_rows = "".join(
        f"<tr><td>{safe(source)}</td><td>{safe(destination)}</td></tr>"
        for source, destination in payload["checked_field_map"].items()
    )
    input_rows = "".join(
        f"<tr><td>{safe(item['role'])}</td><td>{safe(item['name'])}</td>"
        f"<td class='hash'>{safe(item['sha256'])}</td></tr>"
        for item in payload.get("input_files", [])
    )
    mapping_section = (
        "<table><thead><tr><th>Original column</th><th>Migrated column</th></tr></thead>"
        f"<tbody>{mapping_rows}</tbody></table>"
        if mapping_rows else "<p>Field placement was not checked. No field map was selected.</p>"
    )
    findings_section = (
        "<table><thead><tr><th>Finding</th><th>Record ID</th><th>Evidence or next action</th></tr></thead>"
        f"<tbody>{finding_rows}</tbody></table>"
        if rows else "<p>No issues flagged by the selected automated checks.</p>"
    )
    title = safe(report_title(payload))
    synthetic = "<p class='sample'>Sample using invented records</p>" if payload.get("synthetic") else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>CSV review · {title}</title>
<style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #eef2f5; color: #233649; font: 16px/1.55 'Segoe UI', sans-serif; }}
main {{ max-width: 1050px; margin: 32px auto; padding: 38px; background: white; border-radius: 16px; }}
.brand {{ color: #126c70; font-weight: 700; letter-spacing: .12em; font-size: 13px; }}
h1 {{ color: #172b45; margin: 8px 0; font-size: clamp(26px, 5vw, 38px); line-height: 1.2; }}
h2 {{ color: #172b45; font-size: 21px; margin: 32px 0 12px; }}
p {{ margin: 8px 0 14px; }}
.decision {{ background: #f1f5f8; border-left: 5px solid #126c70; padding: 18px; margin: 24px 0; }}
.decision strong {{ display: block; font-size: 22px; }}
.sample {{ font-weight: 600; color: #80531a; }}
.table-wrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid #dce4eb; padding: 12px 10px; overflow-wrap: anywhere; }}
thead th {{ background: #f1f5f8; }}
tbody th {{ font-weight: 600; width: 24%; }}
.record {{ width: 17%; }}
.value {{ white-space: pre-wrap; }}
.hash {{ font: 12px/1.6 Consolas, monospace; word-break: break-all; }}
.muted, footer {{ color: #536575; font-size: 14px; }}
li {{ margin: 8px 0; }}
footer {{ margin-top: 36px; padding-top: 20px; border-top: 1px solid #dce4eb; }}
@media (max-width: 600px) {{ main {{ margin: 0; padding: 22px 16px; border-radius: 0; }} th, td {{ padding: 10px 6px; }} }}
@media print {{ body {{ background: white; font-size: 11pt; }} main {{ max-width: none; margin: 0; padding: 0; }} h2 {{ break-after: avoid; }} tr {{ break-inside: avoid; }} thead {{ display: table-header-group; }} .table-wrap {{ overflow: visible; }} }}
</style></head><body><main>
<div class="brand">TECHPARTNER</div>
<h1>CSV migration review</h1>
<p class="muted">Automated findings · Human review pending</p>{synthetic}
<section class="decision" aria-label="Check result"><strong>{title}</strong>
<span>Original rows {safe(payload['source_count'])} · Migrated rows {safe(payload['destination_count'])}</span></section>
<h2>What was checked</h2>
<p>Record ID column: <strong>{safe(payload.get('id_field', 'not recorded in this report'))}</strong>.</p>
<p>Record IDs use case-insensitive, whitespace-normalized matching. Mapped values are compared exactly, including case, whitespace and empty values.</p>
<div class="table-wrap">{mapping_section}</div>
<p class="muted">Only the listed columns receive exact field checks. Other original values receive a preservation scan.</p>
<p class="muted">Multiline-note check column: {safe(payload.get('notes_field', 'not recorded in this report'))}.</p>
<h2>Findings</h2><div class="table-wrap">{findings_section}</div>
<h2>Before signing off</h2><ul>
<li>Resolve duplicate IDs before relying on comparisons for those records.</li>
<li>Review potential value loss against the agreed mapping and intended conversions.</li>
<li>Confirm mapping completeness, exclusions and the business meaning of the data.</li>
<li>Correct the export in the source system, then run a fresh check of the corrected files.</li>
</ul>
<h2>Files reviewed</h2><p class="muted">SHA256 fingerprints identify the exact file contents checked.</p>
<div class="table-wrap"><table><thead><tr><th>Role</th><th>File</th><th>SHA256</th></tr></thead><tbody>{input_rows}</tbody></table></div>
<footer><p>This report can contain source records. Share only with authorized recipients. It opens offline and can be printed using your browser.</p>
<p>TechPartner · techpartner.base44.app · alexwboles@gmail.com</p></footer>
</main></body></html>"""
