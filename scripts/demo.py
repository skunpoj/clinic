"""
Interactive CLI demo of the retrieval system.

Usage:
    python scripts/demo.py                    # interactive query loop
    python scripts/demo.py --query "..."      # single query then exit
    python scripts/demo.py --sample           # use sample docs (no CSV required)
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import ACTIVE_EMBEDDING_MODEL, INDEX_PATH
from app.retrieval import ClinicalRetriever
from app.summarizer import summarize
from data.loader import get_sample_documents, load_mtsamples, build_documents

logging.basicConfig(level=logging.WARNING)


def run_query(retriever: ClinicalRetriever, query: str, top_k: int = 5) -> None:
    print(f"\nQuery: {query}")
    print("-" * 60)

    results = retriever.retrieve(query, top_k=top_k)

    for r in results:
        print(
            f"[{r['rank']}] score={r['score']:.4f}  "
            f"{r.get('specialty',''):25s}  {r.get('description','')[:70]}"
        )

    print("\nGenerating clinical summary…")
    summary = summarize(query, results)
    print("\n--- SUMMARY ---")
    print(summary)
    print("-" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clinical Note Retrieval Demo")
    parser.add_argument("--query", default=None, help="Run a single query and exit")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--sample", action="store_true", help="Use sample documents")
    parser.add_argument("--csv", default=None, help="Path to mtsamples.csv")
    args = parser.parse_args()

    retriever = ClinicalRetriever(model_name=ACTIVE_EMBEDDING_MODEL)
    index_path = Path(INDEX_PATH)

    if args.sample or not index_path.exists():
        if args.csv and Path(args.csv).exists():
            df = load_mtsamples(args.csv)
            docs = build_documents(df)
            print(f"Loaded {len(docs)} documents from {args.csv}")
        else:
            docs = get_sample_documents()
            print(f"Using {len(docs)} built-in sample documents.")
        retriever.build_index(docs)
    else:
        retriever.load_index()
        print(f"Loaded index with {retriever.index.ntotal} documents.")

    if args.query:
        run_query(retriever, args.query, top_k=args.top_k)
    else:
        print("\nClinical Note Retrieval System — interactive mode")
        print("Type 'quit' to exit.\n")
        while True:
            try:
                query = input("Query> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if query.lower() in ("quit", "exit", "q"):
                break
            if not query:
                continue
            run_query(retriever, query, top_k=args.top_k)


if __name__ == "__main__":
    main()
