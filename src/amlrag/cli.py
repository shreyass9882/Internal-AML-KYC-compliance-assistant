"""Command-line interface: amlrag fetch | build | ask | eval | serve | doctor | stats."""
from __future__ import annotations

import argparse
import json
import logging
import sys
import textwrap

from amlrag.config import load_config


def _cfg(args):
    cfg = load_config(args.config)
    if getattr(args, "offline", False):
        cfg = cfg.override("embedding.backend", "hash").override("generation.backend", "stub") \
                 .override("eval.judge_backend", "lexical")
    if getattr(args, "fast", False):
        cfg = cfg.override("generation.model", cfg.generation.fallback_model)
    return cfg


def cmd_fetch(args) -> int:
    from amlrag.ingest.fetch import fetch_snapshot

    cfg = _cfg(args)
    report = fetch_snapshot(cfg, refresh=args.refresh, only=args.only)
    for key, items in report.items():
        if items:
            print(f"{key:>8}: {', '.join(items)}")
    if report["changed"]:
        print("\nWARNING: these sources changed since the locked snapshot. Rebuild the index and re-run the "
              "evaluation before relying on earlier results:", ", ".join(report["changed"]))
    print(f"\nLock file: {cfg.path('lock_file')}")
    return 1 if report["failed"] and not (report["fetched"] or report["skipped"] or report["manual"]) else 0


def cmd_build(args) -> int:
    from amlrag.backends import make_embedder
    from amlrag.index.store import build_index
    from amlrag.ingest.build import build_chunks, read_chunks
    from amlrag.ingest.fetch import snapshot_date

    cfg = _cfg(args)
    stats = build_chunks(cfg)
    print(f"Parsed {stats['sections']} sections -> {stats['chunks']} chunks")
    for doc, n in sorted(stats["per_doc"].items()):
        print(f"  {doc:<40} {n:>4} chunks")
    if stats["missing"]:
        print("Missing (not fetched and no manual file):", ", ".join(stats["missing"]))
    if stats["chunks"] == 0:
        print("Nothing to index. Run `amlrag fetch` first (or place files in kb/manual/).")
        return 1
    if args.skip_index:
        return 0
    embedder = make_embedder(cfg)
    chunks = read_chunks(cfg.path("chunks_file"))

    def progress(done, total):
        print(f"\r  embedding {done}/{total}", end="", flush=True)

    manifest = build_index(chunks, embedder, cfg.path("chroma_dir"), cfg.retrieval.collection,
                           snapshot_date(cfg), progress)
    print(f"\nIndexed {manifest['chunks']} chunks with {manifest['embedder']} (dim {manifest['dim']}) "
          f"into {cfg.path('chroma_dir')}")
    return 0


def _print_result(r: dict) -> None:
    w = textwrap.TextWrapper(width=100, subsequent_indent="    ")
    if r.get("offline_stub"):
        print("!! OFFLINE STUB MODE: not a real model answer !!")
    if r["mode"] == "determine":
        print(f"\nTier: {str(r['tier']).upper()}   confidence: {r['confidence']}"
              + ("   [NEEDS REVIEW]" if r["needs_review"] else ""))
    print("\n" + w.fill(r["summary"] or ""))
    for p in r["points"]:
        labels = ", ".join(c["label"] for c in p["citations"]) or "no valid citation"
        flag = "" if p["supported"] else "  (weak support)"
        print(w.fill(f"  - {p['text']} [{labels}]{flag}"))
    if r["missing_information"]:
        print("\nMissing information: " + "; ".join(r["missing_information"]))
    for warning in r["warnings"]:
        print(w.fill(f"! {warning}"))
    cited = [s for s in r["sources"] if s["cited"]]
    if cited:
        print("\nSources:")
        for s in cited:
            print(f"  [{s['label']}] {s['citation']}\n       {s['url'] or ''}")
    print(f"\n({r['timings'].get('total_s', 0):.1f}s, snapshot {r.get('snapshot') or 'unknown'})")


def cmd_ask(args) -> int:
    from amlrag.pipeline import Assistant

    cfg = _cfg(args)
    text = " ".join(args.text) if args.text else sys.stdin.read()
    result = Assistant.from_config(cfg).ask(args.mode, text)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_result(result)
    return 0


def cmd_eval(args) -> int:
    from amlrag.eval.runner import run_all_presets, run_eval

    cfg = _cfg(args)
    if args.judge:
        cfg = cfg.override("eval.judge_backend", args.judge)
    if args.preset == "all":
        base = run_all_presets(cfg, gold_path=args.gold, limit=args.limit, ids=args.ids)
        print(f"\nAblation comparison: {base / 'comparison.md'}")
        return 0
    out_dir, metrics = run_eval(cfg, preset=args.preset, gold_path=args.gold, limit=args.limit, ids=args.ids)
    print(f"\n[{args.preset}] results in {out_dir}")
    for k, v in metrics.get("headline", {}).items():
        print(f"  {k:<32} {v}")
    failed = [a["name"] for a in metrics.get("acceptance", []) if not a["passed"]]
    print("\nAcceptance: " + ("all thresholds met" if not failed else "FAILED " + ", ".join(failed)))
    return 0


