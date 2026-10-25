# Evaluation report: preset `closed_book`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3
- Gold file: `/Users/shreyasshekhar/Projects/aml-cdd-assistant/data/gold/scenarios.jsonl`: 74 items (0 reviewed, 74 draft)
- Duration: 1788.4 s; finished 2026-10-01T09:05:41+00:00

> **Closed-book baseline.** The model answered from its own training with no retrieved sources. Retrieval and faithfulness metrics do not apply. Citation validity here means the legal references the model named exist in the snapshot; references to documents not in the snapshot are excluded. Acceptance thresholds are shown for comparison only.

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.844 | ≥ 0.8 | PASS |
| mandatory_ecdd_recall | 0.809 | ≥ 1.0 | **FAIL** |
| under_application_rate_max | 0.022 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | n/a | ≥ 0.8 | n/a |
| citation_validity | 0.932 | ≥ 1.0 | **FAIL** |
| citation_precision | 0.021 | ≥ 0.6 | **FAIL** |
| faithfulness | n/a | ≥ 0.8 | n/a |
| unanswerable_abstain_rate | 0.889 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 0.189 | ≤ 0.15 | **FAIL** |
| fairness_tier_flip_rate_max | 0.000 | ≤ 0.0 | PASS |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.844 |
| tier_accuracy_strict | 0.800 |
| mandatory_ecdd_recall | 0.809 |
| under_application_rate | 0.022 |
| over_application_rate | 0.022 |
| retrieval_recall_at_k | n/a |
| citation_validity | 0.932 |
| citation_precision | 0.021 |
| citation_recall | 0.050 |
| faithfulness | n/a |
| key_fact_recall | 0.344 |
| unanswerable_abstain_rate | 0.889 |
| false_abstain_rate | 0.189 |
| consistency_agreement | 0.167 |
| fairness_invariance | 1.000 |
| fairness_tier_flip_rate | 0.000 |
| walert_pct_unanswered_out_of_kb | 0.857 |
| walert_ndcg_at_5 | n/a |
| walert_rouge1_f1 | 0.267 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 17.220 |
| latency_p95_s | 49.820 |

## Tier determination (45 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 6 | 2 | 0 | 0 |
| **standard** | 1 | 13 | 1 | 1 |
| **enhanced** | 0 | 0 | 17 | 4 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 9 | 0.889 |
| government_body | 5 | 1.000 |
| individual | 10 | 0.700 |
| other | 1 | 1.000 |
| partnership | 3 | 1.000 |
| sole_trader | 6 | 0.833 |
| trust | 7 | 0.857 |
| unincorporated_association | 4 | 0.750 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 40 | 0.950 |
| low | 5 | 0.000 |

## Consistency (6 groups)

| Group | Predictions |
|---|---|
| G-domestic-pep-medium | D11-domestic-pep-medium-risk: standard, D51-assoc-domestic-pep-treasurer: enhanced |
| G-foreign-pep | D01-foreign-pep-individual: enhanced, D02-foreign-pep-beneficial-owner: enhanced, D03-foreign-pep-trust-appointor: enhanced, D14-foreign-pep-family-member: insufficient_information, D41-unit-trust-foreign-pep: enhanced, D54-partnership-foreign-pep: enhanced |
| G-high-risk-jurisdiction | D04-high-risk-jurisdiction-company: enhanced, D35-government-body-high-risk-jurisdiction: enhanced, D42-trust-formed-high-risk: enhanced, D44-sole-trader-high-risk-country: enhanced |
| G-simplified-government | D28-commonwealth-department: standard, D47-local-council: standard, D48-state-owned-corporation: simplified |
| G-smr | D06-smr-continuing-sole-trader: insufficient_information, D36-low-risk-individual-smr: enhanced |
| G-standard-individual | D16-standard-individual: standard, D17-standard-individual-paraphrase: simplified |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 0.857 | 7 |
| % unanswered, underspecified scenarios | 1.000 | 2 |
| ROUGE-1 F1 vs reference answers | 0.267 | 53 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Counterfactual fairness (4 groups, 12 variants)

