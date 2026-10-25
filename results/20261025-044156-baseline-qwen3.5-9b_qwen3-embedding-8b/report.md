# Evaluation report: preset `baseline`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.3
- Gold file: `/Users/shreyasshekhar/Projects/aml-cdd-assistant/data/gold/scenarios.jsonl`: 74 items (0 reviewed, 74 draft)
- Duration: 9430.2 s (answering 5974.7 s, then grading 3455.4 s); finished 2026-10-24T20:19:07+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.911 | ≥ 0.8 | PASS |
| mandatory_ecdd_recall | 0.905 | ≥ 1.0 | **FAIL** |
| under_application_rate_max | 0.044 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 0.670 | ≥ 0.8 | **FAIL** |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.383 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.846 | ≥ 0.8 | PASS |
| unanswerable_abstain_rate | 0.778 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 0.019 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | 0.000 | ≤ 0.0 | PASS |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.911 |
| tier_accuracy_strict | 0.911 |
| mandatory_ecdd_recall | 0.905 |
| under_application_rate | 0.044 |
| over_application_rate | 0.022 |
| retrieval_recall_at_k | 0.670 |
| citation_validity | 1.000 |
| citation_precision | 0.383 |
| citation_recall | 0.606 |
| faithfulness | 0.846 |
| key_fact_recall | 0.938 |
| unanswerable_abstain_rate | 0.778 |
| false_abstain_rate | 0.019 |
| consistency_agreement | 0.833 |
| fairness_invariance | 1.000 |
| fairness_tier_flip_rate | 0.000 |
| walert_pct_unanswered_out_of_kb | 0.714 |
| walert_ndcg_at_5 | 0.439 |
| walert_rouge1_f1 | 0.236 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 83.650 |
| latency_p95_s | 101.540 |

## Answer checks

Citation validity means each citation points to a passage that was really retrieved. Whether that passage supports the claim is measured separately (faithfulness, below).

- Answers with a point that cites nothing: 0
- Answers that call a fact the scenario rules out unknown: 0

## Tier determination (45 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 8 | 0 | 0 | 0 |
| **standard** | 1 | 14 | 1 | 0 |
| **enhanced** | 0 | 1 | 19 | 1 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 9 | 0.889 |
| government_body | 5 | 0.800 |
| individual | 10 | 1.000 |
| other | 1 | 1.000 |
| partnership | 3 | 1.000 |
| sole_trader | 6 | 1.000 |
| trust | 7 | 0.857 |
| unincorporated_association | 4 | 0.750 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 34 | 0.912 |
| low | 1 | 0.000 |
| medium | 10 | 1.000 |

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
| % unanswered, out-of-knowledge-base questions | 0.714 | 7 |
| % unanswered, underspecified scenarios | 1.000 | 2 |
| NDCG@1 (known questions) | 0.438 | 32 |
| NDCG@3 (known questions) | 0.468 | 32 |
| NDCG@5 (known questions) | 0.498 | 32 |
| NDCG@1 (inferred questions) | 0.333 | 21 |
| NDCG@3 (inferred questions) | 0.292 | 21 |
| NDCG@5 (inferred questions) | 0.349 | 21 |
| NDCG@1 (all questions) | 0.396 | 53 |
| NDCG@3 (all questions) | 0.398 | 53 |
| NDCG@5 (all questions) | 0.439 | 53 |
| ROUGE-1 F1 vs reference answers | 0.236 | 53 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 45 | 0.622 | 0.911 |
| key_points | 50 | 0.900 | 1.000 |
| required_measures | 166 | 0.861 | 0.982 |
| rule | 68 | 0.824 | 1.000 |
| scenario_fact | 61 | 0.951 | 0.951 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.827** supported by the judge.

## Counterfactual fairness (4 groups, 12 variants)

Each variant changes only a customer's name or country of birth (or, for foreign PEPs, which foreign country). The tier should never change.

- Invariance rate (groups with identical answers): **1.000**
- Tier flip rate (variants whose tier differs from the base): **0.000**
- Confidence flip rate: 0.083
- Variant accuracy (acceptable tier): 1.000

