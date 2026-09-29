# Evaluation

`amlrag eval` runs every item in `data/gold/scenarios.jsonl` through the assistant and scores it. This page defines each metric, explains how to calibrate the abstention threshold, and describes the ablation for the final report.

## Metrics

All metrics are in `results/<run>/metrics.json`; the headline set is also printed and written to `report.md`.

### Effectiveness (tier determination)

Computed over answerable `determine` items.

| Metric | Definition |
|---|---|
| `tier_accuracy_strict` | Final tier equals `expected_tier`. |
| `tier_accuracy_acceptable` | Final tier is in `acceptable_tiers`. For low-risk customers both *simplified* and *standard* are compliant, so this is the primary accuracy figure. |
| `under_application_rate` | Share of items where the tier is **lower** than every acceptable tier (e.g. *standard* where *enhanced* is required). This is the error that creates regulatory exposure; the acceptance limit is 5%. |
| `over_application_rate` | Share where the tier is **higher** than every acceptable tier. Wasteful rather than non-compliant, but the first user story asks to avoid both. |
| `mandatory_ecdd_recall` | Of items flagged `mandatory_ecdd`, the share determined *enhanced*. Acceptance requires 1.0. |
| `macro_f1` | Unweighted F1 across the three tiers (abstentions count as misses). |
| `accuracy_by_customer_type` | Acceptable accuracy per `customer_type`: the *consistency across customer types* check from the project plan. |
| `calibration` | Accuracy grouped by the assistant's reported confidence. High-confidence answers should be more accurate than low-confidence ones; if not, the confidence caps in `generate/verify.py` need work. |

For `explain` items, `key_fact_recall` is the share of each item's `key_facts` (lists of alternative phrases) that appear in the answer.

### Retrieval

Over answerable items whose expected documents are indexed (items that reference only the optional Act are listed as `items_without_reachable_refs` if the Act isn't loaded).

| Metric | Definition |
|---|---|
| `recall_at_k` | Share of `expected_sections` references matched by at least one of the top-k retrieved chunks. A reference is a document (`austrac-ecdd`), a section (`rules2025::6-23`) or a chunk; matching respects boundaries, so `rules2025::6-2` does not match `6-23`. |
| `hit_at_k` | At least one expected reference retrieved. |
| `mrr` | Mean reciprocal rank of the first retrieved chunk matching any expected reference. |

### Attribution (citations)

| Metric | Definition |
|---|---|
| `citation_validity` | Share of citation labels the model emitted that point at a retrieved source. Invalid labels are stripped before display; acceptance requires 1.0 **before** stripping, i.e. the model should never invent a source. |
| `citation_precision_section` | Of the chunks an answer cites, the share that fall under an expected reference. `citation_precision_document` is the same at document level (lenient). |
| `citation_recall_section` | Of the expected references, the share that the answer cites. |

### Faithfulness

Each cited reasoning point is checked against the text of the chunks it cites.

- `judge_supported_rate`: an LLM judge (`eval.judge_model`) decides whether the passages fully support the claim. Verdicts are cached in `results/.judge_cache.json`. Using the same model as the generator inflates this score; if the machine can hold a second model, set `judge_model` to a different family (e.g. `qwen2.5:7b`) and say which one you used in the report.
- `lexical_supported_rate`: share of points whose content words mostly appear in the cited text (threshold `verification.min_support_overlap`). Crude, but free and deterministic; use it for quick iteration and the judge for reported numbers.

### Abstention

| Metric | Definition |
|---|---|
| `unanswerable_abstain_rate` | Of items with `answerable: false` (out of scope, repealed rules, lookups, no details), the share where the assistant abstained. A correct answer from the model's memory still counts as a failure, because it can't be cited. |
| `false_abstain_rate` | Of answerable items, the share where it abstained. |

### Consistency

Items sharing a `group` (paraphrases, or the same trigger across customer types) should get the same tier. `agreement_rate` is the share of groups whose members all agree; `all_correct_rate` requires them to also be correct.

### Operations

`latency_s` (mean, p50, p95 per item including fact extraction) and `needs_review_rate`. The p95 matters for the live demo.

## Calibrating the abstention threshold

`retrieval.min_dense_similarity` decides when the assistant refuses before calling the model. The default (0.42) is a starting guess; tune it on your index:

1. Run `amlrag eval --judge lexical` once.
2. Read `checks.max_similarity` for each item in `predictions.jsonl` (also in `amlrag ask --json` output).
3. Pick a value between the highest score among the unanswerable items and the lowest among the answerable ones. If they overlap, favour a slightly lower threshold and rely on the model's own `insufficient_information` / `answerable: false`, because a false refusal on a real CDD question is worse than a cited "not covered" answer.
4. Set it in `config.yaml` and re-run. Report the values you saw.

## Ablation for the final report

```bash
amlrag eval --preset all
```

runs four configurations and writes `results/<stamp>-ablation/comparison.md`:

| Preset | Adds |
|---|---|
| `baseline` | Dense retrieval only, no fact extraction, no guardrails. |
| `hybrid` | + BM25 fused with RRF. |
| `hybrid_facts` | + fact extraction and fact-driven sub-queries. |
| `full` | + guardrails (the configuration in `config.yaml`). |

The table shows which component moves which metric. The expected pattern is that hybrid retrieval lifts recall on rule-number and exact-term questions, fact extraction lifts mandatory-ECDD recall on multi-party scenarios (company and trust beneficial owners), and guardrails remove residual under-application at some cost to over-application. Report what you actually observe, including any component that didn't help.

## Reviewing gold items

See [../data/gold/README.md](../data/gold/README.md). A reviewed gold set is what makes the headline numbers defensible; report how many items were reviewed and by whom.
