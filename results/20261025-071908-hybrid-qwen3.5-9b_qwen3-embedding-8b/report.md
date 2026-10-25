# Evaluation report: preset `hybrid`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.3
- Gold file: `/Users/shreyasshekhar/Projects/aml-cdd-assistant/data/gold/scenarios.jsonl`: 74 items (0 reviewed, 74 draft)
- Duration: 8714.2 s (answering 5950.5 s, then grading 2763.7 s); finished 2026-10-24T22:44:22+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.822 | ≥ 0.8 | PASS |
| mandatory_ecdd_recall | 0.905 | ≥ 1.0 | **FAIL** |
| under_application_rate_max | 0.133 | ≤ 0.05 | **FAIL** |
| retrieval_recall_at_k | 0.623 | ≥ 0.8 | **FAIL** |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.389 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.840 | ≥ 0.8 | PASS |
| unanswerable_abstain_rate | 1.000 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | 0.083 | ≤ 0.0 | **FAIL** |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.822 |
| tier_accuracy_strict | 0.822 |
| mandatory_ecdd_recall | 0.905 |
| under_application_rate | 0.133 |
| over_application_rate | 0.044 |
| retrieval_recall_at_k | 0.623 |
| citation_validity | 1.000 |
| citation_precision | 0.389 |
| citation_recall | 0.585 |
| faithfulness | 0.840 |
| key_fact_recall | 0.875 |
| unanswerable_abstain_rate | 1.000 |
| false_abstain_rate | 0.000 |
| consistency_agreement | 0.833 |
| fairness_invariance | 0.750 |
| fairness_tier_flip_rate | 0.083 |
| walert_pct_unanswered_out_of_kb | 1.000 |
| walert_ndcg_at_5 | 0.414 |
| walert_rouge1_f1 | 0.230 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 79.650 |
| latency_p95_s | 100.980 |

## Answer checks

Citation validity means each citation points to a passage that was really retrieved. Whether that passage supports the claim is measured separately (faithfulness, below).

- Answers with a point that cites nothing: 0
- Answers that call a fact the scenario rules out unknown: 0

## Tier determination (45 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 8 | 0 | 0 | 0 |
| **standard** | 4 | 10 | 2 | 0 |
| **enhanced** | 0 | 2 | 19 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 9 | 0.778 |
| government_body | 5 | 0.800 |
| individual | 10 | 0.800 |
| other | 1 | 1.000 |
| partnership | 3 | 1.000 |
| sole_trader | 6 | 1.000 |
| trust | 7 | 0.714 |
| unincorporated_association | 4 | 0.750 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 33 | 0.818 |
| low | 1 | 0.000 |
| medium | 11 | 0.909 |

## Consistency (6 groups)

| Group | Predictions |
|---|---|
| G-domestic-pep-medium | D11-domestic-pep-medium-risk: enhanced, D51-assoc-domestic-pep-treasurer: enhanced |
| G-foreign-pep | D01-foreign-pep-individual: enhanced, D02-foreign-pep-beneficial-owner: enhanced, D03-foreign-pep-trust-appointor: enhanced, D14-foreign-pep-family-member: enhanced, D41-unit-trust-foreign-pep: enhanced, D54-partnership-foreign-pep: enhanced |
| G-high-risk-jurisdiction | D04-high-risk-jurisdiction-company: enhanced, D35-government-body-high-risk-jurisdiction: enhanced, D42-trust-formed-high-risk: enhanced, D44-sole-trader-high-risk-country: enhanced |
| G-simplified-government | D28-commonwealth-department: simplified, D47-local-council: simplified, D48-state-owned-corporation: simplified |
| G-smr | D06-smr-continuing-sole-trader: enhanced, D36-low-risk-individual-smr: enhanced |
| G-standard-individual | D16-standard-individual: standard, D17-standard-individual-paraphrase: simplified |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 1.000 | 7 |
| % unanswered, underspecified scenarios | 1.000 | 2 |
| NDCG@1 (known questions) | 0.344 | 32 |
| NDCG@3 (known questions) | 0.430 | 32 |
| NDCG@5 (known questions) | 0.445 | 32 |
| NDCG@1 (inferred questions) | 0.429 | 21 |
| NDCG@3 (inferred questions) | 0.338 | 21 |
| NDCG@5 (inferred questions) | 0.367 | 21 |
| NDCG@1 (all questions) | 0.377 | 53 |
| NDCG@3 (all questions) | 0.394 | 53 |
| NDCG@5 (all questions) | 0.414 | 53 |
| ROUGE-1 F1 vs reference answers | 0.230 | 53 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 47 | 0.617 | 0.872 |
| key_points | 38 | 0.947 | 1.000 |
| required_measures | 164 | 0.884 | 0.982 |
| rule | 71 | 0.718 | 0.972 |
| scenario_fact | 61 | 0.967 | 0.934 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.816** supported by the judge.

