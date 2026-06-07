"""FastAPI application for clinical note retrieval."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import app.config as cfg
from app.retrieval import ClinicalRetriever
from app.summarizer import summarize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

retriever: ClinicalRetriever | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever
    retriever = ClinicalRetriever(
        model_name=cfg.ACTIVE_EMBEDDING_MODEL,
        index_path=cfg.INDEX_PATH,
        metadata_path=cfg.METADATA_PATH,
    )
    index_path = Path(cfg.INDEX_PATH)
    if index_path.exists():
        logger.info("Loading existing FAISS index…")
        retriever.load_index()
    else:
        logger.warning(
            "No FAISS index found at %s. "
            "Loading sample documents for demo purposes. "
            "Run `python scripts/ingest.py` to index the full dataset.",
            cfg.INDEX_PATH,
        )
        from data.loader import get_sample_documents
        docs = get_sample_documents()
        retriever.build_index(docs)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Clinical Note Retrieval API",
    description=(
        "Semantic retrieval of clinical notes using dense embeddings (sentence-transformers) "
        "and an LLM-generated summary (Claude). "
        "POST /retrieve to query the corpus."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RetrieveRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language clinical query",
        examples=["diabetic patient with kidney complications and elevated creatinine"],
    )
    top_k: int = Field(
        default=cfg.TOP_K_DEFAULT,
        ge=1,
        le=20,
        description="Number of notes to retrieve",
    )
    include_summary: bool = Field(
        default=True,
        description="Generate an LLM summary of retrieved results",
    )


class NoteResult(BaseModel):
    rank: int
    score: float
    specialty: str
    sample_name: str
    description: str
    keywords: str
    transcription_excerpt: str


class RetrieveResponse(BaseModel):
    query: str
    total_retrieved: int
    embedding_model: str
    results: list[NoteResult]
    summary: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict[str, Any]:
    if retriever is None or not retriever.is_loaded():
        raise HTTPException(status_code=503, detail="Index not ready")
    return {
        "status": "ok",
        "index_size": retriever.index.ntotal,
        "embedding_model": retriever.model_name,
    }


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_notes(req: RetrieveRequest) -> RetrieveResponse:
    """
    Retrieve the most semantically relevant clinical notes for a natural language query.

    Returns ranked notes and an optional LLM-generated clinical summary.
    """
    if retriever is None or not retriever.is_loaded():
        raise HTTPException(status_code=503, detail="Index not ready")

    raw_results = retriever.retrieve(req.query, top_k=req.top_k)

    note_results = [
        NoteResult(
            rank=r["rank"],
            score=round(r["score"], 4),
            specialty=r.get("specialty", ""),
            sample_name=r.get("sample_name", ""),
            description=r.get("description", ""),
            keywords=r.get("keywords", ""),
            transcription_excerpt=r.get("transcription", "")[:500],
        )
        for r in raw_results
    ]

    summary = None
    if req.include_summary:
        summary = summarize(req.query, raw_results)

    return RetrieveResponse(
        query=req.query,
        total_retrieved=len(note_results),
        embedding_model=retriever.model_name,
        results=note_results,
        summary=summary,
    )


@app.get("/retrieve", response_model=RetrieveResponse)
async def retrieve_notes_get(
    query: str = Query(..., min_length=3, description="Natural language clinical query"),
    top_k: int = Query(default=cfg.TOP_K_DEFAULT, ge=1, le=20),
    include_summary: bool = Query(default=True),
) -> RetrieveResponse:
    """GET-friendly version of /retrieve for quick browser/curl testing."""
    return await retrieve_notes(
        RetrieveRequest(query=query, top_k=top_k, include_summary=include_summary)
    )
