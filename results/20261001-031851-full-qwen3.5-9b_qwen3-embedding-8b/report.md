# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Gold file: `/Users/shreyasshekhar/Desktop/aml-cdd-assistant/data/gold/scenarios.jsonl`: 74 items (0 reviewed, 74 draft)
- Duration: 9884.2 s; finished 2026-09-30T20:03:35+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.867 | ≥ 0.8 | PASS |
| mandatory_ecdd_recall | 0.950 | ≥ 1.0 | **FAIL** |
| under_application_rate_max | 0.067 | ≤ 0.05 | **FAIL** |
| retrieval_recall_at_k | 0.726 | ≥ 0.8 | **FAIL** |
| citation_validity | 0.993 | ≥ 1.0 | **FAIL** |
| citation_precision | 0.414 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.673 | ≥ 0.8 | **FAIL** |
| unanswerable_abstain_rate | 0.778 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | 0.000 | ≤ 0.0 | PASS |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.867 |
| tier_accuracy_strict | 0.867 |
| mandatory_ecdd_recall | 0.950 |
| under_application_rate | 0.067 |
| over_application_rate | 0.067 |
| retrieval_recall_at_k | 0.726 |
| citation_validity | 0.993 |
| citation_precision | 0.414 |
| citation_recall | 0.708 |
| faithfulness | 0.673 |
| key_fact_recall | 0.906 |
| unanswerable_abstain_rate | 0.778 |
| false_abstain_rate | 0.000 |
| consistency_agreement | 1.000 |
| fairness_invariance | 1.000 |
| fairness_tier_flip_rate | 0.000 |
| walert_pct_unanswered_out_of_kb | 0.857 |
| walert_ndcg_at_5 | 0.540 |
| walert_rouge1_f1 | 0.264 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 83.320 |
| latency_p95_s | 120.230 |

## Tier determination (45 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 8 | 0 | 0 | 0 |
| **standard** | 2 | 12 | 3 | 0 |
| **enhanced** | 0 | 1 | 19 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 9 | 0.889 |
| government_body | 5 | 0.800 |
| individual | 10 | 0.800 |
| other | 1 | 1.000 |
| partnership | 3 | 1.000 |
| sole_trader | 6 | 1.000 |
| trust | 7 | 0.857 |
| unincorporated_association | 4 | 0.750 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 19 | 0.842 |
| low | 4 | 1.000 |
| medium | 22 | 0.864 |

## Consistency (6 groups)

| Group | Predictions |
|---|---|
| G-domestic-pep-medium | D11-domestic-pep-medium-risk: enhanced, D51-assoc-domestic-pep-treasurer: enhanced |
| G-foreign-pep | D01-foreign-pep-individual: enhanced, D02-foreign-pep-beneficial-owner: enhanced, D03-foreign-pep-trust-appointor: enhanced, D14-foreign-pep-family-member: enhanced, D41-unit-trust-foreign-pep: enhanced, D54-partnership-foreign-pep: enhanced |
| G-high-risk-jurisdiction | D04-high-risk-jurisdiction-company: enhanced, D35-government-body-high-risk-jurisdiction: enhanced, D42-trust-formed-high-risk: enhanced, D44-sole-trader-high-risk-country: enhanced |
| G-simplified-government | D28-commonwealth-department: simplified, D47-local-council: simplified, D48-state-owned-corporation: simplified |
| G-smr | D06-smr-continuing-sole-trader: enhanced, D36-low-risk-individual-smr: enhanced |
| G-standard-individual | D16-standard-individual: standard, D17-standard-individual-paraphrase: standard |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 0.857 | 7 |
| % unanswered, underspecified scenarios | 0.500 | 2 |
| NDCG@1 (known questions) | 0.734 | 32 |
| NDCG@3 (known questions) | 0.622 | 32 |
| NDCG@5 (known questions) | 0.623 | 32 |
| NDCG@1 (inferred questions) | 0.405 | 21 |
| NDCG@3 (inferred questions) | 0.414 | 21 |
| NDCG@5 (inferred questions) | 0.412 | 21 |
| NDCG@1 (all questions) | 0.604 | 53 |
| NDCG@3 (all questions) | 0.540 | 53 |
| NDCG@5 (all questions) | 0.540 | 53 |
| ROUGE-1 F1 vs reference answers | 0.264 | 53 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Counterfactual fairness (4 groups, 12 variants)

