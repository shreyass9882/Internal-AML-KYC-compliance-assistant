# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 1
- Gold file: `data/gold/adversarial.jsonl`: 8 items (0 reviewed, 8 draft)
- Duration: 2019.8 s (answering 2019.8 s, then grading 0.0 s); finished 2026-10-05T13:01:13+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.667 | ≥ 0.8 | **FAIL** |
| mandatory_ecdd_recall | 0.000 | ≥ 1.0 | **FAIL** |
| under_application_rate_max | 0.000 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 0.000 | ≥ 0.8 | **FAIL** |
| citation_validity | n/a | ≥ 1.0 | n/a |
| citation_precision | n/a | ≥ 0.6 | n/a |
| faithfulness | n/a | ≥ 0.8 | n/a |
| unanswerable_abstain_rate | 1.000 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 1.000 | ≤ 0.15 | **FAIL** |
| fairness_tier_flip_rate_max | n/a | ≤ 0.0 | n/a |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.667 |
| tier_accuracy_strict | 0.000 |
| mandatory_ecdd_recall | 0.000 |
| under_application_rate | 0.000 |
| over_application_rate | 0.000 |
| retrieval_recall_at_k | 0.000 |
| citation_validity | n/a |
| citation_precision | n/a |
| citation_recall | n/a |
| faithfulness | n/a |
| key_fact_recall | n/a |
| unanswerable_abstain_rate | 1.000 |
| false_abstain_rate | 1.000 |
| consistency_agreement | n/a |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | 1.000 |
| walert_ndcg_at_5 | 0.000 |
| walert_rouge1_f1 | 0.000 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | n/a |
| latency_p95_s | n/a |

## Answer checks

Citation validity means each citation points to a passage that was really retrieved. Whether that passage supports the claim is measured separately (faithfulness, below).

- Answers with a point that cites nothing: 0
- Answers that call a fact the scenario rules out unknown: 0

## Tier determination (6 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 0 | 0 | 0 | 0 |
| **standard** | 0 | 0 | 0 | 5 |
| **enhanced** | 0 | 0 | 0 | 1 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 6 | 0.667 |

| Model confidence | n | Accuracy |
|---|---|---|
| none | 6 | 0.667 |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 1.000 | 1 |
| % unanswered, underspecified scenarios | 1.000 | 1 |
| NDCG@1 (inferred questions) | 0.000 | 6 |
| NDCG@3 (inferred questions) | 0.000 | 6 |
| NDCG@5 (inferred questions) | 0.000 | 6 |
| NDCG@1 (all questions) | 0.000 | 6 |
| NDCG@3 (all questions) | 0.000 | 6 |
| NDCG@5 (all questions) | 0.000 | 6 |
| ROUGE-1 F1 vs reference answers | 0.000 | 6 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Failures

### A02-grey-list-not-call-for-action: expected standard, got None

> An Australian-registered company is owned by a person who lives in a country on the FATF list of jurisdictions under increased monitoring (the grey list). That country is not subject to a FATF call for action. We rate the customer as medium risk and none of the people involved is a politically exposed person.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-high-risk-countries
- retrieved: -
- cited: -
- gold note: Adversarial test added 3 Oct 2026: a FATF grey-list country is not a call-for-action country. Reviewer to confirm against AUSTRAC's 'High-risk countries, regions and groups' page in the locked snapshot.

### A03-call-for-action-measures-risk-based: expected enhanced, got None

> A company formed in a country that FATF has called for enhanced due diligence on wants to open a business account with us. Apart from that, we would rate it medium risk, and none of its owners or directors is a politically exposed person.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd
- retrieved: -
- cited: -
- gold note: Adversarial test added 3 Oct 2026. Prompt v3.1 listed example measures under 'What you need to do' as if all were required and said enhanced CDD applies 'regardless of other factors'. Check by reading the answer: measures a source gives as examples should carry required: false.


## Unsupported claims (0)

