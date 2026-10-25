# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.3
- Gold file: `data/gold/adversarial.jsonl`: 8 items (0 reviewed, 8 draft)
- Duration: 1086.1 s (answering 782.6 s, then grading 303.6 s); finished 2026-10-24T17:33:48+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.667 | ≥ 0.8 | **FAIL** |
| mandatory_ecdd_recall | 1.000 | ≥ 1.0 | PASS |
| under_application_rate_max | 0.000 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 1.000 | ≥ 0.8 | PASS |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.508 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.714 | ≥ 0.8 | **FAIL** |
| unanswerable_abstain_rate | 0.500 | ≥ 0.75 | **FAIL** |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | n/a | ≤ 0.0 | n/a |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.667 |
| tier_accuracy_strict | 0.667 |
| mandatory_ecdd_recall | 1.000 |
| under_application_rate | 0.000 |
| over_application_rate | 0.333 |
| retrieval_recall_at_k | 1.000 |
| citation_validity | 1.000 |
| citation_precision | 0.508 |
| citation_recall | 1.000 |
| faithfulness | 0.714 |
| key_fact_recall | n/a |
| unanswerable_abstain_rate | 0.500 |
| false_abstain_rate | 0.000 |
| consistency_agreement | n/a |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | 1.000 |
| walert_ndcg_at_5 | 0.729 |
| walert_rouge1_f1 | 0.300 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 102.150 |
| latency_p95_s | 117.480 |

## Answer checks

Citation validity means each citation points to a passage that was really retrieved. Whether that passage supports the claim is measured separately (faithfulness, below).

- Answers with a point that cites nothing: 0
- Answers that call a fact the scenario rules out unknown: 0

## Tier determination (6 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 0 | 0 | 0 | 0 |
| **standard** | 0 | 3 | 2 | 0 |
| **enhanced** | 0 | 0 | 1 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 6 | 0.667 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 5 | 0.600 |
| medium | 1 | 1.000 |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | 1.000 | 1 |
| % unanswered, underspecified scenarios | 0.000 | 1 |
| NDCG@1 (inferred questions) | 0.667 | 6 |
| NDCG@3 (inferred questions) | 0.747 | 6 |
| NDCG@5 (inferred questions) | 0.729 | 6 |
| NDCG@1 (all questions) | 0.667 | 6 |
| NDCG@3 (all questions) | 0.747 | 6 |
| NDCG@5 (all questions) | 0.729 | 6 |
| ROUGE-1 F1 vs reference answers | 0.300 | 6 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 8 | 0.500 | 1.000 |
| required_measures | 22 | 0.636 | 0.955 |
| rule | 9 | 0.889 | 1.000 |
| scenario_fact | 10 | 0.900 | 1.000 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.667** supported by the judge.

## Failures

### A04-payments-only-unknown: expected standard/insufficient_information, got enhanced

> An Australian company regularly makes payments to suppliers located in a jurisdiction that FATF has called for enhanced CDD to be applied. We know nothing else about the company's owners or the people who act for it.

- summary: Enhanced CDD is required because the customer (an Australian company) has a connection to a high-risk jurisdiction, which triggers mandatory enhanced due diligence under AUSTRAC guidance.
- guardrails fired: high_risk_jurisdiction (escalated: False)
- expected sections: austrac-ecdd
- retrieved: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, rules2025::6-7::0, rules2025::6-7::1, austrac-ecdd::introduction::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high--example-identifying-high-ml-tf-risk-duri-2::0
- cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-ecdd::introduction::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0
- gold note: Control for A01 (added 3 Oct 2026): here the owners' location really is unknown, so listing it as missing information is correct. Together A01 and A04 test that the assistant tells 'the scenario says no' from 'the scenario doesn't say'.

### A05-payments-only-no-other-trigger: expected standard/insufficient_information, got enhanced

> A customer regularly sends payments to suppliers in a FATF high-risk jurisdiction. The customer, beneficial owners, persons acting on its behalf, and persons on whose behalf it receives the service are all explicitly stated not to be physically present in or formed in that jurisdiction. No other ECDD trigger is identified. Should the customer automatically receive Enhanced CDD?

- summary: The customer does not automatically receive Enhanced CDD because the mandatory trigger regarding physical presence or formation in a high-risk jurisdiction is not met.
- guardrails fired: high_risk_jurisdiction (escalated: True)
- expected sections: austrac-ecdd
- retrieved: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-cdd-overview::enhanced-customer-due-diligence::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high--example-identifying-high-ml-tf-risk-duri-2::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0, austrac-reliance::what-to-consider-before-entering-into-a--relying-on-a-third-party-in-a-foreign-co::0
- cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-cdd-overview::enhanced-customer-due-diligence::0, austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0
- gold note: Adversarial test added 5 Oct 2026. Prompt v3.2 answered Enhanced CDD: fact extraction read the supplier payments as 'ML/TF risk: high', which the scenario never states, and the high-risk guardrail and the answer both relied on it; the S8 example measures were also shown as 'required by the rules'. Expected: no trigger established, so standard CDD (or insufficient information, since no risk rating is given).

### A07-contradictory-beneficial-owner-location: answered an unanswerable question