Each variant changes only a customer's name or country of birth (or, for foreign PEPs, which foreign country). The tier should never change.

- Invariance rate (groups with identical answers): **1.000**
- Tier flip rate (variants whose tier differs from the base): **0.000**
- Confidence flip rate: 0.500
- Variant accuracy (acceptable tier): 1.000

| Base | Predictions |
|---|---|
| D01-foreign-pep-individual | D01-foreign-pep-individual: enhanced, D01-cf-new-zealand: enhanced, D01-cf-united-kingdom: enhanced, D01-cf-india: enhanced |
| D16-standard-individual | D16-standard-individual: standard, D16-cf-aisha-rahman: standard, D16-cf-nguyen-thi-lan: standard, D16-cf-priya-sharma: standard |
| D17-standard-individual-paraphrase | D17-standard-individual-paraphrase: standard, D17-cf-born-india: standard, D17-cf-born-china: standard, D17-cf-born-greece: standard |
| D18-sole-trader | D18-sole-trader: standard, D18-cf-mohammed-hassan: standard, D18-cf-tran-van-minh: standard, D18-cf-kwame-mensah: standard |

## Failures

### D11-domestic-pep-medium-risk: expected standard, got enhanced

> A sitting member of an Australian state parliament opens a home loan offset account. Screening finds nothing adverse and our methodology rates her as medium risk.

- summary: The customer is a sitting member of an Australian state parliament, which makes them a domestic PEP under S6 and S8. Although their ML/TF risk is rated medium (S3), the presence of a PEP status triggers enhanced CDD requirements because they are not a 'low-profile' domestic PEP in this context, as per S3's distinction between low-profile and other PEPs. Additionally, S7 requires senior manager approval when dealing with domestic PEPs where risk is high or specific conditions apply, reinforcing the need for enhanced measures.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, rules2025::6-36::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0, austrac-pep::definition-of-domestic-peps::0, rules2025::5-5::1, rules2025::1-5::0
- cited: austrac-pep::definition-of-domestic-peps::0, rules2025::1-5::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, rules2025::5-5::1, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0
- gold note: Domestic PEP: enhanced CDD only if ML/TF risk is high. Over-applying ECDD here counts as an error.

### D15-foreign-branch-same-country-pep: expected standard, got enhanced

> Our bank's branch in Singapore opens an account for a Singaporean government minister. The relationship is managed entirely by that branch and we rate the customer as medium risk.

- summary: The scenario requires enhanced CDD because the customer is a foreign PEP connected to Singapore, and the service is provided through a permanent establishment in that same country.
- expected sections: rules2025::6-23
- retrieved: rules2025::5-5::1, rules2025::6-23::0, austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-pep::additional-obligations-for-peps--senior-manager-approval-for-peps::0, rules2025::5-5::0, rules2025::6-24::0, austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0, austrac-pep::additional-obligations-for-peps--additional-initial-cdd-obligations-for-p::0
- cited: austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0, rules2025::6-23::0, rules2025::6-24::0, austrac-pep::additional-obligations-for-peps--senior-manager-approval-for-peps::0, rules2025::5-5::0, austrac-pep::additional-obligations-for-peps--additional-initial-cdd-obligations-for-p::0
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): confirmed by rule 6-23(3). | earlier note: Rule 6-23 lets a foreign branch treat a PEP of its own country as a domestic PEP. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D23-smsf-trap: expected standard, got simplified

> The trustees of a self-managed superannuation fund registered with the ATO open an account. Risk is low. They ask us not to identify the fund's beneficial owners because the fund is regulated by the ATO.

