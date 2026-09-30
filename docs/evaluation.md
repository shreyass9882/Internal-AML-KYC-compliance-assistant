# Evaluation

`amlrag eval` runs every item in `data/gold/scenarios.jsonl` through the assistant and scores it. This page defines each metric, explains how to calibrate the abstention threshold, and describes the ablation for the final report.

## Metrics

All metrics are in `results/<run>/metrics.json`; the headline set is also printed and written to `report.md`.

Counterfactual variants (gold items with `counterfactual_of` set) are used **only** in the fairness block, so each scenario counts once everywhere else.

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

- `judge_supported_rate`: an LLM judge (`eval.judge_model`) decides whether the passages fully support the claim. Verdicts are cached in `results/.judge_cache.json`. Using the same model as the generator inflates this score, so the judge (`llama3.1:8b`) is from a different family than the answer model (`qwen3.5:9b`). If you evaluate `--model llama3.1:8b`, change the judge for that run. Say which judge you used in the report.
- `lexical_supported_rate`: share of points whose content words mostly appear in the cited text (threshold `verification.min_support_overlap`). Crude, but free and deterministic; use it for quick iteration and the judge for reported numbers.

### Abstention

| Metric | Definition |
|---|---|
| `unanswerable_abstain_rate` | Of items with `answerable: false` (out of scope, repealed rules, lookups, no details), the share where the assistant abstained. A correct answer from the model's memory still counts as a failure, because it can't be cited. |
| `false_abstain_rate` | Of answerable items, the share where it abstained. |

### Consistency

Items sharing a `group` (paraphrases, or the same trigger across customer types) should get the same tier. `agreement_rate` is the share of groups whose members all agree; `all_correct_rate` requires them to also be correct.

### Walert-comparable measures

These follow Walert (Pathiyan Cherumanal et al., CHIIR 2024) so the results can be set beside the course's reference project. Walert grouped questions into *known* (a passage answers directly), *inferred* (answer needs several passages) and *out-of-KB* (in the domain but not answerable from the knowledge base); every gold item has an `answer_type` with those values, plus `underspecified` for scenarios that don't give enough facts to decide.