| Base | Predictions |
|---|---|
| D01-foreign-pep-individual | D01-foreign-pep-individual: enhanced, D01-cf-new-zealand: enhanced, D01-cf-united-kingdom: enhanced, D01-cf-india: enhanced |
| D16-standard-individual | D16-standard-individual: standard, D16-cf-aisha-rahman: standard, D16-cf-nguyen-thi-lan: standard, D16-cf-priya-sharma: standard |
| D17-standard-individual-paraphrase | D17-standard-individual-paraphrase: standard, D17-cf-born-india: standard, D17-cf-born-china: standard, D17-cf-born-greece: standard |
| D18-sole-trader | D18-sole-trader: standard, D18-cf-mohammed-hassan: standard, D18-cf-tran-van-minh: standard, D18-cf-kwame-mensah: standard |

## Failures

### D07-nested-services: expected enhanced, got insufficient_information

> An overseas money remitter asks our bank to provide it with accounts through which its own customers' payments into Australia will be processed.

- summary: The scenario describes an overseas money remitter asking for accounts to process payments into Australia. However, it does not state whether this overseas entity is a 'reliable third party' under the Act (as defined in S1), nor does it confirm if the entity has previously provided services to these specific customers in their home country (required for simplified CDD under S4/S5). Without knowing if prior foreign compliance exists or if the entity qualifies as a reliable third party, we cannot apply simplified rules. We also do not know if the customer is an individual or company, nor if any enhanced triggers (like high ML/TF risk) are present.
- expected sections: rules2025::6-25
- retrieved: austrac-reliance::what-to-consider-before-entering-into-a--relying-on-a-third-party-in-a-foreign-co::0, austrac-transitioning::you-complied-with-relevant-obligations-i::0, rules2025::6-12::1, rules2025::6-11::0, austrac-transitioning::you-complied-with-relevant-obligations-i--previous-compliance-in-a-foreign-country::0, rules2025::6-13::0, austrac-transitioning::you-complied-with-relevant-obligations-i--designated-service-provided-in-another-c::0, rules2025::1-4::3
- cited: rules2025::6-11::0, austrac-reliance::what-to-consider-before-entering-into-a--relying-on-a-third-party-in-a-foreign-co::0

### D23-smsf-trap: expected standard, got simplified

> The trustees of a self-managed superannuation fund registered with the ATO open an account. Risk is low. They ask us not to identify the fund's beneficial owners because the fund is regulated by the ATO.

- summary: The scenario describes a self-managed superannuation fund (SMF) which is low ML/TF risk and regulated by the ATO. The customer requests not to identify beneficial owners based on this regulation. Under AUSTRAC guidance, an entity subject to regulatory oversight by a prudential or investor protection regulator through registration/licensing qualifies for simplified CDD where beneficial owner identification is not required. SMFs are registered with the ATO (an investor protection regulator). Therefore, the condition for simplified CDD is met.
- expected sections: rules2025::6-18
- retrieved: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, rules2025::6-18::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, rules2025::6-7::0, rules2025::6-7::1, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0
- cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier KEPT (interpretation; reviewer to confirm). AUSTRAC 'Initial CDD for trust' (updated 5 May 2026), 'When you don't need to check beneficial owners', limits the relief to an entity 'subject to regulatory oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements' and gives APRA-regulated superannuation as the example. An SMSF is regulated by the ATO, a tax regulator, and is controlled by its own members, so the relief does not clearly apply. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers a person 'subject to oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements'. The text does not expressly exclude ATO-regulated SMSFs; decide whether the ATO counts before relying on this item. | earlier note: ATO-registered SMSFs are excluded from the 'actively regulated' simplification in rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D49-embassy-ambassador-signatory: expected enhanced, got standard

> A foreign country's embassy in Canberra opens an account for its operating costs. The ambassador will be the main account signatory. The country is not on any FATF list and we would otherwise rate the customer as medium risk.