def cmd_serve(args) -> int:
    import uvicorn

    from amlrag.server.app import create_app

    cfg = _cfg(args)
    uvicorn.run(create_app(cfg), host=args.host, port=args.port, log_level="info")
    return 0


def cmd_doctor(args) -> int:
    from amlrag.backends import make_client
    from amlrag.index.store import read_manifest
    from amlrag.ingest.fetch import load_lock

    cfg = _cfg(args)
    ok = True
    lock = load_lock(cfg)
    n_docs = len(lock.get("documents", {}))
    print(f"[{'ok' if n_docs else '--'}] snapshot: {n_docs} documents locked (created {lock.get('snapshot_created')})")
    manifest = read_manifest(cfg.path("chroma_dir"))
    print(f"[{'ok' if manifest else '--'}] index: " +
          (f"{manifest['chunks']} chunks, {manifest['embedder']}, built {manifest['built_at'][:19]}" if manifest
           else "not built (run `amlrag build`)"))
    ok &= bool(manifest)
    if cfg.embedding.backend == "ollama" or cfg.generation.backend == "ollama":
        client = make_client(cfg)
        try:
            models = client.list_models()
            print(f"[ok] ollama {client.version() or ''} at {cfg.ollama.host}")
            for need in {cfg.embedding.model, cfg.generation.model}:
                have = any(m == need or m.startswith(need + ":") or m.split(":")[0] == need for m in models)
                print(f"[{'ok' if have else '!!'}] model {need}" + ("" if have else f"  -> ollama pull {need}"))
                ok &= have
        except Exception as exc:
            print(f"[!!] {exc}")
            ok = False
    print(f"[..] generation num_ctx={cfg.generation.num_ctx}, final_k={cfg.retrieval.final_k}, "
          f"hybrid={cfg.retrieval.use_hybrid}, facts={cfg.retrieval.use_fact_extraction}, "
          f"guardrails={cfg.verification.guardrails}/{cfg.verification.guardrail_mode}")
    return 0 if ok else 1


def cmd_stats(args) -> int:
    from amlrag.ingest.build import read_chunks

    cfg = _cfg(args)
    chunks = read_chunks(cfg.path("chunks_file"))
    words = sorted(c.word_count for c in chunks)
    print(f"{len(chunks)} chunks; words min {words[0]}, median {words[len(words)//2]}, max {words[-1]}")
    if args.grep:
        for c in chunks:
            if args.grep.lower() in c.text.lower() or args.grep.lower() in c.chunk_id.lower():
                print(f"\n{c.chunk_id}\n  {c.citation}\n  {c.text[:300]}")
    return 0


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="amlrag", description=__doc__)
    p.add_argument("--config", help="path to config.yaml (default: nearest config.yaml)")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        sp = sub.add_parser(name, help=help_)
        sp.set_defaults(fn=fn)
        sp.add_argument("--offline", action="store_true",
                        help="hash embedder + stub generator (no Ollama; for tests/UI work, NOT real answers)")
        return sp

    sp = add("fetch", cmd_fetch, "download and version-lock the knowledge-base sources")
    sp.add_argument("--refresh", action="store_true", help="re-download everything and report changes")
    sp.add_argument("--only", nargs="+", help="only these document ids")

    sp = add("build", cmd_build, "parse, chunk, embed and index the snapshot")
    sp.add_argument("--skip-index", action="store_true", help="parse and chunk only")

    sp = add("ask", cmd_ask, "ask a question from the terminal")
    sp.add_argument("text", nargs="*")
    sp.add_argument("--mode", choices=["determine", "explain"], default="determine")
    sp.add_argument("--json", action="store_true")
    sp.add_argument("--fast", action="store_true", help="use generation.fallback_model")

    sp = add("eval", cmd_eval, "run the gold-standard evaluation")
    sp.add_argument("--gold", help="gold JSONL (default paths.gold_file)")
    sp.add_argument("--preset", default="full", help="full | baseline | hybrid | hybrid_facts | no_guardrails | all")
    sp.add_argument("--limit", type=int)
    sp.add_argument("--ids", nargs="+")
    sp.add_argument("--judge", choices=["ollama", "lexical"])
    sp.add_argument("--fast", action="store_true")

    sp = add("serve", cmd_serve, "start the web UI + API")
    sp.add_argument("--host", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=8000)
    sp.add_argument("--fast", action="store_true")

    add("doctor", cmd_doctor, "check Ollama, models, snapshot and index")
    sp = add("stats", cmd_stats, "chunk statistics / grep chunks")
    sp.add_argument("--grep")

    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s")
    sys.exit(args.fn(args))
