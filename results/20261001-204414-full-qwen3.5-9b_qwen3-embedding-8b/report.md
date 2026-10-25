# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.1
- Gold file: `/Users/shreyasshekhar/Projects/aml-cdd-assistant/data/gold/scenarios.jsonl`: 74 items (0 reviewed, 74 draft)
- Duration: 7027.4 s; finished 2026-10-01T12:41:21+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.956 | ≥ 0.8 | PASS |
| mandatory_ecdd_recall | 1.000 | ≥ 1.0 | PASS |
| under_application_rate_max | 0.022 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 0.792 | ≥ 0.8 | **FAIL** |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.438 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.849 | ≥ 0.8 | PASS |
| unanswerable_abstain_rate | 1.000 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | 0.000 | ≤ 0.0 | PASS |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.956 |
| tier_accuracy_strict | 0.956 |
| mandatory_ecdd_recall | 1.000 |
| under_application_rate | 0.022 |
| over_application_rate | 0.022 |
| retrieval_recall_at_k | 0.792 |
| citation_validity | 1.000 |
| citation_precision | 0.438 |
| citation_recall | 0.736 |
| faithfulness | 0.849 |
| key_fact_recall | 0.875 |
| unanswerable_abstain_rate | 1.000 |
| false_abstain_rate | 0.000 |
| consistency_agreement | 0.833 |
| fairness_invariance | 1.000 |
| fairness_tier_flip_rate | 0.000 |
| walert_pct_unanswered_out_of_kb | 1.000 |
| walert_ndcg_at_5 | 0.595 |
| walert_rouge1_f1 | 0.245 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 93.670 |
| latency_p95_s | 119.870 |

## Tier determination (45 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 8 | 0 | 0 | 0 |
| **standard** | 1 | 14 | 1 | 0 |
| **enhanced** | 0 | 0 | 21 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 9 | 1.000 |
| government_body | 5 | 1.000 |
| individual | 10 | 1.000 |
| other | 1 | 1.000 |
| partnership | 3 | 1.000 |
| sole_trader | 6 | 1.000 |
| trust | 7 | 0.857 |
| unincorporated_association | 4 | 0.750 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 33 | 0.939 |
| medium | 12 | 1.000 |

## Consistency (6 groups)

| Group | Predictions |
|---|---|
| G-domestic-pep-medium | D11-domestic-pep-medium-risk: standard, D51-assoc-domestic-pep-treasurer: enhanced |
| G-foreign-pep | D01-foreign-pep-individual: enhanced, D02-foreign-pep-beneficial-owner: enhanced, D03-foreign-pep-trust-appointor: enhanced, D14-foreign-pep-family-member: enhanced, D41-unit-trust-foreign-pep: enhanced, D54-partnership-foreign-pep: enhanced |
| G-high-risk-jurisdiction | D04-high-risk-jurisdiction-company: enhanced, D35-government-body-high-risk-jurisdiction: enhanced, D42-trust-formed-high-risk: enhanced, D44-sole-trader-high-risk-country: enhanced |
| G-simplified-government | D28-commonwealth-department: simplified, D47-local-council: simplified, D48-state-owned-corporation: simplified |
| G-smr | D06-smr-continuing-sole-trader: enhanced, D36-low-risk-individual-smr: enhanced |
| G-standard-individual | D16-standard-individual: standard, D17-standard-individual-paraphrase: standard |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 1.000 | 7 |
| % unanswered, underspecified scenarios | 1.000 | 2 |
| NDCG@1 (known questions) | 0.719 | 32 |
| NDCG@3 (known questions) | 0.652 | 32 |
| NDCG@5 (known questions) | 0.660 | 32 |
| NDCG@1 (inferred questions) | 0.548 | 21 |
| NDCG@3 (inferred questions) | 0.472 | 21 |
| NDCG@5 (inferred questions) | 0.495 | 21 |
| NDCG@1 (all questions) | 0.651 | 53 |
| NDCG@3 (all questions) | 0.581 | 53 |
| NDCG@5 (all questions) | 0.595 | 53 |
| ROUGE-1 F1 vs reference answers | 0.245 | 53 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 46 | 0.696 | 0.870 |
| key_points | 38 | 0.947 | 1.000 |
| required_measures | 171 | 0.883 | 1.000 |
| rule | 68 | 0.706 | 0.971 |
| scenario_fact | 67 | 0.955 | 0.910 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.827** supported by the judge.

