# Results by item: adversarial.jsonl

*found@8*: expected references in the top 8 retrieved passages. *1st*: rank of the first one. *facts*: share of the item's key facts in the answer. *cites ok*: share of cited passages that are expected or partially relevant references. An Explain item passes when it answers, finds at least one expected passage in the top 8 and contains at least 60% of its key facts. A Determine item passes when its tier is one of the acceptable tiers. A question the assistant should decline passes only when it declines.

| | item | result | found@8 | 1st | facts | cites ok | missing key facts |
|---|---|---|---|---|---|---|---|
| ✓ | A01-payments-only-ruled-out | standard (expected standard) | 1/1 | 7 | - | 100% | called a ruled-out fact unknown |
| ✓ | A02-grey-list-not-call-for-action | standard (expected standard) | 1/1 | 2 | - | 75% |  |
| ✓ | A03-call-for-action-measures-risk-based | enhanced (expected enhanced) | 1/1 | 1 | - | 100% |  |
| ✗ | A04-payments-only-unknown | enhanced (expected standard) | 1/1 | 1 | - | 100% |  |

**3 of 4 passed.**