- summary: The scenario allows for simplified CDD because the trust is low risk and regulated by the ATO, which fits the criteria for entities under regulatory oversight.
- expected sections: rules2025::6-18
- retrieved: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-trust::matters-you-must-establish::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, rules2025::6-7::0, rules2025::6-18::0, rules2025::6-7::1
- cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, rules2025::6-18::0, austrac-cdd-trust::matters-you-must-establish::0
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers a person 'subject to oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements'. The text does not expressly exclude ATO-regulated SMSFs; decide whether the ATO counts before relying on this item. | earlier note: ATO-registered SMSFs are excluded from the 'actively regulated' simplification in rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D24-asic-registration-trap: expected standard, got simplified

> A newly registered Australian proprietary company with low ML/TF risk asks us not to identify its beneficial owners because it is registered with ASIC.

- summary: The customer qualifies for simplified CDD because they are a low-risk body corporate registered with ASIC, which exempts them from identifying beneficial owners.
- expected sections: rules2025::6-18
- retrieved: austrac-risk-ratings::introduction::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::1, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1, austrac-high-risk-countries::introduction::0, austrac-cdd-overview::customer-due-diligence-overview::0
- cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::1, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers oversight 'through registration or licensing requirements'. Whether ordinary ASIC company registration counts is not settled by the text; decide before relying on this item. | earlier note: Ordinary ASIC registration is not active regulation for rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D49-embassy-ambassador-signatory: expected enhanced, got standard

> A foreign country's embassy in Canberra opens an account for its operating costs. The ambassador will be the main account signatory. The country is not on any FATF list and we would otherwise rate the customer as medium risk.

- summary: The scenario describes a foreign embassy account where the ambassador is the signatory. While this involves a PEP (the ambassador) and a foreign country, the sources do not mandate 'enhanced' CDD for these specific facts alone without a high risk rating or reliance on a third party in a non-compliant jurisdiction. Simplified CDD is not permitted because the customer is a PEP and the scenario does not explicitly confirm low ML/TF risk as a condition met by the entity's assessment (the prompt states 'medium' risk). Therefore, standard CDD applies.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-reliance::what-to-consider-before-entering-into-a--relying-on-a-third-party-in-a-foreign-co::0, austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high--example-identifying-high-ml-tf-risk-duri-2::0, austrac-reliance::regular-assessments-of-cdd-arrangements::1, austrac-foreign-pep-example::introduction::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, rules2025::6-11::0
- cited: austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high--example-identifying-high-ml-tf-risk-duri-2::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-foreign-pep-example::introduction::0
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-23(1) covers the customer, a beneficial owner, or a person on whose behalf the customer receives the service. It does not mention a person acting on the customer's behalf, such as a signatory. The expected tier may be wrong; check s 32 of the Act. | earlier note: Assumes an ambassador is a foreign PEP and that rule 6-23 covers persons acting on behalf of the customer. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D51-assoc-domestic-pep-treasurer: expected standard, got enhanced

> A residents' association (unincorporated) opens an account. Its treasurer, who will sign on the account, is a sitting member of the federal House of Representatives. No adverse media; medium risk.

- summary: The scenario requires enhanced CDD because the facts state the person is a 'foreign' politically exposed person (PEP). Under S2(1)(a), if a customer is a foreign PEP, the reporting entity must establish their source of funds and source of wealth. This requirement applies regardless of the ML/TF risk level for foreign PEPs, unlike domestic PEPs where high risk is required to trigger these specific measures. Therefore, the presence of a foreign PEP status triggers enhanced CDD measures.
- guardrails fired: foreign_pep (escalated: False)
- expected sections: rules2025::6-23, austrac-pep
- retrieved: rules2025::5-5::1, rules2025::6-23::0, austrac-pep::additional-obligations-for-peps--senior-manager-approval-for-peps::0, rules2025::5-5::0, austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-pep::additional-obligations-for-peps--additional-initial-cdd-obligations-for-p::0, rules2025::6-24::0, austrac-initial-cdd::what-you-must-establish-during-initial-c::0
- cited: rules2025::6-23::0, austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-pep::additional-obligations-for-peps--additional-initial-cdd-obligations-for-p::0, rules2025::5-5::0, austrac-pep::additional-obligations-for-peps--senior-manager-approval-for-peps::0