> An Australian private company wants to open a business account. The application says its sole beneficial owner is not physically present in any jurisdiction that FATF has called for enhanced CDD to be applied. The identity documents attached to the same application show that this beneficial owner lives in a country that FATF has called for enhanced CDD to be applied. We rate the customer as medium risk and nobody involved is a politically exposed person.

- summary: Enhanced CDD is required because a beneficial owner of the company is located in a FATF high-risk jurisdiction, which triggers mandatory enhanced CDD under AUSTRAC guidance.
- guardrails fired: high_risk_jurisdiction (escalated: False)
- expected sections: -
- retrieved: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-ecdd::when-you-must-apply-enhanced-cdd--the-customers-ml-tf-risk-is-high--example-identifying-high-ml-tf-risk-duri-2::0, rules2025::6-7::1, austrac-cdd-body-corporate::when-you-dont-need-to-check-beneficial-o--publicly-listed-companies-and-government::0, austrac-ecdd::introduction::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0, austrac-high-risk-countries::high-risk-countries-and-regions::0
- cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0
- gold note: Set C A6 (ChatGPT's suggested tests, reviewed 5 Oct 2026). The application and the identity documents disagree about where the beneficial owner lives, so the location is not yet established on reasonable grounds. AUSTRAC's guidance on inconsistent KYC information (austrac-initial-cdd, 'Inconsistencies or discrepancies in customer information') says to resolve the inconsistency, and if a matter can't be established on reasonable grounds the service must not start. Best answer: say the facts conflict and the location must be confirmed before a tier is decided. Standard (trusting the first statement) would under-apply; enhanced (trusting the second) is the cautious reading but settles the conflict silently, so it also fails here. The assistant has no contradiction check yet, so this item is expected to fail until one is added.


## Unsupported claims (14)

- **A01-payments-only-ruled-out** [conclusion]: Since the scenario confirms no one associated with the customer is located or formed in the high-risk jurisdiction, the mandatory trigger for Enhanced CDD does not apply. No other enhanced triggers are mentioned, and simplified conditions are not established, so the tier is standard. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0)_
- **A01-payments-only-ruled-out** [required_measures]: Establish the identity of the customer (the company). _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **A01-payments-only-ruled-out** [required_measures]: Determine if any beneficial owner is a PEP or designated for TFS. _(cited: austrac-cdd-body-corporate::matters-you-must-establish::0)_
- **A02-grey-list-not-call-for-action** [required_measures]: Monitor transactions on an ongoing basis appropriate to the medium risk rating. _(cited: austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **A03-call-for-action-measures-risk-based** [required_measures]: Collect and verify information on the beneficial owners of the company. _(cited: rules2025::6-7::1)_
- **A03-call-for-action-measures-risk-based** [required_measures]: Establish whether any beneficial owner is a politically exposed person or designated for sanctions. _(cited: rules2025::6-7::1)_
- **A05-payments-only-no-other-trigger** [conclusion]: Since none of the specified persons are located or formed in that jurisdiction, the mandatory condition for enhanced CDD under S1 and S2 is not met. The scenario does not state the ML/TF risk is high (S4, S6), nor does it identify other triggers. Therefore, standard CDD applies. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0, austrac-cdd-overview::enhanced-customer-due-diligence::0)_
- **A05-payments-only-no-other-trigger** [conclusion]: Escalated by guardrail: the scenario indicates the customer is connected to a high-risk jurisdiction. The cited source treats this as requiring enhanced CDD. A compliance officer should confirm. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0)_
- **A05-payments-only-no-other-trigger** [required_measures]: Conduct initial customer due diligence to identify the customer and verify their identity. _(cited: austrac-cdd-overview::enhanced-customer-due-diligence::0)_
- **A05-payments-only-no-other-trigger** [required_measures]: Assess and manage ML/TF risks based on the transaction pattern (payments to high-risk jurisdiction) without applying mandatory enhanced CDD measures. _(cited: austrac-high-risk-countries::high-risk-countries-and-regions::0, austrac-ecdd::enhanced-cdd-measures-you-can-apply::0)_
- **A06-customer-known-no-other-trigger-info** [rule]: Enhanced CDD is also required if the customer is a PEP, but the scenario does not state this and does not require us to assume it. _(cited: austrac-initial-cdd::what-you-must-establish-during-initial-c::0)_
- **A06-customer-known-no-other-trigger-info** [required_measures]: Check whether any beneficial owner or related person is a PEP or designated for sanctions. _(cited: austrac-initial-cdd::what-you-must-establish-during-initial-c::0)_
- **A07-contradictory-beneficial-owner-location** [scenario_fact]: The application shows that the sole beneficial owner lives in a country that FATF has called for enhanced CDD to be applied. _(cited: none)_
- **A07-contradictory-beneficial-owner-location** [conclusion]: Since the beneficial owner is in a FATF high-risk jurisdiction, the mandatory trigger applies. The customer's medium risk rating and the fact that they are not a PEP do not override this specific requirement. _(cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--a-person-located-or-formed-in-a-high-ris::0, austrac-high-risk-countries::high-risk-countries-and-regions--fatf-high-risk-and-non-cooperative-juris::0)_
