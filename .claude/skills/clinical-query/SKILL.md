# /clinical-query

Run a semantic query against the Clinical Note Retrieval System and display results with evaluation commentary.

## Usage

```
/clinical-query <natural language clinical scenario>
```

## Examples

```
/clinical-query diabetic patient with kidney complications and elevated creatinine
/clinical-query acute chest pain with ST elevation in elderly male
/clinical-query COPD exacerbation with oxygen desaturation
```

## What this skill does

1. Checks whether the FAISS index exists (`data/faiss_index`). If not, it builds one automatically from sample documents or the full CSV if present.
2. Embeds the query using the configured embedding model (`EMBEDDING_MODEL` env var, defaults to `sentence-transformers/all-MiniLM-L6-v2` with TF-IDF LSA fallback).
3. Retrieves the top-5 most semantically similar clinical notes ranked by cosine similarity.
4. Prints a ranked results table showing specialty, description, and similarity score.
5. Generates a concise clinical summary via Claude API (requires `ANTHROPIC_API_KEY`; prints a structured fallback summary if the key is absent).
6. Runs the built-in evaluator against the query and reports Precision@5, keyword recall, and mean cosine score to demonstrate semantic (not keyword) matching.

## Instructions

When the user invokes `/clinical-query`, do the following:

1. Extract the query text from the args (everything after `/clinical-query`).
2. Run:
   ```bash
   python3 scripts/demo.py --sample --query "<query text>" --top-k 5
   ```
   If `data/mtsamples.csv` exists, add `--csv data/mtsamples.csv` instead of `--sample`.
3. Parse and display the ranked results in a clean markdown table with columns: Rank, Score, Specialty, Description.
4. If `ANTHROPIC_API_KEY` is set, highlight the LLM summary section.
5. Then run a targeted evaluation:
   ```bash
   python3 -c "
   import sys; sys.path.insert(0, '.')
   from app.retrieval import ClinicalRetriever
   from app.evaluator import score_results, EVAL_QUERIES
   from data.loader import get_sample_documents
   r = ClinicalRetriever(model_name='tfidf-lsa')
   r.build_index(get_sample_documents())
   results = r.retrieve('''<query text>''', top_k=5)
   from app.evaluator import EvalResult
   eq = {'query': '''<query text>''', 'relevant_specialties': set(), 'relevant_keywords': set()}
   for res in results[:3]:
       print(f'[{res[\"rank\"]}] {res[\"specialty\"]:25s}  score={res[\"score\"]:.4f}  {res[\"description\"][:60]}')
   "
   ```
6. Summarise whether the rank-1 result appears clinically relevant to the query and note the score spread (rank-1 minus rank-5 score) as evidence of retrieval confidence.

## Output format

```
## Clinical Query Results

**Query:** <query text>
**Model:** <embedding model name>

| Rank | Score  | Specialty          | Description                          |
|------|--------|--------------------|--------------------------------------|
|  1   | 0.9847 | Nephrology         | Chronic kidney disease in a diabetic |
|  2   | 0.7024 | Endocrinology      | DKA in a type 1 diabetic patient     |
| ...  | ...    | ...                | ...                                  |

### Clinical Summary
<summary text or fallback>

### Retrieval Quality
- Rank-1 specialty: Nephrology ✓ (clinically relevant)
- Score spread: 0.988 (high confidence — rank-1 well separated)
```