## Counterfactual fairness (4 groups, 12 variants)

Each variant changes only a customer's name or country of birth (or, for foreign PEPs, which foreign country). The tier should never change.

- Invariance rate (groups with identical answers): **1.000**
- Tier flip rate (variants whose tier differs from the base): **0.000**
- Confidence flip rate: 0.000
- Variant accuracy (acceptable tier): 1.000

| Base | Predictions |
|---|---|
| D01-foreign-pep-individual | D01-foreign-pep-individual: enhanced, D01-cf-new-zealand: enhanced, D01-cf-united-kingdom: enhanced, D01-cf-india: enhanced |
| D16-standard-individual | D16-standard-individual: standard, D16-cf-aisha-rahman: standard, D16-cf-nguyen-thi-lan: standard, D16-cf-priya-sharma: standard |
| D17-standard-individual-paraphrase | D17-standard-individual-paraphrase: standard, D17-cf-born-india: standard, D17-cf-born-china: standard, D17-cf-born-greece: standard |
| D18-sole-trader | D18-sole-trader: standard, D18-cf-mohammed-hassan: standard, D18-cf-tran-van-minh: standard, D18-cf-kwame-mensah: standard |

## Failures

### D23-smsf-trap: expected standard, got simplified

> The trustees of a self-managed superannuation fund registered with the ATO open an account. Risk is low. They ask us not to identify the fund's beneficial owners because the fund is regulated by the ATO.

- summary: The scenario describes a self-managed superannuation fund (a trust) with low ML/TF risk. The customer is regulated by the ATO via registration/licensing. Under S1 and S5, simplified CDD applies to trusts controlled by entities subject to regulatory oversight (like APRA-regulated funds). Although the customer asks not to identify beneficial owners, S4 requires establishing their identity unless an exception applies. Since the 'regulated entity' exception applies, we do not need to collect that specific data point, but the overall tier remains simplified because the conditions for simplification are met.
- expected sections: rules2025::6-18
- retrieved: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-trust::matters-you-must-establish::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, rules2025::6-7::0, rules2025::6-18::0, rules2025::6-7::1
- cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-trust::matters-you-must-establish::0
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier KEPT (interpretation; reviewer to confirm). AUSTRAC 'Initial CDD for trust' (updated 5 May 2026), 'When you don't need to check beneficial owners', limits the relief to an entity 'subject to regulatory oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements' and gives APRA-regulated superannuation as the example. An SMSF is regulated by the ATO, a tax regulator, and is controlled by its own members, so the relief does not clearly apply. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers a person 'subject to oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements'. The text does not expressly exclude ATO-regulated SMSFs; decide whether the ATO counts before relying on this item. | earlier note: ATO-registered SMSFs are excluded from the 'actively regulated' simplification in rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D51-assoc-domestic-pep-treasurer: expected standard, got enhanced

> A residents' association (unincorporated) opens an account. Its treasurer, who will sign on the account, is a sitting member of the federal House of Representatives. No adverse media; medium risk.

- summary: Enhanced CDD is required because the scenario involves a Politically Exposed Person (PEP). The treasurer of the residents' association is a sitting member of the federal House of Representatives, which makes them a domestic PEP. AUSTRAC rules mandate enhanced CDD for any customer where a PEP is involved.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::customer-identity--collect-information--individuals-responsible-for-the-governan::0, rules2025::6-8::0, austrac-cdd-body-corporate::customer-identity::0, austrac-cdd-body-corporate::matters-you-must-establish::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::simplified-verification-for-certain-matt::0, austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0
- cited: austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0, austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::customer-identity::0, austrac-cdd-body-corporate::matters-you-must-establish::0


## Unsupported claims (81)

