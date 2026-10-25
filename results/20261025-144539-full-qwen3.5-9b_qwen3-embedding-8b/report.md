# Evaluation report: preset `full`

- Generator: `ollama:qwen3.5:9b`; embedder: `ollama:qwen3-embedding:8b`; judge: `ollama:llama3.1:8b`
- Knowledge-base snapshot: 2026-09-30 (index digest `6a09f4b4a9e9a849`)
- Answer instructions: prompt version 3.3
- Gold file: `data/gold/heldout.jsonl`: 12 items (0 reviewed, 12 draft)
- Duration: 1587.4 s (answering 1086.3 s, then grading 501.1 s); finished 2026-10-25T04:12:07+00:00

> Draft gold items have not yet been checked against the locked snapshot by a reviewer. Treat these numbers as provisional.

## Acceptance thresholds

| Check | Value | Limit | Result |
|---|---|---|---|
| tier_accuracy_acceptable | 0.909 | ≥ 0.8 | PASS |
| mandatory_ecdd_recall | 1.000 | ≥ 1.0 | PASS |
| under_application_rate_max | 0.000 | ≤ 0.05 | PASS |
| retrieval_recall_at_k | 0.818 | ≥ 0.8 | PASS |
| citation_validity | 1.000 | ≥ 1.0 | PASS |
| citation_precision | 0.430 | ≥ 0.6 | **FAIL** |
| faithfulness | 0.886 | ≥ 0.8 | PASS |
| unanswerable_abstain_rate | 1.000 | ≥ 0.75 | PASS |
| false_abstain_rate_max | 0.000 | ≤ 0.15 | PASS |
| fairness_tier_flip_rate_max | n/a | ≤ 0.0 | n/a |

## Headline metrics

| Metric | Value |
|---|---|
| tier_accuracy_acceptable | 0.909 |
| tier_accuracy_strict | 0.909 |
| mandatory_ecdd_recall | 1.000 |
| under_application_rate | 0.000 |
| over_application_rate | 0.091 |
| retrieval_recall_at_k | 0.818 |
| citation_validity | 1.000 |
| citation_precision | 0.430 |
| citation_recall | 0.682 |
| faithfulness | 0.886 |
| key_fact_recall | n/a |
| unanswerable_abstain_rate | 1.000 |
| false_abstain_rate | 0.000 |
| consistency_agreement | n/a |
| fairness_invariance | n/a |
| fairness_tier_flip_rate | n/a |
| walert_pct_unanswered_out_of_kb | n/a |
| walert_ndcg_at_5 | 0.640 |
| walert_rouge1_f1 | 0.281 |
| walert_bertscore_f1 | n/a |
| latency_p50_s | 92.920 |
| latency_p95_s | 96.430 |

## Answer checks

Citation validity means each citation points to a passage that was really retrieved. Whether that passage supports the claim is measured separately (faithfulness, below).

- Answers with a point that cites nothing: 0
- Answers that call a fact the scenario rules out unknown: 1

## Tier determination (11 answerable scenarios)

Rows are the expected tier, columns the assistant's final tier.

| expected \ predicted | simplified | standard | enhanced | insufficient_information |
|---|---|---|---|---|
| **simplified** | 1 | 0 | 0 | 0 |
| **standard** | 0 | 4 | 1 | 0 |
| **enhanced** | 0 | 0 | 5 | 0 |

| Customer type | n | Accuracy (acceptable) |
|---|---|---|
| company | 2 | 1.000 |
| individual | 6 | 0.833 |
| partnership | 1 | 1.000 |
| trust | 2 | 1.000 |

| Model confidence | n | Accuracy |
|---|---|---|
| high | 8 | 0.875 |
| medium | 3 | 1.000 |

## Walert-comparable measures

Same measures as Walert (Pathiyan Cherumanal et al., CHIIR 2024), so results can be set beside theirs. NDCG uses graded relevance: `expected_sections` = 2 (highly relevant), `partial_sections` = 1 (partially relevant).

| Measure | Value | n |
|---|---|---|
| % unanswered, out-of-knowledge-base questions | n/a | 0 |
| % unanswered, underspecified scenarios | 1.000 | 1 |
| NDCG@1 (known questions) | 0.591 | 11 |
| NDCG@3 (known questions) | 0.632 | 11 |
| NDCG@5 (known questions) | 0.640 | 11 |
| NDCG@1 (all questions) | 0.591 | 11 |
| NDCG@3 (all questions) | 0.632 | 11 |
| NDCG@5 (all questions) | 0.640 | 11 |
| ROUGE-1 F1 vs reference answers | 0.281 | 11 |
| BERTScore F1 (roberta-large) | n/a | 0 |

_BERTScore: skipped (bert-score not installed)._

## Faithfulness by kind of claim

Each claim is judged against its own evidence: a fact restated from the scenario against the scenario, a rule against the passages it cites, a conclusion against its cited passages and the scenario, and a measure or key point against its cited passages. Runs before prompt version 2 have no kinds, so their reasoning points appear as `reasoning`.

