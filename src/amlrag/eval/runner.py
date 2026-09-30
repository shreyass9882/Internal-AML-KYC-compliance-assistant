"""Run the gold set through the assistant and write predictions, metrics and a Markdown report."""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from amlrag.backends import make_judge
from amlrag.config import Config
from amlrag.eval.gold import GoldItem, load_gold
from amlrag.eval.judge import Judge
from amlrag.eval.metrics import check_thresholds, compute_metrics
from amlrag.eval.report import write_comparison, write_report
from amlrag.eval.textmetrics import bertscore, bertscore_available, bertscore_settings
from amlrag.pipeline import Assistant

log = logging.getLogger(__name__)

# Ablations for the final report. closed_book is the no-RAG baseline (the model on its
# own); each later preset switches on one more component.
PRESETS: dict[str, dict[str, Any]] = {
    "closed_book": {"retrieval.enabled": False, "retrieval.use_fact_extraction": False,
                    "verification.guardrails": False},
    "baseline": {"retrieval.enabled": True, "retrieval.use_hybrid": False, "retrieval.use_fact_extraction": False,
                 "verification.guardrails": False},
    "hybrid": {"retrieval.enabled": True, "retrieval.use_hybrid": True, "retrieval.use_fact_extraction": False,
               "verification.guardrails": False},
    "hybrid_facts": {"retrieval.enabled": True, "retrieval.use_hybrid": True, "retrieval.use_fact_extraction": True,
                     "verification.guardrails": False},
    "full": {"retrieval.enabled": True},
}


def apply_preset(cfg: Config, preset: str) -> Config:
    if preset not in PRESETS:
        raise ValueError(f"unknown preset {preset!r}; choose from {sorted(PRESETS)} or 'all'")
    for key, value in PRESETS[preset].items():
        cfg = cfg.override(key, value)
    return cfg


def _prediction(item: GoldItem, result: dict[str, Any], judge: Judge | None, chunk_text: dict[str, str]) -> dict:
    closed = bool(result.get("closed_book"))
    points = []
    for pt in result.get("points", []):
        cids = [c["chunk_id"] for c in pt.get("citations", []) if c.get("chunk_id")]
        # Closed-book points have no passages to check against, so faithfulness is not applicable.
        verdict = None if (closed or not judge) else judge.supported(
            pt["text"], [chunk_text[c] for c in cids if c in chunk_text])
        points.append({"text": pt["text"], "group": pt.get("group"), "chunk_ids": cids,
                       "reference": pt.get("reference"), "support": pt.get("support"),
                       "supported_lexical": None if closed else pt.get("supported"), "judge_supported": verdict})
    cited = []
    for pt in points:
        for c in pt["chunk_ids"]:
            if c not in cited:
                cited.append(c)
    answer_text = " ".join([result.get("summary") or ""] + [p["text"] for p in points])
    return {
        "id": item.id, "mode": item.mode, "tier": result.get("tier"), "model_tier": result.get("model_tier"),
        "abstained": result.get("abstained"), "confidence": result.get("confidence"),
        "needs_review": result.get("needs_review"), "warnings": result.get("warnings", []),
        "retrieved": [s["chunk_id"] for s in result.get("sources", [])], "cited": cited, "points": points,
        "answer_text": answer_text, "summary": result.get("summary"), "facts": result.get("facts"),
        "guardrails_fired": result.get("guardrails_fired", []), "escalated": result.get("escalated", False),
        "checks": result.get("checks", {}), "latency_s": result.get("timings", {}).get("total_s"),
        "closed_book": closed,
        "judge_name": judge.name if judge else "lexical",
    }


def _select(items: list[GoldItem], ids, tags, limit) -> list[GoldItem]:
    if ids:
        items = [i for i in items if i.id in ids]
    if tags:
        wanted = set(tags)
        items = [i for i in items if wanted & set(i.tags)]
        # Keep the base of every selected counterfactual so invariance can be measured.
        chosen = {i.id for i in items}
        bases = {i.counterfactual_of for i in items if i.counterfactual_of} - chosen
        items = items + [i for i in _ALL_ITEMS.get("items", []) if i.id in bases]
    if limit:
        items = items[:limit]
    return items


_ALL_ITEMS: dict[str, list[GoldItem]] = {}


def _add_bertscore(cfg: Config, items: list[GoldItem], preds: dict[str, dict[str, Any]]) -> dict[str, Any]:
    settings = bertscore_settings(cfg.eval)
    info = {"model": settings["model_type"], "rescale_with_baseline": settings["rescale_with_baseline"]}
    if settings["enabled"] in ("false", "off", "no"):
        return {**info, "status": "disabled"}
    if not bertscore_available():
        if settings["enabled"] in ("true", "on", "yes"):
            raise RuntimeError('eval.bertscore.enabled is true but bert-score is not installed: '
                               'pip install -e ".[walert]"')
        return {**info, "status": "skipped (bert-score not installed)"}
    scored = [i for i in items if i.answerable and i.reference_answer and i.id in preds]
    scores = bertscore([preds[i.id].get("answer_text", "") for i in scored], [i.reference_answer for i in scored],
                       settings["model_type"], settings["lang"], settings["rescale_with_baseline"],
                       settings["batch_size"])
    for item, sc in zip(scored, scores):
        preds[item.id]["bertscore"] = {k: round(v, 4) for k, v in sc.items()}
    return {**info, "status": f"computed for {len(scores)} answers"}


