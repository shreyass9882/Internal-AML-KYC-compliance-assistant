# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 2
- Gold file: `/Users/shreyasshekhar/Desktop/aml-cdd-assistant/data/gold/scenarios.jsonl`: 7 items (0 reviewed, 7 draft)
- Duration: 819.9 s; finished 2026-10-01T03:40:58+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.800 | ≥ 0.8 | PASS |
| mandatory_ecdd_recall | 1.000 | ≥ 1.0 | PASS |
| under_application_rate_max | 0.000 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 0.400 | ≥ 0.8 | **FAIL** |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.400 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.738 | ≥ 0.8 | **FAIL** |
| unanswerable_abstain_rate | 0.500 | ≥ 0.75 | **FAIL** |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | n/a | ≤ 0.0 | **FAIL** |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.800 |
| tier_accuracy_strict | 0.800 |
| mandatory_ecdd_recall | 1.000 |
| under_application_rate | 0.000 |
| over_application_rate | 0.200 |
| retrieval_recall_at_k | 0.400 |
| citation_validity | 1.000 |
| citation_precision | 0.400 |
| citation_recall | 0.400 |
| faithfulness | 0.738 |
| key_fact_recall | n/a |
| unanswerable_abstain_rate | 0.500 |
| false_abstain_rate | 0.000 |
| consistency_agreement | 0.000 |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | 1.000 |
| walert_ndcg_at_5 | 0.434 |
| walert_rouge1_f1 | 0.278 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 84.630 |
| latency_p95_s | 113.000 |

## Tier determination (5 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 0 | 0 | 0 | 0 |
| **standard** | 0 | 2 | 1 | 0 |
| **enhanced** | 0 | 0 | 2 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 2 | 1.000 |
| government_body | 1 | 1.000 |
| individual | 1 | 1.000 |
| unincorporated_association | 1 | 0.000 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 3 | 0.667 |
| medium | 2 | 1.000 |

## Consistency (1 groups)

| Group | Predictions |
|---|---|
| G-domestic-pep-medium | D11-domestic-pep-medium-risk: standard, D51-assoc-domestic-pep-treasurer: enhanced |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 1.000 | 1 |
| % unanswered, underspecified scenarios | 0.000 | 1 |
| NDCG@1 (inferred questions) | 0.400 | 5 |
| NDCG@3 (inferred questions) | 0.424 | 5 |
| NDCG@5 (inferred questions) | 0.434 | 5 |
| NDCG@1 (all questions) | 0.400 | 5 |
| NDCG@3 (all questions) | 0.424 | 5 |
| NDCG@5 (all questions) | 0.434 | 5 |
| ROUGE-1 F1 vs reference answers | 0.278 | 5 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 8 | 0.500 | 0.625 |
| required_measures | 17 | 0.941 | 1.000 |
| rule | 10 | 0.700 | 0.900 |
| scenario_fact | 7 | 0.571 | 1.000 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.771** supported by the judge.

## Failures

### D51-assoc-domestic-pep-treasurer: expected standard, got enhanced

> A residents' association (unincorporated) opens an account. Its treasurer, who will sign on the account, is a sitting member of the federal House of Representatives. No adverse media; medium risk.

- summary: Enhanced CDD applies because the customer has a Politically Exposed Person (PEP) involved in governance, which triggers enhanced measures regardless of the medium risk rating.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::customer-identity--collect-information--individuals-responsible-for-the-governan::0, rules2025::6-8::0, rules2025::5-5::1, austrac-cdd-body-corporate::customer-identity::0, austrac-cdd-body-corporate::matters-you-must-establish::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::simplified-verification-for-certain-matt::0
- cited: austrac-cdd-body-corporate::matters-you-must-establish::0, rules2025::5-5::1, austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::simplified-verification-for-certain-matt::0

### D37-no-details: answered an unanswerable question

> A customer wants to open an account. Which CDD tier applies?

- summary: The scenario describes a customer wanting to open an account but provides no information about their identity, risk rating, or specific circumstances (like being a sole trader or having low risk). Without these facts, we cannot apply the rules for simplified CDD (which requires low risk) or enhanced CDD (which requires specific triggers). Therefore, standard initial CDD applies as the default.
- expected sections: -
- retrieved: austrac-risk-ratings::step-2-identify-customer-risk-for-initia::0, austrac-cdd-overview::initial-customer-due-diligence::0, austrac-delayed-cdd::general-requirements-for-delayed-initial--interrupting-the-ordinary-course-of-busi::0, austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0, rules2025::6-39::0, austrac-initial-cdd::how-to-establish-matters-on-reasonable-g--initial-cdd-for-different-customer-types::0, austrac-delayed-cdd::opening-an-account-and-allowing-deposits::0, rules2025::6-13::0
- cited: austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0, austrac-cdd-overview::initial-customer-due-diligence::0, austrac-risk-ratings::step-2-identify-customer-risk-for-initia::0


## Unsupported claims (11)

- **D02-foreign-pep-beneficial-owner** [scenario_fact]: The customer is Harbourline Imports Pty Ltd, an Australian private company with two directors. _(cited: none)_
- **D11-domestic-pep-medium-risk** [rule]: S2 states that enhanced CDD matters apply to a domestic PEP only if the ML/TF risk is high. Since this customer's risk is medium, S2 does not trigger enhanced requirements. _(cited: rules2025::6-23::0)_
- **D11-domestic-pep-medium-risk** [required_measures]: Collect and verify KYC information appropriate to the medium ML/TF risk level. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D24-asic-registration-trap** [scenario_fact]: The customer is a newly registered Australian proprietary company with low ML/TF risk. _(cited: none)_
- **D24-asic-registration-trap** [rule]: S2 confirms that the deeming provisions for exempting beneficial owner identification apply only to listed public companies or government bodies, which this customer is not. _(cited: rules2025::6-7::0)_
- **D24-asic-registration-trap** [conclusion]: Since the customer does not qualify for simplified CDD exemptions and no enhanced triggers are present, standard CDD applies. The scenario lacks information on whether beneficial owners were established or if the entity is unable to do so, preventing a 'simplified' or 'enhanced' classification based on inability. _(cited: austrac-cdd-body-corporate::identifying-beneficial-owners::0, austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **D49-embassy-ambassador-signatory** [conclusion]: Because the scenario states the risk is medium, the conditions for enhanced CDD are not met. Therefore, the entity does not need to apply enhanced measures or seek senior manager approval based on PEP status alone. _(cited: austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, rules2025::6-23::0)_
- **D49-embassy-ambassador-signatory** [conclusion]: Escalated by guardrail: the scenario indicates a foreign politically exposed person is involved. The cited source treats this as requiring enhanced CDD. A compliance officer should confirm. _(cited: austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0)_
- **D37-no-details** [scenario_fact]: The scenario states a customer wants to open an account but does not specify who the customer is, their risk level, or any special circumstances. _(cited: none)_
- **D37-no-details** [rule]: Enhanced CDD triggers require specific conditions like high ML/TF risk or being a PEP, which are not mentioned in the scenario. _(cited: none)_
- **D37-no-details** [conclusion]: Since we cannot confirm low risk (for simplification) nor identify any enhanced triggers, and the customer identity is unknown, the tier is 'standard' because the scenario lacks sufficient information to justify simplification or enhancement. _(cited: austrac-cdd-overview::initial-customer-due-diligence::0, austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0)_
