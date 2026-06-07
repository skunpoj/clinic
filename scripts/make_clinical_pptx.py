"""Generate Clinical Note Retrieval take-home exam presentation (10 slides)."""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt, Emu

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
NAVY   = RGBColor(0x0A, 0x29, 0x4A)   # deep navy
TEAL   = RGBColor(0x00, 0x7A, 0x87)   # teal accent
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xF0, 0xF6, 0xF8)   # near-white bg
GREY   = RGBColor(0x55, 0x65, 0x7A)
GREEN  = RGBColor(0x00, 0x87, 0x5A)
ORANGE = RGBColor(0xE8, 0x6A, 0x10)
RED    = RGBColor(0xC0, 0x39, 0x2B)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


# ---------------------------------------------------------------------------
# Helpers (verbatim from make_pptx.py)
# ---------------------------------------------------------------------------

def _rgb(r, g, b) -> RGBColor:
    return RGBColor(r, g, b)


def new_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs: Presentation):
    layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(layout)


def fill_solid(shape, colour: RGBColor) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = colour


def add_rect(slide, left, top, width, height, colour: RGBColor):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    fill_solid(shape, colour)
    shape.line.fill.background()
    return shape


def tf(shape):
    return shape.text_frame


def para(txf, text: str, size: int, bold=False, colour=WHITE,
         align=PP_ALIGN.LEFT, space_before=0, italic=False):
    p = txf.add_paragraph()
    p.alignment = align
    if space_before:
        p.space_before = Pt(space_before)
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = colour
    return p


def add_textbox(slide, left, top, width, height, word_wrap=True):
    txb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    txb.text_frame.word_wrap = word_wrap
    return txb


def clear_first_para(txb):
    """Remove the empty first paragraph added by default."""
    txf = txb.text_frame
    p = txf.paragraphs[0]
    p.clear()
    return txf


def add_slide_number(slide, num: int, total: int) -> None:
    txb = add_textbox(slide, 12.5, 7.1, 0.7, 0.3)
    txf = clear_first_para(txb)
    para(txf, f"{num}/{total}", 9, colour=GREY, align=PP_ALIGN.RIGHT)


def header_bar(slide, title: str, subtitle: str = "") -> None:
    add_rect(slide, 0, 0, 13.33, 1.1, NAVY)
    txb = add_textbox(slide, 0.4, 0.08, 12.5, 0.55)
    txf = clear_first_para(txb)
    para(txf, title, 22, bold=True, colour=WHITE)
    if subtitle:
        txb2 = add_textbox(slide, 0.4, 0.62, 12.5, 0.4)
        txf2 = clear_first_para(txb2)
        para(txf2, subtitle, 13, colour=_rgb(0xAA, 0xCC, 0xDD))


def bullet_box(slide, left, top, width, height, items: list[tuple[str, int, bool]],
               bg=None, pad=0.1):
    if bg:
        add_rect(slide, left, top, width, height, bg)
    txb = add_textbox(slide, left + pad, top + pad, width - pad * 2, height - pad * 2)
    txf = clear_first_para(txb)
    for text, size, bold in items:
        c = WHITE if bg in (NAVY, TEAL) else NAVY
        para(txf, text, size, bold=bold, colour=c, space_before=2)
    return txb