- summary: The customer is a foreign embassy (medium risk) with a foreign PEP signatory. The scenario states the ML/TF risk is medium, not high. Enhanced CDD triggers require high risk or specific FATF-listed jurisdictions. Simplified CDD requires low risk and no triggers. Therefore, standard CDD applies.
- expected sections: austrac-ecdd, austrac-pep
- retrieved: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, rules2025::5-5::1, rules2025::6-23::0, austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, rules2025::5-5::0, austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-reliance::what-to-consider-before-entering-into-a--relying-on-a-third-party-in-a-foreign-co::0
- cited: rules2025::6-23::0, austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier CONFIRMED. AUSTRAC 'Enhanced customer due diligence' (updated 15 Jul 2026), 'Foreign politically exposed persons', and AUSTRAC 'Politically exposed persons' (updated 29 Jul 2026), 'Enhanced CDD obligations', both require enhanced CDD when 'any person acting on behalf of the customer' is a foreign PEP; the PEP definition includes ambassadors. Reference answer corrected: rules 6-23 and 5-5 (source of wealth/funds, senior manager approval) cover the customer, beneficial owners and persons on whose behalf the service is received, not persons acting on the customer's behalf. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-23(1) covers the customer, a beneficial owner, or a person on whose behalf the customer receives the service. It does not mention a person acting on the customer's behalf, such as a signatory. The expected tier may be wrong; check s 32 of the Act. | earlier note: Assumes an ambassador is a foreign PEP and that rule 6-23 covers persons acting on behalf of the customer. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D51-assoc-domestic-pep-treasurer: expected standard, got enhanced

> A residents' association (unincorporated) opens an account. Its treasurer, who will sign on the account, is a sitting member of the federal House of Representatives. No adverse media; medium risk.

- summary: The scenario describes a customer with medium ML/TF risk and a PEP acting on their behalf. The sources require enhanced CDD when these conditions exist.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::matters-you-must-establish::0, austrac-cdd-body-corporate::politically-exposed-persons-and-sanction::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::simplified-verification-for-certain-matt::0
- cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::politically-exposed-persons-and-sanction::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::matters-you-must-establish::0

### U01-ttr-threshold: answered an unanswerable question

> What is the dollar threshold for a threshold transaction report and when must it be lodged?

- summary: The dollar threshold for a transaction report is $10,000, and transactions appearing to be structured below this amount must also be monitored as unusual behaviour.
- expected sections: -
- retrieved: austrac-ongoing-cdd::what-you-must-monitor-for--responding-to-unusual-transactions-and-b::0, rules2025::6-12::1, rules2025::6-35::1, rules2025::6-32::1, austrac-ecdd::enhanced-cdd-measures-you-can-apply--source-of-funds-and-source-of-wealth--example-unexplained-wealth::0, austrac-risk-ratings::step-3-identify-and-assess-customer-risk::0, rules2025::6-35::0, rules2025::6-32::0
- cited: austrac-ongoing-cdd::what-you-must-monitor-for--responding-to-unusual-transactions-and-b::0, austrac-risk-ratings::step-3-identify-and-assess-customer-risk::0
- gold note: Reporting obligations are outside the CDD knowledge base; a correct answer from memory still fails.

### U07-enrolment: answered an unanswerable question

> How do we enrol our accounting practice with AUSTRAC as a newly regulated tranche 2 business?

- summary: To enrol as a new regulated business, you must collect specific registrable details and submit them to AUSTRAC before providing designated services.
- expected sections: -
- retrieved: rules2025::1-7::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::1, rules2025::6-1::0, austrac-cdd-trust::customer-identity--collect-information--unique-identifier-for-the-trust-if-any::0, austrac-transitioning::you-conducted-applicable-customer-identi::0, rules2025::6-12::1, rules2025::6-12::0
- cited: rules2025::1-7::0


## Unsupported claims (90)

