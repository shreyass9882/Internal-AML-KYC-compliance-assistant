# Results by item: retrieval-stress.jsonl

*found@8*: expected references in the top 8 retrieved passages. *1st*: rank of the first one. *facts*: share of the item's key facts in the answer. *cites ok*: share of cited passages that are expected or partially relevant references. An Explain item passes when it answers, finds at least one expected passage in the top 8 and contains at least 60% of its key facts. A Determine item passes when its tier is one of the acceptable tiers. A question the assistant should decline passes only when it declines.

| | item | result | found@8 | 1st | facts | cites ok | missing key facts |
|---|---|---|---|---|---|---|---|
| ✓ | R01-initial-cdd-matters | answered | 1/1 | 2 | 67% | 33% | authority to act, sanction, nature and purpose |
| ✗ | R02-body-corporate-beneficial-owners | answered | 2/3 | 3 | 40% | 83% | ownership and control, 25%, politically exposed |
| ✓ | R03-person-acting-on-behalf | answered | 1/4 | 1 | 60% | 67% | politically exposed, additional ml/tf risk |
| ✗ | R04-ecdd-mandatory-circumstances | answered | 1/6 | 5 | 33% | 50% | suspicious matter, unusual, nested, foreign politically exposed |
| ✓ | R05-ecdd-measures-high-risk | answered | 1/1 | 1 | 80% | 50% | monitoring |
| ✓ | R06-call-for-action-vs-increased-monitoring | answered | 2/2 | 1 | 67% | 57% | called for enhanced |
| ✓ | R07-delayed-initial-cdd | answered | 1/1 | 3 | 100% | 75% |  |
| ✓ | R08-pep-matters | answered | 2/3 | 4 | 83% | 75% | senior manager |

**6 of 8 passed.**