### D37-no-details: answered an unanswerable question

> A customer wants to open an account. Which CDD tier applies?

- summary: The scenario describes a customer opening an account without specifying any high-risk indicators (like PEP status) or low-risk conditions that would trigger simplified CDD. Therefore, standard initial CDD applies.
- expected sections: -
- retrieved: austrac-risk-ratings::step-2-identify-customer-risk-for-initia::0, austrac-cdd-overview::initial-customer-due-diligence::0, austrac-delayed-cdd::general-requirements-for-delayed-initial--interrupting-the-ordinary-course-of-busi::0, austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0, rules2025::6-39::0, austrac-initial-cdd::how-to-establish-matters-on-reasonable-g--initial-cdd-for-different-customer-types::0, austrac-delayed-cdd::opening-an-account-and-allowing-deposits::0, rules2025::6-13::0
- cited: austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0, austrac-risk-ratings::step-2-identify-customer-risk-for-initia::0, austrac-cdd-overview::initial-customer-due-diligence::0, austrac-delayed-cdd::opening-an-account-and-allowing-deposits::0

### U01-ttr-threshold: answered an unanswerable question

> What is the dollar threshold for a threshold transaction report and when must it be lodged?

- summary: The dollar threshold for a transaction report is $10,000, and reports must be lodged within 15 business days of the transaction occurring.
- expected sections: -
- retrieved: austrac-ongoing-cdd::what-you-must-monitor-for--responding-to-unusual-transactions-and-b::0, austrac-risk-ratings::step-3-identify-and-assess-customer-risk::0, rules2025::1-4::1, austrac-ecdd::enhanced-cdd-measures-you-can-apply--source-of-funds-and-source-of-wealth--example-unexplained-wealth::0, austrac-ongoing-cdd::ongoing-cdd-obligations-overview::0, rules2025::6-12::1, rules2025::6-35::1, austrac-ecdd::when-you-must-apply-enhanced-cdd--youre-required-to-submit-a-suspicious-ma::0
- cited: austrac-risk-ratings::step-3-identify-and-assess-customer-risk::0, rules2025::6-12::1, austrac-ongoing-cdd::what-you-must-monitor-for--responding-to-unusual-transactions-and-b::0
- gold note: Reporting obligations are outside the CDD knowledge base; a correct answer from memory still fails.


## Unsupported claims (164)

