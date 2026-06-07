# clinic vs openmed — Full Technical Comparison

> **clinic** — `skunpoj/clinic` — Clinical Note Retrieval System (semantic search + LLM summarisation)
> **openmed** — `maziyarpanahi/openmed` — Production Medical NLP Toolkit (NER + PII de-identification)

---

## Table of Contents

1. [Repository at a Glance](#1-repository-at-a-glance)
2. [Directory Structure](#2-directory-structure)
3. [Feature Comparison — Full Matrix](#3-feature-comparison--full-matrix)
   - 3.1 Retrieval & Search
   - 3.2 Entity Extraction & NER
   - 3.3 Privacy & De-identification
   - 3.4 LLM / Generative Layer
   - 3.5 REST API
   - 3.6 Embedding / Model Backends
   - 3.7 Evaluation & Metrics
   - 3.8 Batch & Throughput
   - 3.9 Deployment
   - 3.10 Platform & Device
   - 3.11 Language Support
   - 3.12 Configuration & Profiles
   - 3.13 Developer Experience
   - 3.14 Security
   - 3.15 Testing
   - 3.16 Documentation
4. [What clinic does that OpenMed does not](#4-what-clinic-does-that-openmed-does-not)
5. [What OpenMed does that clinic defers entirely](#5-what-openmed-does-that-clinic-defers-entirely)
6. [Model Ecosystem](#6-model-ecosystem)
7. [API Surface Detail](#7-api-surface-detail)
8. [Production Pipeline — Merged Architecture](#8-production-pipeline--merged-architecture)
9. [Verdict](#9-verdict)

---

## 1. Repository at a Glance

| | **clinic** | **openmed** |
|---|---|---|
| Full name | `skunpoj/clinic` | `maziyarpanahi/openmed` |
| Purpose | Semantic retrieval + LLM summarisation of clinical notes | NER entity extraction + PII de-identification of clinical text |
| Stars / Forks | — (assessment project) | 1,400 ★ / 170 forks |
| Commits | ~5 | 838 |
| Releases | 0 | 32 (PyPI `openmed` v1.5.2, May 2026) |
| arXiv paper | — | 2508.01630 |
| License | MIT | Apache 2.0 |
| Languages | Python 100% | Python 63.5% + Swift 36.1% |
| Python version | 3.11 (Docker base) | ≥ 3.10 |
| Build tooling | pip + `requirements.txt` | uv + `pyproject.toml` + `Makefile` |
| CI / CD | None | `.github/` workflows |
| Docs site | README.md + CLINICAL_EXAM.md | `mkdocs.yml` (full hosted docs) |
| Claude Code | `.claude/skills/` (2 skills) | `.claude/` (also present) |

---

## 2. Directory Structure

```
clinic/                                   openmed/
├── app/                                  ├── openmed/                  ← pip-installable package
│   ├── config.py                         │   ├── core/
│   ├── main.py         (FastAPI)         │   │   ├── models.py
│   ├── retrieval.py    (FAISS + embeds)  │   │   ├── model_registry.py  (247+ models)
│   ├── summarizer.py   (Claude API)      │   │   ├── pii.py             (extract_pii, deidentify)
│   └── evaluator.py    (Precision@k)     │   │   ├── pii_i18n.py        (12-language routing)
│                                         │   │   ├── pii_entity_merger.py (BIOES/Viterbi)
├── data/                                 │   │   ├── quality_gates.py   (span validation)
│   └── loader.py       (CSV → docs)      │   │   ├── config.py          (profiles)
│                                         │   │   ├── backends.py        (torch/mlx routing)
├── scripts/                              │   │   └── anonymizer/
│   ├── ingest.py       (build index)     │   │       └── providers/      (Aadhaar, NPI, MRN…)
│   ├── demo.py         (CLI)             │   ├── mlx/                   ← Apple Silicon backend
│   ├── evaluate.py     (metrics)         │   │   ├── inference.py
│   └── make_*_pptx.py  (6 generators)   │   │   ├── convert.py
│                                         │   │   └── artifact.py
├── tests/                                │   ├── torch/
│   ├── test_api.py     (10 tests)        │   │   └── privacy_filter.py
│   └── test_retrieval.py (12 tests)      │   ├── coreml/                ← CoreML export
│                                         │   ├── processing/
├── .claude/skills/                       │   │   ├── text.py            (TextProcessor)
│   ├── clinical-query/SKILL.md           │   │   ├── outputs.py         (JSON/CSV/HTML)
│   └── make-pptx/SKILL.md               │   │   ├── batch.py           (BatchProcessor)
│                                         │   │   └── advanced_ner.py
├── Dockerfile                            │   ├── service/
├── requirements.txt                      │   │   └── app.py             (FastAPI)
├── README.md                             │   ├── zero_shot/             ← GLiNER
├── CLINICAL_EXAM.md                      │   └── utils/
└── CLAUDE_SKILLS_GUIDE.md               │
                                          ├── swift/OpenMedKit/          ← iOS/macOS SDK
                                          ├── examples/
                                          │   ├── notebooks/             ← Jupyter guides
                                          │   └── privacy_filter_studio/ ← web demo
                                          ├── tests/
                                          │   ├── unit/                  (218+ tests)
                                          │   └── integration/
                                          ├── docs/
                                          ├── .github/                   ← CI/CD
                                          ├── pyproject.toml
                                          ├── Package.swift              ← Swift SDK
                                          ├── uv.lock
                                          ├── Makefile
                                          ├── mkdocs.yml
                                          └── .pre-commit-config.yaml
```

---

## 3. Feature Comparison — Full Matrix

### 3.1 Retrieval & Search

| Feature | clinic | openmed |
|---|---|---|
| Semantic vector search | ✅ FAISS `IndexFlatIP` (exact cosine) | ❌ Not a retrieval system |
| Natural language query interface | ✅ `POST /retrieve?query=...` | ❌ |
| Top-k configurable results | ✅ `top_k` param (1–20) | ❌ |
| Ranked results with scores | ✅ rank + cosine score per result | ❌ |
| Result metadata (specialty, description, excerpt) | ✅ | ❌ |
| Keyword search | ❌ (embedding only) | ❌ |
| Hybrid search (dense + sparse) | ❌ | ❌ |
| Cross-encoder re-ranking | ❌ (listed as next step) | ❌ |
| Scale | 5,000 notes (demo) | N/A |
| Index persistence | ✅ FAISS binary + metadata pickle | N/A |
| Index reload on startup | ✅ < 1 s cold start | N/A |

---

### 3.2 Entity Extraction & NER

| Feature | clinic | openmed |
|---|---|---|
| Named Entity Recognition (NER) | ❌ | ✅ Token classification |
| Disease / condition detection | ❌ | ✅ `disease_detection_superclinical` (434M) |
| Drug / pharmaceutical detection | ❌ | ✅ `pharma_detection_superclinical` (434M) |
| Anatomy / body part detection | ❌ | ✅ `anatomy_detection_electramed` (109M) |
| Oncology entity detection | ❌ | ✅ `oncology_detection_superclinical` (434M) |
| Genomic / gene detection | ❌ | ✅ `gene_detection_genecorpus` (109M) |
| Zero-shot NER (new entity types, no retraining) | ❌ | ✅ GLiNER |
| Zero-shot text classification | ❌ | ✅ GLiClass |
| Relation extraction | ❌ | ✅ GLiNER-Relex |
| Medical-aware tokenization | Partial (embedding text concat) | ✅ pySBD + hyphenation (COVID-19, IL-6, CAR-T) |
| Confidence scores per entity | ❌ | ✅ 0–1 per span |
| Entity span validation | ❌ | ✅ `quality_gates.py` (start < end, in-bounds, text-match) |
| Overlap detection | ❌ | ✅ `detect_overlapping_entities()` |
| BIOES sequence labeling | ❌ | ✅ with Viterbi decoding (span repair) |
| Smart entity merging (tokenisation fragments) | ❌ | ✅ `pii_entity_merger.py` |

---

### 3.3 Privacy & De-identification

| Feature | clinic | openmed |
|---|---|---|
| PHI detection before indexing | ❌ Notes indexed raw | ✅ `extract_pii()` |
| HIPAA Safe Harbor identifiers covered | 0 of 18 | ✅ All 18 |
| Masking `[NAME]`, `[DATE]` | ❌ | ✅ `deidentify(method="mask")` |
| Removal of PHI spans | ❌ | ✅ `deidentify(method="remove")` |
| Faker-backed realistic replacement | ❌ | ✅ `deidentify(method="replace")` — locale-aware |
| Format-preserving replacement | ❌ | ✅ digit-group lengths for phones, separator/order for dates |
| Checksum-valid national ID surrogates | ❌ | ✅ SSN, Aadhaar (Verhoeff), TCKN, CPF/CNPJ, BSN, Codice Fiscale |
| Deterministic / seeded de-id | ❌ | ✅ `consistent=True, seed=42` |
| Date shifting (temporal relationships preserved) | ❌ | ✅ `deidentify(method="shift_dates")` |
| Cryptographic hashing (record linking) | ❌ | ✅ `deidentify(method="hash")` |
| De-id reversal for audit trails | ❌ | ✅ `reidentify(result, mapping)` |
| Confidence-aware PHI scoring | ❌ | ✅ 90/10 model/pattern weight + context scoring |
| Validation-aware confidence | ❌ | ✅ Confidence lowered when checksum fails |
| Custom Faker providers | ❌ | ✅ Aadhaar, German Steuer-ID, NPI, MRN, CPF/CNPJ, BSN, NIR, Codice Fiscale |
| 20+ PII regex patterns | ❌ | ✅ Dates, SSN, phone, email, street, postal, national IDs |
| HIPAA Safe Harbor compliance automated | ❌ | ✅ |
| Air-gapped de-identification | Partial (TF-IDF path) | ✅ Full on-premise |

---

### 3.4 LLM / Generative Layer

| Feature | clinic | openmed |
|---|---|---|
| LLM summarisation of retrieved notes | ✅ Claude claude-sonnet-4-6 via API | ❌ Pure extraction, no generation |
| Clinical system prompt (red flags, no hallucination) | ✅ 5-rule system prompt | ❌ |
| Rule-based fallback summary (no API key) | ✅ Lists specialties + scores | ❌ |
| Configurable max tokens | ✅ 1,024 default | ❌ |
| `include_summary` toggle (skip LLM call) | ✅ | ❌ |
| LLM-generated entity labels | ❌ | ❌ (NER, not generative) |
| Structured summary + retrieved docs in one response | ✅ | ❌ |

---

### 3.5 REST API

| Endpoint | clinic | openmed |
|---|---|---|
| `GET /health` | ✅ index size, model name | ✅ profile, status |
| `POST /retrieve` | ✅ | ❌ |
| `GET /retrieve` | ✅ (query params) | ❌ |
| `POST /analyze` | ❌ | ✅ NER entity extraction |
| `POST /pii/extract` | ❌ | ✅ PII detection |
| `POST /pii/deidentify` | ❌ | ✅ 5 de-id modes |
| Output formats | JSON only | JSON, dict, HTML, CSV |
| Input validation | ✅ Pydantic (query 3–1000 chars, top_k 1–20) | ✅ Pydantic |
| Structured error envelopes | Basic FastAPI defaults | ✅ validation / bad-request / timeout / internal |
| Batch endpoint | ❌ | ✅ via `BatchProcessor` |
| Model preloading at startup | Auto (index) | ✅ `OPENMED_SERVICE_PRELOAD_MODELS` env var |
| Request timeout handling | ❌ | ✅ |
| CORS | ✅ | Not confirmed |

---

### 3.6 Embedding / Model Backends

| Feature | clinic | openmed |
|---|---|---|
| Backend abstraction layer | ✅ `EmbeddingBackend` ABC | ✅ `backends.py` (torch / mlx / coreml) |
| Dense embedding backend | ✅ SentenceTransformer (HF) | ❌ (NER, not embedding) |
| Sparse/offline embedding backend | ✅ TF-IDF + LSA (scikit-learn, 256-dim) | ❌ |
| HuggingFace Transformers | ✅ `sentence-transformers` | ✅ `transformers` (NER) |
| Auto-fallback when HF Hub unreachable | ✅ TF-IDF/LSA activates | ❌ |
| MLX (Apple Silicon) backend | ❌ | ✅ `openmed[mlx]` |
| CoreML backend | ❌ | ✅ `openmed[coreml]` |
| PyTorch backend | ✅ (via sentence-transformers) | ✅ `openmed/torch/` |
| L2 normalisation before indexing | ✅ Guarantees cosine via inner product | N/A |
| Model swap without code change | ✅ `EMBEDDING_MODEL` env var | ✅ `model_name` param or env var |
| Model registry | 3 options | 247 PII + 12+ NER models |
| Model sizes available | 22M–768M | 33M–568M |
| Privacy Filter arch (gpt-oss sparse-MoE, tiktoken) | ❌ | ✅ Nemotron + Multilingual variants |
| GitHub Actions model conversion pipeline | ❌ | ✅ `convert-models.yml` (HF → MLX) |

---

### 3.7 Evaluation & Metrics

| Feature | clinic | openmed |
|---|---|---|
| Precision@k (specialty match) | ✅ | ❌ |
| Keyword recall@k | ✅ | ❌ |
| Mean cosine score | ✅ | ❌ |
| Score spread (rank-1 minus rank-k) | ✅ | ❌ |
| Predefined test queries | ✅ 7 clinical queries | ❌ |
| Model comparison mode (`--compare-models`) | ✅ | ❌ |
| Per-query + macro averages | ✅ | ❌ |
| Semantic-vs-keyword proof | ✅ Vocabulary-disjoint queries | ❌ |
| NER benchmark numbers | ❌ | ✅ SOTA on 10/12 biomedical NER benchmarks (+9.7 F1 pp) |
| Per-model F1 / precision / recall | ❌ | ✅ (arXiv 2508.01630) |
| Regression test suite for multilingual PII | ❌ | ✅ `test_pii_multilingual_regression.py` |

---

### 3.8 Batch & Throughput

| Feature | clinic | openmed |
|---|---|---|
| Single-request inference | ✅ | ✅ |
| Batch document processing | ❌ | ✅ `BatchProcessor` (`BatchItem`, `BatchItemResult`, `BatchResult`) |
| Progress tracking for batch | ❌ | ✅ |
| Performance profiling | ❌ | ✅ `profile_inference()` / `ProfileReport` |
| Embedding batch size (ingest) | ✅ `batch_size=64` during index build | N/A |
| Async endpoints | ❌ (sync FastAPI) | Not confirmed |

---

### 3.9 Deployment

| Feature | clinic | openmed |
|---|---|---|
| Docker | ✅ `python:3.11-slim` | ✅ CPU-focused, health-check configured |
| Docker Compose | ❌ | Not confirmed |
| uvicorn | ✅ | ✅ |
| On-premise / air-gapped | Partial (TF-IDF path) | ✅ Full support documented |
| Sovereign AI positioning | ❌ | ✅ "No data leaves the machine" |
| Health-check in Dockerfile | ❌ | ✅ |
| Multi-stage Docker build | ❌ | Not confirmed |
| `.dockerignore` | ❌ | ✅ |
| Makefile targets | ❌ | ✅ |
| Pre-commit hooks | ❌ | ✅ `.pre-commit-config.yaml` |

---

### 3.10 Platform & Device

| Platform | clinic | openmed |
|---|---|---|
| Linux server | ✅ | ✅ |
| Docker | ✅ | ✅ |
| Apple Silicon Mac (MLX) | ❌ | ✅ |
| iOS / iPadOS | ❌ | ✅ CoreML + MLX via OpenMedKit |
| macOS (native) | ❌ | ✅ Swift package |
| iOS demo app | ❌ | ✅ Document → OCR → PII → Extract → Summary → Export |
| CoreML `.mlpackage` export | ❌ | ✅ `openmed/coreml/` |
| Swift Package Manager | ❌ | ✅ `Package.swift` |
| SwiftUI | ❌ | ✅ (tagged in repo topics) |

---

### 3.11 Language Support

| Language | clinic | openmed |
|---|---|---|
| English | ✅ | ✅ + SSN regex validator |
| French | ❌ | ✅ + NIR (French SSN), postal codes (dept. 01–95, 971–976) |
| German | ❌ | ✅ + Steuer-ID (leading-zero rejection) |
| Italian | ❌ | ✅ + Codice Fiscale |
| Spanish | ❌ | ✅ + DNI/NIE |
| Dutch | ❌ | ✅ + BSN |
| Hindi | ❌ | ✅ + Aadhaar (Verhoeff checksum) |
| Telugu | ❌ | ✅ + Aadhaar |
| Portuguese | ❌ | ✅ + CPF/CNPJ (checksum) |
| Arabic | ❌ | ✅ + national ID patterns |
| Japanese | ❌ | ✅ |
| Turkish | ❌ | ✅ + TCKN (checksum validated) |
| Day-first date parsing | ❌ | ✅ FR, DE, IT, ES, NL, HI, TE, PT, AR, TR |
| Per-language model | ❌ | ✅ Dedicated checkpoint per language |

---

### 3.12 Configuration & Profiles

| Feature | clinic | openmed |
|---|---|---|
| Environment variables | ✅ `EMBEDDING_MODEL`, `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, `TOP_K`, `INDEX_PATH`, `DATA_CSV_PATH` | ✅ Extensive |
| Config object | ❌ (env vars only) | ✅ `OpenMedConfig(device, cache_dir, backend, auth_token, ...)` |
| Built-in profiles | ❌ | ✅ `dev`, `prod`, `test`, `fast` |
| YAML config support | ❌ | ✅ |
| Profile management | ❌ | ✅ `list_profiles()`, `get_profile()`, `save_profile()`, `delete_profile()` |
| Model preload env var | ❌ | ✅ `OPENMED_SERVICE_PRELOAD_MODELS` |
| Trusted remote code allowlist | ❌ | ✅ `OPENMED_TRUSTED_REMOTE_CODE_MODELS` |

---

### 3.13 Developer Experience

| Feature | clinic | openmed |
|---|---|---|
| pip install | ❌ (clone repo) | ✅ `pip install openmed[hf]` |
| One-liner inference | ❌ | ✅ `openmed.analyze_text(text)` |
| CLI demo | ✅ `scripts/demo.py` | ❌ (confirmed — no CLI entry point found) |
| Jupyter notebooks | ❌ | ✅ `PII_Detection_Complete_Guide.ipynb`, `Multilingual_PII_Detection_Guide.ipynb`, `Sentence_Detection_Batching.ipynb` |
| Web demo (privacy filter studio) | ❌ | ✅ FastAPI + static HTML (`examples/privacy_filter_studio/`) |
| Claude Code skills | ✅ `/clinical-query`, `/make-pptx` | ✅ `.claude/` (skills unknown) |
| Custom PPTX presentation generator | ✅ (6 generators, 2 detailed decks) | ❌ |
| Model obfuscation demo | ❌ | ✅ `examples/obfuscation_demo.py` |
| Model comparison script | ✅ `--compare-models` flag | ✅ `examples/pii_model_comparison.py` |
| Output format choice | JSON | JSON, dict, HTML, CSV |

---

### 3.14 Security

| Feature | clinic | openmed |
|---|---|---|
| `trust_remote_code` hardening | N/A (no remote code paths) | ✅ Hard allowlist in v1.5.2 (patched RCE) |
| Allowlist for trusted model repos | N/A | ✅ `TRUSTED_REMOTE_CODE_MODELS` + operator override |
| Security-specific test file | ❌ | ✅ `test_privacy_filter_security.py` |
| Known past vulnerability | None | v1.5.2 patched RCE: any model named "privacy-filter" previously got `trust_remote_code=True` — enabling RCE via `/pii/extract` |
| Attack surface | Low (no remote code execution) | Broader (model loading) — now hardened |
| Input validation | ✅ Pydantic (min 3 chars, top_k bounds) | ✅ Pydantic + structured error envelopes |

---

### 3.15 Testing

| | clinic | openmed |
|---|---|---|
| Total tests | 20 | 218+ |
| Unit — retrieval / NER | 12 | `test_pii.py`, `test_anonymizer.py`, `test_quality_gates.py` |
| Unit — routing / registry | ❌ | `test_privacy_filter_routing.py`, `test_model_registry_multilingual.py`, `test_label_map_consistency.py` |
| Unit — MLX | ❌ | `mlx/test_mlx_inference.py` |
| API tests | 10 (FastAPI TestClient) | `service/test_api.py` |
| Integration | ❌ | `test_sentence_detection_real.py` |
| Regression (multilingual PII) | ❌ | `test_pii_multilingual_regression.py` |
| Security | ❌ | `test_privacy_filter_security.py` |
| Span validation guards | ❌ | 19 dedicated tests in `quality_gates.py` |
| No external dependencies for tests | ✅ TF-IDF fallback | ✅ (assumed) |

---

### 3.16 Documentation

| | clinic | openmed |
|---|---|---|
| README | ✅ | ✅ |
| Architecture explanation | ✅ (README + CLINICAL_EXAM.md) | ✅ |
| Assessment submission doc | ✅ CLINICAL_EXAM.md | ❌ |
| Full docs site | ❌ | ✅ `mkdocs.yml` |
| API reference | ✅ (in README) | ✅ (docs site) |
| Jupyter notebooks | ❌ | ✅ 3 notebooks |
| CHANGELOG | ❌ | ✅ `CHANGELOG.md` |
| arXiv paper | ❌ | ✅ 2508.01630 |
| Skills guide | ✅ CLAUDE_SKILLS_GUIDE.md | ❌ |
| Presentation decks | ✅ 5 PPTX files (10–15 slides each) | ❌ |

---

## 4. What clinic does that OpenMed does not

OpenMed is a de-identification and entity extraction toolkit. It does **not** search, rank, or synthesise — that is entirely clinic's territory.

| Capability | Detail |
|---|---|
| **Semantic retrieval** | FAISS `IndexFlatIP` (exact cosine similarity) over 5,000+ embedded clinical notes. Given a doctor's natural language query, returns ranked relevant past cases. OpenMed has no search capability whatsoever. |
| **Doctor query interface** | `POST /retrieve` accepts free-text clinical queries and returns ranked notes with similarity scores — the primary clinical decision-support interaction that OpenMed never addresses. |
| **LLM synthesis layer** | Claude claude-sonnet-4-6 generates a ≤ 300-word clinical summary across the top-k retrieved notes, with red-flag highlighting and no-hallucination enforcement. OpenMed is purely extractive — it finds entities but never generates prose. |
| **Rule-based fallback summary** | When `ANTHROPIC_API_KEY` is absent, a structured fallback summary still runs (lists specialties, scores, top terms). The system is functional without any external API. |
| **TF-IDF + LSA offline embedding** | When HuggingFace Hub is unreachable, TF-IDF + Truncated SVD (256-dim, scikit-learn) activates automatically. Same FAISS index structure, same API surface — zero code changes. OpenMed has no equivalent offline retrieval path. |
| **Precision@k evaluation** | Structured evaluation framework: Precision@k (specialty match), keyword recall@k, mean cosine score, score spread. Seven predefined clinical queries with expected specialty labels. OpenMed ships NER benchmark numbers from arXiv but no retrieval evaluation. |
| **Semantic-vs-keyword proof** | Vocabulary-disjoint test queries (query uses "renal insufficiency", document says "chronic kidney disease") demonstrate that dense embeddings succeed where keyword search returns zero results. Quantified, reproducible. |
| **Model comparison mode** | `scripts/evaluate.py --compare-models` runs the evaluation harness on both base and clinical embedding models side-by-side with delta metrics. |
| **Custom Claude Code skills** | `/clinical-query` (semantic search via chat) and `/make-pptx` (automated PPTX generation with QA and git commit). Operational automation that OpenMed doesn't have in its `.claude/` setup (skills unknown). |
| **Presentation generation** | Six PPTX generators producing 10–15-slide decks with QA loops. Not relevant to clinical NLP, but shows a complete workflow automation story that OpenMed doesn't ship. |

---

## 5. What OpenMed does that clinic defers entirely

Every item below is either explicitly listed as a future step in clinic's slides or simply absent with no mention.

| Capability | clinic status | OpenMed detail |
|---|---|---|
| **PHI de-identification** | Slide 15: *"PHI de-identification layer before any production use"* | Five methods: mask, remove, replace (Faker, format-preserving, checksum-valid), hash, shift_dates. Plus `reidentify()` for audit reversal. |
| **HIPAA Safe Harbor (18 identifiers)** | 0 of 18 covered — notes indexed raw | All 18 detected and removable. Smart entity merging handles tokenisation fragments. |
| **De-id reversal (audit trail)** | Not addressed | `reidentify(result, mapping)` reverses de-identification using stored entity mappings — critical for clinical audit. |
| **Clinical NER (disease, drug, anatomy, oncology, gene)** | Not addressed | 12+ curated NER models from 65M to 568M params, SOTA on 10/12 biomedical benchmarks. |
| **Zero-shot NER** | Not addressed | GLiNER: detect any entity type without retraining — add new clinical concepts on the fly. |
| **Multilingual support** | English only | 12 languages, each with a dedicated fine-tuned checkpoint and locale-specific regex validators + checksum-valid national ID surrogates. |
| **Fine-tuned biomedical models** | Slide 10: *"Optional: Fine-tune the embedding model"* (estimated, not implemented) | DAPT + LoRA fine-tuning on biomedical corpora, SOTA on 10/12 benchmarks. Already shipped. |
| **Batch document processing** | Not addressed | `BatchProcessor` with `BatchItem`, `BatchItemResult`, `BatchResult` — multi-document workflows with progress tracking. |
| **Apple Silicon acceleration** | Not addressed | MLX backend — native Apple Silicon inference via `openmed[mlx]`. |
| **iOS / macOS native SDK** | Not addressed | OpenMedKit Swift package: token classification, GLiNER, Privacy Filter on iPhone/iPad via CoreML/MLX. iOS demo app (OCR → PII → Extract → Summary → Export). |
| **Output format flexibility** | JSON only | JSON, dict, HTML, CSV — plugs into reporting pipelines without transformation. |
| **Performance profiling** | Not addressed | `profile_inference()` / `ProfileReport` — bottleneck analysis built in. |
| **Config profiles** | env vars only | `dev`, `prod`, `test`, `fast` profiles via `OpenMedConfig`. YAML-serialisable for reproducible deployments. |
| **CI/CD pipeline** | None | `.github/` workflows including automated HF → MLX model conversion (`convert-models.yml`). |
| **Security hardening** | No attack surface (no remote code paths) | v1.5.2 patched RCE: hard `trust_remote_code` allowlist, security test file, operator override env var. |
| **Production packaging** | Clone + pip | `pip install openmed[hf]` — semantic versioned PyPI releases (32 to date), `uv.lock` for reproducible installs. |
| **Relation extraction** | Not addressed | GLiNER-Relex — extract structured relations between clinical entities (e.g. drug–disease, anatomy–procedure). |

---

## 6. Model Ecosystem

### clinic — 3 options

| Model | Params | Dims | Task | Source |
|---|---|---|---|---|
| `all-MiniLM-L6-v2` | 22M | 384 | Sentence embedding (default) | Pretrained, HuggingFace |
| `S-PubMedBert-MS-MARCO` | ~110M | 768 | Clinical sentence embedding | Pretrained, HuggingFace |
| TF-IDF + LSA | — | 256 | Sparse embedding (offline fallback) | scikit-learn `TruncatedSVD` |

Plus: **Claude claude-sonnet-4-6** via API (not local) for the summarisation layer.

### openmed — 247 PII models + 12+ NER models

**Clinical NER models (`OpenMed/OpenMed-NER-*`):**

| Registry key | Model ID | Domain | Params |
|---|---|---|---|
| `disease_detection_superclinical` | OpenMed-NER-DiseaseDetect-SuperClinical-434M | Disease | 434M |
| `disease_detection_tiny` | OpenMed-NER-DiseaseDetect-TinyMed-135M | Disease | 135M |
| `oncology_detection_superclinical` | OpenMed-NER-OncologyDetect-SuperClinical-434M | Oncology | 434M |
| `oncology_detection_tiny` | OpenMed-NER-OncologyDetect-TinyMed-65M | Oncology | 65M |
| `pharma_detection_superclinical` | OpenMed-NER-PharmaDetect-SuperClinical-434M | Pharmaceutical | 434M |
| `pharma_detection_bigmed` | OpenMed-NER-PharmaDetect-BigMed-278M | Pharmaceutical | 278M |
| `anatomy_detection_electramed` | OpenMed-NER-AnatomyDetect-ElectraMed | Anatomy | 109M |
| `gene_detection_genecorpus` | OpenMed-NER-GenomicDetect-PubMed-109M | Gene/Genomic | 109M |
| `oncology_multimed` | OpenMed-NER-OncologyDetect-MultiMed-568M | Oncology | 568M |

**PII model families (247 total across 12 languages):**

Model name suffixes encode backbone + size:
`TinyMed` (33–65M) · `LiteClinical` · `FastClinical` (82M) · `SuperClinical-Small` (44M) · `ClinicalE5-Base` (109M) · `ClinicalE5-Large` (335M) · `BigMed-Large` (560M) · `SnowflakeMed-Large` (568M) · `NomicMed-Large` (395M) · `ModernMed-Base` (149M) · `mSuperClinical-Large` (279M) · `SuperMedical` (355M) · `MultiMed` (568M)

**Privacy Filter family (3 variants, each with PyTorch + MLX + MLX-8bit):**

| Family | Architecture | Training data |
|---|---|---|
| OpenAI Privacy Filter | gpt-oss sparse-MoE, tiktoken `o200k_base`, RoPE/YaRN, Viterbi BIOES | OpenAI PII set |
| Nemotron Privacy Filter | Same arch | NVIDIA Nemotron-PII-v1 |
| Multilingual Privacy Filter | Same arch | OpenMed multilingual PII corpus, 16 languages |

Architecture bases supported (MLX path): BERT, DistilBERT, RoBERTa, XLM-RoBERTa, ELECTRA, DeBERTa-v2/v3, gpt-oss sparse-MoE, GLiNER bi-encoder span.

---

## 7. API Surface Detail

### clinic endpoints

```
GET  /health
     → { "status": "ok", "doc_count": 5000,
         "embedding_model": "all-MiniLM-L6-v2" }

POST /retrieve
     Body: { "query": str (3–1000 chars),
             "top_k": int (1–20, default 5),
             "include_summary": bool (default true) }
     → { "query": str,
         "total_retrieved": int,
         "embedding_model": str,
         "results": [
           { "rank": int,
             "score": float,        // cosine similarity 0–1
             "specialty": str,
             "description": str,
             "keywords": str,
             "excerpt": str         // first 500 chars of transcription
           }
         ],
         "summary": str | null      // LLM or rule-based fallback
       }

GET  /retrieve?query=...&top_k=5   // same response, browser-friendly
```

### openmed endpoints

```
GET  /health
     → { "status": "ok", "profile": "prod", ... }

POST /analyze
     Body: { "text": str, "model_name": str, "output_format": str }
     → dict of extracted medical entities

POST /pii/extract
     Body: { "text": str, "model_name": str | null,
             "lang": str (default "en"),
             "confidence_threshold": float (default 0.5),
             "use_smart_merging": bool }
     → PredictionResult.to_dict():
       { "entities": [
           { "type": "NAME" | "DATE" | "SSN" | "PHONE" | "EMAIL" |
                     "ADDRESS" | "MRN" | "DISEASE" | ...,
             "text": str,
             "start": int, "end": int,
             "score": float }
         ] }

POST /pii/deidentify
     Body: { "text": str,
             "method": "mask"|"remove"|"replace"|"hash"|"shift_dates",
             "lang": str,
             "locale": str | null,
             "consistent": bool,
             "seed": int | null,
             "confidence_threshold": float }
     → DeidentificationResult:
       { "deidentified_text": str,
         "entity_mapping": { original: surrogate, ... },  // for reidentify()
         "entities": [...] }
```

---

## 8. Production Pipeline — Merged Architecture

The two systems are complementary. OpenMed is the missing upstream step; clinic is the downstream interface.

```
Raw discharge notes
(LinkedIn post: average 13 PHI identifiers per note × 5,000 notes
= 65,000+ pieces of raw PHI currently embedded verbatim in clinic's FAISS index)

        │
        ▼
┌───────────────────────────────────────────────────────┐
│  openmed.deidentify(                                  │  ← ONE function call
│      text,                                            │     added to data/loader.py
│      method="replace",       # realistic surrogates   │     _build_embedding_text()
│      lang="en",                                       │
│      consistent=True,        # same surrogate per run │
│      seed=42                 # deterministic          │
│  )                                                    │
│                                                       │
│  "John Smith" → "Mary Jones"  (format-preserving)    │
│  "MRN-289341" → "MRN-847291"  (same digit structure) │
│  "04/15/1965" → "07/22/1971"  (date shifted)         │
└───────────────────────────────────────────────────────┘
        │
        ▼ de-identified text
┌───────────────────────────────────────────────────────┐
│  scripts/ingest.py                                    │  ← clinic (unchanged)
│  → FAISS IndexFlatIP                                  │
│  → data/faiss.index + data/metadata.pkl               │
└───────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  POST /retrieve                                       │  ← clinic (unchanged)
│  { "query": "diabetic patient with kidney             │
│              complications", "top_k": 5 }             │
│                                                       │
│  1. Embed query (all-MiniLM-L6-v2)                   │
│  2. FAISS cosine search                               │
│  3. Return ranked results + Claude summary            │
└───────────────────────────────────────────────────────┘
        │
        ▼
HIPAA-safe clinical decision support
```

**Code change required in clinic:** 3 lines in `data/loader.py`:

```python
# Before (current):
def _build_embedding_text(row) -> str:
    return f"{row['specialty']} | {row['description']} | {row['transcription'][:2000]}"

# After (HIPAA-safe):
from openmed import deidentify

def _build_embedding_text(row) -> str:
    raw = f"{row['specialty']} | {row['description']} | {row['transcription'][:2000]}"
    return deidentify(raw, method="replace", consistent=True, seed=42).deidentified_text
```

Nothing else changes. Retrieval, scoring, summarisation, API surface — all identical.

---

## 9. Verdict

| Dimension | clinic | openmed | Winner |
|---|---|---|---|
| Semantic retrieval quality | Dense embeddings + FAISS exact cosine | N/A | **clinic** |
| LLM synthesis | Claude claude-sonnet-4-6, clinical system prompt | None | **clinic** |
| Offline resilience | TF-IDF/LSA auto-fallback | None equivalent | **clinic** |
| Retrieval evaluation framework | Precision@k, recall, score spread, 7 queries | None | **clinic** |
| Privacy / PHI / HIPAA compliance | 0 of 18 identifiers | All 18 + 5 de-id modes + reidentify | **openmed** |
| Model diversity | 3 options | 247 PII + 12+ NER | **openmed** |
| NER / entity extraction | None | 12+ clinical NER models, SOTA benchmarks | **openmed** |
| Multilingual | English only | 12 languages, per-lang validators + checkpoints | **openmed** |
| Platform breadth | Python + Docker | Python + Docker + MLX + iOS + macOS | **openmed** |
| Production readiness | Assessment prototype | v1.5.2, 838 commits, CI/CD, 32 releases, 1M+ downloads | **openmed** |
| Batch processing | Single request only | BatchProcessor class | **openmed** |
| Security posture | Low attack surface | Patched RCE (v1.5.2), security test file | **openmed** (depth) |
| Test coverage | 20 tests | 218+ tests | **openmed** |
| Developer onboarding | Clone repo | `pip install openmed[hf]` | **openmed** |
| Simplicity / focus | Single, well-defined task | Broad toolkit — steeper learning curve | **clinic** |
| Integration potential | — | — | **Complementary** |

**Bottom line:** These repos solve different halves of the same production problem.
The LinkedIn post ("your discharge summary has 13 identifiers") is the precise argument for why clinic's
deferred "PHI de-identification layer" is not optional — it is a hard prerequisite.
OpenMed is the best open-source answer to that prerequisite.
Plugging `openmed.deidentify()` into `data/loader.py` is a 3-line change that makes the entire
clinic pipeline HIPAA-safe without touching retrieval, scoring, or summarisation.

---

*Sources:*
- *[skunpoj/clinic — GitHub](https://github.com/skunpoj/clinic)*
- *[maziyarpanahi/openmed — GitHub](https://github.com/maziyarpanahi/openmed)*
- *[openmed on PyPI v1.5.2](https://pypi.org/project/openmed/)*
- *[OpenMed NER — arXiv 2508.01630](https://arxiv.org/pdf/2508.01630)*
- *[Maziyar Panahi — HuggingFace: NER announcement](https://huggingface.co/posts/MaziyarPanahi/751516664507693)*
- *[Maziyar Panahi — HuggingFace: Multilingual PII](https://huggingface.co/posts/MaziyarPanahi/635149700926351)*
- *[OpenMed-PII-ClinicalE5-Large-335M-v1](https://huggingface.co/OpenMed/OpenMed-PII-ClinicalE5-Large-335M-v1)*