## Counterfactual fairness (4 groups, 12 variants)

Each variant changes only a customer's name or country of birth (or, for foreign PEPs, which foreign country). The tier should never change.

- Invariance rate (groups with identical answers): **0.750**
- Tier flip rate (variants whose tier differs from the base): **0.083**
- Confidence flip rate: 0.083
- Variant accuracy (acceptable tier): 0.667

| Base | Predictions |
|---|---|
| D01-foreign-pep-individual | D01-foreign-pep-individual: enhanced, D01-cf-new-zealand: enhanced, D01-cf-united-kingdom: enhanced, D01-cf-india: enhanced |
| D16-standard-individual | D16-standard-individual: standard, D16-cf-aisha-rahman: standard, D16-cf-nguyen-thi-lan: simplified, D16-cf-priya-sharma: standard |
| D17-standard-individual-paraphrase | D17-standard-individual-paraphrase: simplified, D17-cf-born-india: simplified, D17-cf-born-china: simplified, D17-cf-born-greece: simplified |
| D18-sole-trader | D18-sole-trader: standard, D18-cf-mohammed-hassan: standard, D18-cf-tran-van-minh: standard, D18-cf-kwame-mensah: standard |

**Flips:** D16-cf-nguyen-thi-lan gave simplified where D16-standard-individual gave standard

## Failures

### D07-nested-services: expected enhanced, got standard

> An overseas money remitter asks our bank to provide it with accounts through which its own customers' payments into Australia will be processed.

- summary: The scenario describes an overseas money remitter seeking accounts to process payments into Australia. The sources do not state that this customer is a PEP, located in a high-risk country, or involved in shell banking. Therefore, enhanced CDD triggers are not met. The scenario does not provide facts confirming the specific conditions for simplified CDD (such as low ML/TF risk and no enhanced triggers), so simplified CDD cannot be applied. Consequently, standard initial CDD applies.
- expected sections: rules2025::6-25
- retrieved: austrac-transitioning::you-complied-with-relevant-obligations-i--previous-compliance-in-a-foreign-country::0, rules2025::6-12::1, rules2025::6-25::1, rules2025::6-13::0, rules2025::1-4::2, rules2025::6-12::0, austrac-reliance::what-to-consider-before-entering-into-a--relying-on-a-third-party-in-a-foreign-co::0, austrac-cdd-sole-traders::nature-and-purpose-of-the-business-relat--example-an-accountant-and-sole-trader-cu::0
- cited: rules2025::6-25::1, rules2025::6-12::0

### D11-domestic-pep-medium-risk: expected standard, got enhanced

> A sitting member of an Australian state parliament opens a home loan offset account. Screening finds nothing adverse and our methodology rates her as medium risk.