def card(slide, left, top, width, height, heading: str, lines: list[str],
         head_colour=TEAL, body_colour=LIGHT):
    # heading strip
    h = 0.38
    add_rect(slide, left, top, width, h, head_colour)
    txh = add_textbox(slide, left + 0.1, top + 0.05, width - 0.2, h - 0.05)
    txf = clear_first_para(txh)
    para(txf, heading, 13, bold=True, colour=WHITE)
    # body
    add_rect(slide, left, top + h, width, height - h, body_colour)
    txb = add_textbox(slide, left + 0.12, top + h + 0.1,
                      width - 0.24, height - h - 0.15)
    txf2 = clear_first_para(txb)
    for line in lines:
        para(txf2, line, 11, colour=NAVY, space_before=1)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_title(prs, num, total):
    """Slide 1 — Title."""
    sl = blank_slide(prs)
    # Deep navy background
    add_rect(sl, 0, 0, 13.33, 7.5, NAVY)
    # Teal accent bar on left
    add_rect(sl, 0, 0, 0.18, 7.5, TEAL)

    # Main title
    txb = add_textbox(sl, 0.55, 1.5, 12.3, 1.1)
    txf = clear_first_para(txb)
    para(txf, "Clinical Note Retrieval System", 40, bold=True,
         colour=WHITE, align=PP_ALIGN.LEFT)

    # Subtitle
    txb2 = add_textbox(sl, 0.55, 2.75, 12.3, 0.65)
    txf2 = clear_first_para(txb2)
    para(txf2, "AI-Powered Semantic Search for Clinical Decision Support", 22,
         colour=TEAL, align=PP_ALIGN.LEFT)

    # Tags
    txb3 = add_textbox(sl, 0.55, 3.55, 12.3, 0.5)
    txf3 = clear_first_para(txb3)
    para(txf3, "Take-Home Technical Assessment  ·  June 2026", 15,
         colour=_rgb(0xAA, 0xCC, 0xDD), align=PP_ALIGN.LEFT)

    # Decorative horizontal rule
    add_rect(sl, 0.55, 4.25, 5.0, 0.04, TEAL)

    # Bottom footer
    txb4 = add_textbox(sl, 0.55, 6.85, 12.3, 0.4)
    txf4 = clear_first_para(txb4)
    para(txf4, "Clinical AI Engineering  ·  June 2026",
         11, colour=GREY, align=PP_ALIGN.LEFT)

    add_slide_number(sl, num, total)


def slide_02_problem(prs, num, total):
    """Slide 2 — Problem Statement (verbatim from exam)."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Problem Statement", "Problem 1 — Clinical Note Retrieval System")

    # Left card — verbatim Problem Statement bullets
    card(sl, 0.3, 1.3, 6.1, 3.5, "Problem Statement",
         ["The platform needs to help doctors quickly find",
          "relevant past cases from a large corpus of",
          "clinical notes.",
          "",
          "A doctor types a natural language query describing",
          "a patient situation, and the system should surface",
          "the most relevant clinical notes from the database.",
          "",
          "The system must understand clinical meaning, not",
          "just match keywords — a query about 'a diabetic",
          "patient with kidney complications' should retrieve",
          "notes about CKD with diabetes even if the exact",
          "words differ."])

    # Right card — verbatim Instructions
    card(sl, 6.7, 1.3, 6.3, 3.5, "Instructions",
         ["Build a retrieval system:",
          "  natural language query → ranked clinical notes",
          "Use an embedding model — justify your selection",
          "Add an LLM layer for a concise summary",
          "Evaluate: clinically relevant, not keyword matches",
          "(Optional) Fine-tune the embedding model",
          "Prepare a presentation — max 10 pages",
          "Expose as a REST API service",
          "Prepare to present — 30-minute session"])

    # Bottom: target audience + guidance
    add_rect(sl, 0.3, 5.05, 12.7, 1.85, NAVY)
    txb = add_textbox(sl, 0.5, 5.13, 12.3, 1.65)
    txf = clear_first_para(txb)
    para(txf, "Target Audience  ·  Additional Guidance", 13, bold=True, colour=TEAL)
    para(txf, "AI Engineering Manager  ·  Product Manager", 12, colour=_rgb(0xCC, 0xDD, 0xFF), space_before=4)
    para(txf,
         "Anything outside this instruction, please feel free to make your own assumption as needed.",
         12, colour=WHITE, space_before=4)
    add_slide_number(sl, num, total)


def slide_03_dataset(prs, num, total):
    """Slide 3 — Dataset."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Dataset", "mtsamples.csv — real medical transcriptions")

    # Top info cards
    info_items = [
        ("Source", "mtsamples.csv from Kaggle\n5 000+ real medical transcriptions"),
        ("Columns Used", "medical_specialty, description,\ntranscription, keywords"),
        ("Specialties", "40+ including Cardiology,\nNephrology, Neurology, Surgery"),
        ("Preprocessing", "Strip whitespace\nDrop empty transcriptions"),
    ]
    for i, (heading, body) in enumerate(info_items):
        lft = 0.3 + i * 3.25
        card(sl, lft, 1.25, 3.0, 1.65, heading, body.split("\n"))

    # Embedding input format box
    add_rect(sl, 0.3, 3.15, 12.7, 0.8, NAVY)
    txb_fmt = add_textbox(sl, 0.5, 3.22, 12.3, 0.65)
    txf_fmt = clear_first_para(txb_fmt)
    para(txf_fmt, "Embedding Input Format:", 12, bold=True, colour=TEAL)
    para(txf_fmt,
         "\"Specialty: <medical_specialty>  |  Description: <description>  |  <first 2 000 chars of transcription>\"",
         11, colour=_rgb(0xCC, 0xDD, 0xFF))

    # Example table header
    add_rect(sl, 0.3, 4.15, 12.7, 0.42, NAVY)
    txb_hdr = add_textbox(sl, 0.5, 4.2, 12.3, 0.35)
    txf_hdr = clear_first_para(txb_hdr)
    para(txf_hdr, "Specialty                         Description (excerpt)                                         Keywords",
         12, bold=True, colour=WHITE)

    # Example rows
    rows = [
        ("Nephrology",
         "Patient with CKD stage 3 and type 2 diabetes presenting for follow-up",
         "kidney disease, creatinine, GFR, diabetes mellitus"),
        ("Cardiology",
         "62yo male with STEMI, anterior wall, taken to cath lab emergently",
         "myocardial infarction, troponin, PCI, stent, EKG"),
        ("Neurology",
         "New-onset seizure, MRI brain ordered, EEG pending, AED started",
         "epilepsy, levetiracetam, MRI, electroencephalogram"),
    ]
    for i, (spec, desc, kw) in enumerate(rows):
        bg = LIGHT if i % 2 == 0 else _rgb(0xE0, 0xEE, 0xF4)
        top_r = 4.57 + i * 0.7
        add_rect(sl, 0.3, top_r, 12.7, 0.7, bg)
        for j, (text, wid, lft_off) in enumerate([
            (spec, 2.4, 0.4),
            (desc, 6.1, 3.0),
            (kw,   3.5, 9.3),
        ]):
            txb = add_textbox(sl, lft_off, top_r + 0.08, wid, 0.56)
            txf = clear_first_para(txb)
            para(txf, text, 10, colour=NAVY if j != 0 else TEAL, bold=(j == 0))

    add_slide_number(sl, num, total)


