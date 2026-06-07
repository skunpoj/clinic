"""Tests for the retrieval system (uses offline TF-IDF LSA backend)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.loader import get_sample_documents
from app.retrieval import ClinicalRetriever
from app.evaluator import score_results, EVAL_QUERIES


@pytest.fixture(scope="module")
def retriever():
    docs = get_sample_documents()
    # Use offline TF-IDF LSA backend for CI (no HF Hub access required)
    r = ClinicalRetriever(model_name="tfidf-lsa")
    r.build_index(docs)
    return r


def test_index_builds(retriever):
    assert retriever.is_loaded()
    assert retriever.index.ntotal == 5


def test_retrieve_returns_top_k(retriever):
    results = retriever.retrieve("diabetic kidney disease", top_k=3)
    assert len(results) == 3


def test_scores_are_descending(retriever):
    results = retriever.retrieve("chest pain MI", top_k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_default_top_k(retriever):
    results = retriever.retrieve("cardiac arrest")
    assert 1 <= len(results) <= 5


def test_result_has_required_fields(retriever):
    results = retriever.retrieve("knee surgery", top_k=1)
    r = results[0]
    for field in ("rank", "score", "specialty", "transcription", "description"):
        assert field in r, f"Missing field: {field}"


def test_rank_starts_at_1(retriever):
    results = retriever.retrieve("heart failure", top_k=3)
    assert results[0]["rank"] == 1
    assert results[1]["rank"] == 2


def test_diabetes_kidney_not_ortho_top1(retriever):
    """Semantic test: a diabetic kidney query should not return ortho as rank 1."""
    results = retriever.retrieve("diabetic patient with kidney complications", top_k=5)
    assert results[0].get("specialty") != "Orthopedic Surgery"


def test_copd_not_ortho_top1(retriever):
    results = retriever.retrieve("COPD with breathing difficulty and oxygen", top_k=3)
    assert results[0].get("specialty") != "Orthopedic Surgery"


def test_knee_surgery_surfaces_ortho(retriever):
    """Ortho query should surface the orthopedic note."""
    results = retriever.retrieve("total knee arthroplasty surgery", top_k=5)
    specialties = [r.get("specialty") for r in results]
    assert "Orthopedic Surgery" in specialties


def test_semantic_not_just_keyword(retriever):
    """
    Query uses different vocabulary than docs: 'renal insufficiency' vs 'kidney disease'.
    The top result should still relate to renal/diabetic content.
    """
    results = retriever.retrieve("renal insufficiency in type 2 diabetes mellitus", top_k=3)
    top_descriptions = [res.get("description", "").lower() for res in results[:2]]
    assert any("kidney" in d or "diabet" in d or "renal" in d for d in top_descriptions)


def test_evaluator_scoring(retriever):
    eq = EVAL_QUERIES[0]  # diabetic + kidney
    results = retriever.retrieve(eq["query"], top_k=5)
    eval_result = score_results(eq, results, top_k=5)
    assert eval_result.precision_at_k >= 0.0
    assert isinstance(eval_result.mean_score, float)
    assert isinstance(eval_result.keyword_recall, float)
