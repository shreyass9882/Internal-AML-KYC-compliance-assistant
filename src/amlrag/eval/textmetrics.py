"""Answer-vs-reference metrics used by Walert: ROUGE-1 and BERTScore.

ROUGE-1 is implemented here with the same tokenisation as Google's `rouge-score`
package (lowercase, non-alphanumerics to spaces, optional Porter stemming of
tokens longer than 3 characters), so scores match `RougeScorer(["rouge1"])`
without adding its dependencies. BERTScore needs the optional `bert-score`
package (`pip install -e ".[walert]"`), which downloads a transformer model on
first use.
"""
from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache
from typing import Any

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_VALID = re.compile(r"^[a-z0-9]+$")


@lru_cache(maxsize=1)
def _porter():
    try:
        from nltk.stem import porter
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError("eval.rouge_stemmer: true needs nltk (pip install nltk)") from exc
    return porter.PorterStemmer()


def rouge_tokens(text: str, stemmer: bool = False) -> list[str]:
    tokens = re.split(r"\s+", _NON_ALNUM.sub(" ", (text or "").lower()))
    if stemmer:
        st = _porter()
        tokens = [st.stem(t) if len(t) > 3 else t for t in tokens]
    return [t for t in tokens if _VALID.match(t)]


def rouge1(prediction: str, reference: str, stemmer: bool = False) -> dict[str, float]:
    """ROUGE-1 precision, recall and F1 of a prediction against one reference."""
    pred = Counter(rouge_tokens(prediction, stemmer))
    ref = Counter(rouge_tokens(reference, stemmer))
    overlap = sum((pred & ref).values())
    p = overlap / max(sum(pred.values()), 1)
    r = overlap / max(sum(ref.values()), 1)
    f = 2 * p * r / (p + r) if p + r > 0 else 0.0
    return {"precision": p, "recall": r, "f1": f}


def bertscore_available() -> bool:
    import importlib.util

    return importlib.util.find_spec("bert_score") is not None


def bertscore(candidates: list[str], references: list[str], model_type: str | None = "roberta-large",
              lang: str = "en", rescale_with_baseline: bool = False,
              batch_size: int = 16) -> list[dict[str, float]]:
    """BERTScore P/R/F1 per candidate. Raises ImportError if bert-score is not installed."""
    from bert_score import score

    if not candidates:
        return []
    P, R, F = score(candidates, references, model_type=model_type or None, lang=lang,
                    rescale_with_baseline=rescale_with_baseline, batch_size=batch_size, verbose=False)
    return [{"precision": float(p), "recall": float(r), "f1": float(f)}
            for p, r, f in zip(P.tolist(), R.tolist(), F.tolist())]


def bertscore_settings(cfg_eval) -> dict[str, Any]:
    b = cfg_eval.get("bertscore", {})
    return {
        "enabled": str(b.get("enabled", "auto")).lower(),
        "model_type": b.get("model_type", "roberta-large"),
        "lang": b.get("lang", "en"),
        "rescale_with_baseline": bool(b.get("rescale_with_baseline", False)),
        "batch_size": int(b.get("batch_size", 16)),
    }
