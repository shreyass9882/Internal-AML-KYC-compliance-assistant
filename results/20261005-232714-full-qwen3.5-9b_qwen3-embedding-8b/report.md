# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 1
- Gold file: `data/gold/retrieval-stress.jsonl`: 8 items (0 reviewed, 8 draft)
- Duration: 1920.1 s (answering 1920.1 s, then grading 0.0 s); finished 2026-10-05T12:59:14+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | n/a | ≥ 0.8 | n/a |
| mandatory_ecdd_recall | n/a | ≥ 1.0 | n/a |
| under_application_rate_max | n/a | ≤ 0.05 | n/a |
| retrieval_recall_at_k | 0.000 | ≥ 0.8 | **FAIL** |
| citation_validity | n/a | ≥ 1.0 | n/a |
| citation_precision | n/a | ≥ 0.6 | n/a |
| faithfulness | n/a | ≥ 0.8 | n/a |
| unanswerable_abstain_rate | n/a | ≥ 0.75 | n/a |
| false_abstain_rate_max | 1.000 | ≤ 0.15 | **FAIL** |
| fairness_tier_flip_rate_max | n/a | ≤ 0.0 | n/a |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | n/a |
| tier_accuracy_strict | n/a |
| mandatory_ecdd_recall | n/a |
| under_application_rate | n/a |
| over_application_rate | n/a |
| retrieval_recall_at_k | 0.000 |
| citation_validity | n/a |
| citation_precision | n/a |
| citation_recall | n/a |
| faithfulness | n/a |
| key_fact_recall | 0.000 |
| unanswerable_abstain_rate | n/a |
| false_abstain_rate | 1.000 |
| consistency_agreement | n/a |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | n/a |
| walert_ndcg_at_5 | 0.000 |
| walert_rouge1_f1 | 0.000 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | n/a |
| latency_p95_s | n/a |

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
| NDCG@1 (known questions) | 0.000 | 7 |
| NDCG@3 (known questions) | 0.000 | 7 |
| NDCG@5 (known questions) | 0.000 | 7 |
| NDCG@1 (inferred questions) | 0.000 | 1 |
| NDCG@3 (inferred questions) | 0.000 | 1 |
| NDCG@5 (inferred questions) | 0.000 | 1 |
| NDCG@1 (all questions) | 0.000 | 8 |
| NDCG@3 (all questions) | 0.000 | 8 |
| NDCG@5 (all questions) | 0.000 | 8 |
| ROUGE-1 F1 vs reference answers | 0.000 | 8 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Failures

### R01-initial-cdd-matters: abstained on an answerable question

> What matters must a business establish about a customer before providing a designated service?

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-initial-cdd::what-you-must-establish-during-initial-c
- retrieved: -
- cited: -
- gold note: Set D R1 (ChatGPT's suggested tests, reviewed 5 Oct 2026). The guidance lists eight matters in one passage; key facts check the answer keeps the whole list (the PEP answer reviewed the same day dropped one of four groups).

### R02-body-corporate-beneficial-owners: abstained on an answerable question

> What must a business establish about the beneficial owners of a body corporate?

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-cdd-body-corporate::identifying-beneficial-owners, austrac-cdd-body-corporate::identifying-beneficial-owners--collect-information, austrac-cdd-body-corporate::identifying-beneficial-owners--verify-information
- retrieved: -
- cited: -
- gold note: Set D R2 (ChatGPT's suggested tests, reviewed 5 Oct 2026). Rules 6-7 (deemed compliance) and 6-8 (unable to identify) are the exceptions.

### R03-person-acting-on-behalf: abstained on an answerable question

> What must a business establish about a person acting on behalf of a customer?

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-cdd-body-corporate::persons-acting-on-behalf-of-the-customer, austrac-cdd-body-corporate::persons-acting-on-behalf-of-the-customer--collect-information, austrac-cdd-body-corporate::persons-acting-on-behalf-of-the-customer--verify-information, rules2025::6-19
- retrieved: -
- cited: -
- gold note: Set D R3 (ChatGPT's suggested tests, reviewed 5 Oct 2026). Every customer-type guide has a 'persons acting on behalf' section; the body-corporate one plus rule 6-19 carry the rule, the others are partially relevant.

### R04-ecdd-mandatory-circumstances: abstained on an answerable question

> What are the main circumstances in which enhanced CDD must be applied?

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high, austrac-ecdd::when-you-must-apply-enhanced-cdd--youre-required-to-submit-a-suspicious-ma, austrac-ecdd::when-you-must-apply-enhanced-cdd--unusual-large-or-complex-transactions, austrac-ecdd::when-you-must-apply-enhanced-cdd--designated-services-that-are-part-of-a-n, austrac-ecdd::when-you-must-apply-enhanced-cdd--foreign-politically-exposed-persons, austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris
- retrieved: -
- cited: -
- gold note: Set D R4 (ChatGPT's suggested tests, reviewed 5 Oct 2026); a paraphrase of E10, scored at section level: each of AUSTRAC's six 'When you must apply enhanced CDD' sections is a separate reference, so Recall@8 shows how many of the six triggers the retriever finds.

### R05-ecdd-measures-high-risk: abstained on an answerable question

> What kinds of additional enhanced CDD measures may be appropriate for a high-risk customer?

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd::enhanced-cdd-measures-you-can-apply
- retrieved: -
- cited: -
- gold note: Set D R5 (ChatGPT's suggested tests, reviewed 5 Oct 2026). The last key fact checks the answer presents the measures as risk-based options, the same point A03 tests in Determine mode.

### R06-call-for-action-vs-increased-monitoring: abstained on an answerable question

> What is the difference between a high-risk jurisdiction that makes enhanced CDD mandatory and a jurisdiction under FATF increased monitoring?

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris
- retrieved: -
- cited: -
- gold note: Set D R6 (ChatGPT's suggested tests, reviewed 5 Oct 2026). The knowledge base never names FATF's increased-monitoring ('grey') list, so the second half is inferred: the sources tie mandatory enhanced CDD to call-for-action jurisdictions only, and say to use FATF updates in risk assessments. A good answer says the sources don't describe the grey list rather than inventing what it is. A02 tests the same distinction in Determine mode.

### R07-delayed-initial-cdd: abstained on an answerable question

> When can delayed initial CDD be relevant?

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-delayed-cdd::general-requirements-for-delayed-initial
- retrieved: -
- cited: -
- gold note: Set D R7 (ChatGPT's suggested tests, reviewed 5 Oct 2026). E12 asks only about delaying verification; this asks about delayed initial CDD in general, which AUSTRAC lists as five circumstances plus two conditions.

### R08-pep-matters: abstained on an answerable question

> What PEP-related matters must be established during customer due diligence?

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-pep::how-to-establish-if-an-individual-is-a-p, austrac-pep::additional-obligations-for-peps--additional-initial-cdd-obligations-for-p, rules2025::6-23
- retrieved: -
- cited: -
- gold note: Set D R8 (ChatGPT's suggested tests, reviewed 5 Oct 2026). The third key fact is the group the Explain answer on foreign PEPs left out the same day; the fifth checks the domestic and international organisation PEP condition.


## Unsupported claims (0)

