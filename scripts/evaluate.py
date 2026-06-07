"""
Evaluate retrieval quality on predefined clinical test queries.

Usage:
    python scripts/evaluate.py                        # uses saved index
    python scripts/evaluate.py --sample               # build from sample docs first
    python scripts/evaluate.py --compare-models       # compare base vs clinical model
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import (
    ACTIVE_EMBEDDING_MODEL,
    EMBEDDING_MODEL_BASE,
    EMBEDDING_MODEL_CLINICAL,
    INDEX_PATH,
)
from app.evaluator import EVAL_QUERIES, evaluate_retriever, print_report
from app.retrieval import ClinicalRetriever
from data.loader import get_sample_documents, build_documents, load_mtsamples

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def build_retriever(model_name: str, use_sample: bool, csv_path: str | None) -> ClinicalRetriever:
    retriever = ClinicalRetriever(model_name=model_name)
    index_path = Path(INDEX_PATH)

    if use_sample or not index_path.exists():
        if use_sample:
            docs = get_sample_documents()
        else:
            if csv_path and Path(csv_path).exists():
                df = load_mtsamples(csv_path)
                docs = build_documents(df)
            else:
                logger.warning("No CSV found; using sample documents.")
                docs = get_sample_documents()
        retriever.build_index(docs)
    else:
        retriever.load_index()

    return retriever


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval quality")
    parser.add_argument("--sample", action="store_true", help="Use sample docs")
    parser.add_argument("--csv", default=None, help="Path to mtsamples.csv")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--compare-models",
        action="store_true",
        help="Compare base vs clinical embedding model",
    )
    args = parser.parse_args()

    if args.compare_models:
        print("\n" + "=" * 70)
        print(f"MODEL: {EMBEDDING_MODEL_BASE}  (general-purpose)")
        print("=" * 70)
        r1 = build_retriever(EMBEDDING_MODEL_BASE, args.sample, args.csv)
        results1 = evaluate_retriever(r1, top_k=args.top_k)
        print_report(results1)

        print("\n" + "=" * 70)
        print(f"MODEL: {EMBEDDING_MODEL_CLINICAL}  (clinical / PubMed)")
        print("=" * 70)
        r2 = build_retriever(EMBEDDING_MODEL_CLINICAL, args.sample, args.csv)
        results2 = evaluate_retriever(r2, top_k=args.top_k)
        print_report(results2)

        _print_comparison(results1, results2)
    else:
        retriever = build_retriever(ACTIVE_EMBEDDING_MODEL, args.sample, args.csv)
        results = evaluate_retriever(retriever, top_k=args.top_k)
        print_report(results)


def _print_comparison(results1: list, results2: list) -> None:
    import statistics
    p1 = statistics.mean(r.precision_at_k for r in results1)
    p2 = statistics.mean(r.precision_at_k for r in results2)
    s1 = statistics.mean(r.mean_score for r in results1)
    s2 = statistics.mean(r.mean_score for r in results2)

    print("\n" + "=" * 70)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Metric':<35} {'Base':>10} {'Clinical':>10} {'Delta':>10}")
    print("-" * 70)
    print(f"{'Macro Precision@k':<35} {p1:>10.3f} {p2:>10.3f} {p2-p1:>+10.3f}")
    print(f"{'Macro Mean Cosine Score':<35} {s1:>10.4f} {s2:>10.4f} {s2-s1:>+10.4f}")
    print("=" * 70)
    if p2 > p1:
        print("→ Clinical model improves specialty precision.")
    elif p1 > p2:
        print("→ Base model has higher specialty precision on this corpus.")
    else:
        print("→ Models are equivalent on specialty precision.")


if __name__ == "__main__":
    main()