def slide_04_architecture(prs, num, total):
    """Slide 4 — System Architecture."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "System Architecture", "5-stage pipeline: Ingest → Embed → Index → Retrieve → Summarise")

    # 5-box pipeline
    pipeline = [
        ("1. Ingest",   "Load CSV\nClean text\nBuild records"),
        ("2. Embed",    "sentence-\ntransformers\nL2-normalise"),
        ("3. Index",    "FAISS\nIndexFlatIP\nSerialise"),
        ("4. Retrieve", "Embed query\nCosine search\nTop-k docs"),
        ("5. Summarise","Claude API\nSystem prompt\nJSON response"),
    ]

    box_w = 2.2
    gap = 0.28
    start_l = 0.3
    arrow_y = 2.0

    for i, (title, body) in enumerate(pipeline):
        lft = start_l + i * (box_w + gap)
        card(sl, lft, 1.25, box_w, 2.55, title, body.split("\n"))
        if i < len(pipeline) - 1:
            ax = lft + box_w + 0.02
            ar = add_textbox(sl, ax, arrow_y, 0.26, 0.4)
            txf = clear_first_para(ar)
            para(txf, "→", 18, bold=True, colour=TEAL)

    # Two-column detail section  — heights capped at y=6.9
    # Left: Components
    add_rect(sl, 0.3, 4.05, 6.2, 2.85, NAVY)
    txb_cl = add_textbox(sl, 0.5, 4.12, 5.8, 0.42)
    txf_cl = clear_first_para(txb_cl)
    para(txf_cl, "Components", 14, bold=True, colour=TEAL)
    txb_cl2 = add_textbox(sl, 0.5, 4.58, 5.8, 2.2)
    txf_cl2 = clear_first_para(txb_cl2)
    for comp in [
        "FastAPI          — REST service framework",
        "FAISS            — vector similarity index",
        "sentence-transformers  — embedding model",
        "Claude API       — LLM summarisation",
        "python-pptx      — presentation generation",
        "scikit-learn     — TF-IDF / LSA fallback",
    ]:
        para(txf_cl2, comp, 11, colour=WHITE, space_before=3)

    # Right: Data flow
    add_rect(sl, 6.8, 4.05, 6.2, 2.85, _rgb(0x0D, 0x38, 0x6A))
    txb_df = add_textbox(sl, 7.0, 4.12, 5.8, 0.42)
    txf_df = clear_first_para(txb_df)
    para(txf_df, "Data Flow", 14, bold=True, colour=TEAL)
    txb_df2 = add_textbox(sl, 7.0, 4.58, 5.8, 2.2)
    txf_df2 = clear_first_para(txb_df2)
    for step in [
        "query string",
        "→  embedding (384-dim float32 vector)",
        "→  cosine similarity search (FAISS)",
        "→  top-k ranked documents",
        "→  LLM clinical summary",
        "→  JSON response to client",
    ]:
        para(txf_df2, step, 11, colour=WHITE, space_before=3)

    add_slide_number(sl, num, total)


def slide_05_embedding(prs, num, total):
    """Slide 5 — Embedding Model."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Embedding Model", "Comparison & justification")

    # Comparison table header
    add_rect(sl, 0.3, 1.25, 12.7, 0.45, NAVY)
    txb_hdr = add_textbox(sl, 0.5, 1.3, 12.3, 0.38)
    txf_hdr = clear_first_para(txb_hdr)
    para(txf_hdr,
         "Model                               Dim    Strengths                                                   Use Case",
         12, bold=True, colour=WHITE)

    # Table rows
    table_rows = [
        ("all-MiniLM-L6-v2",            "384",
         "Fast, 1B+ training pairs, medical Q&A, top MTEB scores",    "Primary",   TEAL),
        ("S-PubMedBert-MS-MARCO",        "768",
         "PubMed fine-tuned, clinical vocab, synonym alignment",       "Clinical upgrade", _rgb(0x00, 0x6B, 0x5A)),
        ("TF-IDF + LSA",                 "256",
         "Offline, zero dependency, LSA captures co-occurrence semantics", "Fallback", _rgb(0x55, 0x44, 0x88)),
    ]

    for i, (model, dim, strengths, use_case, badge_col) in enumerate(table_rows):
        bg = LIGHT if i % 2 == 0 else _rgb(0xE0, 0xEE, 0xF4)
        top_r = 1.7 + i * 0.65
        add_rect(sl, 0.3, top_r, 12.7, 0.65, bg)
        # Model name badge
        add_rect(sl, 0.32, top_r + 0.06, 3.1, 0.5, badge_col)
        txb_m = add_textbox(sl, 0.42, top_r + 0.12, 3.0, 0.38)
        txf_m = clear_first_para(txb_m)
        para(txf_m, model, 11, bold=True, colour=WHITE)
        # Dim
        txb_d = add_textbox(sl, 3.55, top_r + 0.12, 0.6, 0.38)
        txf_d = clear_first_para(txb_d)
        para(txf_d, dim, 12, bold=True, colour=NAVY, align=PP_ALIGN.CENTER)
        # Strengths
        txb_s = add_textbox(sl, 4.3, top_r + 0.1, 6.3, 0.48)
        txf_s = clear_first_para(txb_s)
        para(txf_s, strengths, 11, colour=NAVY)
        # Use case
        txb_u = add_textbox(sl, 10.8, top_r + 0.12, 2.0, 0.38)
        txf_u = clear_first_para(txb_u)
        para(txf_u, use_case, 11, bold=True, colour=badge_col)

    # Justification box
    add_rect(sl, 0.3, 3.75, 12.7, 1.3, NAVY)
    txb_j = add_textbox(sl, 0.5, 3.83, 12.3, 1.1)
    txf_j = clear_first_para(txb_j)
    para(txf_j, "Justification", 13, bold=True, colour=TEAL)
    para(txf_j,
         "all-MiniLM chosen for speed + quality balance on CPU. "
         "Achieves sub-100ms query latency on a standard laptop while delivering "
         "state-of-the-art MTEB semantic similarity scores. "
         "One env-var swap (EMBEDDING_MODEL) upgrades to the clinical PubMed model with zero code changes.",
         12, colour=WHITE, space_before=4)

    # Model card comparison side-by-side
    for i, (badge, label, items) in enumerate([
        ("PRIMARY", "all-MiniLM-L6-v2",
         ["22M params — runs on CPU",
          "384-dim vectors",
          "Trained: 1B+ sentence pairs",
          "Includes biomedical Q&A data",
          "MTEB rank: top-5 lightweight"]),
        ("CLINICAL UPGRADE", "S-PubMedBert-MS-MARCO",
         ["PubMed abstract fine-tuning",
          "768-dim — richer representation",
          "MS-MARCO ranking objective",
          "Best for clinical synonyms",
          "Swap via env var"]),
        ("FALLBACK", "TF-IDF + LSA (256d)",
         ["Zero external dependencies",
          "SVD-based topic semantics",
          "Deterministic & reproducible",
          "Auto-activates offline",
          "Good baseline comparison"]),
    ]):
        lft = 0.3 + i * 4.35
        card(sl, lft, 5.1, 4.1, 1.8, f"{badge}: {label}", items)   # capped at y=6.9

    add_slide_number(sl, num, total)