| Metric | Definition |
|---|---|
| `pct_unanswered_out_of_kb` | Share of out-of-KB questions the assistant declined to answer. Walert's "% of unanswered out-of-knowledge-base questions"; higher is better. |
| `pct_unanswered_underspecified` | The same for underspecified scenarios. |
| `ndcg` `@1/@3/@5` | Graded NDCG with linear gain, split by known and inferred questions. `expected_sections` count as grade 2 (highly relevant, Walert's label 2) and `partial_sections` as grade 1 (partially relevant). A reference can be a whole document, so several chunks may match it; each reference is credited once, at the first chunk that matches it, and the ideal ranking places every reference once. Not applicable to closed-book. |
| `rouge1` | ROUGE-1 precision, recall and F1 of the answer text (summary plus points) against the item's `reference_answer`. Same tokenisation as Google's `rouge-score` (verified identical); `eval.rouge_stemmer: true` adds Porter stemming. |
| `bertscore` | BERTScore P/R/F1 against `reference_answer`, if `bert-score` is installed (`pip install -e ".[walert]"`). Model and rescaling are set under `eval.bertscore`; report which you used. |

Our answers include reasoning points, so they are longer than the reference answers: ROUGE-1 precision will sit well below recall. Compare F1 across presets rather than against Walert's absolute numbers, which came from a different domain and answer style.

### Counterfactual fairness

Each variant copies a base scenario and changes one attribute that must not affect the tier: the customer's name, their country of birth, or which foreign country a PEP serves. Twelve variants over four base scenarios cover standard individuals, sole traders and foreign PEPs.

| Metric | Definition |
|---|---|
| `invariance_rate` | Share of groups (base plus its variants) whose answers are all identical. |
| `tier_flip_rate` | Share of variants whose tier differs from the base's. Acceptance limit 0.0: any flip is a finding to investigate. |
| `confidence_flip_rate` | Share of variants whose reported confidence differs from the base's. A softer signal of sensitivity to the name. |
| `variant_accuracy` | Share of variants with an acceptable tier. |

The report lists every flip. If one appears, check the retrieved sources and extracted facts for that variant before concluding the model is biased: a flip can also come from retrieval pulling different passages for different names.

### Operations

`latency_s` (mean, p50, p95 per item including fact extraction) and `needs_review_rate`. The p95 matters for the live demo.

## Calibrating the abstention threshold

`retrieval.min_dense_similarity` decides when the assistant refuses before calling the model. The default (0.30) is a deliberately low starting guess, and similarity ranges differ between embedding models, so tune it on your index every time you change the embedding model:

1. Run `amlrag eval --judge lexical` once.
2. Read `checks.max_similarity` for each item in `predictions.jsonl` (also in `amlrag ask --json` output).
3. Pick a value between the highest score among the unanswerable items and the lowest among the answerable ones. If they overlap, favour a slightly lower threshold and rely on the model's own `insufficient_information` / `answerable: false`, because a false refusal on a real CDD question is worse than a cited "not covered" answer.
4. Set it in `config.yaml` and re-run. Report the values you saw.

## Ablation for the final report

```bash
amlrag eval --preset all
```

runs five configurations and writes `results/<stamp>-ablation/comparison.md`:

| Preset | Adds |
|---|---|
| `closed_book` | **No retrieval.** The model answers from its own training and names its legal basis for each point. This is the "is RAG worth it?" baseline. |
| `baseline` | Dense retrieval only, no fact extraction, no guardrails. |
| `hybrid` | + BM25 fused with RRF. |
| `hybrid_facts` | + fact extraction and fact-driven sub-queries. |
| `full` | + guardrails (the configuration in `config.yaml`). |

For `closed_book`, the references the model names ("AML/CTF Rules 2025 s 6-23", "Act s 32") are parsed into section ids, so citation precision and recall work as usual. `citation_validity` means something different: the share of named sections that **exist** in the snapshot. References to the repealed 2007 Rules always count as invalid, and references to documents not in the snapshot (e.g. the Act if you didn't load it) are left out rather than counted as wrong. Retrieval, NDCG and faithfulness don't apply. `amlrag ask --closed-book "..."` shows the same thing for a single question, which is useful for a side-by-side in the demo video.

The table shows which component moves which metric. The expected pattern is that hybrid retrieval lifts recall on rule-number and exact-term questions, fact extraction lifts mandatory-ECDD recall on multi-party scenarios (company and trust beneficial owners), and guardrails remove residual under-application at some cost to over-application. Report what you actually observe, including any component that didn't help.

## Comparing models

Run the same preset with each model on the same index and gold set, then put the runs side by side:

```bash
amlrag eval --preset full --model llama3.1:8b --judge lexical
amlrag eval --preset full --judge lexical          # qwen3.5:9b
amlrag compare results/<first run> results/<second run>
```

For embedding models, build an index for each (each goes in its own folder), then evaluate with `--embedding-model`:

```bash
amlrag build --embedding-model nomic-embed-text
amlrag eval --preset full --judge lexical --embedding-model nomic-embed-text
amlrag eval --preset full --judge lexical          # qwen3-embedding:8b
amlrag compare results/<first run> results/<second run>
```

Retrieval recall and NDCG isolate the effect of the embedding model; tier accuracy shows whether better search turns into better answers. Recalibrate the abstention threshold for each embedding model before comparing refusal rates.

Use the same judge for every run you compare. `--judge lexical` is the simplest way to guarantee that; for final numbers use an LLM judge that is a different family from both answer models.

## Reviewing gold items

See [../data/gold/README.md](../data/gold/README.md). A reviewed gold set is what makes the headline numbers defensible; report how many items were reviewed and by whom.
