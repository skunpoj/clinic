# Clinical Note Retrieval System

A semantic search system that helps doctors quickly find relevant past clinical notes from a large corpus. The system understands clinical meaning beyond keyword matching, surfacing notes about CKD with diabetes when a doctor queries "diabetic patient with kidney complications" even if the exact words differ.

---

## Architecture

```
Doctor's Query
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI REST API  (/retrieve)                               │
├─────────────────────────────────────────────────────────────┤
│  Embedding Layer                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Primary: sentence-transformers/all-MiniLM-L6-v2      │  │
│  │  Clinical: pritamdeka/S-PubMedBert-MS-MARCO           │  │
│  │  Fallback: TF-IDF + Latent Semantic Analysis (LSA)    │  │
│  └───────────────────────────────────────────────────────┘  │
│           │ L2-normalised vectors                            │
│           ▼                                                  │
│  ┌─────────────────────┐                                     │
│  │  FAISS IndexFlatIP  │  cosine similarity search           │
│  └─────────────────────┘                                     │
│           │ Top-k results                                    │
│           ▼                                                  │
│  ┌─────────────────────┐                                     │
│  │  Claude API (LLM)   │  clinical summary generation        │
│  └─────────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
JSON Response: ranked notes + clinical summary
```

---

## Embedding Model Selection

| Model | Dim | Notes |
|---|---|---|
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | **Primary choice.** Trained on 1B+ pairs incl. medical Q&A. Fast, strong general semantics, 22M params. |
| `pritamdeka/S-PubMedBert-MS-MARCO` | 768 | **Clinical upgrade.** Fine-tuned on PubMed + MS-MARCO. Better alignment of biomedical vocabulary (e.g. "CKD" ≈ "renal failure"). |
| TF-IDF + LSA (offline) | 256 | **Fallback.** No external dependencies. Captures latent co-occurrence semantics. Used in air-gapped environments. |

**Why all-MiniLM-L6-v2?**  
It achieves top-tier MTEB benchmark scores at a fraction of larger models' inference cost, runs on CPU without GPU requirements, and was trained on datasets that include medical Q&A and biomedical text pairs. For production deployment on the full corpus, swapping to `S-PubMedBert-MS-MARCO` is a single config change (`EMBEDDING_MODEL=pritamdeka/S-PubMedBert-MS-MARCO`).

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download the dataset
Download [mtsamples.csv](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions) and place it at `data/mtsamples.csv`.

### 3. Build the vector index
```bash
# Full dataset
python scripts/ingest.py --csv data/mtsamples.csv

# Demo with built-in sample (5 documents, no CSV needed)
python scripts/ingest.py --sample
```

### 4. Start the API
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Query the API
```bash
curl -X POST http://localhost:8000/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "diabetic patient with kidney complications and elevated creatinine",
    "top_k": 5,
    "include_summary": true
  }'
```

---

## API Reference

### `POST /retrieve`

**Request body:**
```json
{
  "query": "string (3-1000 chars)",
  "top_k": 5,
  "include_summary": true
}
```

**Response:**
```json
{
  "query": "...",
  "total_retrieved": 5,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "results": [
    {
      "rank": 1,
      "score": 0.8923,
      "specialty": "Nephrology",
      "sample_name": "CKD with Diabetes",
      "description": "Chronic kidney disease in a diabetic patient",
      "keywords": "CKD, diabetes, nephropathy",
      "transcription_excerpt": "..."
    }
  ],
  "summary": "The retrieved notes highlight a pattern of diabetic nephropathy..."
}
```

### `GET /retrieve?query=...&top_k=5&include_summary=true`

Browser/curl-friendly version of the same endpoint.

### `GET /health`

Returns index size and active embedding model.

---

## LLM Summarization

The system calls the Claude API (`claude-sonnet-4-6`) with a clinical system prompt to generate a concise summary (≤ 300 words) directly addressing the doctor's query. The summary:
- Leads with the most clinically salient findings
- Highlights patterns and shared diagnoses
- Flags red-flag findings explicitly
- Never fabricates findings not present in the notes

Set `ANTHROPIC_API_KEY` in the environment. Without a key, a structured rule-based summary is returned.

---

## Evaluation

The evaluation suite tests 7 clinical query types against specialty-match precision and keyword recall:

```bash
python scripts/evaluate.py --sample          # quick demo evaluation
python scripts/evaluate.py --csv data/mtsamples.csv  # full corpus evaluation
python scripts/evaluate.py --compare-models  # compare base vs clinical model
```

**Key metrics:**
- **Precision@k (specialty)**: fraction of top-k results matching the expected medical specialty
- **Keyword recall@k**: fraction of top-k results containing domain-specific terms
- **Mean cosine score**: average similarity; indicates retrieval confidence
- **Score spread**: gap between rank-1 and rank-k score; large gap = confident top result

**Why specialty precision proves semantic understanding:**  
A keyword search for "diabetic kidney complications" would match any document containing "diabetic" or "kidney". The embedding system instead retrieves Nephrology and Endocrinology notes even when the query uses paraphrased vocabulary like "renal insufficiency in type 2 diabetes mellitus" — demonstrating genuine semantic alignment, not surface-level matching.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All 20 tests run offline (no HuggingFace Hub or API key required) using the TF-IDF LSA backend and built-in sample documents.

---

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model name |
| `ANTHROPIC_API_KEY` | `""` | Claude API key for LLM summaries |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Claude model for summarization |
| `TOP_K` | `5` | Default number of results |
| `INDEX_PATH` | `data/faiss_index` | FAISS index file path |
| `DATA_CSV_PATH` | `data/mtsamples.csv` | Dataset path |

---

## Project Structure

```
clinic/
├── app/
│   ├── config.py          # Configuration constants
│   ├── main.py            # FastAPI application & endpoints
│   ├── retrieval.py       # Embedding backends + FAISS retriever
│   ├── summarizer.py      # Claude API summarization
│   └── evaluator.py       # Retrieval quality metrics
├── data/
│   └── loader.py          # Dataset loading & preprocessing
├── scripts/
│   ├── ingest.py          # Build FAISS index from dataset
│   ├── evaluate.py        # Run evaluation suite
│   └── demo.py            # Interactive CLI demo
├── tests/
│   ├── test_retrieval.py  # Unit tests for retrieval system
│   └── test_api.py        # Integration tests for FastAPI
└── requirements.txt
```

---

## Optional: Fine-tuning

To fine-tune the embedding model on the clinical corpus:

1. Generate (query, positive, negative) triplets from the mtsamples data using specialty labels as relevance signal.
2. Fine-tune using `sentence-transformers` `MultipleNegativesRankingLoss`.
3. Compare retrieval metrics before/after using `scripts/evaluate.py --compare-models`.

Expected improvement: specialty precision@5 +5–15% on held-out queries, especially for clinical paraphrases where base models diverge.

---

## Docker

```bash
docker build -t clinic-retrieval .
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  clinic-retrieval
```