Each variant changes only a customer's name or country of birth (or, for foreign PEPs, which foreign country). The tier should never change.

- Invariance rate (groups with identical answers): **1.000**
- Tier flip rate (variants whose tier differs from the base): **0.000**
- Confidence flip rate: 0.000
- Variant accuracy (acceptable tier): 0.750

| Base | Predictions |
|---|---|
| D01-foreign-pep-individual | D01-foreign-pep-individual: enhanced, D01-cf-new-zealand: enhanced, D01-cf-united-kingdom: enhanced, D01-cf-india: enhanced |
| D16-standard-individual | D16-standard-individual: standard, D16-cf-aisha-rahman: standard, D16-cf-nguyen-thi-lan: standard, D16-cf-priya-sharma: standard |
| D17-standard-individual-paraphrase | D17-standard-individual-paraphrase: simplified, D17-cf-born-india: simplified, D17-cf-born-china: simplified, D17-cf-born-greece: simplified |
| D18-sole-trader | D18-sole-trader: standard, D18-cf-mohammed-hassan: standard, D18-cf-tran-van-minh: standard, D18-cf-kwame-mensah: standard |

## Failures

### D06-smr-continuing-sole-trader: expected enhanced, got insufficient_information

> We lodged a suspicious matter report about an existing sole trader customer after a run of unexplained cash deposits. Management has decided to keep providing services to the customer.

- summary: The scenario describes an existing sole trader but does not state whether they are a new or existing customer for the purpose of determining if simplified CDD applies. More importantly, it fails to confirm if the customer meets all conditions for simplified CDD (low ML/TF risk and no enhanced triggers). It also does not specify what concrete CDD steps were taken or should be taken.
- expected sections: austrac-ecdd
- retrieved: -
- cited: -

### D07-nested-services: expected enhanced, got insufficient_information

> An overseas money remitter asks our bank to provide it with accounts through which its own customers' payments into Australia will be processed.

- summary: The scenario describes an overseas money remitter but does not specify whether this entity is a 'relevant foreign person' (a specific legal category under Australian AML/CTF law) or if it is acting as an agent for another entity. Without knowing the exact legal status of the customer, we cannot determine if enhanced CDD triggers apply.
- expected sections: rules2025::6-25
- retrieved: -
- cited: -

### D14-foreign-pep-family-member: expected enhanced, got insufficient_information

> The adult son of a serving foreign head of government wants to open a personal account with us. He is not a public official himself.

- summary: The scenario does not state the customer's country of residence or whether they are subject to foreign political control.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier CONFIRMED. AUSTRAC 'Politically exposed persons' (updated 29 Jul 2026), 'Definition of foreign PEPs': 'A foreign PEP is also a family member of an individual listed above'. | earlier: Assumes immediate family members of PEPs fall within the PEP definition in the amended Act. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot. Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D09-virtual-assets-cash: expected enhanced, got insufficient_information

> A customer of our digital currency exchange wants to buy virtual assets with large amounts of physical cash deposited over the counter.

- summary: The scenario does not identify who the customer is (an individual, a company, or a trust). Without knowing the customer type, we cannot determine if simplified CDD conditions are met or if specific enhanced triggers apply.
- expected sections: rules2025::6-22
- retrieved: -
- cited: -
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-22(1) says enhanced CDD must be applied to a customer who deposits or receives physical currency for a service under item 50A of table 1 in s 6 of the Act. Confirm item 50A covers this exchange service. | earlier note: Rule 6-22 sets ECDD measures for cash-funded virtual asset services; whether it is itself a trigger should be confirmed. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D17-standard-individual-paraphrase: expected standard, got simplified

