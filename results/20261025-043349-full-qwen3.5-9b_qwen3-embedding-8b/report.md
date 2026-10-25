# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.3
- Gold file: `data/gold/retrieval-stress.jsonl`: 8 items (0 reviewed, 8 draft)
- Duration: 486.7 s (answering 486.7 s, then grading 0.0 s); finished 2026-10-24T17:41:56+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | n/a | ≥ 0.8 | n/a |
| mandatory_ecdd_recall | n/a | ≥ 1.0 | n/a |
| under_application_rate_max | n/a | ≤ 0.05 | n/a |
| retrieval_recall_at_k | 0.719 | ≥ 0.8 | **FAIL** |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.327 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.950 | ≥ 0.8 | PASS |
| unanswerable_abstain_rate | n/a | ≥ 0.75 | n/a |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | n/a | ≤ 0.0 | n/a |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | n/a |
| tier_accuracy_strict | n/a |
| mandatory_ecdd_recall | n/a |
| under_application_rate | n/a |
| over_application_rate | n/a |
| retrieval_recall_at_k | 0.719 |
| citation_validity | 1.000 |
| citation_precision | 0.327 |
| citation_recall | 0.719 |
| faithfulness | 0.950 |
| key_fact_recall | 0.662 |
| unanswerable_abstain_rate | n/a |
| false_abstain_rate | 0.000 |
| consistency_agreement | n/a |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | n/a |
| walert_ndcg_at_5 | 0.515 |
| walert_rouge1_f1 | 0.451 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 59.510 |
| latency_p95_s | 76.480 |

## Answer checks

Citation validity means each citation points to a passage that was really retrieved. Whether that passage supports the claim is measured separately (faithfulness, below).

- Answers with a point that cites nothing: 0
- Answers that call a fact the scenario rules out unknown: 0

## Tier determination (0 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 0 | 0 | 0 | 0 |
| **standard** | 0 | 0 | 0 | 0 |
| **enhanced** | 0 | 0 | 0 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|

| Model confidence | n | Accuracy |
|---|---|---|

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | n/a | 0 |
| % unanswered, underspecified scenarios | n/a | 0 |
| NDCG@1 (known questions) | 0.357 | 7 |
| NDCG@3 (known questions) | 0.433 | 7 |
| NDCG@5 (known questions) | 0.458 | 7 |
| NDCG@1 (inferred questions) | 1.000 | 1 |
| NDCG@3 (inferred questions) | 1.000 | 1 |
| NDCG@5 (inferred questions) | 0.915 | 1 |
| NDCG@1 (all questions) | 0.438 | 8 |
| NDCG@3 (all questions) | 0.504 | 8 |
| NDCG@5 (all questions) | 0.515 | 8 |
| ROUGE-1 F1 vs reference answers | 0.451 | 8 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| key_points | 40 | 0.950 | 1.000 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.950** supported by the judge.

## Failures

None.

## Unsupported claims (2)

- **R01-initial-cdd-matters** [key_points]: The business must establish on reasonable grounds the matters listed in paragraphs 28(2)(a) and (c) of the Act. _(cited: rules2025::6-12::0)_
- **R06-call-for-action-vs-increased-monitoring** [key_points]: You must also conduct enhanced CDD if a customer's ML/TF risk is identified as high during ongoing monitoring, even if they were not initially high risk. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high--example-identifying-high-ml-tf-risk-duri-2::0)_
