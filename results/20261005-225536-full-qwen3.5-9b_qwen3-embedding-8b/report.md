# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.2
- Gold file: `data/gold/adversarial.jsonl`: 4 items (0 reviewed, 4 draft)
- Duration: 933.3 s (answering 933.3 s, then grading 0.0 s); finished 2026-10-05T12:11:10+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.750 | ≥ 0.8 | **FAIL** |
| mandatory_ecdd_recall | 1.000 | ≥ 1.0 | PASS |
| under_application_rate_max | 0.000 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 1.000 | ≥ 0.8 | PASS |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.583 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.833 | ≥ 0.8 | PASS |
| unanswerable_abstain_rate | n/a | ≥ 0.75 | n/a |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | n/a | ≤ 0.0 | n/a |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.750 |
| tier_accuracy_strict | 0.750 |
| mandatory_ecdd_recall | 1.000 |
| under_application_rate | 0.000 |
| over_application_rate | 0.250 |
| retrieval_recall_at_k | 1.000 |
| citation_validity | 1.000 |
| citation_precision | 0.583 |
| citation_recall | 1.000 |
| faithfulness | 0.833 |
| key_fact_recall | n/a |
| unanswerable_abstain_rate | n/a |
| false_abstain_rate | 0.000 |
| consistency_agreement | n/a |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | n/a |
| walert_ndcg_at_5 | 0.748 |
| walert_rouge1_f1 | 0.300 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 266.710 |
| latency_p95_s | 399.910 |

## Answer checks

Citation validity means each citation points to a passage that was really retrieved. Whether that passage supports the claim is measured separately (faithfulness, below).

- Answers with a point that cites nothing: 0
- Answers that call a fact the scenario rules out unknown: 1

## Tier determination (4 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 0 | 0 | 0 | 0 |
| **standard** | 0 | 2 | 1 | 0 |
| **enhanced** | 0 | 0 | 1 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 4 | 0.750 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 3 | 0.667 |
| medium | 1 | 1.000 |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | n/a | 0 |
| % unanswered, underspecified scenarios | n/a | 0 |
| NDCG@1 (inferred questions) | 0.750 | 4 |
| NDCG@3 (inferred questions) | 0.748 | 4 |
| NDCG@5 (inferred questions) | 0.748 | 4 |
| NDCG@1 (all questions) | 0.750 | 4 |
| NDCG@3 (all questions) | 0.748 | 4 |
| NDCG@5 (all questions) | 0.748 | 4 |
| ROUGE-1 F1 vs reference answers | 0.300 | 4 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 4 | 0.750 | 1.000 |
| required_measures | 15 | 0.800 | 0.933 |
| rule | 5 | 0.800 | 1.000 |
| scenario_fact | 6 | 1.000 | 1.000 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.792** supported by the judge.

## Failures

### A04-payments-only-unknown: expected standard/insufficient_information, got enhanced

> An Australian company regularly makes payments to suppliers located in a jurisdiction that FATF has called for enhanced CDD to be applied. We know nothing else about the company's owners or the people who act for it.

- summary: Enhanced CDD is required because the customer (an Australian company) makes payments to suppliers in a jurisdiction that FATF has called for enhanced CDD. This matches the trigger in S1 and S2 regarding persons acting on behalf of the customer or receiving services from a high-risk jurisdiction.
- guardrails fired: high_risk_jurisdiction (escalated: False)
- expected sections: austrac-ecdd
- retrieved: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, rules2025::6-7::0, rules2025::6-7::1, austrac-ecdd::introduction::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high--example-identifying-high-ml-tf-risk-duri-2::0
- cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0
- gold note: Control for A01 (added 3 Oct 2026): here the owners' location really is unknown, so listing it as missing information is correct. Together A01 and A04 test that the assistant tells 'the scenario says no' from 'the scenario doesn't say'.


## Unsupported claims (5)

- **A01-payments-only-ruled-out** [conclusion]: Since none of the relevant persons are located or formed in the high-risk jurisdiction, the condition for enhanced CDD is not met. The scenario does not mention other triggers (like PEPs or suspicious activity). Thus, standard CDD applies. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0)_
- **A01-payments-only-ruled-out** [required_measures]: Establish the identity of the customer (the company). _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **A01-payments-only-ruled-out** [required_measures]: Establish whether any beneficial owner is a PEP or designated for TFS. _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **A02-grey-list-not-call-for-action** [rule]: Simplified CDD applies only when there are no red flags or enhanced CDD triggers and the risk is low. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **A02-grey-list-not-call-for-action** [required_measures]: Conduct ongoing monitoring appropriate for a medium-risk customer. _(cited: austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
