# Gold-standard test set

`scenarios.jsonl` holds one test item per line. 74 items:

- **47 tier-determination scenarios**: 20 enhanced, 17 standard, 8 simplified, 2 not determinable. The 45 answerable ones cover individuals (10), companies (9), trusts (7), sole traders (6), government bodies (5), unincorporated associations (4), partnerships (3) and one strata owners corporation.
- **12 counterfactual variants** of four scenarios, changing only a name, country of birth, or a foreign PEP's country (fairness).
- **8 plain-language explanation questions.**
- **7 out-of-knowledge-base questions** the assistant should decline (Walert's out-of-KB category).

**Every item is `status: draft`.** The expected answers were drafted from secondary summaries of Part 6 of the AML/CTF Rules 2025 and the structure of AUSTRAC's CDD guidance. Before reporting results, a team member should check each item against the **locked snapshot** and mark it reviewed.

## Fields

| Field | Meaning |
|---|---|
| `id` | Unique, descriptive (`D02-foreign-pep-beneficial-owner`). `D` = determine, `E` = explain, `U` = unanswerable. |
| `mode` | `determine` or `explain`. |
| `query` | The scenario or question, written the way a compliance officer would type it. |
| `answerable` | `false` if the knowledge base cannot or should not answer it. |
| `expected_tier` | Best answer for `determine` items: `simplified`, `standard`, `enhanced`, or `insufficient_information` (unanswerable only). |
| `acceptable_tiers` | Every tier that would be compliant and reasonable. Low-risk customers who may get simplified CDD also accept `standard`. |
| `mandatory_ecdd` | `true` if enhanced CDD is mandatory (feeds `mandatory_ecdd_recall`). |
| `expected_sections` | Highly relevant references (NDCG grade 2): what the answer should rest on. A document id (`austrac-ecdd`), a section (`rules2025::6-23`, `amlctf-act::32`) or a chunk id. |
| `partial_sections` | Partially relevant references (grade 1): useful context, not decisive. |
| `reference_answer` | A short written answer in the assistant's style, used for ROUGE-1 and BERTScore. Required for answerable items. |
| `answer_type` | Walert's category: `known`, `inferred`, `out_of_kb`, or `underspecified`. |
| `counterfactual_of` | For fairness variants: the id of the base scenario. The variant must expect exactly the same answer. |
| `key_facts` | `explain` items only: a list of facts, each a list of alternative phrases; a fact counts if any alternative appears in the answer. |
| `customer_type` | For the per-customer-type breakdown. |
| `group` | Items that should get the same tier (paraphrases, or one trigger across customer types). |
| `tags`, `difficulty` | Free-form; `trap` marks items built to catch a plausible wrong answer. |
| `status`, `reviewer` | `draft` → `reviewed` + reviewer's name. |
| `notes` | Why the answer is what it is, and anything a reviewer should check. |

`amlrag` validates the file on load (unknown fields, a tier outside `acceptable_tiers`, a `mandatory_ecdd` item not expecting `enhanced`, and so on), and `tests/test_eval.py` checks it on every `pytest` run.

## Review procedure

For each item:

1. Read the query and decide the tier yourself from the locked snapshot (`amlrag stats --grep "<term>"` finds passages quickly).
2. Check `expected_tier`, `acceptable_tiers` and `mandatory_ecdd` against the rule or guidance that decides it.
3. Check every `expected_sections` reference exists in `kb/processed/chunks.jsonl` and actually carries the rule. Move references that are useful but not decisive to `partial_sections`; remove ones that are only tangential.
4. Check the `reference_answer` says what the guidance actually requires, in one to three sentences. It is scored word-for-word, so keep it in plain English and in the same style as the assistant.
5. Resolve anything the `notes` field flags as needing confirmation (for example whether immediate family members of PEPs fall within the amended definition, or how rule 6-22 applies).
6. Set `"status": "reviewed"` and `"reviewer": "<name>"`. When a base scenario changes, update its counterfactual variants to match.

Items flagged in `notes` as needing confirmation: D03, D09, D14, D15, D23, D24, D41, D46, D49, E04. Resolve these first.

Counterfactual variants avoid countries on FATF lists so that only the name or birthplace changes; if FATF's lists change before your snapshot, check none of the named countries has been added.

## Adding items

Aim for coverage rather than volume: each new item should test a different rule, customer type or failure mode. Good additions are paraphrases of existing items (same `group`), traps where one fact overrides an otherwise simple answer, and questions from real team members that the assistant got wrong in the **Review gaps** tab.