- **D01-foreign-pep-individual** [required_measures]: Establish source of wealth and source of funds for Maria. _(cited: rules2025::6-23::0)_
- **D02-foreign-pep-beneficial-owner** [scenario_fact]: The customer is Harbourline Imports Pty Ltd, an Australian private company with two directors. _(cited: none)_
- **D02-foreign-pep-beneficial-owner** [conclusion]: Since a beneficial owner is an FPEP, the scenario meets the condition for enhanced CDD. The tier is 'enhanced'. _(cited: rules2025::5-5::0, rules2025::6-23::0)_
- **D03-foreign-pep-trust-appointor** [required_measures]: Establish the identity of the appointor (the serving judge). _(cited: rules2025::6-3::0, rules2025::6-6::0, rules2025::6-3::1, austrac-cdd-trust::politically-exposed-persons-and-sanction::0)_
- **D07-nested-services** [rule]: Simplified CDD applies only if the reporting entity has previously provided a service to the customer in a foreign country where FATF-compliant laws applied, and KYC information is held or accessible (S4). _(cited: rules2025::6-11::0)_
- **D07-nested-services** [conclusion]: Since the scenario does not confirm prior service provision in a foreign country or that the overseas remitter is a 'reliable third party' under the Act, we cannot apply simplified CDD. We also lack information on whether enhanced triggers apply. Therefore, insufficient information exists to determine the tier. _(cited: rules2025::6-11::0, austrac-reliance::what-to-consider-before-entering-into-a--relying-on-a-third-party-in-a-foreign-co::0)_
- **D14-foreign-pep-family-member** [conclusion]: Because the son of a head of government qualifies as a foreign PEP, the scenario triggers the requirement for enhanced CDD. _(cited: austrac-pep::definition-of-foreign-peps::0, austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0)_
- **D11-domestic-pep-medium-risk** [rule]: Simplified CDD applies only to low-risk customers where there are no medium- or high-risk factors or enhanced CDD triggers present. A domestic PEP is explicitly listed as a medium-risk factor, meaning the customer does not meet the conditions for simplified CDD. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen::0)_
- **D11-domestic-pep-medium-risk** [rule]: Enhanced CDD is mandatory only when the ML/TF risk of the customer is high. The scenario states the customer is rated as medium risk, so enhanced CDD is not required. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0)_
- **D11-domestic-pep-medium-risk** [conclusion]: Since the customer is a PEP (preventing simplification) but has a medium risk rating (preventing enhancement), the appropriate tier is standard CDD. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0)_
- **D11-domestic-pep-medium-risk** [required_measures]: Monitor for unusual behaviour and risk factors consistent with a medium-risk rating _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0)_
- **D15-foreign-branch-same-country-pep** [conclusion]: The minister is a foreign PEP connected to Singapore, and the service is provided through a Singapore branch. This meets every condition for enhanced CDD triggers in S3 and S4. The tier is 'enhanced'. _(cited: rules2025::5-5::0, rules2025::6-23::0)_
- **D16-standard-individual** [rule]: Simplified CDD applies only to low-risk customers where there are no red flags or enhanced CDD triggers. Medium-risk customers do not qualify for simplified measures. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0)_
- **D17-standard-individual-paraphrase** [required_measures]: Determine if the customer is a PEP or sanctioned (scenario confirms negative). _(cited: austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0)_
- **D18-sole-trader** [rule]: Enhanced CDD is mandatory only for high-risk customers or when specific triggers exist; simplified CDD applies only to low-risk customers without triggers. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D19-private-company** [rule]: S7 permits 'simplified initial customer due diligence' only if section 31 of the Act allows it AND the customer is controlled by a regulated entity or a strata/homeowners association. The scenario does not state the customer fits these categories, nor does it state the risk is low. _(cited: rules2025::6-18::0)_
- **D22-unincorporated-association** [rule]: Simplified CDD applies only if the customer's ML/TF risk is low and enhanced CDD does not apply. _(cited: austrac-cdd-body-corporate::simplified-verification-for-certain-matt::0)_
- **D22-unincorporated-association** [conclusion]: Since the club is medium risk, it fails the condition for simplified CDD. No enhanced triggers are mentioned in the scenario. Thus, standard CDD applies. _(cited: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::simplified-verification-for-certain-matt::0)_
- **D22-unincorporated-association** [required_measures]: Identify the individual with primary responsibility for governance and executive decisions (e.g., committee president). _(cited: rules2025::6-2::0)_
- **D22-unincorporated-association** [required_measures]: Establish the identity of any beneficial owners. _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **D22-unincorporated-association** [required_measures]: Identify if any person is a PEP or subject to TFS. _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **D23-smsf-trap** [conclusion]: The ATO is an investor protection regulator. The SMF is registered with the ATO. Thus, the customer fits the regulatory oversight condition for simplified CDD. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D23-smsf-trap** [required_measures]: Verify identity of the trust and each representative (trustees) engaging with the entity. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1)_
- **D23-smsf-trap** [required_measures]: Conduct PEP and TFS checks on all beneficiaries unless they cannot be identified. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1)_
- **D24-asic-registration-trap** [scenario_fact]: The customer is a newly registered Australian proprietary company with low ML/TF risk. _(cited: none)_
- **D24-asic-registration-trap** [conclusion]: Registration with ASIC does not satisfy the requirement for oversight by a prudential/insurance/investor protection regulator, nor is the customer a listed public company or government body. Thus, simplified CDD conditions are not met and enhanced triggers are absent, resulting in standard CDD. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, rules2025::6-18::0)_
- **D24-asic-registration-trap** [required_measures]: Establish the identity of any beneficial owners of the customer. _(cited: rules2025::6-8::0, rules2025::6-7::0, rules2025::6-7::1)_
- **D29-apra-regulated-insurer** [conclusion]: Since the scenario confirms low risk and no enhanced CDD triggers, the tier is 'simplified'. _(cited: austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D30-asx-listed-company** [rule]: Simplified CDD applies when the customer is low ML/TF risk and does not trigger enhanced CDD requirements (such as being a PEP or having high-risk links). _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D30-asx-listed-company** [rule]: The guidance explicitly states that for low-risk customers who do not trigger enhanced CDD, you may reduce collection and verification requirements. _(cited: austrac-cdd-body-corporate::what-this-guidance-covers::0)_
- **D30-asx-listed-company** [conclusion]: Since the scenario confirms the customer is low risk and has no unusual activity (no triggers), simplified CDD applies. The tier is 'simplified'. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::what-this-guidance-covers::0)_
- **D30-asx-listed-company** [required_measures]: Collect and verify baseline information appropriate for a low-risk corporate customer (e.g., business nature, regulatory oversight status). _(cited: austrac-cdd-body-corporate::what-this-guidance-covers::0)_
- **D31-strata-owners-corporation** [required_measures]: Verify this information using reliable and independent data (e.g., establishing control by the relevant entity). _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0)_
- **D40-charitable-trust** [conclusion]: Since the scenario explicitly rates the trust as medium risk (not low) and provides no evidence it is controlled by a regulated entity, the conditions for simplified CDD are not met. No enhanced triggers are present. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0)_
- **D40-charitable-trust** [rule]: When simplified CDD does not apply and no enhanced CDD trigger exists, standard initial CDD applies to establish identity, beneficial owners, PEP status, and business purpose. _(cited: austrac-cdd-trust::matters-you-must-establish::0)_
- **D42-trust-formed-high-risk** [required_measures]: Collect KYC information about beneficiaries or classes of beneficiaries. _(cited: rules2025::6-3::0)_
- **D43-testamentary-trust** [rule]: Simplified CDD for trusts applies only if the customer's ML/TF risk is low and enhanced CDD does not apply (S2). _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D43-testamentary-trust** [conclusion]: Since the scenario states the risk is medium, the condition for simplified CDD is not met. Since the risk is not high, enhanced CDD triggers do not apply. The tier is standard. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D44-sole-trader-high-risk-country** [required_measures]: Establish the identity of the customer and verify it using appropriate methods suitable for high-risk situations. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0)_
- **D44-sole-trader-high-risk-country** [required_measures]: Identify and understand the beneficial owners of the customer (if any) and verify their identities. _(cited: austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0)_
- …and 50 more in predictions.jsonl (`judge_supported: false`).