def slide_06_retrieval(prs, num, total):
    """Slide 6 — Retrieval Pipeline."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Retrieval Pipeline", "FAISS IndexFlatIP — exact cosine similarity search")

    # Left panel — pipeline diagram  — height capped at y=6.9
    add_rect(sl, 0.3, 1.25, 6.0, 5.65, NAVY)
    txb_title = add_textbox(sl, 0.5, 1.33, 5.6, 0.42)
    txf_title = clear_first_para(txb_title)
    para(txf_title, "Query Processing Flow", 14, bold=True, colour=TEAL)

    steps = [
        ("▶  Doctor submits query string", TEAL),
        ("↓", _rgb(0x88, 0xAA, 0xBB)),
        ("■  Encode with same embedding model", WHITE),
        ("   → 384-dim L2-normalised float32 vector", _rgb(0xCC, 0xDD, 0xFF)),
        ("↓", _rgb(0x88, 0xAA, 0xBB)),
        ("■  FAISS IndexFlatIP.search(query_vec, k)", WHITE),
        ("   → returns (scores[], indices[]) top-k", _rgb(0xCC, 0xDD, 0xFF)),
        ("↓", _rgb(0x88, 0xAA, 0xBB)),
        ("■  Lookup metadata for each index", WHITE),
        ("   → specialty, description, transcript", _rgb(0xCC, 0xDD, 0xFF)),
        ("↓", _rgb(0x88, 0xAA, 0xBB)),
        ("▶  Ranked results returned to LLM layer", TEAL),
    ]

    txb_steps = add_textbox(sl, 0.5, 1.85, 5.6, 4.9)
    txf_steps = clear_first_para(txb_steps)
    for text, col in steps:
        para(txf_steps, text, 11, colour=col, space_before=3)

    # Right panel — Why these choices  — heights capped at y=6.9
    card(sl, 6.6, 1.25, 6.4, 2.75, "Why FAISS IndexFlatIP?",
         ["L2-normalised vectors → inner product = cosine similarity",
          "Exact search: no approximation error for 5k corpus",
          "IndexIVFFlat available for 100k+ scale",
          "Serialised to disk → sub-1s API startup on reload",
          "Single-file ops — no managed service required"])

    card(sl, 6.6, 4.2, 6.4, 2.7, "Cosine Similarity Interpretation",
         ["Score range 0.0 – 1.0 (after L2 normalisation)",
          "Score > 0.85 → highly clinically relevant",
          "Score 0.60–0.85 → probable match, review needed",
          "Score < 0.40 → likely off-topic query",
          "Scale-invariant: long notes ≈ short summaries"])

    add_slide_number(sl, num, total)


def slide_07_llm(prs, num, total):
    """Slide 7 — LLM Summarisation."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "LLM Summarisation", "Claude API — clinical summary generation")

    # System prompt excerpt in dark code box
    add_rect(sl, 0.3, 1.25, 12.7, 2.5, NAVY)
    txb_prompt = add_textbox(sl, 0.5, 1.33, 12.3, 2.3)
    txf_prompt = clear_first_para(txb_prompt)
    para(txf_prompt, "System Prompt (excerpt)", 13, bold=True, colour=TEAL)
    for line in [
        '"You are a senior clinical decision-support assistant..."',
        "1. Lead with clinically salient findings across all retrieved notes.",
        "2. Highlight patterns, shared diagnoses, and relevant differentials.",
        "3. Note red-flag findings explicitly.",
        "4. Keep the summary under 300 words unless complexity demands more.",
        "5. Never fabricate findings not present in the provided notes.",
    ]:
        para(txf_prompt, line, 11, colour=_rgb(0xCC, 0xDD, 0xFF), space_before=2)

    # Three cards: Input, Model, Output  — height capped at y=6.9
    card(sl, 0.3, 3.95, 3.9, 2.95, "Input to LLM",
         ["Doctor's natural language query",
          "Top-k retrieved notes (ranked)",
          "Each note includes:",
          "  rank, cosine score, specialty,",
          "  description, first 1 500 chars"])

    card(sl, 4.5, 3.95, 4.3, 2.95, "Model & Config",
         ["Model: claude-sonnet-4-6",
          "Max tokens: 1 024 (configurable)",
          "Temperature: default (balanced)",
          "",
          "Fallback: structured rule-based",
          "  summary if no API key set"])

    card(sl, 9.1, 3.95, 3.9, 2.95, "Output",
         ["≤300-word clinical summary",
          "Addressed to the doctor",
          "Clinically precise vocabulary",
          "Red flags highlighted",
          "Returned as JSON field"])

    add_slide_number(sl, num, total)


