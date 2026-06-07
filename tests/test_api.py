"""Integration tests for the FastAPI endpoints (offline TF-IDF LSA backend)."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

# Patch config BEFORE importing the app so lifespan picks up the right values
import app.config as cfg
cfg.INDEX_PATH = "/nonexistent/path"
cfg.ACTIVE_EMBEDDING_MODEL = "tfidf-lsa"

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["index_size"] == 5


def test_retrieve_post_no_summary(client):
    resp = client.post(
        "/retrieve",
        json={"query": "diabetic patient with kidney disease", "top_k": 3, "include_summary": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_retrieved"] == 3
    assert len(data["results"]) == 3
    assert data["summary"] is None


def test_retrieve_get(client):
    resp = client.get(
        "/retrieve",
        params={"query": "COPD dyspnea", "top_k": 2, "include_summary": False},
    )
    assert resp.status_code == 200
    assert resp.json()["total_retrieved"] == 2


def test_retrieve_returns_descending_scores(client):
    resp = client.post(
        "/retrieve",
        json={"query": "chest pain myocardial infarction", "top_k": 5, "include_summary": False},
    )
    data = resp.json()
    scores = [r["score"] for r in data["results"]]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_short_query_rejected(client):
    resp = client.post("/retrieve", json={"query": "x", "top_k": 3})
    assert resp.status_code == 422


def test_retrieve_top_k_capped_to_index_size(client):
    resp = client.post(
        "/retrieve",
        json={"query": "patient with diabetes", "top_k": 20, "include_summary": False},
    )
    data = resp.json()
    assert data["total_retrieved"] <= 5


def test_result_fields(client):
    resp = client.post(
        "/retrieve",
        json={"query": "knee arthroplasty surgery", "top_k": 1, "include_summary": False},
    )
    r = resp.json()["results"][0]
    for field in ("rank", "score", "specialty", "description", "transcription_excerpt"):
        assert field in r


def test_embedding_model_in_response(client):
    resp = client.post(
        "/retrieve",
        json={"query": "hypertension treatment", "top_k": 3, "include_summary": False},
    )
    assert "embedding_model" in resp.json()


def test_fallback_summary_no_api_key(client):
    """Without an API key the system returns a rule-based summary (not None)."""
    resp = client.post(
        "/retrieve",
        json={"query": "diabetic kidney complications", "top_k": 3, "include_summary": True},
    )
    data = resp.json()
    assert data["summary"] is not None
    assert len(data["summary"]) > 10
