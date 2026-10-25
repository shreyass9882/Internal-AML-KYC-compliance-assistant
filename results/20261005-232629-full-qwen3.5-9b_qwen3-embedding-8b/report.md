# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.3
- Gold file: `/Users/shreyasshekhar/Projects/aml-cdd-assistant/data/gold/scenarios.jsonl`: 74 items (0 reviewed, 74 draft)
- Duration: 8991.2 s (answering 8991.2 s, then grading 0.0 s); finished 2026-10-05T23:10:09+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.022 | ≥ 0.8 | **FAIL** |
| mandatory_ecdd_recall | 0.048 | ≥ 1.0 | **FAIL** |
| under_application_rate_max | 0.000 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 0.019 | ≥ 0.8 | **FAIL** |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.429 | ≥ 0.6 | **FAIL** |
| faithfulness | 1.000 | ≥ 0.8 | PASS |
| unanswerable_abstain_rate | 1.000 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 0.981 | ≤ 0.15 | **FAIL** |
| fairness_tier_flip_rate_max | 0.250 | ≤ 0.0 | **FAIL** |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.022 |
| tier_accuracy_strict | 0.022 |
| mandatory_ecdd_recall | 0.048 |
| under_application_rate | 0.000 |
| over_application_rate | 0.000 |
| retrieval_recall_at_k | 0.019 |
| citation_validity | 1.000 |
| citation_precision | 0.429 |
| citation_recall | 1.000 |
| faithfulness | 1.000 |
| key_fact_recall | 0.000 |
| unanswerable_abstain_rate | 1.000 |
| false_abstain_rate | 0.981 |
| consistency_agreement | 0.833 |
| fairness_invariance | 0.750 |
| fairness_tier_flip_rate | 0.250 |
| walert_pct_unanswered_out_of_kb | 1.000 |
| walert_ndcg_at_5 | 0.015 |
| walert_rouge1_f1 | 0.008 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 80.170 |
| latency_p95_s | 80.170 |

## Answer checks

Citation validity means each citation points to a passage that was really retrieved. Whether that passage supports the claim is measured separately (faithfulness, below).

- Answers with a point that cites nothing: 0
- Answers that call a fact the scenario rules out unknown: 0

## Tier determination (45 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 0 | 0 | 0 | 8 |
| **standard** | 0 | 0 | 0 | 16 |
| **enhanced** | 0 | 0 | 1 | 20 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 9 | 0.000 |
| government_body | 5 | 0.000 |
| individual | 10 | 0.100 |
| other | 1 | 0.000 |
| partnership | 3 | 0.000 |
| sole_trader | 6 | 0.000 |
| trust | 7 | 0.000 |
| unincorporated_association | 4 | 0.000 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 1 | 1.000 |
| none | 44 | 0.000 |

## Consistency (6 groups)

| Group | Predictions |
|---|---|
| G-domestic-pep-medium | D11-domestic-pep-medium-risk: None, D51-assoc-domestic-pep-treasurer: None |
| G-foreign-pep | D01-foreign-pep-individual: enhanced, D02-foreign-pep-beneficial-owner: None, D03-foreign-pep-trust-appointor: None, D14-foreign-pep-family-member: None, D41-unit-trust-foreign-pep: None, D54-partnership-foreign-pep: None |
| G-high-risk-jurisdiction | D04-high-risk-jurisdiction-company: None, D35-government-body-high-risk-jurisdiction: None, D42-trust-formed-high-risk: None, D44-sole-trader-high-risk-country: None |
| G-simplified-government | D28-commonwealth-department: None, D47-local-council: None, D48-state-owned-corporation: None |
| G-smr | D06-smr-continuing-sole-trader: None, D36-low-risk-individual-smr: None |
| G-standard-individual | D16-standard-individual: None, D17-standard-individual-paraphrase: None |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 1.000 | 7 |
| % unanswered, underspecified scenarios | 1.000 | 2 |
| NDCG@1 (known questions) | 0.031 | 32 |
| NDCG@3 (known questions) | 0.030 | 32 |
| NDCG@5 (known questions) | 0.025 | 32 |
| NDCG@1 (inferred questions) | 0.000 | 21 |
| NDCG@3 (inferred questions) | 0.000 | 21 |
| NDCG@5 (inferred questions) | 0.000 | 21 |
| NDCG@1 (all questions) | 0.019 | 53 |
| NDCG@3 (all questions) | 0.018 | 53 |
| NDCG@5 (all questions) | 0.015 | 53 |
| ROUGE-1 F1 vs reference answers | 0.008 | 53 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 1 | n/a | 1.000 |
| required_measures | 4 | n/a | 1.000 |
| rule | 1 | n/a | 1.000 |
| scenario_fact | 1 | n/a | 1.000 |

