from pathlib import Path

from amlrag.ingest.chunk import chunk_section, chunk_sections
from amlrag.ingest.parse_html import parse_guidance_html
from amlrag.ingest.parse_legislation import parse_legislation_file, parse_legislation_lines
from amlrag.models import Section

FIX = Path(__file__).parent / "fixtures"
RULES_PATTERN = r"^(\d{1,2}-\d{1,3}[A-Z]?)\s+([A-Z][^\n]{2,160})$"


def _html_sections():
    return parse_guidance_html((FIX / "austrac_ecdd_sample.html").read_bytes(), "austrac-ecdd",
                               "Enhanced customer due diligence", "https://example.org/ecdd")


def test_html_drops_navigation_and_boilerplate():
    secs = _html_sections()
    text = " ".join(s.text for s in secs)
    assert "Skip to main content" not in text
    assert "Industry and business" not in text
    assert "Copyright notice" not in text
    assert all(s.heading_path[-1] != "Related content" for s in secs)


def test_html_sections_follow_heading_hierarchy_and_anchors():
    secs = {s.section_key: s for s in _html_sections()}
    measures = secs["when-you-must-apply-ecdd--measures-you-can-take"]
    assert measures.heading_path == ["Enhanced customer due diligence", "When you must apply ECDD", "Measures you can take"]
    assert measures.url == "https://example.org/ecdd#measures"
    assert "Foreign PEP | Source of wealth and source of funds" in measures.text  # table rendered as rows


def test_html_keeps_nested_lists_and_accordions():
    secs = {s.section_key: s for s in _html_sections()}
    when = secs["when-you-must-apply-ecdd"].text
    assert "- the customer or a beneficial owner is a foreign politically exposed person" in when
    assert "  - this includes a person acting on behalf of the customer" in when
    example = next(s for s in secs.values() if s.heading_path[-1].startswith("Example:"))
    assert "serving minister" in example.text


def test_html_extracts_last_updated():
    assert {s.last_updated for s in _html_sections()} == {"12 March 2026"}


def _rules():
    return parse_legislation_file(FIX / "rules_sample.txt", "rules2025", "Rules", "AML/CTF Rules 2025",
                                  RULES_PATTERN, "s", ["1", "6"])


def test_legislation_skips_table_of_contents_and_running_heads():
    secs = _rules()
    assert [s.section_key for s in secs] == ["1-1", "1-2", "6-18", "6-23"]
    assert all("SYNTHETIC TEST FIXTURE Rules 2025 Compilation" not in s.text for s in secs)
    assert all(not s.text.strip().endswith("40") for s in secs)


def test_legislation_heading_path_and_citation():
    s = next(s for s in _rules() if s.section_key == "6-23")
    assert s.heading_path == ["Part 6—Customer due diligence", "Division 5—Politically exposed persons",
                              "s 6-23 Initial customer due diligence—politically exposed persons"]
    chunk = chunk_section(s)[0]
    assert chunk.chunk_id == "rules2025::6-23::0"
    assert chunk.citation == "AML/CTF Rules 2025, s 6-23 — Initial customer due diligence—politically exposed persons"


def test_legislation_wrapped_numeric_line_is_not_a_heading():
    s = next(s for s in _rules() if s.section_key == "6-18")
    assert "wrapped continuation line" in s.text
    assert "(2) Subsection (1) does not apply" in s.text


def test_legislation_keeps_subsection_breaks():
    s = next(s for s in _rules() if s.section_key == "6-23")
    lines = s.text.split("\n")
    assert lines[0].startswith("(1)") and lines[1].startswith("(2)") and lines[2].startswith("Note:")


def test_legislation_include_parts_filter():
    secs = parse_legislation_file(FIX / "rules_sample.txt", "rules2025", "Rules", "AML/CTF Rules 2025",
                                  RULES_PATTERN, "s", ["6"])
    assert {s.section_key for s in secs} == {"6-18", "6-23"}


def test_legislation_en_dash_numbers_are_normalised():
    lines = ["Part 6—Customer due diligence", "6–9 Nature and purpose",
             "(1) A reporting entity must understand the nature and purpose of the business relationship."]
    from amlrag.ingest.parse_legislation import _clean_line

    secs = parse_legislation_lines([_clean_line(l) for l in lines], "r", "R", "R", RULES_PATTERN)
    assert [s.section_key for s in secs] == ["6-9"]


def _long_section(n_paras=12, words=60):
    paras = [f"({i}) " + " ".join(f"word{i}_{j}" for j in range(words)) + "." for i in range(1, n_paras + 1)]
    return Section(doc_id="d", doc_title="D", kind="legislation", section_key="6-9", heading_path=["x"],
                   text="\n".join(paras), section_title="T", doc_short="D")


def test_chunking_respects_max_words_and_overlaps():
    chunks = chunk_section(_long_section(), max_words=200, overlap_words=70)
    assert len(chunks) > 1
    assert all(c.word_count <= 200 + 70 for c in chunks)
    # The last paragraph of one chunk opens the next.
    first_tail = chunks[0].text.split("\n")[-1]
    assert chunks[1].text.split("\n")[0] == first_tail
    assert [c.chunk_id for c in chunks] == [f"d::6-9::{i}" for i in range(len(chunks))]


def test_chunking_splits_a_single_huge_paragraph():
    s = _long_section(1, 900)
    chunks = chunk_section(s, max_words=300, overlap_words=0)
    # A tiny remainder (< min_words) is folded into the last chunk rather than left as a fragment.
    assert len(chunks) >= 3 and all(c.word_count <= 300 + 20 for c in chunks)


def test_chunk_ids_unique_across_sections():
    s1, s2 = _long_section(), _long_section()
    ids = [c.chunk_id for c in chunk_sections([s1, s2], 200, 40)]
    assert len(ids) == len(set(ids))


def test_embed_text_carries_context_header():
    c = chunk_section(next(s for s in _rules() if s.section_key == "6-18"))[0]
    assert c.embed_text().startswith("AML/CTF Rules 2025, s 6-18")
    assert "Division 3" in c.embed_text()
