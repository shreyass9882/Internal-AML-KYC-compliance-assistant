# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3
- Gold file: `/Users/shreyasshekhar/Projects/aml-cdd-assistant/data/gold/scenarios.jsonl`: 12 items (0 reviewed, 12 draft)
- Duration: 1514.4 s; finished 2026-10-01T04:23:44+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.900 | ≥ 0.8 | PASS |
| mandatory_ecdd_recall | 1.000 | ≥ 1.0 | PASS |
| under_application_rate_max | 0.000 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 0.550 | ≥ 0.8 | **FAIL** |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.258 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.754 | ≥ 0.8 | **FAIL** |
| unanswerable_abstain_rate | 1.000 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | n/a | ≤ 0.0 | n/a |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.900 |
| tier_accuracy_strict | 0.900 |
| mandatory_ecdd_recall | 1.000 |
| under_application_rate | 0.000 |
| over_application_rate | 0.100 |
| retrieval_recall_at_k | 0.550 |
| citation_validity | 1.000 |
| citation_precision | 0.258 |
| citation_recall | 0.450 |
| faithfulness | 0.754 |
| key_fact_recall | n/a |
| unanswerable_abstain_rate | 1.000 |
| false_abstain_rate | 0.000 |
| consistency_agreement | 0.500 |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | 1.000 |
| walert_ndcg_at_5 | 0.410 |
| walert_rouge1_f1 | 0.290 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 97.150 |
| latency_p95_s | 106.210 |

## Tier determination (10 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 2 | 0 | 0 | 0 |
| **standard** | 0 | 3 | 1 | 0 |
| **enhanced** | 0 | 0 | 4 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 3 | 1.000 |
| government_body | 1 | 1.000 |
| individual | 5 | 1.000 |
| unincorporated_association | 1 | 0.000 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 7 | 0.857 |
| medium | 3 | 1.000 |

## Consistency (2 groups)

| Group | Predictions |
|---|---|
| G-domestic-pep-medium | D11-domestic-pep-medium-risk: standard, D51-assoc-domestic-pep-treasurer: enhanced |
| G-foreign-pep | D01-foreign-pep-individual: enhanced, D02-foreign-pep-beneficial-owner: enhanced |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 1.000 | 1 |
| % unanswered, underspecified scenarios | 1.000 | 1 |
| NDCG@1 (known questions) | 0.500 | 3 |
| NDCG@3 (known questions) | 0.428 | 3 |
| NDCG@5 (known questions) | 0.371 | 3 |
| NDCG@1 (inferred questions) | 0.500 | 7 |
| NDCG@3 (inferred questions) | 0.431 | 7 |
| NDCG@5 (inferred questions) | 0.427 | 7 |
| NDCG@1 (all questions) | 0.500 | 10 |
| NDCG@3 (all questions) | 0.430 | 10 |
| NDCG@5 (all questions) | 0.410 | 10 |
| ROUGE-1 F1 vs reference answers | 0.290 | 10 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 10 | 0.700 | 1.000 |
| required_measures | 29 | 0.724 | 1.000 |
| rule | 15 | 0.667 | 0.933 |
| scenario_fact | 15 | 0.933 | 0.867 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.704** supported by the judge.

## Failures

### D51-assoc-domestic-pep-treasurer: expected standard, got enhanced

> A residents' association (unincorporated) opens an account. Its treasurer, who will sign on the account, is a sitting member of the federal House of Representatives. No adverse media; medium risk.

- summary: Enhanced CDD is required because the scenario involves a Politically Exposed Person (PEP). The treasurer of the residents' association is a sitting member of the federal House of Representatives, which makes them a domestic PEP. AUSTRAC rules mandate enhanced CDD for any customer where a PEP is involved.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::customer-identity--collect-information--individuals-responsible-for-the-governan::0, rules2025::6-8::0, austrac-cdd-body-corporate::customer-identity::0, austrac-cdd-body-corporate::matters-you-must-establish::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::simplified-verification-for-certain-matt::0, austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0
- cited: austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0, austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::customer-identity::0, austrac-cdd-body-corporate::matters-you-must-establish::0


## Unsupported claims (17)

- **D11-domestic-pep-medium-risk** [rule]: Under S1, enhanced CDD for a domestic PEP only applies if the ML/TF risk is high. Since this customer's risk is medium, the condition for enhanced CDD is not met. _(cited: rules2025::6-23::0)_
- **D11-domestic-pep-medium-risk** [rule]: Under S5, simplified CDD is reserved for low-risk customers where no red flags or enhanced CDD triggers are present. A medium risk rating indicates the presence of moderate ML/TF risk factors, so simplification does not apply. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D11-domestic-pep-medium-risk** [conclusion]: Because the customer is a domestic PEP with medium risk (not high), enhanced CDD rules do not trigger. Because the risk is medium (not low) and there are moderate factors, simplified CDD rules do not apply. The result is standard CDD. _(cited: rules2025::6-23::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D15-foreign-branch-same-country-pep** [rule]: AUSTRAC guidance states that a foreign PEP is treated as a domestic PEP for enhanced CDD purposes if the service is provided via a foreign branch and the PEP status comes from their connection to that same foreign country. _(cited: austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0)_
- **D15-foreign-branch-same-country-pep** [rule]: When a customer is treated as a domestic PEP, enhanced CDD must be conducted regardless of the ML/TF risk rating. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--foreign-politically-exposed-persons::0)_
- **D15-foreign-branch-same-country-pep** [required_measures]: Conduct enhanced customer due diligence (CDD) for the politically exposed person. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--foreign-politically-exposed-persons::0)_
- **D15-foreign-branch-same-country-pep** [required_measures]: Obtain senior manager approval before commencing the business relationship. _(cited: austrac-pep::additional-obligations-for-peps--senior-manager-approval-for-peps::0, rules2025::5-5::0)_
- **D24-asic-registration-trap** [scenario_fact]: The customer has low ML/TF risk. _(cited: none)_
- **D24-asic-registration-trap** [rule]: Enhanced CDD is required only if specific triggers (such as high ML/TF risk or PEP status) are met. The scenario states the risk is low and no such triggers are present. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0)_
- **D24-asic-registration-trap** [conclusion]: Since the customer does not qualify for simplified CDD (not a listed company or government body) and does not trigger enhanced CDD, the tier is standard. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0)_
- **D24-asic-registration-trap** [required_measures]: Identify all beneficial owners of the customer unless a deeming provision applies (which it does not here). _(cited: austrac-cdd-body-corporate::identifying-beneficial-owners::0)_
- **D24-asic-registration-trap** [required_measures]: Collect and verify KYC information appropriate to the low ML/TF risk. _(cited: austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo::0)_
- **D33-low-risk-pensioner** [conclusion]: Since the scenario meets both conditions (low risk and no enhanced trigger), simplified CDD applies. _(cited: austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0)_
- **D33-low-risk-pensioner** [required_measures]: Collect KYC information appropriate to the low ML/TF risk (e.g., name, DOB) as per standard initial CDD requirements found in S1 and S2. _(cited: austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, rules2025::6-12::0)_
- **D49-embassy-ambassador-signatory** [required_measures]: Establish and/or review the source of funds and source of wealth for the foreign PEP. _(cited: austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0)_
- **D49-embassy-ambassador-signatory** [required_measures]: Review, update, and re-verify KYC information for the foreign PEP. _(cited: austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0)_
- **D51-assoc-domestic-pep-treasurer** [required_measures]: Apply enhanced CDD measures for the customer relationship. _(cited: austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0)_