- summary: Enhanced CDD is required because the customer is a sitting member of an Australian state parliament, which makes them a domestic PEP. While the scenario states the risk is rated as medium, being a PEP (unless explicitly 'low-profile') is a significant factor. The sources indicate that domestic PEPs generally trigger enhanced scrutiny or are classified as high-risk unless specified otherwise (e.g., 'low-profile'). Since the scenario does not state the customer is 'low-profile', and S7 requires specific actions for domestic PEPs where risk is high, and S3 implies non-low-profile PEPs are high risk, the presence of this status without a 'low-profile' qualifier mandates enhanced measures to verify their status and source of wealth/funds.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, rules2025::6-36::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0, austrac-pep::definition-of-domestic-peps::0, rules2025::5-5::1, rules2025::1-5::0
- cited: austrac-pep::definition-of-domestic-peps::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0
- gold note: Domestic PEP: enhanced CDD only if ML/TF risk is high. Over-applying ECDD here counts as an error.

### D17-standard-individual-paraphrase: expected standard, got simplified

> New customer: Daniel Costa, a local high-school teacher who was born in England and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- summary: Daniel Costa qualifies for simplified CDD because he is a low-risk customer with no enhanced CDD triggers.
- expected sections: austrac-cdd-individuals
- retrieved: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen::0, austrac-foreign-pep-example::close-associate-of-a-foreign-pep::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0, austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, austrac-reliance::regular-assessments-of-cdd-arrangements::0
- cited: austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0

### D20-family-trust: expected standard, got simplified

> An Australian discretionary family trust with a corporate trustee opens an investment account. Medium risk, no PEP connections.

- summary: The scenario describes an Australian discretionary family trust with a corporate trustee, rated as medium risk, with no PEP connections. The sources permit simplified CDD for low ML/TF risk customers where enhanced CDD triggers are absent. Although the customer is rated 'medium', the scenario explicitly states there are 'no red flags or enhanced CDD triggers'. Under AUSTRAC guidance, if no enhanced triggers exist and the customer does not fall into high-risk categories (like foreign PEPs or ties to high-risk jurisdictions), simplified CDD applies provided the specific conditions for simplification are met. The scenario confirms the absence of these negative factors.
- expected sections: rules2025::6-3, austrac-cdd-trust
- retrieved: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-cdd-trust::matters-you-must-establish::0, austrac-cdd-trust::politically-exposed-persons-and-sanction--collect-information::0, austrac-cdd-trust::politically-exposed-persons-and-sanction::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-pep::definition-of-domestic-peps::1, austrac-cdd-trust::what-this-guidance-covers--additional-requirements::0
- cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-cdd-trust::matters-you-must-establish::0, austrac-cdd-trust::politically-exposed-persons-and-sanction::0

### D23-smsf-trap: expected standard, got simplified

> The trustees of a self-managed superannuation fund registered with the ATO open an account. Risk is low. They ask us not to identify the fund's beneficial owners because the fund is regulated by the ATO.

- summary: The scenario describes a self-managed superannuation fund (SMF) with low ML/TF risk. The customer is subject to regulatory oversight by APRA for providing superannuation services. Under S1, S3, and S8, this allows simplified CDD regarding beneficial owners. While the customer requested not to identify beneficial owners, the rules permit simplification but do not mandate it; however, since the conditions for simplified CDD are met, that is the applicable tier.
- expected sections: rules2025::6-18
- retrieved: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::1, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-trust::matters-you-must-establish::0, rules2025::6-18::0
- cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, rules2025::6-18::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::1, austrac-cdd-trust::matters-you-must-establish::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier KEPT (interpretation; reviewer to confirm). AUSTRAC 'Initial CDD for trust' (updated 5 May 2026), 'When you don't need to check beneficial owners', limits the relief to an entity 'subject to regulatory oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements' and gives APRA-regulated superannuation as the example. An SMSF is regulated by the ATO, a tax regulator, and is controlled by its own members, so the relief does not clearly apply. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers a person 'subject to oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements'. The text does not expressly exclude ATO-regulated SMSFs; decide whether the ATO counts before relying on this item. | earlier note: ATO-registered SMSFs are excluded from the 'actively regulated' simplification in rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D24-asic-registration-trap: expected standard, got simplified

> A newly registered Australian proprietary company with low ML/TF risk asks us not to identify its beneficial owners because it is registered with ASIC.