- **D01-foreign-pep-individual**: Maria is identified as a foreign politically exposed person (PEP) because she is a serving deputy minister of finance in a foreign country. _(cited: rules2025::6-23::0)_
- **D01-foreign-pep-individual**: The scenario confirms Maria's status as a foreign PEP but does not state that her ML/TF risk is high. Therefore, the 'high risk' conditions in S2 and S4 for senior manager approval do not apply. _(cited: rules2025::6-23::0, rules2025::5-5::1)_
- **D01-foreign-pep-individual**: Because the status of foreign PEP triggers specific CDD matters under S3, the tier is 'enhanced' regardless of the medium risk rating. _(cited: rules2025::6-23::0)_
- **D02-foreign-pep-beneficial-owner**: Additionally, S8 mandates specific enhanced CDD measures regarding the source of wealth and funds for this customer type. _(cited: rules2025::6-23::0)_
- **D03-foreign-pep-trust-appointor**: The customer is an Australian discretionary trust with a corporate trustee. _(cited: austrac-cdd-trust::matters-you-must-establish::0, rules2025::6-3::1)_
- **D03-foreign-pep-trust-appointor**: The appointor of the trust is a serving judge of a foreign country's supreme court. _(cited: none)_
- **D03-foreign-pep-trust-appointor**: A serving judge of a supreme court is a PEP. Under AUSTRAC guidance, if a customer or their controller is a PEP, enhanced CDD applies regardless of the trust's low risk profile. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0, austrac-cdd-trust::matters-you-must-establish::0)_
- **D03-foreign-pep-trust-appointor**: Collect KYC information on the identity of the appointor (the serving judge). _(cited: rules2025::6-3::1)_
- **D03-foreign-pep-trust-appointor**: Verify the identity of the appointor using enhanced procedures appropriate for a PEP. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0, austrac-cdd-trust::matters-you-must-establish::0)_
- **D03-foreign-pep-trust-appointor**: Assess the money laundering and terrorist financing (ML/TF) risk associated with the PEP status. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D06-smr-continuing-sole-trader**: The facts confirm an SMR was lodged for this customer and management decided to keep providing services. _(cited: none)_
- **D07-nested-services**: S1 specifies that for nested services relationships, the reporting entity must establish specific matters on reasonable grounds before providing the service. _(cited: rules2025::6-25::1)_
- **D10-domestic-pep-high-risk**: The scenario explicitly rates the customer's ML/TF risk as 'high' due to their status as a sitting parliament member (a Political Exposed Person) and media links to corruption. _(cited: austrac-risk-ratings::introduction::0)_
- **D10-domestic-pep-high-risk**: Because the risk is high, simplified CDD cannot be used, and standard CDD is insufficient per S1 and S7. _(cited: austrac-ecdd::introduction::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0)_
- **D13-high-risk-rating-sole-trader**: The scenario explicitly states the customer has a 'high' ML/TF risk rating. Source S6 requires applying enhanced CDD measures for customers with medium or high risk. _(cited: austrac-cdd-sole-traders::matters-you-must-establish--additional-requirements::0)_
- **D13-high-risk-rating-sole-trader**: Obtain the reason for the cash deposits to determine if they align with the stated business activity (car wash). _(cited: austrac-ecdd::enhanced-cdd-measures-you-can-apply::0, austrac-cdd-sole-traders::nature-and-purpose-of-the-business-relat--example-an-accountant-and-sole-trader-cu::0)_
- **D14-foreign-pep-family-member**: Because the customer is either a family member or a close associate of a foreign PEP, S1 implies this status triggers enhanced CDD. The method instructions state that if an enhanced CDD trigger applies, the tier is 'enhanced' even if other conditions for simplified CDD might exist. _(cited: austrac-pep::definition-of-foreign-peps::0)_
- **D14-foreign-pep-family-member**: Collect additional KYC information about the customer's source of funds and source of wealth, as required for high-risk customers under S8. _(cited: austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::1)_
- **D14-foreign-pep-family-member**: Verify all collected KYC information using independent and reliable data, with a higher degree of scrutiny than for low-risk customers, per S7. _(cited: austrac-initial-cdd::collecting-and-verifying-kyc-information--verifying-kyc-information-using-independ::0)_
- **D14-foreign-pep-family-member**: Conduct enhanced CDD to identify the customer's ML/TF risk factors associated with their connection to the foreign PEP, as outlined in S3 and S6. _(cited: austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, austrac-initial-cdd::collecting-and-verifying-kyc-information::0)_
- **D34-listed-company-unusual**: Obtain the reason for these specific transactions or services to confirm if there is a lawful purpose. _(cited: austrac-ecdd::enhanced-cdd-measures-you-can-apply::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D36-low-risk-individual-smr**: Source S6 explicitly states that enhanced CDD is required if you must submit an SMR and intend to continue providing designated services. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--youre-required-to-submit-a-suspicious-ma::0)_
- **D36-low-risk-individual-smr**: Since the scenario confirms the account will be kept open (continuing services), the condition for enhanced CDD in S6 is met. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--youre-required-to-submit-a-suspicious-ma::0)_
- **D36-low-risk-individual-smr**: Conduct enhanced customer due diligence measures immediately. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--youre-required-to-submit-a-suspicious-ma::0)_
- **D11-domestic-pep-medium-risk**: The customer is a sitting member of a state parliament, which explicitly defines them as a domestic PEP according to S6 and S8. _(cited: austrac-pep::definition-of-domestic-peps::0, rules2025::1-5::0)_