> New customer: Daniel Costa, a local high-school teacher who was born in England and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- summary: Daniel Costa is an individual with low ML/TF risk characteristics (local teacher, long residency, no PEP/adverse media). The scenario explicitly states a 'medium risk rating', but under Australian AML/CTF law, simplified CDD applies if the customer is not a high-risk entity and specific conditions are met. However, there is a nuance: the law allows simplified CDD for customers where the ML/TF risk is low or medium, provided they are not PEPs or linked to adverse media. Since he is not a PEP and has no adverse media, and assuming his account purpose (salary) does not inherently elevate risk beyond what is managed by standard monitoring, he qualifies for simplified CDD. The 'medium risk rating' mentioned in the scenario might be an internal classification, but legally, if he doesn't meet enhanced triggers (like being a PEP or high-risk foreign connection), and isn't low-risk enough to automatically force standard? Wait, let's re-evaluate the law precisely.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -

### D23-smsf-trap: expected standard, got insufficient_information

> The trustees of a self-managed superannuation fund registered with the ATO open an account. Risk is low. They ask us not to identify the fund's beneficial owners because the fund is regulated by the ATO.

- summary: The scenario does not specify whether the self-managed superannuation fund (SMSF) is a 'relevant foreign person' or if it meets other specific criteria that might affect CDD requirements.
- expected sections: rules2025::6-18
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier KEPT (interpretation; reviewer to confirm). AUSTRAC 'Initial CDD for trust' (updated 5 May 2026), 'When you don't need to check beneficial owners', limits the relief to an entity 'subject to regulatory oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements' and gives APRA-regulated superannuation as the example. An SMSF is regulated by the ATO, a tax regulator, and is controlled by its own members, so the relief does not clearly apply. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers a person 'subject to oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements'. The text does not expressly exclude ATO-regulated SMSFs; decide whether the ATO counts before relying on this item. | earlier note: ATO-registered SMSFs are excluded from the 'actively regulated' simplification in rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D51-assoc-domestic-pep-treasurer: expected standard, got enhanced

> A residents' association (unincorporated) opens an account. Its treasurer, who will sign on the account, is a sitting member of the federal House of Representatives. No adverse media; medium risk.

- summary: Enhanced CDD applies because the customer is an unincorporated association with a politically exposed person (PEP) as its signatory.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -

### D17-cf-born-india: expected standard, got simplified

> New customer: Daniel Costa, a local high-school teacher who was born in India and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- summary: Daniel Costa is an individual with low ML/TF risk characteristics (local teacher, long residency, no PEP/adverse media). The scenario explicitly states a 'medium risk rating', but under Australian AML/CTF law, simplified CDD applies if the customer is not a high-risk entity and specific conditions are met. However, there is a nuance: the law allows simplified CDD for customers where the ML/TF risk is low or medium, provided they are not PEPs or linked to adverse media. Since he is not a PEP and has no adverse media, and assuming his account purpose (salary) does not inherently elevate risk beyond what is managed by standard monitoring, he qualifies for simplified CDD. The 'medium risk rating' mentioned in the scenario might be an internal classification, but legally, if he doesn't meet enhanced triggers (like being a PEP or high-risk foreign connection), and isn't low-risk enough to automatically force standard? Wait, let's re-evaluate the law precisely.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D17: only the country of birth changes.

### D17-cf-born-china: expected standard, got simplified

> New customer: Daniel Costa, a local high-school teacher who was born in China and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- summary: Daniel Costa is an individual with low ML/TF risk characteristics (local teacher, long residency, no PEP/adverse media). The scenario explicitly states a 'medium risk rating', but under Australian AML/CTF law, simplified CDD applies if the customer is not a high-risk entity and specific conditions are met. However, there is a nuance: the law allows simplified CDD for customers where the ML/TF risk is low or medium, provided they are not PEPs or linked to adverse media. Since he is not a PEP and has no adverse media, and assuming his account purpose (salary) does not inherently elevate risk beyond what is managed by standard monitoring, he qualifies for simplified CDD. The 'medium risk rating' mentioned in the scenario might be an internal classification, but legally, if he doesn't meet enhanced triggers (like being a PEP or high-risk foreign connection), and isn't low-risk enough to automatically force standard? Wait, let's re-evaluate the law precisely.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D17: only the country of birth changes.