Claims that must come from a source (all kinds except `scenario_fact`): **n/a** supported by the judge.

## Counterfactual fairness (4 groups, 12 variants)

Each variant changes only a customer's name or country of birth (or, for foreign PEPs, which foreign country). The tier should never change.

- Invariance rate (groups with identical answers): **0.750**
- Tier flip rate (variants whose tier differs from the base): **0.250**
- Confidence flip rate: 0.250
- Variant accuracy (acceptable tier): 0.000

| Base | Predictions |
|---|---|
| D01-foreign-pep-individual | D01-foreign-pep-individual: enhanced, D01-cf-new-zealand: None, D01-cf-united-kingdom: None, D01-cf-india: None |
| D16-standard-individual | D16-standard-individual: None, D16-cf-aisha-rahman: None, D16-cf-nguyen-thi-lan: None, D16-cf-priya-sharma: None |
| D17-standard-individual-paraphrase | D17-standard-individual-paraphrase: None, D17-cf-born-india: None, D17-cf-born-china: None, D17-cf-born-greece: None |
| D18-sole-trader | D18-sole-trader: None, D18-cf-mohammed-hassan: None, D18-cf-tran-van-minh: None, D18-cf-kwame-mensah: None |

**Flips:** D01-cf-new-zealand gave None where D01-foreign-pep-individual gave enhanced; D01-cf-united-kingdom gave None where D01-foreign-pep-individual gave enhanced; D01-cf-india gave None where D01-foreign-pep-individual gave enhanced

## Failures

### D02-foreign-pep-beneficial-owner: expected enhanced, got None

> Harbourline Imports Pty Ltd, an Australian private company, applies for a business transaction account. It has two directors. One of them owns 45% of the shares and is a serving member of a foreign national parliament.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D03-foreign-pep-trust-appointor: expected enhanced, got None

> The corporate trustee of the Nguyen Family Trust, an Australian discretionary trust, opens an investment account. The trust's appointor, who can remove and replace the trustee, is a serving judge of a foreign country's supreme court.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier CONFIRMED. AUSTRAC 'Initial CDD for trust' (updated 5 May 2026), 'Matters you must establish': beneficial owners of a trust include appointors; a supreme court judge of a foreign country is a foreign PEP ({PEP}). | earlier: Assumes senior foreign judicial officers fall within the foreign PEP definition. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot. Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D04-high-risk-jurisdiction-company: expected enhanced, got None

> A company incorporated in a country that is currently subject to a FATF call for action wants to use our remittance service to make regular payments to Australian suppliers.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd, austrac-high-risk-countries
- retrieved: -
- cited: -

### D06-smr-continuing-sole-trader: expected enhanced, got None

> We lodged a suspicious matter report about an existing sole trader customer after a run of unexplained cash deposits. Management has decided to keep providing services to the customer.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd
- retrieved: -
- cited: -

### D07-nested-services: expected enhanced, got None

> An overseas money remitter asks our bank to provide it with accounts through which its own customers' payments into Australia will be processed.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-25
- retrieved: -
- cited: -

### D08-unusual-complex-structure: expected enhanced, got None