- summary: The customer is a low ML/TF risk body corporate. The scenario states it is registered with ASIC, which satisfies the condition that the entity is subject to regulatory oversight by a prudential or investor protection regulator (ASIC). Since enhanced CDD triggers are not present and the conditions for simplified CDD are met, the tier is 'simplified'.
- expected sections: rules2025::6-18
- retrieved: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::1, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1, rules2025::6-8::0, austrac-cdd-body-corporate::customer-identity--verify-information--registered-foreign-company::0, rules2025::6-7::0
- cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::1
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier KEPT. AUSTRAC 'Initial CDD for body corporate' (updated 25 Aug 2026), 'Low risk customers', gives banks, insurers and businesses holding an Australian Financial Services Licence as examples of regulatory oversight; ordinary company registration with ASIC is not oversight 'by a prudential, insurance, or investor protection regulator'. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers oversight 'through registration or licensing requirements'. Whether ordinary ASIC company registration counts is not settled by the text; decide before relying on this item. | earlier note: Ordinary ASIC registration is not active regulation for rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D49-embassy-ambassador-signatory: expected enhanced, got standard

> A foreign country's embassy in Canberra opens an account for its operating costs. The ambassador will be the main account signatory. The country is not on any FATF list and we would otherwise rate the customer as medium risk.

- summary: The scenario describes a foreign embassy account with medium risk. No enhanced triggers are present, and simplified conditions are not met due to the customer being a foreign entity (embassy) rather than a low-risk individual or specific category.
- expected sections: austrac-ecdd, austrac-pep
- retrieved: austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-reliance::what-to-consider-before-entering-into-a--relying-on-a-third-party-in-a-foreign-co::0, austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high--example-identifying-high-ml-tf-risk-duri-2::0, austrac-reliance::regular-assessments-of-cdd-arrangements::1, austrac-foreign-pep-example::introduction::0, rules2025::6-11::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0
- cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier CONFIRMED. AUSTRAC 'Enhanced customer due diligence' (updated 15 Jul 2026), 'Foreign politically exposed persons', and AUSTRAC 'Politically exposed persons' (updated 29 Jul 2026), 'Enhanced CDD obligations', both require enhanced CDD when 'any person acting on behalf of the customer' is a foreign PEP; the PEP definition includes ambassadors. Reference answer corrected: rules 6-23 and 5-5 (source of wealth/funds, senior manager approval) cover the customer, beneficial owners and persons on whose behalf the service is received, not persons acting on the customer's behalf. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-23(1) covers the customer, a beneficial owner, or a person on whose behalf the customer receives the service. It does not mention a person acting on the customer's behalf, such as a signatory. The expected tier may be wrong; check s 32 of the Act. | earlier note: Assumes an ambassador is a foreign PEP and that rule 6-23 covers persons acting on behalf of the customer. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D51-assoc-domestic-pep-treasurer: expected standard, got enhanced

> A residents' association (unincorporated) opens an account. Its treasurer, who will sign on the account, is a sitting member of the federal House of Representatives. No adverse media; medium risk.

- summary: Enhanced CDD applies because the customer's treasurer is a sitting member of the federal House of Representatives, which makes them a Politically Exposed Person (PEP). The scenario states the ML/TF risk is medium, but S7 mandates establishing PEP status regardless of the overall risk rating. Since an enhanced trigger exists, simplified CDD does not apply.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::customer-identity--collect-information--individuals-responsible-for-the-governan::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-foreign-pep-example::close-associate-of-a-foreign-pep::0, austrac-cdd-body-corporate::matters-you-must-establish::0, austrac-delayed-cdd::opening-an-account-and-allowing-deposits::0, austrac-cdd-body-corporate::politically-exposed-persons-and-sanction::0, rules2025::6-36::0
- cited: austrac-cdd-body-corporate::politically-exposed-persons-and-sanction::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::matters-you-must-establish::0

### D16-cf-nguyen-thi-lan: expected standard, got simplified

> Nguyen Thi Lan, an Australian-resident nurse, opens an everyday transaction account in a branch. She is not a PEP, has no links to high-risk countries, and our methodology rates her as medium risk.

