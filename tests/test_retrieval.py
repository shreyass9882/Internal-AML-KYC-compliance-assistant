from amlrag.models import Chunk, Retrieved, ref_matches
from amlrag.retrieve.facts import normalise_facts, sub_queries
from amlrag.textutil import content_words, expand_abbreviations, tokenize


def test_tokenize_keeps_rule_numbers_and_normalises_section_refs():
    toks = tokenize("See rule 6-23 and section 32 of the Act (s 28).")
    assert "6-23" in toks
    assert "s32" in toks and "s28" in toks
    assert "s6" not in toks  # "section 6-23" must not produce a bogus s6 token
    assert "s6" not in tokenize("section 6-23 applies")


def test_expand_abbreviations():
    assert "politically exposed person" in expand_abbreviations("Is the PEP a risk?")
    assert "source of wealth" in expand_abbreviations("Check SoW")


def test_content_words_light_stemming():
    assert {"verify", "identity"} <= content_words("verifying identities")
    assert "the" not in content_words("the customer")


def test_ref_matches_is_boundary_aware():
    assert ref_matches("rules2025::6-23::0", "rules2025::6-23")
    assert ref_matches("rules2025::6-23::0", "rules2025")
    assert not ref_matches("rules2025::6-23::0", "rules2025::6-2")
    assert not ref_matches("austrac-ecdd-extra::x::0", "austrac-ecdd")


def test_sub_queries_follow_facts():
    facts = normalise_facts({"customer_type": "trust", "pep_status": "foreign", "high_risk_jurisdiction": True,
                             "ml_tf_risk": "bogus"})
    assert facts["ml_tf_risk"] == "unknown"
    qs = " | ".join(sub_queries(facts))
    assert "trust" in qs and "foreign politically exposed" in qs and "call for action" in qs
    assert sub_queries(None) == []


def test_foreign_pep_scenario_retrieves_pep_rule(assistant):
    res = assistant.retriever.search("customer is a foreign politically exposed person; source of wealth?")
    top3 = [r.chunk.chunk_id for r in res[:3]]
    assert "rules2025::6-23::0" in top3


def test_retrieval_caps_chunks_per_section_and_k(assistant):
    res = assistant.retriever.search("customer due diligence", k=4)
    assert len(res) <= 4
    refs = [r.chunk.section_ref for r in res]
    assert max(refs.count(x) for x in refs) <= assistant.retriever.max_per_section


def test_subqueries_are_tracked(assistant):
    res = assistant.retriever.search("an account for a club", ["simplified customer due diligence beneficial owners government body"])
    assert any(q != "primary" for r in res for q in r.matched_queries)


def test_bm25_exact_rule_number(assistant):
    hits = assistant.retriever.bm25.query("6-18", 3)
    assert hits and hits[0][0].startswith("rules2025::6-18")


def _chunk(cid="d::s::0"):
    return Chunk(cid, "d", "s", "Cite", "path", "text", None, "guidance", 0, 1)


def test_retrieved_to_dict_rounding():
    d = Retrieved(_chunk(), 0.0123456, 0.876543, 3.14159).to_dict()
    assert d["dense_similarity"] == 0.8765 and d["bm25_score"] == 3.142


def test_embedding_prompt_formats(offline_cfg):
    from amlrag.backends import embedding_prefixes, index_dir

    cfg = offline_cfg.override("embedding.backend", "ollama")
    q3 = cfg.override("embedding.model", "qwen3-embedding:8b")
    doc, query = embedding_prefixes(q3)
    assert doc == "" and query.startswith("Instruct: ") and query.endswith("\nQuery:")
    assert embedding_prefixes(cfg.override("embedding.model", "nomic-embed-text")) == ("search_document: ",
                                                                                         "search_query: ")
    assert embedding_prefixes(cfg.override("embedding.model", "qwen3-embedding:4b"))[1] == query  # same family
    custom = cfg.override("embedding.model", "some-new-embedder").override("embedding.query_prefix", "q: ")
    assert embedding_prefixes(custom) == ("", "q: ")
    assert embedding_prefixes(cfg.override("embedding.model", "unknown-model")) == ("", "")
    # Every embedding model gets its own index folder.
    assert index_dir(q3).name == "qwen3-embedding-8b"
    assert index_dir(cfg.override("embedding.model", "nomic-embed-text")).name == "nomic-embed-text"
    assert index_dir(offline_cfg).name == "hash-512"


def test_embedding_model_flag(built_cfg):
    import argparse

    from amlrag.cli import _cfg

    args = argparse.Namespace(config=str(built_cfg.root / "config.yaml"), offline=False, model=None,
                              embedding_model="nomic-embed-text", fast=False, closed_book=False)
    assert _cfg(args).embedding.model == "nomic-embed-text"