> A new corporate customer sits at the bottom of a chain of five holding companies in three countries. It wants to move an unusually large amount through our services and cannot explain the business purpose of the transfers.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-20
- retrieved: -
- cited: -

### D10-domestic-pep-high-risk: expected enhanced, got None

> A sitting member of an Australian state parliament wants to open an account. Recent media reports link her to an ongoing corruption inquiry and our risk methodology rates her ML/TF risk as high.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D13-high-risk-rating-sole-trader: expected enhanced, got None

> A cash-intensive car wash run by a sole trader keeps depositing cash in amounts just below $10,000. Our risk methodology rates the customer as high ML/TF risk.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd
- retrieved: -
- cited: -

### D14-foreign-pep-family-member: expected enhanced, got None

> The adult son of a serving foreign head of government wants to open a personal account with us. He is not a public official himself.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier CONFIRMED. AUSTRAC 'Politically exposed persons' (updated 29 Jul 2026), 'Definition of foreign PEPs': 'A foreign PEP is also a family member of an individual listed above'. | earlier: Assumes immediate family members of PEPs fall within the PEP definition in the amended Act. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot. Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D34-listed-company-unusual: expected enhanced, got None

> An ASX-listed company that we normally treat as low risk asks us to route an unusually large and complex series of transfers through several offshore entities, with no clear business reason.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-20
- retrieved: -
- cited: -

### D35-government-body-high-risk-jurisdiction: expected enhanced, got None

> A state-owned enterprise of a country that is subject to a FATF call for action wants to open an account with us.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd, austrac-high-risk-countries
- retrieved: -
- cited: -

### D36-low-risk-individual-smr: expected enhanced, got None

> A long-standing individual customer, previously rated low risk, suddenly receives several large international transfers that do not match his profile. We lodged a suspicious matter report and will keep the account open.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd
- retrieved: -
- cited: -

### D09-virtual-assets-cash: expected enhanced, got None

> A customer of our digital currency exchange wants to buy virtual assets with large amounts of physical cash deposited over the counter.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-22
- retrieved: -
- cited: -
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-22(1) says enhanced CDD must be applied to a customer who deposits or receives physical currency for a service under item 50A of table 1 in s 6 of the Act. Confirm item 50A covers this exchange service. | earlier note: Rule 6-22 sets ECDD measures for cash-funded virtual asset services; whether it is itself a trigger should be confirmed. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D11-domestic-pep-medium-risk: expected standard, got None

> A sitting member of an Australian state parliament opens a home loan offset account. Screening finds nothing adverse and our methodology rates her as medium risk.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Domestic PEP: enhanced CDD only if ML/TF risk is high. Over-applying ECDD here counts as an error.

### D15-foreign-branch-same-country-pep: expected enhanced, got None

> Our bank's branch in Singapore opens an account for a Singaporean government minister. The relationship is managed entirely by that branch and we rate the customer as medium risk.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-pep, austrac-ecdd
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: CORRECTED from standard. AUSTRAC 'Politically exposed persons' (updated 29 Jul 2026), 'Important note about foreign PEPs if you provide designated services in a foreign country', lets a foreign PEP be treated as domestic only for senior manager approval, source of funds/wealth and KYC review (rules 5-5(2), 6-23(3), 6-24(2)); the enhanced CDD obligation for foreign PEPs (Act s 32; AUSTRAC 'Enhanced customer due diligence' (updated 15 Jul 2026), 'Foreign politically exposed persons') has no such exception. The earlier check confirmed only rule 6-23(3), which covers source of wealth and funds, not the enhanced CDD trigger. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): confirmed by rule 6-23(3). | earlier note: Rule 6-23 lets a foreign branch treat a PEP of its own country as a domestic PEP. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D16-standard-individual: expected standard, got None

> Emily Walker, an Australian-resident nurse, opens an everyday transaction account in a branch. She is not a PEP, has no links to high-risk countries, and our methodology rates her as medium risk.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -

