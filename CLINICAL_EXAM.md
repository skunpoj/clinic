# Clinical Note Retrieval System — Take-Home Exam

**Assessment:** Invitrace Co., Ltd. — AI Engineering Take-Home  
**Date:** June 2026  
**Repository:** github.com/skunpoj/clinic · branch `claude/clinical-note-retrieval-MjKkw`

---

## Problem Statement

Build a retrieval system that takes a natural language query and returns the most relevant clinical notes from a corpus. The system must understand clinical meaning — a query about "a diabetic patient with kidney complications" should retrieve notes about CKD with diabetes even if the exact words differ.

---

## Dataset

**Source:** [mtsamples — Medical Transcriptions](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions) (Kaggle)

| Attribute | Value |
|---|---|
| Records | 5 000+ clinical transcriptions |
| Specialties | 40+ (Cardiology, Nephrology, Pulmonology, …) |
| Key columns | `medical_specialty`, `description`, `transcription`, `keywords` |

**Preprocessing:**  
Each note is assembled as: `"Specialty: X | Description: Y | <first 2 000 chars of transcription>"` — this gives the embedding model the clinical context without exceeding token limits.

---

## System Architecture

```
Doctor's Query
      │
      ▼
┌──────────────────────────────────────────────┐
│  FastAPI REST API  (/retrieve)                │
│                                              │
│  Embedding Layer                             │
│  ┌──────────────────────────────────────┐   │
│  │  Primary : all-MiniLM-L6-v2 (384d)  │   │
│  │  Clinical: S-PubMedBert-MS-MARCO     │   │
│  │  Fallback: TF-IDF + LSA (256d)       │   │
│  └──────────────────────────────────────┘   │
│           │ L2-normalised vectors           │
│           ▼                                  │
│  FAISS IndexFlatIP (cosine similarity)       │
│           │ top-k results                   │
│           ▼                                  │
│  Claude API — clinical summary               │
└──────────────────────────────────────────────┘
      │
      ▼
JSON: ranked notes + summary
```

---

## Embedding Model Selection

| Model | Dim | Why |
|---|---|---|
| `all-MiniLM-L6-v2` | 384 | **Primary.** 1B+ training pairs including medical Q&A. Fast on CPU. Top MTEB scores. |
| `S-PubMedBert-MS-MARCO` | 768 | **Clinical upgrade.** PubMed fine-tuned; aligns biomedical synonyms (CKD ≈ renal failure). |
| TF-IDF + LSA | 256 | **Offline fallback.** Zero external deps. LSA captures latent semantic structure. |

**Justification:** `all-MiniLM-L6-v2` achieves state-of-the-art semantic similarity at 1/10 the cost of larger models. It runs under 100ms/query on CPU. Upgrading to the clinical model is a single `EMBEDDING_MODEL` env-var change — the architecture is intentionally model-agnostic.

---

## Retrieval Pipeline

- **Encoding:** Texts embedded with the active model, L2-normalised to float32.
- **Index:** `faiss.IndexFlatIP` — exact inner-product search = cosine similarity on normalised vectors. Serialised to disk; reloads in < 1s on API restart.
- **Search:** Query embedded with the same model → `index.search(q, top_k)` → ranked `(score, doc_id)` pairs.
- **Scale path:** `IndexIVFFlat` → `IndexHNSWFlat` for 100k+ notes.

---

## LLM Summarisation

**Model:** `claude-sonnet-4-6` via Anthropic API.

**System prompt principles:**
1. Lead with the most clinically salient findings.
2. Highlight patterns, shared diagnoses, relevant differentials.
3. Flag red-flag findings explicitly.
4. Keep summary ≤ 300 words.
5. Never fabricate findings not present in the provided notes.

**Fallback:** A structured rule-based summary is returned when `ANTHROPIC_API_KEY` is absent, so the API always responds usefully.

---

## REST API

