"""Best-effort masking of personal identifiers before a question is written to the query log.

Structured identifiers (emails, phone numbers, dates, street addresses, long
numbers such as account, card, TFN or ABN numbers, "#12345"-style references)
are caught reliably. Personal names are caught when they follow a title
("Mr", "Dr"...), follow "named"/"called", appear as two or more capitalised
words, or appear capitalised mid-sentence. A single first name at the very
start of a sentence ("Maria wants...") is NOT caught. For real customer data,
set query_log.store_text to "none" or tell staff not to type names (the UI says so).
"""
from __future__ import annotations

import re

_MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December|"
           "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec")
_STREET = ("Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Court|Ct|Place|Pl|Lane|Ln|Crescent|Cres|Parade|Pde|"
           "Highway|Hwy|Terrace|Tce|Boulevard|Blvd|Way|Close|Cl|Grove|Gr|Circuit|Cct|Square|Sq")
_HONORIFIC = r"(?:Mr|Mrs|Ms|Miss|Mx|Dr|Prof|Sir|Dame|Hon|Senator|Judge|Justice)\.?"
_CAP = r"[A-Z][a-z'’A-Z-]*[a-z][\w'’-]*"

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    ("URL", re.compile(r"\bhttps?://\S+|\bwww\.\S+", re.I)),
    ("ADDRESS", re.compile(rf"\b(?:\d{{1,5}}/)?\d{{1,5}}[A-Za-z]?\s+(?:{_CAP}\s+){{1,3}}(?:{_STREET})\b\.?")),
    ("DATE", re.compile(r"\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")),
    ("DATE", re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{_MONTHS})\.?,?\s+\d{{4}}\b")),
    ("DATE", re.compile(rf"\b(?:{_MONTHS})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}\b")),
    ("PHONE", re.compile(r"(?<![\w-])(?:\+?61[ -]?|0)[2-478](?:[ -]?\d){8}(?![\w-])")),
    ("ID", re.compile(r"#\s?\d{3,}\b")),
    ("NUMBER", re.compile(r"(?<![\w-])\d(?:[ -]?\d){6,}(?![\w-])")),
    ("NAME", re.compile(rf"\b{_HONORIFIC}\s+{_CAP}(?:\s+{_CAP})*")),
]
_NAMED = re.compile(rf"\b(named|called|name is|known as)\s+({_CAP}(?:\s+{_CAP})*)")

# Capitalised words that are not personal names: sentence starters, legal/organisation
# words, places and acronyms that give a question its meaning.
_ALLOW = set("""
A An The This That These Those Our Your Their His Her Its We They She He It I You In On At Of For And Or But If
When Where While After Before During Apart Also Then However With Without From To As By Is Are Was Were Has Have
Had Can Could Should Would Will May Must Do Does Did Not No Yes What Which Who Why How Please Customer Customers
New Existing Recent Management Screening Risk Low Medium High Standard Simplified Enhanced Initial Ongoing
Pty Ltd Limited Inc Incorporated Co Company Corporation Corp Trust Trustee Family Fund Funds Super Superannuation
Self-Managed Estate Council Department Government Commonwealth State States Territory Parliament Senate House
Representatives Court Supreme High Federal Bank Banking Club Association Church Foundation Charity Charitable
Partnership Partners Partner Holdings Group Services Imports Exports Trading Enterprises Ministry Minister Embassy
Office Branch Authority Agency Tax Office Deputy Treasurer President Director Chair Board Committee University
Unit Units Investment Investments Capital Finance Financial Insurance Insurer Exchange Markets Securities
Australia Australian Australians Victoria Victorian Queensland Tasmania Tasmanian Canberra Melbourne Sydney
Brisbane Perth Adelaide Hobart Darwin Geelong South North East West Western Northern Southern Eastern Wales
New Zealand United Kingdom Britain British England English Scotland Ireland Irish America American Canada
India Indian China Chinese Singapore Hong Kong Japan Japanese Indonesia Malaysia Philippines Vietnam Vietnamese
Thailand Greece Greek Italy Italian Germany German France French Fiji Papua Guinea Pacific Korea Iran Myanmar
Lebanon Africa African Europe European Asia Asian Middle Kingdom Republic Democratic People
Singaporean Malaysian Indonesian Filipino Thai Korean Iranian Lebanese Canadian Fijian Samoan Tongan Nigerian
Kenyan Ghanaian Egyptian Pakistani Pakistan Bangladeshi Bangladesh Sri Lanka Lankan Nepal Nepalese Afghanistan
Afghan Nigeria Kenya Ghana Egypt Turkey Turkish Russia Russian Ukraine Ukrainian Brazil Brazilian Mexico Mexican
Argentina Spain Spanish Portugal Portuguese Netherlands Dutch Switzerland Swiss Sweden Swedish Norway Norwegian
Denmark Danish Poland Polish Emirates Emirati Saudi Arabia Arabian Qatar Israel Israeli Taiwan Taiwanese
Cambodia Cambodian Laos Samoa Tonga Vanuatu Solomon Islands Island Timor Burma Burmese Syria Syrian Iraq Iraqi
Yemen Somalia Sudan Ethiopia Nordic Caribbean Latin Gulf Territories Territorian Queenslander
January February March April May June July August September October November December
Monday Tuesday Wednesday Thursday Friday Saturday Sunday Rules Act Part Division Section Chapter Schedule Note
Example Guidance Tier Rule
""".split())


def _is_name_token(tok: str) -> bool:
    parts = [p for p in re.split(r"[-’']", tok) if p]
    if not parts:
        return False
    if all(p.isupper() and len(p) <= 8 for p in parts if p[0].isalpha()):  # acronyms: ASX, APRA, PEP
        return False
    return not all(p in _ALLOW or not p[0].isupper() or p.isupper() for p in parts)


_TOKEN = re.compile(r"[A-Za-z][\w'’-]*")
_SENT_END = re.compile(r"[.!?:;]\s*$|\n\s*$")


def _mask_capitalised(text: str) -> str:
    out: list[str] = []
    last = 0
    tokens = list(_TOKEN.finditer(text))
    i = 0
    while i < len(tokens):
        m = tokens[i]
        tok = m.group(0)
        if not tok[0].isupper() or not _is_name_token(tok):
            i += 1
            continue
        # Extend a run of capitalised words separated only by spaces.
        j = i
        while (j + 1 < len(tokens) and tokens[j + 1].group(0)[0].isupper()
               and text[tokens[j].end():tokens[j + 1].start()] == " "):
            j += 1
        prefix = text[:m.start()]
        sentence_start = not prefix.strip() or bool(_SENT_END.search(prefix))
        run = tokens[i:j + 1]
        if j == i and sentence_start:
            i += 1          # lone capitalised word opening a sentence: could be any word
            continue
        # Mask only the name-like words in the run, keep "Family Trust", "Pty Ltd" etc.
        for t in run:
            if _is_name_token(t.group(0)):
                out.append(text[last:t.start()])
                out.append("[NAME]")
                last = t.end()
        i = j + 1
    out.append(text[last:])
    return re.sub(r"\[NAME\](?:\s+\[NAME\])+", "[NAME]", "".join(out))


def redact(text: str) -> str:
    """Mask personal identifiers in free text. See the module docstring for what is and isn't caught."""
    if not text:
        return text
    for label, pattern in _PATTERNS:
        text = pattern.sub(f"[{label}]", text)
    text = _NAMED.sub(lambda m: f"{m.group(1)} [NAME]", text)
    return _mask_capitalised(text)