def run_eval(cfg: Config, preset: str = "full", gold_path: str | None = None, limit: int | None = None,
             ids: list[str] | None = None, out_dir: Path | None = None, verbose: bool = True,
             llm=None, tags: list[str] | None = None) -> tuple[Path, dict[str, Any]]:
    cfg = apply_preset(cfg, preset)
    all_items = load_gold(gold_path or cfg.path("gold_file"))
    _ALL_ITEMS["items"] = all_items
    items = _select(all_items, ids, tags, limit)
    assistant = Assistant.from_config(cfg, llm=llm)
    chunk_text = {cid: c.text for cid, c in assistant.retriever.chunks.items()}
    available_docs = {c.doc_id for c in assistant.retriever.chunks.values()}

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = out_dir or cfg.path("results_dir") / f"{stamp}-{preset}"
    out_dir.mkdir(parents=True, exist_ok=True)
    judge_llm = make_judge(cfg)
    judge = Judge(judge_llm, cfg.path("results_dir") / ".judge_cache.json") if judge_llm else None

    preds: dict[str, dict[str, Any]] = {}
    t0 = time.perf_counter()
    with open(out_dir / "predictions.jsonl", "w", encoding="utf-8") as fh:
        for n, item in enumerate(items, start=1):
            try:
                result = assistant.ask(item.mode, item.query)
                pred = _prediction(item, result, judge, chunk_text)
            except Exception as exc:  # keep going; the error is reported
                log.exception("item %s failed", item.id)
                pred = {"id": item.id, "mode": item.mode, "tier": None, "abstained": True, "error": str(exc),
                        "retrieved": [], "cited": [], "points": [], "answer_text": "", "checks": {}}
            preds[item.id] = pred
            fh.write(json.dumps(pred, ensure_ascii=False) + "\n")
            fh.flush()
            if verbose:
                exp = item.expected_tier or ("answerable" if item.answerable else "abstain")
                got = pred.get("tier") or ("abstained" if pred.get("abstained") else "answered")
                mark = "ok " if _item_ok(item, pred) else "XX "
                print(f"  {mark}[{n:>2}/{len(items)}] {item.id:<42} expected={exp:<24} got={got}", flush=True)
    if judge:
        judge.save()

    bert_info = _add_bertscore(cfg, items, preds)
    if bert_info["status"].startswith("computed"):          # rewrite with the scores included
        with open(out_dir / "predictions.jsonl", "w", encoding="utf-8") as fh:
            for pred in preds.values():
                fh.write(json.dumps(pred, ensure_ascii=False) + "\n")

    metrics = compute_metrics(items, preds, available_docs, cfg.retrieval.final_k,
                              tuple(cfg.eval.get("ndcg_cutoffs", [1, 3, 5])),
                              bool(cfg.eval.get("rouge_stemmer", False)))
    metrics["acceptance"] = check_thresholds(metrics["headline"], cfg.eval.thresholds.to_dict())
    metrics["run"] = {
        "preset": preset, "started": stamp, "duration_s": round(time.perf_counter() - t0, 1),
        "gold_file": str(gold_path or cfg.path("gold_file")), "n_items": len(items),
        "generator": getattr(assistant.llm, "name", "?"), "embedder": assistant.embedder_name,
        "judge": judge.name if judge else "lexical", "snapshot": assistant.snapshot, "bertscore": bert_info,
        "index_digest": assistant.retriever.store.manifest.get("chunks_digest"),
        "gold_status": {s: sum(i.status == s for i in items) for s in ("draft", "reviewed")},
        "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out_dir / "config_used.yaml").write_text(yaml.safe_dump(cfg.to_dict(), sort_keys=False), encoding="utf-8")
    write_report(out_dir / "report.md", items, preds, metrics)
    latest = cfg.path("results_dir") / f"latest-{preset}.json"
    latest.write_text(json.dumps({"dir": str(out_dir), "headline": metrics["headline"]}, indent=2),
                      encoding="utf-8")
    return out_dir, metrics


def _item_ok(item: GoldItem, pred: dict[str, Any]) -> bool:
    if not item.answerable:
        return bool(pred.get("abstained"))
    if item.mode == "determine":
        return (pred.get("tier") or "") in item.acceptable
    return not pred.get("abstained")


def run_all_presets(cfg: Config, **kwargs) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = cfg.path("results_dir") / f"{stamp}-ablation"
    results = {}
    for preset in PRESETS:
        print(f"\n=== preset: {preset} ===")
        _, metrics = run_eval(cfg, preset=preset, out_dir=base / preset, **kwargs)
        results[preset] = metrics
    write_comparison(base / "comparison.md", results)
    return base
