# Gold-standard test set

`scenarios.jsonl` holds one test item per line. 42 items: 31 tier determinations (14 enhanced, 10 standard, 5 simplified, 2 not determinable), 7 plain-language explanations, and 4 out-of-scope questions the assistant should refuse.

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
| `expected_sections` | References the answer should rest on: a document id (`austrac-ecdd`), a section (`rules2025::6-23`, `amlctf-act::32`) or a chunk id. |
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
3. Check every `expected_sections` reference exists in `kb/processed/chunks.jsonl` and actually carries the rule. Add missing ones; remove ones that are only tangential.
4. Resolve anything the `notes` field flags as needing confirmation (for example whether immediate family members of PEPs fall within the amended definition, or how rule 6-22 applies).
5. Set `"status": "reviewed"` and `"reviewer": "<name>"`.

Items flagged in `notes` as needing confirmation: D03, D09, D14, D15, D23, D24, E04. Resolve these first.

## Adding items

Aim for coverage rather than volume: each new item should test a different rule, customer type or failure mode. Good additions are paraphrases of existing items (same `group`), traps where one fact overrides an otherwise simple answer, and questions from real team members that the assistant got wrong in the **Review gaps** tab.
