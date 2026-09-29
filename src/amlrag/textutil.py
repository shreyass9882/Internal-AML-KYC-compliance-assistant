"""Small text helpers: normalisation, tokenisation, slugs."""
from __future__ import annotations

import re
import unicodedata

# Tokens keep legislative references intact: "6-23", "s32", "37a".
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[0-9]+[a-z]?)?")

STOPWORDS = frozenset(
    """a an and are as at be been being but by can could did do does for from had has have
    how i if in into is it its may might must no not of on or our shall should so such
    than that the their them then there these they this those to under up upon was we
    were what when where which while who whom why will with would you your per via also
    any all each other only own same both more most some""".split()
)

# Collapse common spellings so BM25 treats them as one term.
_SYNONYMS = {
    "pep": "politically exposed person",
    "peps": "politically exposed persons",
    "ecdd": "enhanced customer due diligence",
    "edd": "enhanced customer due diligence",
    "cdd": "customer due diligence",
    "kyc": "know your customer",
    "smr": "suspicious matter report",
    "ml/tf": "money laundering terrorism financing",
    "mltf": "money laundering terrorism financing",
    "vasp": "virtual asset service provider",
    "sow": "source of wealth",
    "sof": "source of funds",
}


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace(" ", " ").replace("‑", "-")
    text = re.sub(r"(?<=\S)[ \t]+", " ", text)          # collapse runs, keep leading indentation
    text = re.sub(r"[ \t]+$", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def expand_abbreviations(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        word = m.group(0)
        exp = _SYNONYMS.get(word.lower())
        return f"{word} ({exp})" if exp else word

    return re.sub(r"\b[A-Za-z/]{2,6}\b", repl, text)


def tokenize(text: str, drop_stopwords: bool = True) -> list[str]:
    text = text.lower().replace("—", " ").replace("–", "-")
    # "section 32" / "s 32" / "s.32" -> also emit "s32" so either form matches.
    # Rules-style "6-23" references are left alone (handled by _TOKEN_RE).
    text = re.sub(r"\b(?:section|sect|s)\.?\s*(\d{1,3}[a-z]?)\b(?!-)", r"s\1 \1", text)
    toks = _TOKEN_RE.findall(text)
    if drop_stopwords:
        toks = [t for t in toks if t not in STOPWORDS]
    return toks


def content_words(text: str) -> set[str]:
    """Stemmed-ish content words for lexical support checks."""
    out = set()
    for tok in tokenize(text):
        if len(tok) < 3 and not any(c.isdigit() for c in tok):
            continue
        out.add(_light_stem(tok))
    return out


def _light_stem(tok: str) -> str:
    for suf in ("ings", "ing", "ies", "ied", "es", "ed", "s"):
        if len(tok) > len(suf) + 3 and tok.endswith(suf):
            return tok[: -len(suf)] + ("y" if suf in ("ies", "ied") else "")
    return tok


def slugify(text: str, max_len: int = 60) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:max_len].rstrip("-") or "section"


def word_count(text: str) -> int:
    return len(text.split())