| Kind | n | Judge: supported | Lexical: supported |
|---|---|---|---|
| conclusion | 11 | 0.727 | 0.909 |
| required_measures | 39 | 0.923 | 0.949 |
| rule | 15 | 0.800 | 1.000 |
| scenario_fact | 14 | 1.000 | 1.000 |

Claims that must come from a source (all kinds except `scenario_fact`): **0.862** supported by the judge.

## Failures

### H08-smr-customer-is-victim: expected standard, got enhanced

> We lodged a suspicious matter report about a scam in which one of our customers, a retired teacher, was the victim: she was tricked into sending money to a fraudster. She is not suspected of any wrongdoing, she will keep her account with us, and our risk methodology rates her as medium risk.

- summary: Enhanced CDD is required because the scenario states there is an obligation to submit a suspicious matter report (SMR) for this customer and the entity intends to continue providing services.
- guardrails fired: smr_continuing (escalated: False)
- expected sections: austrac-ecdd
- retrieved: austrac-ecdd::when-you-must-apply-enhanced-cdd--youre-required-to-submit-a-suspicious-ma::0, austrac-ongoing-cdd::ongoing-cdd-obligations-overview::0, austrac-transitioning::customer-is-a-pre-commencement-customer--when-you-must-complete-initial-cdd-on-pr::0, austrac-initial-cdd::offences-that-apply-to-evasive-behaviour::0, austrac-ecdd::responding-to-enhanced-cdd-findings::0, rules2025::6-33::2, rules2025::6-9::0, austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0
- cited: austrac-ecdd::when-you-must-apply-enhanced-cdd--youre-required-to-submit-a-suspicious-ma::0, austrac-ongoing-cdd::ongoing-cdd-obligations-overview::0, austrac-ecdd::responding-to-enhanced-cdd-findings::0
- gold note: Held-out item written 25 Oct 2026, after development stopped (v3.3, 5 Oct); never used for tuning. Drafted with AI help and checked against the locked snapshot; not independently reviewed. Basis: AUSTRAC enhanced CDD page, 'You're required to submit a suspicious matter report': no enhanced CDD expected for a customer who isn't the subject of the suspicion, e.g. a victim of suspected fraud.


## Unsupported claims (9)

- **H01-intl-org-pep-medium** [rule]: Enhanced CDD is mandatory for international organisation PEPs only if the ML/TF risk is high. The scenario states the risk is medium, so this trigger does not apply. _(cited: rules2025::6-23::0, rules2025::6-24::0)_
- **H01-intl-org-pep-medium** [rule]: Enhanced CDD is also mandatory for foreign PEPs regardless of risk rating, but this customer is an international organisation PEP, not a foreign PEP. _(cited: austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0)_
- **H01-intl-org-pep-medium** [conclusion]: Since the enhanced CDD triggers do not apply and simplified CDD is not permitted for PEPs, the tier is standard. _(cited: rules2025::6-23::0, rules2025::6-24::0, austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0)_
- **H01-intl-org-pep-medium** [required_measures]: Identify and document the customer's ML/TF risk as medium. _(cited: austrac-initial-cdd::how-to-establish-matters-on-reasonable-g::0, austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **H02-trust-beneficiary-high-risk-jurisdiction** [required_measures]: Conduct enhanced due diligence measures appropriate to the high risk associated with the beneficiary's location (e.g., deeper background checks, understanding source of funds/wealth related to that jurisdiction). _(cited: austrac-cdd-trust::matters-you-must-establish::0, austrac-cdd-trust::politically-exposed-persons-and-sanction::0)_
- **H03-born-in-high-risk-country-lives-in-australia** [rule]: Enhanced CDD is also mandatory if the customer is a foreign PEP or has high ML/TF risk, neither of which applies to this medium-risk individual. _(cited: austrac-risk-ratings::step-1-develop-a-customer-risk-rating-sy--examples-of-customer-risk-ratings::0)_
- **H06-partnership-high-risk-rating** [conclusion]: Because the scenario involves large cash payments (matching the trigger in S6) and explicitly rates the risk as high, the tier is 'enhanced'. The requirement to apply enhanced CDD overrides any potential for simplified CDD. _(cited: austrac-ecdd::when-you-must-apply-specific-enhanced-cd--source-of-funds-and-source-of-wealth-whe--when-source-of-funds-and-source-of-wealt::0)_
- **H07-apra-superannuation-fund-low-risk** [required_measures]: Conduct PEP and TFS checks on the trustee (individual representative). _(cited: austrac-cdd-trust::when-you-dont-need-to-check-beneficial-o::1)_
- **H09-domestic-pep-family-member-medium** [conclusion]: Since the customer is not a PEP and her risk is medium (not high), enhanced CDD triggers do not apply. The scenario does not state that she meets conditions for simplified CDD, so standard CDD applies. _(cited: rules2025::6-23::0, austrac-pep::additional-obligations-for-peps--enhanced-cdd-obligations::0)_
