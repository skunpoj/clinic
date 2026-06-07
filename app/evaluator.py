"""
Retrieval evaluation utilities.

We evaluate semantic relevance rather than keyword matching using two approaches:

1. Specialty-match precision@k: a retrieved note is "relevant" if its medical
   specialty aligns with the clinical domain of the query.  We define a small
   ground-truth mapping of test queries → expected specialties.

2. Cosine-score distribution: mean / min similarity scores show whether the
   model is returning confidently-relevant notes or scraping the bottom.

3. Cross-encoder re-ranking correlation: compare retrieval order from the
   bi-encoder vs a cross-encoder to spot systematic mis-ranks.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Test queries with known-relevant specialty labels
# ---------------------------------------------------------------------------
EVAL_QUERIES: list[dict[str, Any]] = [
    {
        "query": "diabetic patient with kidney complications and elevated creatinine",
        "relevant_specialties": {"Nephrology", "Endocrinology", "Internal Medicine"},
        "relevant_keywords": {"diabetes", "kidney", "creatinine", "renal", "CKD"},
    },
    {
        "query": "acute chest pain with ST elevation myocardial infarction",
        "relevant_specialties": {"Cardiology", "Emergency Medicine"},
        "relevant_keywords": {"chest pain", "MI", "troponin", "EKG", "stent"},
    },
    {
        "query": "COPD exacerbation with dyspnea and oxygen therapy",
        "relevant_specialties": {"Pulmonology", "Emergency Medicine"},
        "relevant_keywords": {"COPD", "dyspnea", "oxygen", "nebulizer", "bronchodilator"},
    },
    {
        "query": "post-operative knee arthroplasty rehabilitation",
        "relevant_specialties": {"Orthopedic Surgery", "Physical Medicine"},
        "relevant_keywords": {"knee", "arthroplasty", "replacement", "orthopedic"},
    },
    {
        "query": "insulin-dependent diabetes with ketoacidosis and high blood sugar",
        "relevant_specialties": {"Endocrinology", "Internal Medicine"},
        "relevant_keywords": {"DKA", "insulin", "ketoacidosis", "glucose", "diabetes"},
    },
    {
        "query": "hypertension management in elderly patient with heart failure",
        "relevant_specialties": {"Cardiology", "Internal Medicine", "Geriatrics"},
        "relevant_keywords": {"hypertension", "heart failure", "ACE", "diuretic"},
    },
    {
        "query": "appendectomy laparoscopic surgery acute abdomen",
        "relevant_specialties": {"General Surgery", "Surgery"},
        "relevant_keywords": {"appendix", "appendectomy", "laparoscopic", "abdomen"},
    },
]


@dataclass
class EvalResult:
    query: str
    top_k: int
    retrieved: list[dict[str, Any]]
    precision_at_k: float
    mean_score: float
    score_gap: float          # score[0] - score[-1]: spread indicates ranking confidence
    keyword_recall: float
    notes: list[str] = field(default_factory=list)


def evaluate_retriever(retriever: Any, top_k: int = 5) -> list[EvalResult]:
    """Run all EVAL_QUERIES and return per-query EvalResult objects."""
    results = []
    for eq in EVAL_QUERIES:
        try:
            retrieved = retriever.retrieve(eq["query"], top_k=top_k)
        except Exception as exc:
            logger.warning("Retrieval failed for query '%s': %s", eq["query"], exc)
            continue
        result = score_results(eq, retrieved, top_k)
        results.append(result)
    return results


def score_results(
    eval_query: dict[str, Any],
    retrieved: list[dict[str, Any]],
    top_k: int,
) -> EvalResult:
    relevant_specs = eval_query["relevant_specialties"]
    relevant_kws = {k.lower() for k in eval_query["relevant_keywords"]}

    hits = 0
    keyword_hits = 0
    for doc in retrieved:
        spec = doc.get("specialty", "")
        # specialty match
        if any(rs.lower() in spec.lower() for rs in relevant_specs):
            hits += 1
        # keyword match in transcription
        trx = (doc.get("transcription", "") + " " + doc.get("keywords", "")).lower()
        if any(kw in trx for kw in relevant_kws):
            keyword_hits += 1

    precision = hits / len(retrieved) if retrieved else 0.0
    kw_recall = keyword_hits / len(retrieved) if retrieved else 0.0
    scores = [r["score"] for r in retrieved]
    mean_score = sum(scores) / len(scores) if scores else 0.0
    score_gap = (scores[0] - scores[-1]) if len(scores) > 1 else 0.0

    notes = []
    if precision < 0.4:
        notes.append("LOW specialty precision — consider clinical embedding model")
    if mean_score < 0.3:
        notes.append("Low mean similarity — query may be out-of-distribution")

    return EvalResult(
        query=eval_query["query"],
        top_k=top_k,
        retrieved=retrieved,
        precision_at_k=precision,
        mean_score=mean_score,
        score_gap=score_gap,
        keyword_recall=kw_recall,
        notes=notes,
    )


def print_report(results: list[EvalResult]) -> None:
    print("\n" + "=" * 70)
    print("RETRIEVAL EVALUATION REPORT")
    print("=" * 70)

    macro_precision = sum(r.precision_at_k for r in results) / len(results) if results else 0
    macro_kw_recall = sum(r.keyword_recall for r in results) / len(results) if results else 0
    macro_mean_score = sum(r.mean_score for r in results) / len(results) if results else 0

    for r in results:
        print(f"\nQuery : {r.query}")
        print(f"  Precision@{r.top_k} (specialty): {r.precision_at_k:.2f}")
        print(f"  Keyword recall@{r.top_k}       : {r.keyword_recall:.2f}")
        print(f"  Mean cosine score              : {r.mean_score:.4f}")
        print(f"  Score spread (top-bottom)      : {r.score_gap:.4f}")
        for note in r.notes:
            print(f"  ⚠ {note}")
        print("  Top-3 retrieved:")
        for doc in r.retrieved[:3]:
            print(
                f"    [{doc['rank']}] {doc.get('specialty', 'N/A'):25s} "
                f"score={doc['score']:.4f}  {doc.get('description', '')[:60]}"
            )

    print("\n" + "-" * 70)
    print(f"MACRO Precision@k (specialty) : {macro_precision:.2f}")
    print(f"MACRO Keyword recall@k        : {macro_kw_recall:.2f}")
    print(f"MACRO Mean cosine score       : {macro_mean_score:.4f}")
    print("=" * 70 + "\n")
