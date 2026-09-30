"""Markdown reports: one per run, plus an ablation comparison table."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from amlrag import ABSTAIN
from amlrag.eval.gold import GoldItem

_TIER_COLS = ["simplified", "standard", "enhanced", ABSTAIN]


def _fmt(v: Any) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def write_report(path: Path, items: list[GoldItem], preds: dict[str, dict], m: dict[str, Any]) -> None:
    run = m.get("run", {})
    L: list[str] = []
    L.append(f"# Evaluation report: preset `{run.get('preset')}`\n")
    L.append(f"- Generator: `{run.get('generator')}`; embedder: `{run.get('embedder')}`; judge: `{run.get('judge')}`")
    L.append(f"- Knowledge-base snapshot: {run.get('snapshot') or 'unknown'} (index digest `{run.get('index_digest')}`)")
    L.append(f"- Gold file: `{run.get('gold_file')}`: {run.get('n_items')} items "
             f"({run.get('gold_status', {}).get('reviewed', 0)} reviewed, {run.get('gold_status', {}).get('draft', 0)} draft)")
    L.append(f"- Duration: {run.get('duration_s')} s; finished {run.get('finished')}\n")
    if run.get("preset") == "closed_book":
        L.append("> **Closed-book baseline.** The model answered from its own training with no retrieved sources. "
                 "Retrieval and faithfulness metrics do not apply. Citation validity here means the legal references "
                 "the model named exist in the snapshot; references to documents not in the snapshot are excluded. "
                 "Acceptance thresholds are shown for comparison only.\n")
    if run.get("gold_status", {}).get("draft"):
        L.append("> Draft gold items have not yet been checked against the locked snapshot by a reviewer. "
                 "Treat these numbers as provisional.\n")

    L.append("## Acceptance thresholds\n")
    L.append("| Check | Value | Limit | Result |\n|---|---|---|---|")
    for a in m.get("acceptance", []):
        op = "≥" if a["direction"] == "min" else "≤"
        L.append(f"| {a['name']} | {_fmt(a['value'])} | {op} {a['limit']} | {'PASS' if a['passed'] else '**FAIL**'} |")

    L.append("\n## Headline metrics\n")
    L.append("| Metric | Value |\n|---|---|")
    for k, v in m["headline"].items():
        L.append(f"| {k} | {_fmt(v)} |")

    t = m["tier"]
    L.append(f"\n## Tier determination ({t['n']} answerable scenarios)\n")
    L.append("Rows are the expected tier, columns the assistant's final tier.\n")
    L.append("| expected \\ predicted | " + " | ".join(_TIER_COLS) + " |")
    L.append("|---|" + "---|" * len(_TIER_COLS))
    for exp in ("simplified", "standard", "enhanced"):
        row = t["confusion"].get(exp, {})
        L.append(f"| **{exp}** | " + " | ".join(str(row.get(c, 0)) for c in _TIER_COLS) + " |")
    L.append("\n| Customer type | n | Accuracy (acceptable) |\n|---|---|---|")
    for ctype, v in t["accuracy_by_customer_type"].items():
        L.append(f"| {ctype} | {v['n']} | {_fmt(v['accuracy'])} |")
    L.append("\n| Model confidence | n | Accuracy |\n|---|---|---|")
    for c, v in m["calibration"].items():
        L.append(f"| {c} | {v['n']} | {_fmt(v['accuracy'])} |")

    c = m["consistency"]
    if c["detail"]:
        L.append(f"\n## Consistency ({c['groups']} groups)\n")
        L.append("| Group | Predictions |\n|---|---|")
        for g, members in c["detail"].items():
            L.append(f"| {g} | " + ", ".join(f"{i}: {v}" for i, v in members.items()) + " |")

    L.append("\n## Failures\n")
    by_id = {i.id: i for i in items}
    fails = []
    for pid, p in preds.items():
        g = by_id[pid]
        if not g.answerable:
            if not p.get("abstained"):
                fails.append((g, p, "answered an unanswerable question"))
        elif g.mode == "determine" and (p.get("tier") or ABSTAIN) not in g.acceptable:
            fails.append((g, p, f"expected {'/'.join(g.acceptable)}, got {p.get('tier')}"))
        elif g.mode == "explain" and p.get("abstained"):
            fails.append((g, p, "abstained on an answerable question"))
    if not fails:
        L.append("None.")
    for g, p, why in fails:
        L.append(f"### {g.id}: {why}\n")
        L.append(f"> {g.query}\n")
        if p.get("error"):
            L.append(f"- **error:** {p['error']}")
        if p.get("summary"):
            L.append(f"- summary: {p['summary']}")
        if p.get("guardrails_fired"):
            L.append(f"- guardrails fired: {', '.join(p['guardrails_fired'])} (escalated: {p.get('escalated')})")
        L.append(f"- expected sections: {', '.join(g.expected_sections) or '-'}")
        L.append(f"- retrieved: {', '.join(p.get('retrieved', [])[:8]) or '-'}")
        L.append(f"- cited: {', '.join(p.get('cited', [])) or '-'}")
        refs = [pt.get("reference") for pt in p.get("points", []) if pt.get("reference")]
        if refs:
            L.append(f"- references named by the model: {'; '.join(dict.fromkeys(refs))}")
        if g.notes:
            L.append(f"- gold note: {g.notes}")
        L.append("")

    weak = [(pid, pt) for pid, p in preds.items() if not p.get("closed_book") for pt in p.get("points", [])
            if pt.get("judge_supported") is False or (pt.get("judge_supported") is None and not pt.get("supported_lexical"))]
    L.append(f"\n## Unsupported claims ({len(weak)})\n")
    for pid, pt in weak[:25]:
        L.append(f"- **{pid}**: {pt['text']} _(cited: {', '.join(pt['chunk_ids']) or 'none'})_")

    miss = m["retrieval"].get("items_without_reachable_refs")
    if miss:
        L.append(f"\n_Items skipped for retrieval metrics because none of their expected documents is indexed: "
                 f"{', '.join(miss)}_")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def write_comparison(path: Path, results: dict[str, dict[str, Any]]) -> None:
    presets = list(results)
    keys = list(next(iter(results.values()))["headline"].keys())
    L = ["# Ablation comparison\n", "Each preset adds one component: baseline (dense only) → hybrid (+BM25) → "
         "hybrid_facts (+fact extraction sub-queries) → full (+guardrails).\n",
         "| Metric | " + " | ".join(presets) + " |", "|---|" + "---|" * len(presets)]
    for k in keys:
        L.append(f"| {k} | " + " | ".join(_fmt(results[p]["headline"].get(k)) for p in presets) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
