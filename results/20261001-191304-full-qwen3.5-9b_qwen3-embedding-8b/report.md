# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.1
- Gold file: `/Users/shreyasshekhar/Projects/aml-cdd-assistant/data/gold/scenarios.jsonl`: 15 items (0 reviewed, 15 draft)
- Duration: 710.5 s; finished 2026-10-01T09:25:23+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | n/a | ≥ 0.8 | n/a |
| mandatory_ecdd_recall | n/a | ≥ 1.0 | n/a |
| under_application_rate_max | n/a | ≤ 0.05 | n/a |
| retrieval_recall_at_k | 0.938 | ≥ 0.8 | PASS |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.557 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.947 | ≥ 0.8 | PASS |
| unanswerable_abstain_rate | 1.000 | ≥ 0.75 | PASS |
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
| retrieval_recall_at_k | 0.938 |
| citation_validity | 1.000 |
| citation_precision | 0.557 |
| citation_recall | 0.938 |
| faithfulness | 0.947 |
| key_fact_recall | 0.875 |
| unanswerable_abstain_rate | 1.000 |
| false_abstain_rate | 0.000 |
| consistency_agreement | n/a |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | 1.000 |
| walert_ndcg_at_5 | 0.679 |
| walert_rouge1_f1 | 0.311 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 43.000 |
| latency_p95_s | 60.310 |

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
| % unanswered, out-of-knowledge-base questions | 1.000 | 7 |
| % unanswered, underspecified scenarios | n/a | 0 |
| NDCG@1 (known questions) | 0.750 | 8 |
| NDCG@3 (known questions) | 0.668 | 8 |
| NDCG@5 (known questions) | 0.679 | 8 |
| NDCG@1 (all questions) | 0.750 | 8 |
| NDCG@3 (all questions) | 0.668 | 8 |
| NDCG@5 (all questions) | 0.679 | 8 |
| ROUGE-1 F1 vs reference answers | 0.311 | 8 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| key_points | 38 | 0.947 | 1.000 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.947** supported by the judge.

## Failures

None.

## Unsupported claims (2)

- **E03-trust-kyc** [key_points]: Collect KYC information about the nature and purpose of the trust's business or operations. _(cited: rules2025::6-3::1, rules2025::6-3::0)_
- **E08-simplified-beneficial-owners** [key_points]: You may skip identifying beneficial owners if the customer is a government body. _(cited: rules2025::6-7::1, rules2025::6-7::0)_