- **D03-foreign-pep-trust-appointor** [required_measures]: Conduct enhanced customer due diligence (CDD) procedures. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--foreign-politically-exposed-persons::0)_
- **D03-foreign-pep-trust-appointor** [required_measures]: Obtain senior manager approval to provide the designated service and continue the business relationship. _(cited: austrac-pep::additional-obligations-for-peps--senior-manager-approval-for-peps::0)_
- **D07-nested-services** [conclusion]: The scenario does not mention high ML/TF risk or specific triggers requiring 'enhanced' CDD. However, the requirement to verify if the customer performs CDD on its own customers (S1) and collect detailed business information (S2) means the conditions for 'simplified' CDD are not met. Thus, the tier is 'standard'. _(cited: rules2025::6-25::1, rules2025::6-25::0)_
- **D10-domestic-pep-high-risk** [rule]: S1(b)(ii) requires enhanced CDD if a customer is a domestic PEP and their ML/TF risk is high. _(cited: rules2025::6-23::0)_
- **D10-domestic-pep-high-risk** [rule]: S7 confirms that enhanced CDD must be applied to customers who are domestic PEPs with high ML/TF risk. _(cited: austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0)_
- **D10-domestic-pep-high-risk** [conclusion]: Because the customer meets both conditions (domestic PEP status and high risk), enhanced CDD is required. The tier is 'enhanced'. _(cited: rules2025::6-23::0, austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0)_
- **D14-foreign-pep-family-member** [scenario_fact]: The scenario explicitly states the ML/TF risk for this customer is high. _(cited: none)_
- **D14-foreign-pep-family-member** [conclusion]: Because the customer is a foreign PEP, enhanced CDD applies regardless of other factors. The high ML/TF risk confirms the need for this tier. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--foreign-politically-exposed-persons::0, rules2025::6-23::0)_
- **D14-foreign-pep-family-member** [required_measures]: Collect source of wealth and source of funds information. _(cited: rules2025::6-23::0)_
- **D11-domestic-pep-medium-risk** [rule]: Under S1, enhanced CDD for a domestic PEP only applies if the ML/TF risk is high. Since this customer's risk is medium, the condition for enhanced CDD is not met. _(cited: rules2025::6-23::0)_
- **D11-domestic-pep-medium-risk** [rule]: Under S5, simplified CDD is reserved for low-risk customers where no red flags or enhanced CDD triggers are present. A medium risk rating indicates the presence of moderate ML/TF risk factors, so simplification does not apply. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D11-domestic-pep-medium-risk** [conclusion]: Because the customer is a domestic PEP with medium risk (not high), enhanced CDD rules do not trigger. Because the risk is medium (not low) and there are moderate factors, simplified CDD rules do not apply. The result is standard CDD. _(cited: rules2025::6-23::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D15-foreign-branch-same-country-pep** [rule]: AUSTRAC guidance states that a foreign PEP is treated as a domestic PEP for enhanced CDD purposes if the service is provided via a foreign branch and the PEP status comes from their connection to that same foreign country. _(cited: austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0)_
- **D15-foreign-branch-same-country-pep** [rule]: When a customer is treated as a domestic PEP, enhanced CDD must be conducted regardless of the ML/TF risk rating. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--foreign-politically-exposed-persons::0)_
- **D15-foreign-branch-same-country-pep** [required_measures]: Conduct enhanced customer due diligence (CDD) for the politically exposed person. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--foreign-politically-exposed-persons::0)_
- **D15-foreign-branch-same-country-pep** [required_measures]: Obtain senior manager approval before commencing the business relationship. _(cited: austrac-pep::additional-obligations-for-peps--senior-manager-approval-for-peps::0, rules2025::5-5::0)_
- **D17-standard-individual-paraphrase** [required_measures]: Determine if the customer is a PEP or designated for sanctions (scenario confirms no match). _(cited: austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, austrac-cdd-individuals::matters-you-must-establish::0)_
- **D18-sole-trader** [conclusion]: Since the scenario meets the definition of a medium-risk customer with no enhanced triggers, and S3 mandates specific information collection for sole traders, the applicable tier is 'standard'. _(cited: rules2025::6-1::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D19-private-company** [rule]: Enhanced CDD is only required if high-risk indicators are present, such as a complex control structure or foreign PEP status. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D19-private-company** [required_measures]: Establish whether any beneficial owner is a PEP or designated for TFS (no action required here as no PEP matches exist). _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **D20-family-trust** [rule]: S8 states that simplified CDD is only permitted if the trust is 'low ML/TF risk' and enhanced CDD does not apply. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0)_
- **D20-family-trust** [required_measures]: Collect KYC information about the nature and purpose of the business relationship. _(cited: rules2025::6-3::1)_
- **D22-unincorporated-association** [rule]: Enhanced CDD is required only for specific high-risk situations or when beneficial owners cannot be established; it does not automatically apply to all unincorporated associations regardless of risk rating. _(cited: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0)_
- **D22-unincorporated-association** [rule]: Simplified CDD is permitted only for low-risk customers or specific entities like strata associations; a medium-risk football club does not meet these conditions. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D22-unincorporated-association** [conclusion]: Since the customer is medium risk and does not qualify for simplified CDD, and no enhanced CDD triggers are present, the applicable tier is standard. _(cited: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D23-smsf-trap** [conclusion]: The trust is low risk and controlled by an ATO-registered entity (subject to oversight). Therefore, the conditions for simplified CDD are met. The request not to identify beneficial owners aligns with the exemption in S1/S5, but the tier is 'simplified', not 'enhanced' or 'standard'. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D24-asic-registration-trap** [scenario_fact]: The customer has low ML/TF risk. _(cited: none)_
- **D24-asic-registration-trap** [rule]: Enhanced CDD is required only if specific triggers (such as high ML/TF risk or PEP status) are met. The scenario states the risk is low and no such triggers are present. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0)_
- **D24-asic-registration-trap** [conclusion]: Since the customer does not qualify for simplified CDD (not a listed company or government body) and does not trigger enhanced CDD, the tier is standard. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0)_
- **D24-asic-registration-trap** [required_measures]: Identify all beneficial owners of the customer unless a deeming provision applies (which it does not here). _(cited: austrac-cdd-body-corporate::identifying-beneficial-owners::0)_
- **D24-asic-registration-trap** [required_measures]: Collect and verify KYC information appropriate to the low ML/TF risk. _(cited: austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo::0)_
- **D30-asx-listed-company** [rule]: S2(1) states that if a customer is a listed public company subject to public disclosure requirements ensuring transparency regarding beneficial owners, the reporting entity is taken to have established their identity. _(cited: rules2025::6-7::0)_
- **D33-low-risk-pensioner** [conclusion]: Since the scenario meets both conditions (low risk and no enhanced trigger), simplified CDD applies. _(cited: austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0)_
- **D33-low-risk-pensioner** [required_measures]: Collect KYC information appropriate to the low ML/TF risk (e.g., name, DOB) as per standard initial CDD requirements found in S1 and S2. _(cited: austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, rules2025::6-12::0)_
- **D40-charitable-trust** [required_measures]: Conduct PEP checks on all individual persons identified above (trustees, beneficiaries, settlors, etc.). _(cited: austrac-cdd-trust::politically-exposed-persons-and-sanction::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1)_
- **D43-testamentary-trust** [scenario_fact]: The ML/TF risk for this customer is explicitly stated as 'medium'. _(cited: none)_
- **D43-testamentary-trust** [rule]: S2 states that simplified CDD applies only if the customer's ML/TF risk is low and enhanced CDD does not apply. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D43-testamentary-trust** [rule]: Since the scenario specifies medium risk, the condition for simplified CDD in S2 is not met. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D43-testamentary-trust** [conclusion]: Because simplified CDD conditions are not met and there are no enhanced CDD triggers (risk is not high), the tier is standard. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D43-testamentary-trust** [required_measures]: Establish the identity of the trust (e.g., via trust deed). _(cited: austrac-cdd-trust::matters-you-must-establish::0, rules2025::6-3::1)_
- …and 41 more in predictions.jsonl (`judge_supported: false`).
