"""One line per test item for a finished run: did it pass, what did retrieval find, which key facts
were missing. The main report gives averages; this shows which question caused them.

    python -m amlrag.eval.items results/<run> --gold data/gold/retrieval-stress.jsonl

Prints a table and writes items.md next to the run's report.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from amlrag import ABSTAIN
from amlrag.eval.gold import GoldItem, load_gold
from amlrag.eval.metrics import key_fact_recall
from amlrag.models import ref_matches

# An Explain item passes when it answers, retrieves at least one expected passage in the top k, and
# its answer contains at least this share of the item's key facts.
MIN_KEY_FACTS = 0.6
PASS_RULE = (f"An Explain item passes when it answers, finds at least one expected passage in the top k "
             f"and contains at least {round(MIN_KEY_FACTS * 100)}% of its key facts. A Determine item passes "
             "when its tier is one of the acceptable tiers. A question the assistant should decline passes "
             "only when it declines.")


def _tier(t: str | None) -> str:
    return "cannot determine" if t == ABSTAIN else str(t)


def item_row(g: GoldItem, p: dict[str, Any], k: int = 8) -> dict[str, Any]:
    tier = p.get("tier") or (ABSTAIN if p.get("abstained") else None)
    if p.get("error"):
        ok, result = False, f"error: {p['error']}"
    elif not g.answerable:
        ok = bool(p.get("abstained"))
        result = "declined" if ok else (f"answered ({_tier(tier)})" if g.mode == "determine" else "answered")
    elif g.mode == "determine":
        ok = tier in g.acceptable
        result = f"{_tier(tier)} (expected {_tier(g.expected_tier)})"
    else:
        ok = not p.get("abstained")
        result = "answered" if ok else "declined"

    facts = missing = None
    if g.key_facts and g.answerable and g.mode == "explain":
        facts = key_fact_recall(p.get("answer_text", ""), g.key_facts)
        text = p.get("answer_text", "").lower()
        if not p.get("abstained"):          # a declined answer misses every fact; say so once, not per fact
            missing = [alts[0] for alts in g.key_facts if not any(a.lower() in text for a in alts)]

    found = first = None
    if g.expected_sections and not p.get("closed_book"):
        retrieved = (p.get("retrieved") or [])[:k]
        found = sum(any(ref_matches(c, r) for c in retrieved) for r in g.expected_sections)
        first = next((n for n, c in enumerate(retrieved, 1)
                      if any(ref_matches(c, r) for r in g.expected_sections)), None)

    if g.mode == "explain" and g.answerable and ok:
        ok = (facts is None or facts >= MIN_KEY_FACTS) and (found is None or found >= 1)

    cited = p.get("cited") or []
    refs = g.expected_sections + g.partial_sections
    precision = (sum(any(ref_matches(c, r) for r in refs) for c in cited) / len(cited)
                 if cited and refs and not p.get("abstained") else None)
    checks = p.get("checks") or {}
    return {"id": g.id, "ok": ok, "result": result, "found": found, "expected": len(g.expected_sections),
            "first": first, "facts": facts, "missing": missing or [], "cited": len(cited), "precision": precision,
            "ruled_out_called_unknown": bool(checks.get("ruled_out_called_unknown")),
            "needs_review": bool(p.get("needs_review")), "warnings": p.get("warnings") or [],
            "seconds": p.get("latency_s")}


def _pct(x: float | None) -> str:
    return "-" if x is None else f"{round(100 * x)}%"


def rows_for_run(run_dir: Path, gold_path: Path, k: int = 8) -> list[dict[str, Any]]:
    gold = {g.id: g for g in load_gold(gold_path)}
    preds = [json.loads(line) for line in (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines()
             if line.strip()]
    return [item_row(gold[p["id"]], p, k) for p in preds if p.get("id") in gold]


def render_text(rows: list[dict[str, Any]], k: int = 8) -> str:
    out = [f"{'':2}{'item':46} {'result':38} {'found@' + str(k):>8} {'1st':>4} {'facts':>6} {'cites ok':>9}"]
    for r in rows:
        found = "-" if r["found"] is None else f"{r['found']}/{r['expected']}"
        out.append(f"{'✓' if r['ok'] else '✗':2}{r['id'][:46]:46} {r['result'][:38]:38} {found:>8} "
                   f"{r['first'] or '-':>4} {_pct(r['facts']):>6} {_pct(r['precision']):>9}")
        if r["missing"]:
            out.append(f"{'':4}missing key facts: {', '.join(r['missing'])}")
        if r["ruled_out_called_unknown"]:
            out.append(f"{'':4}called a fact the scenario rules out 'unknown'")
    passed = sum(r["ok"] for r in rows)
    out.append(f"\n{passed} of {len(rows)} passed. {PASS_RULE.replace('top k', f'top {k}')}")
    return "\n".join(out)


def render_markdown(rows: list[dict[str, Any]], k: int = 8, title: str = "Results by item") -> str:
    L = [f"# {title}\n",
         f"*found@{k}*: expected references in the top {k} retrieved passages. *1st*: rank of the first one. "
         "*facts*: share of the item's key facts in the answer. *cites ok*: share of cited passages that are "
         "expected or partially relevant references. " + PASS_RULE.replace("top k", f"top {k}") + "\n",
         f"| | item | result | found@{k} | 1st | facts | cites ok | missing key facts |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        found = "-" if r["found"] is None else f"{r['found']}/{r['expected']}"
        notes = ", ".join(r["missing"])
        if r["ruled_out_called_unknown"]:
            notes = (notes + "; " if notes else "") + "called a ruled-out fact unknown"
        L.append(f"| {'✓' if r['ok'] else '✗'} | {r['id']} | {r['result']} | {found} | {r['first'] or '-'} | "
                 f"{_pct(r['facts'])} | {_pct(r['precision'])} | {notes} |")
    L.append(f"\n**{sum(r['ok'] for r in rows)} of {len(rows)} passed.**")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run", help="results/<run> folder")
    ap.add_argument("--gold", required=True, help="the gold JSONL the run used")
    ap.add_argument("--k", type=int, default=8, help="retrieval depth (retrieval.final_k)")
    a = ap.parse_args(argv)
    run_dir = Path(a.run)
    rows = rows_for_run(run_dir, Path(a.gold), a.k)
    print(render_text(rows, a.k))
    (run_dir / "items.md").write_text(render_markdown(rows, a.k, f"Results by item: {Path(a.gold).name}"),
                                      encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