- summary: Nguyen Thi Lan qualifies for simplified CDD because she is a low-risk individual Australian resident with no enhanced CDD triggers.
- expected sections: austrac-cdd-individuals
- retrieved: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0, austrac-risk-ratings::step-3-identify-and-assess-customer-risk::0, austrac-foreign-pep-example::introduction::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0, austrac-foreign-pep-example::source-of-funds-and-source-of-wealth-che::0
- cited: austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0
- gold note: Counterfactual of D16-standard-individual: only the name/country changes.

### D17-cf-born-india: expected standard, got simplified

> New customer: Daniel Costa, a local high-school teacher who was born in India and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- summary: The customer Daniel Costa is identified as low risk based on his profile (Australian resident, individual, no red flags). The scenario explicitly states there are no enhanced CDD triggers and the ML/TF risk is not high. Therefore, simplified CDD applies.
- expected sections: austrac-cdd-individuals
- retrieved: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen::0, austrac-foreign-pep-example::close-associate-of-a-foreign-pep::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0, austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, austrac-reliance::regular-assessments-of-cdd-arrangements::0
- cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0
- gold note: Counterfactual of D17: only the country of birth changes.

### D17-cf-born-china: expected standard, got simplified

> New customer: Daniel Costa, a local high-school teacher who was born in China and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- summary: The customer is Daniel Costa, an Australian resident individual with no PEP status, no adverse media, and no foreign connections. His risk rating is explicitly stated as 'medium'. However, the scenario states there are 'no enhanced CDD triggers' present. According to the sources, simplified CDD applies when a customer has no medium- to high-risk factors or enhanced CDD triggers. Since the scenario confirms the absence of these specific triggers and identifies him as an individual with low-risk service needs (basic salary account), he qualifies for simplified CDD despite the 'medium' label in the scenario's internal rating, provided that label does not override the explicit absence of triggers required for enhancement.
- expected sections: austrac-cdd-individuals
- retrieved: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen::0, austrac-foreign-pep-example::close-associate-of-a-foreign-pep::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0, austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, austrac-reliance::regular-assessments-of-cdd-arrangements::0
- cited: austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0
- gold note: Counterfactual of D17: only the country of birth changes.

### D17-cf-born-greece: expected standard, got simplified

> New customer: Daniel Costa, a local high-school teacher who was born in Greece and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- summary: The customer Daniel Costa is identified as low risk based on his profile (Australian resident, individual, no red flags). The scenario explicitly states there are no enhanced CDD triggers and the ML/TF risk is not high. Therefore, simplified CDD applies.
- expected sections: austrac-cdd-individuals
- retrieved: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen::0, austrac-foreign-pep-example::close-associate-of-a-foreign-pep::0, austrac-risk-ratings::why-customer-risk-ratings-matter::0, austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, austrac-reliance::regular-assessments-of-cdd-arrangements::0
- cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0
- gold note: Counterfactual of D17: only the country of birth changes.


## Unsupported claims (72)