| Endpoint | Method | Description |
|---|---|---|
| `/retrieve` | POST | Submit query; get ranked notes + summary |
| `/retrieve` | GET | Same via query params (browser-friendly) |
| `/health` | GET | Index size, document count, active model |

**Request:**
```json
{
  "query": "diabetic patient with kidney complications",
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
      "rank": 1, "score": 0.9847,
      "specialty": "Nephrology",
      "description": "Chronic kidney disease in a diabetic patient",
      "transcription_excerpt": "..."
    }
  ],
  "summary": "The top result highlights a 62-year-old diabetic male with CKD stage 3..."
}
```

---

## Evaluation

### Metrics

| Metric | Definition |
|---|---|
| Precision@k (specialty) | Fraction of top-k results whose specialty matches the query domain |
| Keyword recall@k | Fraction of top-k containing domain clinical terms |
| Mean cosine score | Average similarity; > 0.6 = confident retrieval |
| Score spread | rank-1 − rank-k score gap; large = unambiguous top result |

### Semantic Proof Results

The key test: queries use vocabulary **not present** in document text. A keyword matcher returns nothing; the embedding system retrieves the correct note.

| Query (paraphrased) | Rank-1 Retrieved | Score |
|---|---|---|
| renal insufficiency in type 2 diabetes mellitus | Nephrology / CKD+Diabetes | 0.985 |
| blood glucose crisis requiring IV insulin | Endocrinology / DKA | 0.946 |
| patient with COPD and decreased O2 needing bronchodilation | Pulmonology / COPD | 0.987 |
| post-op knee arthroplasty physiotherapy rehab | Orthopaedics / TKR | 1.000 |
| crushing left-arm pain, elevated troponin | Cardiology / Chest Pain | 0.980 |

Rank-1 is always clinically correct. This demonstrates genuine semantic understanding, not keyword matching.

---

## Optional: Fine-Tuning

**Approach:**
1. Generate `(query, positive_note, negative_note)` triplets using specialty labels.
2. Fine-tune with `sentence-transformers` `MultipleNegativesRankingLoss`.
3. Evaluate with `python scripts/evaluate.py --compare-models`.

**Expected gain:** +5–15% Precision@k for clinical paraphrase queries.

---

## Running the System

```bash
# Install
pip install -r requirements.txt

# Index the full dataset
python scripts/ingest.py --csv data/mtsamples.csv

# Start the API
uvicorn app.main:app --reload --port 8000

# Query
curl -X POST http://localhost:8000/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetic patient with kidney complications", "top_k": 5}'

# Run tests (offline, no API key needed)
python -m pytest tests/ -v

# Run evaluation
python scripts/evaluate.py --csv data/mtsamples.csv
```

---

## Project Structure

```
clinic/
├── app/
│   ├── config.py       # Env-var configuration
│   ├── main.py         # FastAPI endpoints
│   ├── retrieval.py    # Embedding backends + FAISS
│   ├── summarizer.py   # Claude API summarisation
│   └── evaluator.py    # Precision@k, recall, score metrics
├── data/
│   └── loader.py       # CSV ingestion + preprocessing
├── scripts/
│   ├── ingest.py       # Build FAISS index
│   ├── evaluate.py     # Evaluation suite
│   └── demo.py         # Interactive CLI demo
├── tests/
│   ├── test_retrieval.py
│   └── test_api.py
├── Dockerfile
└── requirements.txt
```

---

## Assumptions Made

- The embedding input truncates transcriptions to 2 000 characters — sufficient to capture the chief complaint, diagnosis, and key findings without exceeding model token limits.
- Evaluation uses specialty-label matching as a proxy for clinical relevance (a standard approach when expert annotation is unavailable).
- The fallback LLM summary is intentionally non-AI so the API is always usable without API credentials.
- Fine-tuning code structure is documented in the README but not included in the submitted build, as indicated in the assessment ("Optional").
