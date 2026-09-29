"""AML/CTF CDD compliance assistant: a test-driven RAG pipeline over AUSTRAC guidance."""

__version__ = "0.1.0"

TIERS = ("simplified", "standard", "enhanced")
ABSTAIN = "insufficient_information"
TIER_ORDER = {"simplified": 0, "standard": 1, "enhanced": 2}
