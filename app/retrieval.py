"""
Embedding-based retrieval using FAISS vector index.

Two embedding backends:
  1. SentenceTransformerBackend  — dense neural embeddings (requires HF Hub access)
     • Base: sentence-transformers/all-MiniLM-L6-v2 (fast, strong general semantics)
     • Clinical: pritamdeka/S-PubMedBert-MS-MARCO (PubMed-tuned, better bio-term alignment)

  2. TFIDFLSABackend — TF-IDF + Truncated SVD (Latent Semantic Analysis)
     • Zero external dependencies; fully offline
     • Captures latent semantic structure beyond exact keyword overlap (LSA)
     • Used as fallback when HuggingFace Hub is unreachable

Both backends produce L2-normalised float32 vectors so the same FAISS
IndexFlatIP (cosine similarity via inner product) is used for retrieval.

Model selection justification:
  all-MiniLM-L6-v2 is the recommended starting point because it:
    - Was trained on 1B+ sentence pairs including medical Q&A datasets
    - Achieves strong MTEB scores at 1/10 the cost of large models
    - Fits comfortably on CPU (22M params, 384-dim embeddings)
  S-PubMedBert-MS-MARCO additionally fine-tunes on PubMed abstracts,
  improving alignment of clinical vocabulary (e.g. "CKD" ≈ "renal failure").
"""
from __future__ import annotations

import logging
import os
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.config import (
    ACTIVE_EMBEDDING_MODEL,
    INDEX_PATH,
    METADATA_PATH,
    TOP_K_DEFAULT,
)

logger = logging.getLogger(__name__)

_HF_BLOCKED = False  # set True at runtime if HF Hub is unreachable


# ---------------------------------------------------------------------------
# Embedding backends
# ---------------------------------------------------------------------------

class EmbeddingBackend(ABC):
    @abstractmethod
    def encode(self, texts: list[str]) -> np.ndarray:
        """Return L2-normalised float32 embeddings of shape (N, dim)."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def dim(self) -> int: ...


class SentenceTransformerBackend(EmbeddingBackend):
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading SentenceTransformer: %s", model_name)
        self._model = SentenceTransformer(model_name)
        self._name = model_name
        self._dim = self._model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str]) -> np.ndarray:
        emb = self._model.encode(
            texts,
            batch_size=64,
            show_progress_bar=len(texts) > 100,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return emb.astype(np.float32)

    @property
    def name(self) -> str:
        return self._name

    @property
    def dim(self) -> int:
        return self._dim


class TFIDFLSABackend(EmbeddingBackend):
    """
    TF-IDF vectoriser + Truncated SVD (Latent Semantic Analysis).

    LSA captures co-occurrence semantics — e.g. documents containing
    "CKD" and "renal failure" end up in the same latent dimensions even
    without sharing exact terms.  It is fully offline and deterministic.
    """

    _LSA_COMPONENTS = 256  # embedding dimension

    def __init__(self) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        from sklearn.preprocessing import normalize

        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            max_features=50_000,
        )
        self._svd = TruncatedSVD(n_components=self._LSA_COMPONENTS, random_state=42)
        self._normalize = normalize
        self._fitted = False

    def fit(self, texts: list[str]) -> None:
        from sklearn.decomposition import TruncatedSVD

        tfidf = self._vectorizer.fit_transform(texts)
        # n_components must be < min(n_samples, n_features)
        max_components = min(self._LSA_COMPONENTS, tfidf.shape[0] - 1, tfidf.shape[1] - 1)
        if max_components != self._svd.n_components:
            self._svd = TruncatedSVD(n_components=max_components, random_state=42)
        self._svd.fit(tfidf)
        self._fitted = True
        logger.info(
            "TF-IDF LSA fitted on %d docs, components=%d, explained_var=%.3f",
            len(texts),
            self._svd.n_components,
            self._svd.explained_variance_ratio_.sum(),
        )

    def encode(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Call fit() on corpus before encode().")
        tfidf = self._vectorizer.transform(texts)
        lsa = self._svd.transform(tfidf).astype(np.float32)
        return self._normalize(lsa)

    @property
    def name(self) -> str:
        return f"tfidf-lsa-{self._svd.n_components}d"

    @property
    def dim(self) -> int:
        return int(self._svd.n_components)


# ---------------------------------------------------------------------------
# Main retriever
# ---------------------------------------------------------------------------

def _load_backend(model_name: str) -> EmbeddingBackend:
    """Try SentenceTransformer; fall back to TF-IDF LSA if HF is unreachable."""
    if model_name == "tfidf-lsa":
        logger.info("Using TF-IDF LSA backend (explicit request).")
        return TFIDFLSABackend()
    try:
        return SentenceTransformerBackend(model_name)
    except Exception as exc:
        logger.warning(
            "SentenceTransformer unavailable (%s). Falling back to TF-IDF LSA.", exc
        )
        return TFIDFLSABackend()


class ClinicalRetriever:
    """
    Semantic retrieval over clinical notes.

    Selects the best available embedding backend at construction time,
    builds a FAISS IndexFlatIP for cosine-similarity search, and caches
    the index to disk for fast subsequent loads.
    """

    def __init__(
        self,
        model_name: str = ACTIVE_EMBEDDING_MODEL,
        index_path: str = INDEX_PATH,
        metadata_path: str = METADATA_PATH,
    ) -> None:
        self.model_name = model_name
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        self.backend: EmbeddingBackend = _load_backend(model_name)
        self.index: faiss.IndexFlatIP | None = None
        self.documents: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def build_index(self, documents: list[dict[str, Any]]) -> None:
        """Embed all documents and build a FAISS index."""
        logger.info("Building FAISS index for %d documents…", len(documents))
        texts = [doc["text_for_embedding"] for doc in documents]

        if isinstance(self.backend, TFIDFLSABackend) and not self.backend._fitted:
            self.backend.fit(texts)

        embeddings = self.backend.encode(texts)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        self.documents = documents
        logger.info(
            "Index built: %d vectors, dim=%d, backend=%s",
            self.index.ntotal, dim, self.backend.name,
        )

    def save_index(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        payload = {"documents": self.documents, "backend": self.backend}
        with open(self.metadata_path, "wb") as f:
            pickle.dump(payload, f)
        logger.info("Saved index to %s", self.index_path)

    def load_index(self) -> None:
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"No FAISS index found at {self.index_path}. "
                "Run `python scripts/ingest.py` first."
            )
        self.index = faiss.read_index(str(self.index_path))
        with open(self.metadata_path, "rb") as f:
            payload = pickle.load(f)
        self.documents = payload["documents"]
        self.backend = payload["backend"]
        logger.info(
            "Loaded index: %d vectors, backend=%s",
            self.index.ntotal, self.backend.name,
        )

    def is_loaded(self) -> bool:
        return self.index is not None and len(self.documents) > 0

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self, query: str, top_k: int = TOP_K_DEFAULT
    ) -> list[dict[str, Any]]:
        """
        Return top-k most semantically similar documents to *query*.

        Each result dict has all original document fields plus:
          - score: cosine similarity (0–1 for neural, can be negative for LSA)
          - rank: 1-based retrieval rank
        """
        if not self.is_loaded():
            raise RuntimeError("Index not loaded. Call load_index() or build_index().")

        q_emb = self.backend.encode([query])
        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q_emb, top_k)

        results = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
            if idx < 0:
                continue
            doc = dict(self.documents[idx])
            doc["score"] = float(score)
            doc["rank"] = rank
            results.append(doc)

        return results
