"""Legislation PDF parsing: running heads, page numbers, contents pages, en dashes."""
import pytest

from amlrag.ingest.parse_legislation import parse_legislation_file

reportlab = pytest.importorskip("reportlab")
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

PATTERN = r"^(\d{1,2}-\d{1,3}[A-Z]?)\s+([A-Z][^\n]{2,160})$"
HEAD = "Synthetic Rules 2025  Compilation No. 3  Compilation date: 01/07/2026"

PAGES = [
    ["Contents", "Part 6—Customer due diligence", "6–1 Sole traders ........ 2",
     "6–2 Bodies corporate ........ 3", "6–3 Trusts ........ 4"],
    ["Part 6—Customer due diligence", "Division 1—Initial customer due diligence", "6–1 Sole traders",
     "(1) For a customer who is a sole trader, the reporting entity must collect the customer's full name,",
     "business name and ABN, and the principal place of business.",
     "(2) The reporting entity must also understand the nature and purpose of the relationship."],
    ["6–2 Bodies corporate",
     "(1) For a body corporate the reporting entity must collect the full name, registered office and",
     "the names of directors, and identify the beneficial owners."],
    ["6–3 Trusts", "(1) For a trust the reporting entity must collect the name of the trust, the trustee,",
     "the settlor and the beneficiaries or a description of the class of beneficiaries.",
     "Note: See also section 6-7 on beneficial owners."],
]


# Per-page headers that change page to page, as in Federal Register compilations.
PAGE_HEADS = [[], ["Customer due diligence  Part 6", "Initial customer due diligence  Division 1", "Section 6-1"],
              ["Customer due diligence  Part 6", "Section 6-2"], ["Customer due diligence  Part 6", "Section 6-3"]]


def _make_pdf(path):
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    for n, lines in enumerate(PAGES, start=1):
        c.setFont("Helvetica", 8)
        c.drawString(40, h - 30, HEAD)
        for j, head in enumerate(PAGE_HEADS[n - 1]):
            c.drawString(40, h - 42 - 10 * j, head)
        c.setFont("Helvetica", 10)
        y = h - 70
        for line in lines:
            c.drawString(50, y, line)
            y -= 16
        c.setFont("Helvetica", 8)
        c.drawString(w / 2, 30, str(n))
        c.showPage()
    c.save()


def test_pdf_legislation_parse(tmp_path):
    pdf = tmp_path / "rules.pdf"
    _make_pdf(pdf)
    secs = parse_legislation_file(pdf, "rules2025", "Rules", "AML/CTF Rules 2025", PATTERN, "s", ["6"])
    assert [s.section_key for s in secs] == ["6-1", "6-2", "6-3"]
    body = {s.section_key: s.text for s in secs}
    # Running head and page numbers are gone; wrapped lines re-joined; subsections kept apart.
    assert all("Compilation" not in t for t in body.values())
    assert all("Section 6-" not in t and "Part 6" not in t for t in body.values())
    assert "full name, business name and ABN" in body["6-1"]
    assert body["6-1"].split("\n")[1].startswith("(2)")
    assert body["6-3"].rstrip().endswith("section 6-7 on beneficial owners.")
    assert secs[0].heading_path[:2] == ["Part 6—Customer due diligence", "Division 1—Initial customer due diligence"]
