# Gold-standard test set

`scenarios.jsonl` holds one test item per line. 74 items:

- **47 tier-determination scenarios**: 20 enhanced, 17 standard, 8 simplified, 2 not determinable. The 45 answerable ones cover individuals (10), companies (9), trusts (7), sole traders (6), government bodies (5), unincorporated associations (4), partnerships (3) and one strata owners corporation.
- **12 counterfactual variants** of four scenarios, changing only a name, country of birth, or a foreign PEP's country (fairness).
- **8 plain-language explanation questions.**
- **7 out-of-knowledge-base questions** the assistant should decline (Walert's out-of-KB category).

**Adversarial set (`adversarial.jsonl`, 4 items, added 3 October 2026).** Hand-made trick cases kept apart from the 74 so earlier runs stay comparable. Run them with `amlrag eval --gold data/gold/adversarial.jsonl`.

- **A01 / A04:** payments to suppliers in a FATF call-for-action country. In A01 the scenario says the owners and agents are *not* there; in A04 it says nothing about them. The assistant must treat A01's denied facts as false, not missing (the report's "Answer checks" counts answers that don't), and may list A04's as missing.
- **A02:** a FATF grey-list country, which is not a call-for-action country.
- **A03:** a mandatory trigger. The answer should mark example measures as risk-based options, not as all required.

A01 and A03 failed under prompt v3.1, and prompt v3.2 was written to fix them: the tests came first.

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

Items still needing a reviewer's decision: D09, D23, D46 (see their `notes`). D03, D14, D15, D24, D41 and D49 were settled against AUSTRAC's own guidance on 2026-10-01 (below).

Several items were checked against the text of **Rules 2025 Compilation No. 1 (31 March 2026)**; their `notes` start "Checked against…". Two findings changed the set: the 2026 amendments moved beneficial-owner relief for government bodies from rule 6-18 to rule 6-7(1A)/(1B), so D28, D35, D47, D48 and E08 now cite 6-7; and rule 6-22(1) makes enhanced CDD mandatory for cash-funded virtual asset services, so D09 is now `mandatory_ecdd`. D15 and E04 were confirmed. The notes on D23, D24 and D49 explain where the text doesn't support the draft answer as clearly as assumed. Checking a live answer later showed a gap in the knowledge base itself: rule 5-5(1) (in Part 5, which was not indexed) requires senior manager approval before serving a foreign PEP, or a domestic or international organisation PEP whose ML/TF risk is high. Rule 5-5 is now indexed, and the ten PEP items where it applies (D01 and its three variants, D02, D03, D10, D14, D41, D54) list it in `partial_sections` and mention the approval in their reference answers. D49 does not: its PEP is a signatory acting for the customer, which 5-5(1) doesn't cover.

**Checked against AUSTRAC's guidance pages (2026-10-01).** The first baseline run (`results/20261001-031851-full-…`) got eight items wrong, and checking them against the saved AUSTRAC pages in `kb/manual/` changed three gold items:

- **D15 was wrong and is now `enhanced` (mandatory).** AUSTRAC's PEP page says a foreign PEP served through a branch in their own country may be treated as a domestic PEP only for senior manager approval, source of wealth/funds and KYC review. The enhanced CDD obligation for foreign PEPs (Act s 32) has no such exception. The earlier "confirmed by rule 6-23(3)" check looked only at the Rules, and rule 6-23 covers source of wealth and funds, not the enhanced CDD trigger.
- **D49 is confirmed `enhanced`**: AUSTRAC's ECDD and PEP pages both list "any person acting on behalf of the customer" among the people whose foreign PEP status triggers enhanced CDD. Its reference answer no longer claims source of wealth/funds and senior manager approval are required, because rules 6-23 and 5-5 don't extend to a person acting on the customer's behalf.
- **D24 is confirmed `standard`**: AUSTRAC's examples of "regulatory oversight" are banks, insurers and licensed financial services businesses, not ordinary ASIC company registration. **D23 is kept as `standard`** on the same reasoning (an SMSF is regulated by the ATO, not a prudential, insurance or investor protection regulator), but the guidance doesn't name SMSFs, so a reviewer should confirm it.
- D03, D14 and D41 are confirmed by AUSTRAC's definitions (appointors are beneficial owners; family members of foreign PEPs are foreign PEPs; trust beneficiaries trigger enhanced CDD).

Lesson for the method: the Rules alone are not enough to write gold answers. Several triggers sit in the Act (here, s 32) and AUSTRAC's guidance states them; check both.

Counterfactual variants avoid countries on FATF lists so that only the name or birthplace changes; if FATF's lists change before your snapshot, check none of the named countries has been added.

## Adding items

Aim for coverage rather than volume: each new item should test a different rule, customer type or failure mode. Good additions are paraphrases of existing items (same `group`), traps where one fact overrides an otherwise simple answer, and questions from real team members that the assistant got wrong in the **Review gaps** tab.