### D17-standard-individual-paraphrase: expected standard, got None

> New customer: Daniel Costa, a local high-school teacher who was born in England and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -

### D18-sole-trader: expected standard, got None

> Jack Thompson, a self-employed electrician trading under a registered business name with an ABN, opens a business account. Risk rating medium; no PEP or sanctions matches.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-1, austrac-cdd-sole-traders
- retrieved: -
- cited: -

### D19-private-company: expected standard, got None

> An Australian proprietary company that runs a café opens a business account. It has two directors who each own 50% of the shares. Medium risk, no PEP matches.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-2, austrac-cdd-body-corporate
- retrieved: -
- cited: -

### D20-family-trust: expected standard, got None

> An Australian discretionary family trust with a corporate trustee opens an investment account. Medium risk, no PEP connections.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-3, austrac-cdd-trust
- retrieved: -
- cited: -

### D22-unincorporated-association: expected standard, got None

> A local amateur football club, an unincorporated association with no owners, opens an account to collect membership fees. The committee president is our contact. We rate the club as medium risk.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-2, rules2025::6-8
- retrieved: -
- cited: -

### D23-smsf-trap: expected standard, got None

> The trustees of a self-managed superannuation fund registered with the ATO open an account. Risk is low. They ask us not to identify the fund's beneficial owners because the fund is regulated by the ATO.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-18
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier KEPT (interpretation; reviewer to confirm). AUSTRAC 'Initial CDD for trust' (updated 5 May 2026), 'When you don't need to check beneficial owners', limits the relief to an entity 'subject to regulatory oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements' and gives APRA-regulated superannuation as the example. An SMSF is regulated by the ATO, a tax regulator, and is controlled by its own members, so the relief does not clearly apply. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers a person 'subject to oversight by a prudential, insurance, or investor protection regulator through registration or licensing requirements'. The text does not expressly exclude ATO-regulated SMSFs; decide whether the ATO counts before relying on this item. | earlier note: ATO-registered SMSFs are excluded from the 'actively regulated' simplification in rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D24-asic-registration-trap: expected standard, got None

> A newly registered Australian proprietary company with low ML/TF risk asks us not to identify its beneficial owners because it is registered with ASIC.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-18
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier KEPT. AUSTRAC 'Initial CDD for body corporate' (updated 25 Aug 2026), 'Low risk customers', gives banks, insurers and businesses holding an Australian Financial Services Licence as examples of regulatory oversight; ordinary company registration with ASIC is not oversight 'by a prudential, insurance, or investor protection regulator'. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-18(1)(b)(ii) covers oversight 'through registration or licensing requirements'. Whether ordinary ASIC company registration counts is not settled by the text; decide before relying on this item. | earlier note: Ordinary ASIC registration is not active regulation for rule 6-18. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D28-commonwealth-department: expected simplified/standard, got None

> A Commonwealth government department opens an account to receive application fees. We rate the ML/TF risk as low.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-7, rules2025::6-4
- retrieved: -
- cited: -
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): the 2026 amendments moved beneficial-owner relief for government bodies and government-controlled entities from rule 6-18 to rule 6-7(1A)/(1B), which does not depend on simplified CDD.

### D29-apra-regulated-insurer: expected simplified/standard, got None

> An APRA-regulated general insurer opens a business account with us. Our assessment rates it as low risk and there are no enhanced CDD indicators.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-18
- retrieved: -
- cited: -

### D30-asx-listed-company: expected simplified/standard, got None

> A company listed on the ASX, and subject to its continuous disclosure rules, opens a corporate account. Low risk, no unusual activity.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-7
- retrieved: -
- cited: -

### D31-strata-owners-corporation: expected simplified/standard, got None

> The owners corporation of a residential strata scheme opens an account for its levies. We rate it as low risk.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-18
- retrieved: -
- cited: -

### D33-low-risk-pensioner: expected simplified/standard, got None

