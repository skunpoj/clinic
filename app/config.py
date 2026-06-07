import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Embedding models
EMBEDDING_MODEL_BASE = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_MODEL_CLINICAL = "pritamdeka/S-PubMedBert-MS-MARCO"

ACTIVE_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL_BASE)

# Retrieval
TOP_K_DEFAULT = int(os.getenv("TOP_K", "5"))
INDEX_PATH = os.getenv("INDEX_PATH", str(BASE_DIR / "data" / "faiss_index"))
METADATA_PATH = os.getenv("METADATA_PATH", str(BASE_DIR / "data" / "metadata.pkl"))

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
SUMMARY_MAX_TOKENS = int(os.getenv("SUMMARY_MAX_TOKENS", "1024"))

# Data
DATA_CSV_PATH = os.getenv("DATA_CSV_PATH", str(BASE_DIR / "data" / "mtsamples.csv"))
