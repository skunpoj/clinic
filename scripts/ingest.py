"""
Ingest the mtsamples dataset and build the FAISS vector index.

Usage:
    python scripts/ingest.py                         # uses DATA_CSV_PATH env var
    python scripts/ingest.py --csv data/mtsamples.csv
    python scripts/ingest.py --sample                # use built-in sample docs
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import DATA_CSV_PATH, ACTIVE_EMBEDDING_MODEL
from app.retrieval import ClinicalRetriever
from data.loader import build_documents, get_sample_documents, load_mtsamples

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest clinical notes into FAISS index")
    parser.add_argument("--csv", default=DATA_CSV_PATH, help="Path to mtsamples.csv")
    parser.add_argument(
        "--sample", action="store_true", help="Use built-in sample documents (no CSV needed)"
    )
    parser.add_argument(
        "--model",
        default=ACTIVE_EMBEDDING_MODEL,
        help="Sentence-transformer model name",
    )
    args = parser.parse_args()

    if args.sample:
        logger.info("Using built-in sample documents (5 records).")
        documents = get_sample_documents()
    else:
        csv_path = Path(args.csv)
        if not csv_path.exists():
            logger.error(
                "CSV not found: %s\n"
                "Download the dataset from:\n"
                "  https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions\n"
                "or run with --sample for a demo.",
                csv_path,
            )
            sys.exit(1)

        logger.info("Loading dataset from %s …", csv_path)
        df = load_mtsamples(csv_path)
        logger.info("Loaded %d valid records.", len(df))
        documents = build_documents(df)

    retriever = ClinicalRetriever(model_name=args.model)
    retriever.build_index(documents)
    retriever.save_index()
    logger.info("Done. Index saved.")


if __name__ == "__main__":
    main()