> A retired Australian pensioner opens a term deposit funded from her existing account at another Australian bank. She is not a PEP and we rate her as low risk.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-17, rules2025::6-16
- retrieved: -
- cited: -

### D40-charitable-trust: expected standard, got None

> A registered charitable trust that funds scholarships opens an account. Its trustee is an Australian company run by volunteers. We rate it as medium risk and there are no PEP or sanctions matches.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-3, austrac-cdd-trust
- retrieved: -
- cited: -

### D41-unit-trust-foreign-pep: expected enhanced, got None

> An Australian unit trust opens an investment account through its corporate trustee. One investor holds 30% of the units and is a serving minister in a foreign government.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier CONFIRMED. AUSTRAC 'Enhanced customer due diligence' (updated 15 Jul 2026), 'Foreign politically exposed persons': enhanced CDD applies when any person on whose behalf the customer receives the service, 'such as a beneficiary of a trust', is a foreign PEP, so the 30% unit holder triggers it whether or not they are also a beneficial owner. | earlier: Assumes a 25% ownership threshold for beneficial owners. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot. Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D42-trust-formed-high-risk: expected enhanced, got None

> A trust established under the laws of a country that is subject to a FATF call for action wants to open an account in Australia to hold investment funds.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd, austrac-high-risk-countries
- retrieved: -
- cited: -

### D43-testamentary-trust: expected standard, got None

> The executor of a deceased estate, acting as trustee of a testamentary trust created by the will, opens an account. The beneficiaries are 'the grandchildren of the deceased'. Medium risk, no PEP matches.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-3, austrac-cdd-trust
- retrieved: -
- cited: -

### D44-sole-trader-high-risk-country: expected enhanced, got None

> A freelance graphic designer operating as a sole trader, who lives in and works from a country subject to a FATF call for action, wants to open an Australian business account to receive payments.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: austrac-ecdd, austrac-high-risk-countries
- retrieved: -
- cited: -

### D45-sole-trader-low-risk: expected simplified/standard, got None

> A bookkeeper who has traded as a sole trader for 15 years opens a second business account funded from her existing Australian bank account. She is not a PEP and we rate her as low risk.

- **error:** Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s.
- expected sections: rules2025::6-17, rules2025::6-16
- retrieved: -
- cited: -

### D46-sole-trader-no-standard-id: expected standard, got None

> A sole trader running a mobile cleaning business recently arrived in Australia on a humanitarian visa and has no passport or driver licence. He has a letter from a government agency confirming his identity. We rate him as medium risk; he is not a PEP.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-10
- retrieved: -
- cited: -
- gold note: Tests that missing standard ID is handled through alternative verification, not escalation. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D47-local-council: expected simplified/standard, got None

> A local council opens an account to hold building-permit bonds. We rate the ML/TF risk as low.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-7, rules2025::6-4
- retrieved: -
- cited: -
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): the 2026 amendments moved beneficial-owner relief for government bodies and government-controlled entities from rule 6-18 to rule 6-7(1A)/(1B), which does not depend on simplified CDD.

### D48-state-owned-corporation: expected simplified/standard, got None

> A water corporation wholly owned by a state government opens a corporate account. Low risk, no unusual activity.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-7
- retrieved: -
- cited: -
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): the 2026 amendments moved beneficial-owner relief for government bodies and government-controlled entities from rule 6-18 to rule 6-7(1A)/(1B), which does not depend on simplified CDD.

### D49-embassy-ambassador-signatory: expected enhanced, got None