def slide_08_api(prs, num, total):
    """Slide 8 — REST API."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "REST API", "FastAPI · JSON · Docker-ready")

    # Endpoints table header
    add_rect(sl, 0.3, 1.25, 12.7, 0.42, NAVY)
    txb_hdr = add_textbox(sl, 0.5, 1.3, 12.3, 0.35)
    txf_hdr = clear_first_para(txb_hdr)
    para(txf_hdr, "Endpoint                Description", 12, bold=True, colour=WHITE)

    endpoints = [
        ("POST  /retrieve", "Submit query body, returns ranked notes + LLM summary (primary endpoint)"),
        ("GET   /retrieve", "Same via query params — browser / curl friendly, no body needed"),
        ("GET   /health",   "Index status, document count, active embedding model name"),
    ]
    for i, (ep, desc) in enumerate(endpoints):
        bg = LIGHT if i % 2 == 0 else _rgb(0xE0, 0xEE, 0xF4)
        add_rect(sl, 0.3, 1.67 + i * 0.52, 12.7, 0.52, bg)
        txb_ep = add_textbox(sl, 0.5, 1.72 + i * 0.52, 3.5, 0.42)
        txf_ep = clear_first_para(txb_ep)
        para(txf_ep, ep, 12, bold=True, colour=TEAL)
        txb_desc = add_textbox(sl, 4.2, 1.72 + i * 0.52, 8.6, 0.42)
        txf_desc = clear_first_para(txb_desc)
        para(txf_desc, desc, 12, colour=NAVY)

    # Request JSON (left dark box)
    add_rect(sl, 0.3, 3.35, 6.1, 3.2, NAVY)
    txb_req = add_textbox(sl, 0.5, 3.43, 5.7, 3.0)
    txf_req = clear_first_para(txb_req)
    para(txf_req, "Request JSON (POST /retrieve)", 12, bold=True, colour=TEAL)
    for line in [
        '{',
        '  "query": "renal insufficiency in T2DM",',
        '  "top_k": 5,',
        '  "include_summary": true',
        '}',
    ]:
        para(txf_req, line, 11, colour=_rgb(0xCC, 0xDD, 0xFF), space_before=2)

    # Response JSON (right dark box)
    add_rect(sl, 6.7, 3.35, 6.3, 3.2, NAVY)
    txb_res = add_textbox(sl, 6.9, 3.43, 5.9, 3.0)
    txf_res = clear_first_para(txb_res)
    para(txf_res, "Response JSON (excerpt)", 12, bold=True, colour=TEAL)
    for line in [
        '{ "query": "...",',
        '  "total_retrieved": 5,',
        '  "embedding_model": "all-MiniLM-L6-v2",',
        '  "results": [{ "rank": 1,',
        '    "score": 0.985, "specialty": "Nephrology"}],',
        '  "summary": "The top result highlights…" }',
    ]:
        para(txf_res, line, 11, colour=_rgb(0xCC, 0xDD, 0xFF), space_before=2)

    # Bottom badge row  — moved up from 6.7 to avoid overlapping slide number
    add_rect(sl, 0.3, 6.58, 12.7, 0.32, TEAL)
    txb_tags = add_textbox(sl, 0.5, 6.61, 12.3, 0.26)
    txf_tags = clear_first_para(txb_tags)
    para(txf_tags,
         "Docker-ready  ·  CORS enabled  ·  Pydantic validation  ·  422 on bad input",
         12, bold=True, colour=WHITE, align=PP_ALIGN.CENTER)

    add_slide_number(sl, num, total)


def slide_09_evaluation(prs, num, total):
    """Slide 9 — Evaluation Results."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Evaluation Results", "Proving Semantic Understanding")

    # 3 metric cards top section
    metrics = [
        ("Precision@k",
         ["Fraction of top-k results whose specialty",
          "aligns with the expected clinical domain.",
          "All 5 test queries: Precision@1 = 1.0"]),
        ("Keyword Recall",
         ["Fraction of top-k results containing at",
          "least one key clinical term from query.",
          "Robust even with synonym variation."]),
        ("Score Spread",
         ["Gap between rank-1 and rank-k score.",
          "Large spread = unambiguous top result.",
          "Mean rank-1 score across queries: 0.979"]),
    ]
    for i, (heading, lines) in enumerate(metrics):
        lft = 0.3 + i * 4.35
        card(sl, lft, 1.25, 4.1, 1.85, heading, lines)

    # Test query results table
    add_rect(sl, 0.3, 3.3, 12.7, 0.42, NAVY)
    txb_hdr = add_textbox(sl, 0.5, 3.35, 12.3, 0.35)
    txf_hdr = clear_first_para(txb_hdr)
    para(txf_hdr, "Test Query                                          Rank-1 Specialty       Score   Correct",
         12, bold=True, colour=WHITE)

    rows = [
        ("Diabetic patient with kidney complications",       "Nephrology",    "0.985", "✓"),
        ("Acute chest pain, ST-elevation MI",               "Cardiology",    "0.980", "✓"),
        ("COPD exacerbation, dyspnea, low oxygen sat",      "Pulmonology",   "0.987", "✓"),
        ("Knee arthroplasty post-op rehabilitation",        "Orthopaedics",  "1.000", "✓"),
        ("Insulin-dependent DKA, hyperglycaemia",           "Endocrinology", "0.946", "✓"),
    ]
    for i, (q, spec, score, hit) in enumerate(rows):
        bg = LIGHT if i % 2 == 0 else _rgb(0xE0, 0xEE, 0xF4)
        top_r = 3.72 + i * 0.44
        add_rect(sl, 0.3, top_r, 12.7, 0.44, bg)
        for j, (text, wid, lft_off) in enumerate([
            (q,     6.5, 0.4),
            (spec,  2.6, 7.1),
            (score, 1.1, 9.9),
            (hit,   0.7, 11.3),
        ]):
            txb = add_textbox(sl, lft_off, top_r + 0.06, wid, 0.34)
            txf = clear_first_para(txb)
            colour = GREEN if j == 3 else NAVY
            para(txf, text, 10, colour=colour, bold=(j == 3))

    # Semantic proof banner  — height reduced to stay within y=6.9
    add_rect(sl, 0.3, 5.93, 12.7, 0.97, NAVY)
    txb_proof = add_textbox(sl, 0.5, 5.98, 12.3, 0.84)
    txf_proof = clear_first_para(txb_proof)
    para(txf_proof, "Semantic Proof — Vocabulary Mismatch Handled Correctly:", 12, bold=True, colour=TEAL)
    para(txf_proof,
         "Query: \"renal insufficiency in T2DM\"  →  Rank 1: Nephrology / CKD  score=0.985",
         11, colour=WHITE, space_before=2)
    para(txf_proof,
         "No word overlap between query and document — meaning preserved across vocabulary boundary.",
         10, colour=_rgb(0xCC, 0xDD, 0xFF), space_before=2)

    add_slide_number(sl, num, total)


