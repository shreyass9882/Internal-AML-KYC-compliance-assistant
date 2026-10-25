# Results by item: adversarial.jsonl

*found@8*: expected references in the top 8 retrieved passages. *1st*: rank of the first one. *facts*: share of the item's key facts in the answer. *cites ok*: share of cited passages that are expected or partially relevant references. An Explain item passes when it answers, finds at least one expected passage in the top 8 and contains at least 60% of its key facts. A Determine item passes when its tier is one of the acceptable tiers. A question the assistant should decline passes only when it declines.

| | item | result | found@8 | 1st | facts | cites ok | missing key facts |
|---|---|---|---|---|---|---|---|
| ✗ | A01-payments-only-ruled-out | error: Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s. | 0/1 | - | - | - |  |
| ✗ | A02-grey-list-not-call-for-action | error: Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s. | 0/1 | - | - | - |  |
| ✗ | A03-call-for-action-measures-risk-based | error: Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s. | 0/1 | - | - | - |  |
| ✗ | A04-payments-only-unknown | error: Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s. | 0/1 | - | - | - |  |
| ✗ | A05-payments-only-no-other-trigger | error: Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s. | 0/1 | - | - | - |  |
| ✗ | A06-customer-known-no-other-trigger-info | error: Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s. | 0/2 | - | - | - |  |
| ✗ | A07-contradictory-beneficial-owner-location | error: Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s. | - | - | - | - |  |
| ✗ | A08-smr-deadline-out-of-kb | error: Ollama timed out after 240s on /api/embed. Try a smaller model (generation.fallback_model) or raise ollama.timeout_s. | - | - | - | - |  |

**0 of 8 passed.**