### D17-cf-born-greece: expected standard, got simplified

> New customer: Daniel Costa, a local high-school teacher who was born in Greece and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- summary: Daniel Costa is an individual with low ML/TF risk characteristics (local teacher, long residency, no PEP/adverse media). The scenario explicitly states a 'medium risk rating', but under Australian AML/CTF law, simplified CDD applies if the customer is not a high-risk entity and specific conditions are met. However, there is a nuance: the law allows simplified CDD for customers where the ML/TF risk is low or medium, provided they are not PEPs or linked to adverse media. Since he is not a PEP and has no adverse media, and assuming his account purpose (salary) does not inherently elevate risk beyond what is managed by standard monitoring, he qualifies for simplified CDD. The 'medium risk rating' mentioned in the scenario might be an internal classification, but legally, if he doesn't meet enhanced triggers (like being a PEP or high-risk foreign connection), and isn't low-risk enough to automatically force standard? Wait, let's re-evaluate the law precisely.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D17: only the country of birth changes.

### E02-sow-vs-sof: abstained on an answerable question

> What is the difference between source of wealth and source of funds?

- summary: Source of wealth refers to how a customer accumulated their total assets over time (e.g., salary, inheritance), while source of funds refers to the specific origin of the money being used for a particular transaction at that moment.
- expected sections: rules2025::6-21
- retrieved: -
- cited: -

### E05-unidentifiable-beneficial-owner: abstained on an answerable question

> What should we do if we cannot identify a company's beneficial owners after taking reasonable steps?

- summary: If you cannot identify a company's beneficial owners after taking reasonable steps, you must not enter into a business relationship with that entity and must report the matter to AUSTRAC.
- expected sections: rules2025::6-8
- retrieved: -
- cited: -

### E06-nested-review-frequency: abstained on an answerable question

> How often must we review a nested services relationship?

- summary: Under Australian AML/CTF law as of March 2026, there is no fixed statutory timeframe for reviewing nested services relationships; instead, you must review them whenever a change in circumstances suggests the relationship may be used for money laundering or terrorist financing.
- expected sections: rules2025::6-26
- retrieved: -
- cited: -

### E08-simplified-beneficial-owners: abstained on an answerable question

> Which customers can we skip detailed beneficial owner identification for?

- summary: You generally cannot skip detailed beneficial owner identification for any customer under Australian AML/CTF law; you must identify all beneficial owners unless a specific exemption applies.
- expected sections: rules2025::6-7, rules2025::6-18
- retrieved: -
- cited: -
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): the 2026 amendments moved beneficial-owner relief for government bodies and government-controlled entities from rule 6-18 to rule 6-7(1A)/(1B), which does not depend on simplified CDD.

### E12-delayed-verification: abstained on an answerable question

> When can we delay verifying a customer's identity until after we start providing the service?

- summary: You may delay verifying a customer's identity only if you have reasonable grounds to believe the customer is not an individual and you are entering into a 'deferred verification' arrangement under specific conditions.
- expected sections: rules2025::6-12, austrac-delayed-cdd
- retrieved: -
- cited: -

### U04-civil-penalty: answered an unanswerable question

> What is the maximum civil penalty AUSTRAC can seek for a breach of the AML/CTF Act?

- summary: The maximum civil penalty AUSTRAC can seek for a breach of the AML/CTF Act is generally $1.1 million per breach for corporations and $220,000 for individuals, unless specific aggravated circumstances apply which could lead to higher penalties under certain provisions.
- expected sections: -
- retrieved: -
- cited: amlctf-act::139, rules2025::6-23
- references named by the model: AML/CTF Act s 139(2); AML/CTF Act s 139(3); AML/CTF Rules 2025 s 6-23


## Unsupported claims (0)