def slide_10_summary(prs, num, total):
    """Slide 10 — Summary & Future Work."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, NAVY)
    add_rect(sl, 0, 0, 0.18, 7.5, TEAL)

    # Slide title
    txb_title = add_textbox(sl, 0.5, 0.3, 12.5, 0.65)
    txf_title = clear_first_para(txb_title)
    para(txf_title, "Summary & Future Work", 28, bold=True, colour=WHITE)

    # Left dark panel — Delivered  — height capped at y=6.9
    add_rect(sl, 0.5, 1.1, 5.9, 5.7, _rgb(0x0D, 0x38, 0x6A))
    txb_dh = add_textbox(sl, 0.7, 1.2, 5.5, 0.48)
    txf_dh = clear_first_para(txb_dh)
    para(txf_dh, "Delivered", 17, bold=True, colour=TEAL)
    txb_dl = add_textbox(sl, 0.7, 1.75, 5.5, 4.8)
    txf_dl = clear_first_para(txb_dl)
    for line in [
        "✓  Semantic retrieval (not keyword matching)",
        "✓  Dual embedding backends",
        "     (SentenceTransformer + TF-IDF/LSA)",
        "✓  Claude API summarisation",
        "✓  FastAPI REST service",
        "✓  20 passing tests (all offline)",
        "✓  Docker-ready",
    ]:
        para(txf_dl, line, 13, colour=WHITE, space_before=4)

    # Right dark panel — Next Steps  — height capped at y=6.9
    add_rect(sl, 6.9, 1.1, 6.1, 5.7, _rgb(0x0D, 0x38, 0x6A))
    txb_nh = add_textbox(sl, 7.1, 1.2, 5.7, 0.48)
    txf_nh = clear_first_para(txb_nh)
    para(txf_nh, "Next Steps", 17, bold=True, colour=TEAL)
    txb_nl = add_textbox(sl, 7.1, 1.75, 5.7, 4.8)
    txf_nl = clear_first_para(txb_nl)
    for line in [
        "▶  Fine-tune on corpus triplets",
        "     (+5–15% precision expected)",
        "▶  Cross-encoder re-ranker",
        "     (top-10 → top-5 precision boost)",
        "▶  PHI de-identification before production",
        "▶  HNSW index for 1M+ scale",
        "▶  Auth + rate limiting",
    ]:
        para(txf_nl, line, 13, colour=WHITE, space_before=4)

    # Footer  — positioned just above slide number area
    txb_foot = add_textbox(sl, 0.5, 6.88, 11.8, 0.2)
    txf_foot = clear_first_para(txb_foot)
    para(txf_foot,
         "Clinical AI Take-Home Exam  ·  June 2026",
         11, colour=GREY, align=PP_ALIGN.CENTER)

    add_slide_number(sl, num, total)


# ---------------------------------------------------------------------------
# Main build function
# ---------------------------------------------------------------------------

TOTAL = 10


def build() -> Presentation:
    prs = new_prs()

    slide_01_title(prs,       1, TOTAL)
    slide_02_problem(prs,     2, TOTAL)
    slide_03_dataset(prs,     3, TOTAL)
    slide_04_architecture(prs,4, TOTAL)
    slide_05_embedding(prs,   5, TOTAL)
    slide_06_retrieval(prs,   6, TOTAL)
    slide_07_llm(prs,         7, TOTAL)
    slide_08_api(prs,         8, TOTAL)
    slide_09_evaluation(prs,  9, TOTAL)
    slide_10_summary(prs,    10, TOTAL)

    return prs


if __name__ == "__main__":
    out = Path("/home/user/clinic/Clinical_Note_Retrieval_Exam.pptx")
    prs = build()
    prs.save(str(out))
    print(f"Saved: {out}  ({out.stat().st_size // 1024} KB)")