> A foreign country's embassy in Canberra opens an account for its operating costs. The ambassador will be the main account signatory. The country is not on any FATF list and we would otherwise rate the customer as medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: austrac-ecdd, austrac-pep
- retrieved: -
- cited: -
- gold note: Checked 2026-10-01 against AUSTRAC guidance: expected tier CONFIRMED. AUSTRAC 'Enhanced customer due diligence' (updated 15 Jul 2026), 'Foreign politically exposed persons', and AUSTRAC 'Politically exposed persons' (updated 29 Jul 2026), 'Enhanced CDD obligations', both require enhanced CDD when 'any person acting on behalf of the customer' is a foreign PEP; the PEP definition includes ambassadors. Reference answer corrected: rules 6-23 and 5-5 (source of wealth/funds, senior manager approval) cover the customer, beneficial owners and persons on whose behalf the service is received, not persons acting on the customer's behalf. | earlier: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): rule 6-23(1) covers the customer, a beneficial owner, or a person on whose behalf the customer receives the service. It does not mention a person acting on the customer's behalf, such as a signatory. The expected tier may be wrong; check s 32 of the Act. | earlier note: Assumes an ambassador is a foreign PEP and that rule 6-23 covers persons acting on behalf of the customer. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### D50-church-group: expected standard, got None

> A small community church group, an unincorporated association, opens an account for weekly offerings. The treasurer will operate it. Medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-2, rules2025::6-8
- retrieved: -
- cited: -

### D51-assoc-domestic-pep-treasurer: expected standard, got None

> A residents' association (unincorporated) opens an account. Its treasurer, who will sign on the account, is a sitting member of the federal House of Representatives. No adverse media; medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -

### D52-assoc-unusual-cash: expected enhanced, got None

> A newly formed unincorporated association receives large cash donations it cannot explain and asks us to send the money overseas straight away. It gives no clear purpose for the transfers.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-20, austrac-ecdd
- retrieved: -
- cited: -

### D53-law-partnership: expected standard, got None

> A law firm run as a general partnership of four solicitors opens an office account. No partner is a PEP; we rate the firm as medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-2, austrac-cdd-body-corporate
- retrieved: -
- cited: -

### D54-partnership-foreign-pep: expected enhanced, got None

> An accounting partnership opens a business account. One of its three equal partners is a serving member of a foreign national parliament.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D55-farming-partnership: expected standard, got None

> A husband and wife run a farm as a partnership and open an account for grain sales. Medium risk, no PEP matches.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-2
- retrieved: -
- cited: -

### D16-cf-aisha-rahman: expected standard, got None

> Aisha Rahman, an Australian-resident nurse, opens an everyday transaction account in a branch. She is not a PEP, has no links to high-risk countries, and our methodology rates her as medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D16-standard-individual: only the name/country changes.

### D16-cf-nguyen-thi-lan: expected standard, got None

> Nguyen Thi Lan, an Australian-resident nurse, opens an everyday transaction account in a branch. She is not a PEP, has no links to high-risk countries, and our methodology rates her as medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D16-standard-individual: only the name/country changes.

### D16-cf-priya-sharma: expected standard, got None

> Priya Sharma, an Australian-resident nurse, opens an everyday transaction account in a branch. She is not a PEP, has no links to high-risk countries, and our methodology rates her as medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D16-standard-individual: only the name/country changes.

### D17-cf-born-india: expected standard, got None

> New customer: Daniel Costa, a local high-school teacher who was born in India and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D17: only the country of birth changes.

### D17-cf-born-china: expected standard, got None

> New customer: Daniel Costa, a local high-school teacher who was born in China and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D17: only the country of birth changes.

### D17-cf-born-greece: expected standard, got None

> New customer: Daniel Costa, a local high-school teacher who was born in Greece and has lived in Australia for 20 years, wants a basic account for his salary. Medium risk rating, no PEP match, no adverse media, no foreign connections.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: austrac-cdd-individuals
- retrieved: -
- cited: -
- gold note: Counterfactual of D17: only the country of birth changes.

### D01-cf-new-zealand: expected enhanced, got None

> Maria wants to open a savings account with us in Melbourne. During onboarding she tells us she is a serving deputy minister of finance in New Zealand. Apart from that, our risk methodology would rate her as medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Counterfactual of D01: a foreign PEP is a foreign PEP whichever country; tier must stay enhanced. Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D01-cf-united-kingdom: expected enhanced, got None

