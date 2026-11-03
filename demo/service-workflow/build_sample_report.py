"""Build a customer-readable PDF from the bundled synthetic demo only.

ReportLab is an optional documentation dependency, not an application dependency.
Run from any directory; output stays in this checkout's ignored output/pdf folder.
"""
from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)

import run_demo

ROOT = Path(__file__).resolve().parents[2]
NAVY = colors.HexColor("#172B45")
TEAL = colors.HexColor("#146E70")
INK = colors.HexColor("#24364A")
MUTED = colors.HexColor("#5E6C7A")
PALE = colors.HexColor("#F2F5F8")
WHITE = colors.white


def main() -> None:
    # Recompute and validate the actual findings, saved JSON and untouched inputs.
    run_demo.main()
    reports = ROOT / "build" / "synthetic-service-delivery"
    initial = json.loads((reports / "needs-review-report.json").read_text("utf-8"))
    corrected = json.loads((reports / "corrected-report.json").read_text("utf-8"))
    if not initial["synthetic"] or not corrected["synthetic"]:
        raise RuntimeError("Only synthetic demo reports may be published")
    output = ROOT / "output" / "pdf" / "sample-findings-report.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)

    styles = {
        "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=9,
                                leading=12, textColor=TEAL, spaceAfter=8),
        "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=26,
                                leading=30, textColor=NAVY, spaceAfter=8),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9,
                               leading=13, textColor=INK, spaceAfter=8),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8,
                                leading=11, textColor=MUTED, spaceAfter=6),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=12,
                                  leading=16, textColor=NAVY, spaceBefore=9, spaceAfter=7),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.4,
                               leading=11.5, textColor=INK, alignment=TA_LEFT),
        "head": ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8.5,
                               leading=11, textColor=WHITE),
        "hash": ParagraphStyle("hash", fontName="Courier", fontSize=6.8,
                               leading=10, textColor=MUTED, splitLongWords=True),
    }

    def p(text: str, style: str = "body") -> Paragraph:
        return Paragraph(text, styles[style])

    story = [p("TECHPARTNER  /  SAMPLE DELIVERABLE", "label"),
             p("CSV migration review", "title"),
             p("Invented records. Reproducible findings. A clear list of what to fix.", "small"),
             Spacer(1, 7)]

    decision = Table([[p("<b>INITIAL RESULT: REVIEW REQUIRED</b>"),
                       p(f"{initial['source_count']} source rows  /  {initial['destination_count']} destination rows", "small")]],
                     colWidths=[295, 221])
    decision.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF1E6")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#E6B488")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [decision, p("What was checked", "section"),
              p("Source: <b>source.csv</b>. Destination: <b>needs-review.csv</b>. "
                "Match records by <b>Record ID</b>; compare exact values using "
                "<b>Name to Contact</b>, <b>Notes to Activity</b> and <b>Status to Stage</b>. "
                "IDs are case-insensitive and whitespace-normalized.")]

    duplicate = ", ".join(initial["duplicate_destination_ids"])
    missing = ", ".join(initial["missing_destination_ids"])
    unexpected = ", ".join(initial["unexpected_destination_ids"])
    findings = [
        ("Duplicate ID", f"{duplicate} occurs twice in the destination.",
         "Confirm the intended row and remove the extra copy."),
        ("Missing record", f"{missing} is absent from the destination.",
         "Restore its record and mapped fields from the agreed source."),
        ("Unexpected record", f"{unexpected} is absent from the source.",
         "Confirm where it came from and whether it belongs."),
        ("Swapped fields", "1002 has a note in Contact and a name in Activity.",
         "Correct both values using the agreed field map."),
    ]
    rows = [[p("Finding", "head"), p("Evidence", "head"), p("Action for migration owner", "head")]]
    rows += [[p(escape(cell), "cell") for cell in row] for row in findings]
    table = Table(rows, colWidths=[91, 192, 233], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PALE, WHITE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#DDE4EB")),
    ]))
    story += [table, Spacer(1, 6)]

    evidence = initial["field_mismatches"]["1002"]
    detail = "; ".join(
        f"{escape(item['destination_field'])}: expected <b>{escape(item['expected'])}</b>, "
        f"found <b>{escape(item['actual'])}</b>" for item in evidence)
    story += [p("Record 1002 detail: " + detail + ".", "small"),
              p("Duplicate IDs make their value comparisons ambiguous. Resolve the duplicate "
                "before accepting a recheck; equal row counts alone would not prove correctness.", "small"),
              p("After corrections: the recheck", "section"),
              p(f"<b>PASS for the agreed CSV checks.</b> In corrected.csv, all {corrected['source_count']} "
                "original IDs occur exactly once and all three mapped fields match. "
                "This supplied fixture illustrates a recheck; it is not work performed for a customer."),
              p("Limits and next step", "section"),
              p("A person must still confirm the intended mapping, business meaning and exclusions. "
                "Attachments, linked records, automations and transformations are outside this comparison. "
                "A passing CSV recheck does not certify a complete CRM migration. "
                "For a real review, agree the scope and secure transfer/retention arrangements before sending records.", "small"),
              p("Input traceability", "section")]
    trace_inputs = initial["input_files"] + [
        record for record in corrected["input_files"] if record["role"] == "destination"
    ]
    for record in trace_inputs:
        story.append(p(escape(record["name"]) + "  SHA256 " + record["sha256"], "hash"))

    def footer(canvas, doc):
        canvas.setStrokeColor(colors.HexColor("#DDE4EB"))
        canvas.line(48, 40, 564, 40)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(48, 26, "TechPartner | Synthetic sample, not a customer result or testimonial")
        canvas.drawRightString(564, 26, str(doc.page))

    SimpleDocTemplate(str(output), pagesize=(8.5 * inch, 11 * inch),
                      rightMargin=48, leftMargin=48, topMargin=38, bottomMargin=52,
                      title="TechPartner - Synthetic CSV migration review",
                      author="TechPartner", pageCompression=1).build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF: {output}")


if __name__ == "__main__":
    main()