- **D01-foreign-pep-individual** [rule]: Enhanced CDD measures are required when a customer is a PEP or has high ML/TF risk, including establishing source of funds and wealth. _(cited: austrac-ecdd::when-you-must-apply-specific-enhanced-cd--source-of-funds-and-source-of-wealth-whe--when-source-of-funds-and-source-of-wealt::0, austrac-pep::additional-obligations-for-peps--important-note-about-foreign-peps-if-you::0)_
- **D01-foreign-pep-individual** [required_measures]: Obtain senior manager approval before commencing the business relationship _(cited: rules2025::5-5::1)_
- **D02-foreign-pep-beneficial-owner** [conclusion]: Since the customer has a beneficial owner who is a foreign PEP, enhanced CDD measures (including source of wealth/funds checks and senior manager approval) are required. The tier is 'enhanced'. _(cited: austrac-pep::definition-of-foreign-peps::0, rules2025::5-5::0)_
- **D03-foreign-pep-trust-appointor** [required_measures]: Conduct enhanced CDD measures appropriate to the high ML/TF risk associated with the PEP status. _(cited: austrac-cdd-trust::matters-you-must-establish::0)_
- **D07-nested-services** [rule]: Enhanced CDD is required only if specific triggers apply, such as the customer being a PEP, located in a high-risk country, or linked to shell banks. The scenario does not state any of these conditions are met. _(cited: rules2025::6-25::1)_
- **D07-nested-services** [rule]: Simplified CDD applies only if the customer meets every condition set by the sources, including having a low ML/TF risk and no enhanced CDD triggers. The scenario does not state that the ML/TF risk is low or that no triggers exist. _(cited: rules2025::6-12::0)_
- **D07-nested-services** [conclusion]: Since enhanced triggers are absent but simplified conditions are not confirmed, the tier is standard. _(cited: rules2025::6-25::1, rules2025::6-12::0)_
- **D08-unusual-complex-structure** [conclusion]: The scenario facts match the mandatory triggers in S2 and S3. Therefore, the tier is 'enhanced'. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--unusual-large-or-complex-transactions::0, rules2025::6-20::0)_
- **D10-domestic-pep-high-risk** [conclusion]: Because the customer meets the specific conditions of being a domestic PEP with high ML/TF risk, the scenario triggers mandatory enhanced CDD requirements rather than standard or simplified tiers. _(cited: rules2025::5-5::0, rules2025::6-23::0)_
- **D10-domestic-pep-high-risk** [required_measures]: Establish on reasonable grounds that the customer is a domestic politically exposed person. _(cited: rules2025::6-23::0)_
- **D14-foreign-pep-family-member** [conclusion]: Because the customer is a family member of a foreign PEP, he is treated as a foreign PEP. The AML/CTF Rules mandate enhanced CDD for foreign PEPs. _(cited: austrac-pep::definition-of-foreign-peps::0, rules2025::6-23::0)_
- **D11-domestic-pep-medium-risk** [conclusion]: The customer is a domestic PEP. The scenario does not state they are 'low-profile'. S3 lists 'low-profile domestic PEP' as a medium-risk factor, implying other domestic PEPs are high risk or require enhanced measures. Therefore, the tier is enhanced. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--high-risk-customer::0)_
- **D15-foreign-branch-same-country-pep** [scenario_fact]: The scenario explicitly states the bank rates the customer's ML/TF risk as high. _(cited: none)_
- **D15-foreign-branch-same-country-pep** [conclusion]: Since the customer is a foreign PEP and the risk is high, the scenario meets the conditions for enhanced CDD under S7(1)(a). The tier is 'enhanced'. _(cited: rules2025::5-5::0)_
- **D16-standard-individual** [rule]: Simplified CDD applies only to low-risk customers where there are no red flags or enhanced CDD triggers present. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D18-sole-trader** [rule]: Enhanced CDD is only mandatory if high-risk indicators are present; simplified CDD applies to low-risk customers with no triggers. Since this customer is rated medium, standard measures apply. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D18-sole-trader** [required_measures]: Verify identity by comparing provided documents with original copies. _(cited: austrac-risk-ratings::document-and-keep-records--example-of-a-conveyancers-risk-assessmen--low-risk-customer::0)_
- **D19-private-company** [rule]: S5 and S6 require establishing identity, beneficial owners, and the nature of the business for body corporates, which constitutes standard CDD. _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0, rules2025::6-2::0)_
- **D20-family-trust** [rule]: Simplified CDD applies when the customer is low ML/TF risk AND there are no red flags or enhanced CDD triggers present. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D22-unincorporated-association** [rule]: Enhanced CDD is mandatory only if the customer is high ML/TF risk or fits specific low-risk categories (e.g., strata associations) where enhanced measures are not needed. A medium risk rating does not trigger enhanced CDD. _(cited: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0)_
- **D22-unincorporated-association** [rule]: Simplified CDD applies only if the customer is low ML/TF risk and meets specific conditions (e.g., regulated entity or strata association). This customer is medium risk, so simplified CDD does not apply. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D22-unincorporated-association** [conclusion]: Since the customer is medium risk (not high) and does not meet the specific conditions for simplified CDD, the tier is standard. Standard CDD requires establishing identity, beneficial owners (or CEO if none), nature of business, and PEP/sanctions status. _(cited: austrac-cdd-body-corporate::what-this-guidance-covers--additional-requirements::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **D22-unincorporated-association** [required_measures]: Check if any identified individuals are PEPs or subject to sanctions. _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **D23-smsf-trap** [conclusion]: The SMF is licensed by APRA to provide superannuation services, meeting the regulatory oversight condition. Therefore, simplified CDD applies. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, rules2025::6-18::0)_
- **D23-smsf-trap** [required_measures]: Verify the customer is registered/licensed with APRA to provide superannuation services. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::1, rules2025::6-18::0)_
- **D23-smsf-trap** [required_measures]: Conduct PEP and TFS checks on the trust representatives and beneficiaries. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1, rules2025::6-18::0)_
- **D24-asic-registration-trap** [scenario_fact]: The customer is a newly registered Australian proprietary company with low ML/TF risk. _(cited: none)_
- **D24-asic-registration-trap** [conclusion]: ASIC is an investor protection regulator that registers proprietary companies. Therefore, the customer meets the condition for simplified CDD under S2. No enhanced triggers apply. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D29-apra-regulated-insurer** [conclusion]: Since the scenario meets all conditions for simplified CDD (low risk, no enhanced triggers) and no rule mandates enhanced CDD, the tier is 'simplified'. _(cited: austrac-initial-cdd::simplified-cdd-when-the-ml-tf-risk-is-lo--when-you-can-apply-simplified-cdd::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D30-asx-listed-company** [rule]: S2 states that if a customer is low ML/TF risk and enhanced CDD does not apply, simplified CDD applies. This includes customers where you don't need to check beneficial owners. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D30-asx-listed-company** [required_measures]: Verify that the customer is low ML/TF risk based on the scenario facts. _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0)_
- **D31-strata-owners-corporation** [required_measures]: Verify this information using reliable and independent data (e.g., checking ASIC registers or official body corporate records). _(cited: austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--low-risk-customers::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0)_
- **D40-charitable-trust** [rule]: Enhanced CDD is required only if the customer has high-risk indicators (e.g., foreign PEP, ties to high-risk jurisdictions) or if simplified CDD conditions are not met. The scenario states the risk is medium and no enhanced triggers are present. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **D40-charitable-trust** [rule]: Simplified CDD (exemption from checking beneficial owners) applies only if the trust is low ML/TF risk. The scenario states the risk is medium, so this exemption does not apply. _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0)_
- **D40-charitable-trust** [conclusion]: Since the risk is medium (not low), simplified CDD does not apply. Since there are no high-risk indicators or other triggers, enhanced CDD is not required. Therefore, standard CDD applies. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0, austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::0, austrac-cdd-trust::matters-you-must-establish::0)_
- **D41-unit-trust-foreign-pep** [required_measures]: Collect the full name of the individual with primary responsibility for governance (the investor). _(cited: rules2025::6-3::0)_
- **D43-testamentary-trust** [rule]: Simplified CDD applies only if the customer's ML/TF risk is low and enhanced CDD does not apply. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D43-testamentary-trust** [rule]: Enhanced CDD triggers require a high ML/TF risk rating; since the risk here is medium, enhanced CDD is not mandatory based on risk alone. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D43-testamentary-trust** [conclusion]: Because the risk is medium (not low), simplified CDD conditions are not met. Because the risk is not high, enhanced CDD is not triggered. The result is standard CDD. _(cited: austrac-cdd-trust::simplified-verification-for-certain-matt::0)_
- **D43-testamentary-trust** [required_measures]: Establish the identity of the trust (testamentary trust). _(cited: austrac-cdd-trust::matters-you-must-establish::0)_
- …and 32 more in predictions.jsonl (`judge_supported: false`).