> Maria wants to open a savings account with us in Melbourne. During onboarding she tells us she is a serving deputy minister of finance in the United Kingdom. Apart from that, our risk methodology would rate her as medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Counterfactual of D01: a foreign PEP is a foreign PEP whichever country; tier must stay enhanced. Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D01-cf-india: expected enhanced, got None

> Maria wants to open a savings account with us in Melbourne. During onboarding she tells us she is a serving deputy minister of finance in India. Apart from that, our risk methodology would rate her as medium risk.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-23, austrac-pep
- retrieved: -
- cited: -
- gold note: Counterfactual of D01: a foreign PEP is a foreign PEP whichever country; tier must stay enhanced. Rule 5-5(1) (Compilation No. 1): a senior manager must approve before the service starts for a foreign PEP, or a domestic/international organisation PEP at high ML/TF risk; added 2026-10-01.

### D18-cf-mohammed-hassan: expected standard, got None

> Mohammed Hassan, a self-employed electrician trading under a registered business name with an ABN, opens a business account. Risk rating medium; no PEP or sanctions matches.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-1, austrac-cdd-sole-traders
- retrieved: -
- cited: -
- gold note: Counterfactual of D18-sole-trader: only the name/country changes.

### D18-cf-tran-van-minh: expected standard, got None

> Tran Van Minh, a self-employed electrician trading under a registered business name with an ABN, opens a business account. Risk rating medium; no PEP or sanctions matches.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-1, austrac-cdd-sole-traders
- retrieved: -
- cited: -
- gold note: Counterfactual of D18-sole-trader: only the name/country changes.

### D18-cf-kwame-mensah: expected standard, got None

> Kwame Mensah, a self-employed electrician trading under a registered business name with an ABN, opens a business account. Risk rating medium; no PEP or sanctions matches.

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-1, austrac-cdd-sole-traders
- retrieved: -
- cited: -
- gold note: Counterfactual of D18-sole-trader: only the name/country changes.

### E02-sow-vs-sof: abstained on an answerable question

> What is the difference between source of wealth and source of funds?

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-21
- retrieved: -
- cited: -

### E03-trust-kyc: abstained on an answerable question

> What KYC information do we need to collect for a trust customer?

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-3, austrac-cdd-trust
- retrieved: -
- cited: -

### E04-pre-reform-customers: abstained on an answerable question

> Do we need to re-verify customers we already identified before 31 March 2026?

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-42
- retrieved: -
- cited: -
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): confirmed by rule 6-42. | earlier note: Transitional rule 6-42. Legal basis inferred from secondary summaries of the Rules; confirm against the locked snapshot.

### E05-unidentifiable-beneficial-owner: abstained on an answerable question

> What should we do if we cannot identify a company's beneficial owners after taking reasonable steps?

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-8
- retrieved: -
- cited: -

### E06-nested-review-frequency: abstained on an answerable question

> How often must we review a nested services relationship?

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-26
- retrieved: -
- cited: -

### E08-simplified-beneficial-owners: abstained on an answerable question

> Which customers can we skip detailed beneficial owner identification for?

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-7, rules2025::6-18
- retrieved: -
- cited: -
- gold note: Checked against Rules 2025 Compilation No. 1 (31 Mar 2026): the 2026 amendments moved beneficial-owner relief for government bodies and government-controlled entities from rule 6-18 to rule 6-7(1A)/(1B), which does not depend on simplified CDD.

### E10-ecdd-triggers: abstained on an answerable question

> What situations make enhanced customer due diligence mandatory?

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: austrac-ecdd
- retrieved: -
- cited: -

### E12-delayed-verification: abstained on an answerable question

> When can we delay verifying a customer's identity until after we start providing the service?

- **error:** Is Ollama running at http://localhost:11434? Start it with `ollama serve`. Then make sure the model is pulled: `ollama pull qwen3-embedding:8b`.
- expected sections: rules2025::6-12, austrac-delayed-cdd
- retrieved: -
- cited: -


## Unsupported claims (0)

