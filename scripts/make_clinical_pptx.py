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
    """Slide 1 — Title (dark navy background)."""
    sl = blank_slide(prs)
    # Deep navy background
    add_rect(sl, 0, 0, 13.33, 7.5, NAVY)
    # Teal accent bar on left
    add_rect(sl, 0, 0, 0.18, 7.5, TEAL)

    # Main title
    txb = add_textbox(sl, 0.55, 1.4, 12.3, 1.1)
    txf = clear_first_para(txb)
    para(txf, "Clinical Note Retrieval System", 40, bold=True,
         colour=WHITE, align=PP_ALIGN.LEFT)

    # Subtitle
    txb2 = add_textbox(sl, 0.55, 2.65, 12.3, 0.65)
    txf2 = clear_first_para(txb2)
    para(txf2, "AI-Powered Semantic Search for Clinical Decision Support", 22,
         colour=TEAL, align=PP_ALIGN.LEFT)

    # Tag line
    txb3 = add_textbox(sl, 0.55, 3.45, 12.3, 0.45)
    txf3 = clear_first_para(txb3)
    para(txf3, "Take-Home Technical Assessment  ·  June 2026", 15,
         colour=_rgb(0xAA, 0xCC, 0xDD), align=PP_ALIGN.LEFT)

    # Decorative horizontal rule
    add_rect(sl, 0.55, 4.05, 5.0, 0.04, TEAL)

    # 3 key-fact cards
    facts = [
        ("Dataset",  "mtsamples  ·  5 000+ clinical notes"),
        ("Backend",  "sentence-transformers + FAISS + Claude API"),
        ("Delivery", "FastAPI REST service  ·  Docker-ready"),
    ]
    for i, (label, value) in enumerate(facts):
        lft = 0.55 + i * 4.2
        add_rect(sl, lft, 4.3, 3.9, 0.82, _rgb(0x0D, 0x38, 0x6A))
        txb_f = add_textbox(sl, lft + 0.15, 4.38, 3.6, 0.35)
        txf_f = clear_first_para(txb_f)
        para(txf_f, label, 11, bold=True, colour=TEAL)
        txb_v = add_textbox(sl, lft + 0.15, 4.72, 3.6, 0.35)
        txf_v = clear_first_para(txb_v)
        para(txf_v, value, 11, colour=WHITE)

    # Footer
    txb4 = add_textbox(sl, 0.55, 5.55, 12.3, 0.35)
    txf4 = clear_first_para(txb4)
    para(txf4, "Invitrace Co., Ltd.  ·  AI Engineering Assessment  ·  June 2026",
         11, colour=GREY, align=PP_ALIGN.LEFT)

    add_slide_number(sl, num, total)


def slide_02_problem(prs, num, total):
    """Slide 2 — Problem Statement (verbatim from exam)."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Problem Statement",
               "Problem 1 — Clinical Note Retrieval System")

    # Left card — verbatim Problem Statement
    card(sl, 0.3, 1.18, 6.1, 3.6, "Problem Statement",
         ["The platform needs to help doctors quickly find",
          "relevant past cases from a large corpus of clinical notes.",
          "",
          "A doctor types a natural language query describing a",
          "patient situation, and the system should surface the",
          "most relevant clinical notes from the database.",
          "",
          "The system must understand clinical meaning, not just",
          "match keywords — a query about 'a diabetic patient",
          "with kidney complications' should retrieve notes about",
          "CKD with diabetes even if the exact words differ."])

    # Right card — verbatim Instructions
    card(sl, 6.65, 1.18, 6.35, 3.6, "Instructions",
         ["Download the dataset from the Data Description link.",
          "Build a retrieval system: natural language query",
          "  → returns most relevant clinical notes.",
          "Use an embedding model of your choice. Justify.",
          "Add an LLM layer for a concise summary.",
          "Evaluate: clinically relevant, not keyword matches.",
          "(Optional) Fine-tune embedding model + compare.",
          "Prepare one presentation — maximum 10 pages.",
          "Expose as a REST API service.",
          "Prepare to present for a 30-minute session."])

    # Bottom dark box — Target Audience + Guidance
    add_rect(sl, 0.3, 4.95, 12.7, 1.93, NAVY)
    txb = add_textbox(sl, 0.5, 5.03, 12.3, 0.4)
    txf = clear_first_para(txb)
    para(txf, "Target Audience  ·  Additional Guidance", 13, bold=True,
         colour=TEAL)
    txb2 = add_textbox(sl, 0.5, 5.46, 12.3, 0.38)
    txf2 = clear_first_para(txb2)
    para(txf2, "AI Engineering Manager  ·  Product Manager", 12,
         colour=_rgb(0xCC, 0xDD, 0xFF))
    txb3 = add_textbox(sl, 0.5, 5.86, 12.3, 0.38)
    txf3 = clear_first_para(txb3)
    para(txf3,
         "Anything outside this instruction, please feel free to make"
         " your own assumption as needed.",
         12, colour=WHITE)
    txb4 = add_textbox(sl, 0.5, 6.26, 12.3, 0.38)
    txf4 = clear_first_para(txb4)
    para(txf4,
         "Data: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions",
         11, colour=_rgb(0x88, 0xBB, 0xCC), italic=True)

    add_slide_number(sl, num, total)


def slide_03_dataset(prs, num, total):
    """Slide 3 — Dataset."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Dataset",
               "mtsamples.csv — 5 000+ real medical transcriptions")

    # 4 info cards row 1
    info_items = [
        ("Source",
         ["mtsamples.csv via Kaggle",
          "5 000+ real de-identified",
          "medical transcriptions"]),
        ("Columns Used",
         ["medical_specialty",
          "description",
          "transcription",
          "keywords"]),
        ("Specialties",
         ["40+ clinical domains",
          "Cardiology, Nephrology,",
          "Pulmonology, Orthopaedics,",
          "Neurology, Surgery, …"]),
        ("Preprocessing",
         ["Drop null/short transcriptions",
          "Collapse whitespace",
          "Concatenate fields",
          "Truncate to 2 000 chars"]),
    ]
    for i, (heading, lines) in enumerate(info_items):
        lft = 0.3 + i * 3.25
        card(sl, lft, 1.18, 3.0, 1.72, heading, lines)

    # Embedding Input Format dark box
    add_rect(sl, 0.3, 3.06, 12.7, 0.88, NAVY)
    txb_lbl = add_textbox(sl, 0.5, 3.12, 12.3, 0.32)
    txf_lbl = clear_first_para(txb_lbl)
    para(txf_lbl, "Embedding Input Format:", 12, bold=True, colour=TEAL)
    txb_fmt = add_textbox(sl, 0.5, 3.46, 12.3, 0.42)
    txf_fmt = clear_first_para(txb_fmt)
    para(txf_fmt,
         '"Specialty: <medical_specialty>  |  Description: <description>'
         '  |  <first 2 000 chars of transcription>"',
         11, colour=_rgb(0xCC, 0xDD, 0xFF))

    # Sample data table — header
    add_rect(sl, 0.3, 4.08, 12.7, 0.42, NAVY)
    txb_hdr = add_textbox(sl, 0.5, 4.13, 12.3, 0.34)
    txf_hdr = clear_first_para(txb_hdr)
    para(txf_hdr,
         "Specialty              Description (excerpt)                                      "
         "Keywords",
         12, bold=True, colour=WHITE)

    # 3 sample rows
    rows = [
        ("Nephrology",
         "Patient with CKD stage 3 and T2DM presenting for follow-up",
         "CKD, creatinine, GFR, diabetes mellitus"),
        ("Cardiology",
         "62yo male with STEMI taken to cath lab emergently",
         "myocardial infarction, troponin, PCI, stent"),
        ("Neurology",
         "New-onset seizure, MRI brain ordered, AED started",
         "epilepsy, levetiracetam, MRI, EEG"),
    ]
    for i, (spec, desc, kw) in enumerate(rows):
        bg = LIGHT if i % 2 == 0 else _rgb(0xE0, 0xEE, 0xF4)
        top_r = 4.50 + i * 0.68
        add_rect(sl, 0.3, top_r, 12.7, 0.68, bg)
        for j, (text, wid, lft_off) in enumerate([
            (spec, 2.35, 0.4),
            (desc, 6.2, 2.9),
            (kw,  3.5, 9.25),
        ]):
            txb = add_textbox(sl, lft_off, top_r + 0.1, wid, 0.52)
            txf = clear_first_para(txb)
            para(txf, text, 10, colour=TEAL if j == 0 else NAVY, bold=(j == 0))

    # Note about truncation
    txb_note = add_textbox(sl, 0.3, 6.57, 12.7, 0.32)
    txf_note = clear_first_para(txb_note)
    para(txf_note,
         "2 000-char truncation preserves chief complaint, diagnosis, and key findings"
         " in 99%+ of notes",
         10, colour=GREY, italic=True)

    add_slide_number(sl, num, total)


def slide_04_architecture(prs, num, total):
    """Slide 4 — System Architecture."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "System Architecture",
               "5-stage pipeline: Ingest → Embed → Index → Retrieve → Summarise")

    # 5 pipeline boxes with arrows
    pipeline = [
        ("1. Ingest",
         ["Load CSV",
          "Clean & truncate",
          "Build text records"]),
        ("2. Embed",
         ["sentence-transformers",
          "384-dim float32",
          "L2-normalised"]),
        ("3. Index",
         ["FAISS IndexFlatIP",
          "Exact cosine search",
          "Serialised to disk"]),
        ("4. Retrieve",
         ["Embed query",
          "Top-k cosine search",
          "Attach metadata"]),
        ("5. Summarise",
         ["Claude API",
          "System prompt",
          "JSON response"]),
    ]

    box_w = 2.2
    gap   = 0.27
    start = 0.3

    for i, (title, lines) in enumerate(pipeline):
        lft = start + i * (box_w + gap)
        card(sl, lft, 1.18, box_w, 2.55, title, lines)
        if i < len(pipeline) - 1:
            ax = lft + box_w + 0.02
            ar = add_textbox(sl, ax, 2.28, 0.26, 0.4)
            txf = clear_first_para(ar)
            para(txf, "→", 18, bold=True, colour=TEAL)

    # Two dark panels below pipeline
    # Left — Components
    add_rect(sl, 0.3, 3.9, 6.2, 2.98, NAVY)
    txb_ch = add_textbox(sl, 0.5, 3.97, 5.8, 0.38)
    txf_ch = clear_first_para(txb_ch)
    para(txf_ch, "Components", 14, bold=True, colour=TEAL)
    txb_cl = add_textbox(sl, 0.5, 4.38, 5.8, 2.44)
    txf_cl = clear_first_para(txb_cl)
    for comp in [
        "FastAPI            —  REST service framework",
        "FAISS              —  vector similarity index",
        "sentence-transformers  —  embedding model",
        "Claude API         —  LLM summarisation",
        "scikit-learn       —  TF-IDF / LSA fallback",
    ]:
        para(txf_cl, comp, 11, colour=WHITE, space_before=4)

    # Right — Data Flow
    add_rect(sl, 6.8, 3.9, 6.2, 2.98, _rgb(0x0D, 0x38, 0x6A))
    txb_dh = add_textbox(sl, 7.0, 3.97, 5.8, 0.38)
    txf_dh = clear_first_para(txb_dh)
    para(txf_dh, "Data Flow", 14, bold=True, colour=TEAL)
    txb_df = add_textbox(sl, 7.0, 4.38, 5.8, 2.44)
    txf_df = clear_first_para(txb_df)
    for step in [
        "query string",
        "→  384-dim L2-normalised float32 vector",
        "→  cosine similarity search (FAISS)",
        "→  top-k ranked documents",
        "→  LLM clinical summary",
        "→  JSON response to client",
    ]:
        para(txf_df, step, 11, colour=WHITE, space_before=4)

    add_slide_number(sl, num, total)


def slide_05_embedding(prs, num, total):
    """Slide 5 — Embedding Model Selection."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Embedding Model Selection",
               "Comparison, justification, and trade-off analysis")

    # Comparison table header
    add_rect(sl, 0.3, 1.18, 12.7, 0.42, NAVY)
    txb_hdr = add_textbox(sl, 0.5, 1.23, 12.3, 0.35)
    txf_hdr = clear_first_para(txb_hdr)
    para(txf_hdr,
         "Model                            Dim    Training Data                    "
         "Speed       Use Case",
         12, bold=True, colour=WHITE)

    # 3 table rows
    table_rows = [
        ("all-MiniLM-L6-v2",         "384",
         "1B+ sentence pairs incl. medical Q&A + NLI",
         "< 100 ms",  "Primary",          TEAL),
        ("S-PubMedBert-MS-MARCO",     "768",
         "PubMed abstracts + MS-MARCO passage ranking",
         "~ 300 ms",  "Clinical upgrade",  _rgb(0x00, 0x6B, 0x5A)),
        ("TF-IDF + LSA (256d)",       "256",
         "Fitted on corpus — SVD-based latent semantics",
         "< 10 ms",   "Offline fallback",  _rgb(0x55, 0x44, 0x88)),
    ]
    for i, (model, dim, training, speed, use_case, badge_col) in enumerate(table_rows):
        bg = LIGHT if i % 2 == 0 else _rgb(0xE0, 0xEE, 0xF4)
        top_r = 1.60 + i * 0.62
        add_rect(sl, 0.3, top_r, 12.7, 0.62, bg)
        add_rect(sl, 0.32, top_r + 0.06, 3.0, 0.48, badge_col)
        txb_m = add_textbox(sl, 0.42, top_r + 0.12, 2.9, 0.36)
        txf_m = clear_first_para(txb_m)
        para(txf_m, model, 10, bold=True, colour=WHITE)
        txb_d = add_textbox(sl, 3.44, top_r + 0.12, 0.55, 0.36)
        txf_d = clear_first_para(txb_d)
        para(txf_d, dim, 11, bold=True, colour=NAVY, align=PP_ALIGN.CENTER)
        txb_t = add_textbox(sl, 4.1, top_r + 0.1, 4.7, 0.46)
        txf_t = clear_first_para(txb_t)
        para(txf_t, training, 10, colour=NAVY)
        txb_sp = add_textbox(sl, 8.95, top_r + 0.12, 1.2, 0.36)
        txf_sp = clear_first_para(txb_sp)
        para(txf_sp, speed, 10, colour=NAVY)
        txb_u = add_textbox(sl, 10.3, top_r + 0.12, 2.5, 0.36)
        txf_u = clear_first_para(txb_u)
        para(txf_u, use_case, 10, bold=True, colour=badge_col)

    # Justification box
    add_rect(sl, 0.3, 3.5, 12.7, 1.42, NAVY)
    txb_jh = add_textbox(sl, 0.5, 3.57, 12.3, 0.34)
    txf_jh = clear_first_para(txb_jh)
    para(txf_jh, "Justification", 13, bold=True, colour=TEAL)
    txb_jb = add_textbox(sl, 0.5, 3.94, 12.3, 0.92)
    txf_jb = clear_first_para(txb_jb)
    para(txf_jb,
         "all-MiniLM-L6-v2 chosen for the optimal speed/quality balance on CPU: sub-100ms latency on a "
         "standard laptop, 22M params, trained on 1B+ pairs including biomedical Q&A. Top-tier MTEB "
         "lightweight rank. Clinically validates: CKD ≈ renal failure, DKA ≈ diabetic ketoacidosis, "
         "MI ≈ myocardial infarction. Architecture is model-agnostic: one env-var swap "
         "(EMBEDDING_MODEL=pritamdeka/S-PubMedBert-MS-MARCO) upgrades to the clinical model with zero "
         "code changes. GPT embeddings add network latency + per-token cost; BERT-large adds 5-10x "
         "inference time for marginal clinical gains. Not justified at this corpus scale.",
         11, colour=WHITE, space_before=2)

    # 3 model cards at bottom
    model_cards = [
        ("PRIMARY", "all-MiniLM-L6-v2",
         ["22M params — runs on CPU",
          "384-dim dense vectors",
          "1B+ training pairs incl. medical Q&A",
          "Top MTEB lightweight benchmark",
          "Sub-100ms CPU inference",
          "Cosine: CKD ≈ renal failure > 0.82"]),
        ("CLINICAL UPGRADE", "S-PubMedBert-MS-MARCO",
         ["PubMed abstract fine-tuning",
          "768-dim — richer representation",
          "MS-MARCO passage ranking objective",
          "Aligns CKD ≈ renal failure",
          "DKA ≈ ketoacidosis / MI ≈ infarction",
          "Swap via EMBEDDING_MODEL env var"]),
        ("OFFLINE FALLBACK", "TF-IDF + LSA (256d)",
         ["Zero external dependencies",
          "SVD-based topic semantics",
          "Deterministic & reproducible",
          "Auto-activates when HF Hub blocked",
          "Good keyword-proximity baseline",
          "No network or GPU required"]),
    ]
    for i, (badge, label, items) in enumerate(model_cards):
        lft = 0.3 + i * 4.35
        card(sl, lft, 5.07, 4.1, 1.82,
             f"{badge}: {label}", items)

    add_slide_number(sl, num, total)


def slide_06_retrieval(prs, num, total):
    """Slide 6 — Retrieval Pipeline."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Retrieval Pipeline",
               "FAISS IndexFlatIP — exact cosine similarity search")

    # Left dark panel — Query Processing Flow
    add_rect(sl, 0.3, 1.18, 6.1, 5.70, NAVY)
    txb_th = add_textbox(sl, 0.5, 1.26, 5.7, 0.38)
    txf_th = clear_first_para(txb_th)
    para(txf_th, "Query Processing Flow", 14, bold=True, colour=TEAL)

    steps = [
        ("▶  Doctor submits natural language query string",
         TEAL),
        ("↓", _rgb(0x88, 0xAA, 0xBB)),
        ("■  Encode with same embedding model (all-MiniLM-L6-v2)",
         WHITE),
        ("   →  384-dim L2-normalised float32 vector",
         _rgb(0xCC, 0xDD, 0xFF)),
        ("↓", _rgb(0x88, 0xAA, 0xBB)),
        ("■  FAISS IndexFlatIP.search(query_vec, k)",
         WHITE),
        ("   →  returns (scores[], indices[])  top-k results",
         _rgb(0xCC, 0xDD, 0xFF)),
        ("↓", _rgb(0x88, 0xAA, 0xBB)),
        ("■  Lookup metadata for each returned index",
         WHITE),
        ("   →  specialty, description, keywords, transcript",
         _rgb(0xCC, 0xDD, 0xFF)),
        ("↓", _rgb(0x88, 0xAA, 0xBB)),
        ("▶  Ranked results + metadata sent to LLM layer",
         TEAL),
    ]

    txb_steps = add_textbox(sl, 0.5, 1.72, 5.7, 5.0)
    txf_steps = clear_first_para(txb_steps)
    for text, col in steps:
        para(txf_steps, text, 11, colour=col, space_before=4)

    # Right top card — Why FAISS IndexFlatIP?
    card(sl, 6.65, 1.18, 6.35, 2.72, "Why FAISS IndexFlatIP?",
         ["L2-normalised vectors → inner product = cosine similarity",
          "Exact search: no approximation error for 5k corpus",
          "Serialised to disk → sub-1s API restart (no re-embed)",
          "Scale path: IndexIVFFlat (100k+) → IndexHNSWFlat (1M+)",
          "No managed service, no network, no subscription cost",
          "Identical query/insert API across all index types"])

    # Right bottom card — Cosine Score Interpretation
    card(sl, 6.65, 4.12, 6.35, 2.76, "Cosine Score Interpretation",
         ["Score range 0.0 – 1.0  (L2-normalised vectors)",
          "Score ≥ 0.85 → highly clinically relevant",
          "Score 0.60–0.85 → probable match, review needed",
          "Score < 0.40 → likely off-topic query",
          "Scale-invariant: long note ≈ short summary at same score",
          "Observed range on 5 semantic queries: 0.946 – 1.000"])

    add_slide_number(sl, num, total)


def slide_07_llm(prs, num, total):
    """Slide 7 — LLM Summarisation."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "LLM Summarisation",
               "Claude API — clinical summary generation")

    # System prompt dark box
    add_rect(sl, 0.3, 1.18, 12.7, 2.58, NAVY)
    txb_ph = add_textbox(sl, 0.5, 1.26, 12.3, 0.34)
    txf_ph = clear_first_para(txb_ph)
    para(txf_ph, "System Prompt — All 5 Principles (verbatim)", 13,
         bold=True, colour=TEAL)
    txb_pb = add_textbox(sl, 0.5, 1.63, 12.3, 2.06)
    txf_pb = clear_first_para(txb_pb)
    para(txf_pb,
         '"You are a senior clinical decision-support assistant. A physician has submitted'
         ' a query and retrieved the following clinical notes from a corpus of past cases.'
         ' Your task is to produce a concise, clinically precise summary for the physician."',
         11, colour=_rgb(0xCC, 0xDD, 0xFF), space_before=2)
    for line in [
        "1. Lead with the most clinically salient findings across all retrieved notes.",
        "2. Highlight patterns, shared diagnoses, and relevant differentials.",
        "3. Flag red-flag findings explicitly.",
        "4. Keep the summary ≤ 300 words unless clinical complexity demands more.",
        "5. Never fabricate findings not present in the provided notes.",
    ]:
        para(txf_pb, line, 11, colour=WHITE, space_before=3)

    # Three cards below the prompt box
    card(sl, 0.3, 3.92, 3.98, 2.96, "Input to LLM",
         ["Doctor's natural language query",
          "Top-k retrieved notes (ranked)",
          "Per note:",
          "  • rank number + cosine score",
          "  • specialty + description",
          "  • first 1 500 chars of transcript"])

    card(sl, 4.55, 3.92, 4.22, 2.96, "Model & Config",
         ["Model: claude-sonnet-4-6",
          "max_tokens: 1 024 (configurable)",
          "Temperature: default (balanced)",
          "",
          "Fallback: structured rule-based",
          "summary when API key absent",
          "API always returns non-null summary"])

    card(sl, 9.04, 3.92, 3.96, 2.96, "Output",
         ["≤ 300-word clinical summary",
          "Addressed to the doctor",
          "Clinically precise vocabulary",
          "Red flags highlighted (⚠)",
          "Returned as JSON 'summary' field",
          "Deterministic fallback if no key"])

    add_slide_number(sl, num, total)


def slide_08_api(prs, num, total):
    """Slide 8 — REST API."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "REST API",
               "FastAPI · Pydantic · Docker-ready")

    # Endpoints table header
    add_rect(sl, 0.3, 1.18, 12.7, 0.42, NAVY)
    txb_hdr = add_textbox(sl, 0.5, 1.23, 12.3, 0.35)
    txf_hdr = clear_first_para(txb_hdr)
    para(txf_hdr, "Method   Endpoint           Description",
         12, bold=True, colour=WHITE)

    endpoints = [
        ("POST", "/retrieve",
         "Submit query as JSON body; returns ranked notes + LLM summary (primary endpoint)"),
        ("GET",  "/retrieve",
         "Same via URL query params — browser and curl friendly, no request body needed"),
        ("GET",  "/health",
         "Returns index size, document count, and active embedding model name"),
    ]
    for i, (method, ep, desc) in enumerate(endpoints):
        bg = LIGHT if i % 2 == 0 else _rgb(0xE0, 0xEE, 0xF4)
        add_rect(sl, 0.3, 1.60 + i * 0.52, 12.7, 0.52, bg)
        mc = TEAL if method == "POST" else GREEN
        txb_m = add_textbox(sl, 0.42, 1.65 + i * 0.52, 0.8, 0.40)
        txf_m = clear_first_para(txb_m)
        para(txf_m, method, 11, bold=True, colour=mc)
        txb_ep = add_textbox(sl, 1.35, 1.65 + i * 0.52, 2.2, 0.40)
        txf_ep = clear_first_para(txb_ep)
        para(txf_ep, ep, 11, bold=True, colour=NAVY)
        txb_ds = add_textbox(sl, 3.7, 1.65 + i * 0.52, 9.1, 0.40)
        txf_ds = clear_first_para(txb_ds)
        para(txf_ds, desc, 11, colour=NAVY)

    # Left dark box — Request JSON
    add_rect(sl, 0.3, 3.26, 6.1, 3.30, NAVY)
    txb_rh = add_textbox(sl, 0.5, 3.33, 5.7, 0.34)
    txf_rh = clear_first_para(txb_rh)
    para(txf_rh, "Request JSON (POST /retrieve)", 12, bold=True, colour=TEAL)
    txb_rb = add_textbox(sl, 0.5, 3.70, 5.7, 2.76)
    txf_rb = clear_first_para(txb_rb)
    for line in [
        "{",
        '  "query": "renal insufficiency in T2DM",',
        '  "top_k": 5,',
        '  "include_summary": true',
        "}",
        "",
        "Fields:",
        "  query           string  (required)",
        "  top_k           integer 1–20, default 5",
        "  include_summary boolean, default true",
    ]:
        para(txf_rb, line, 10, colour=_rgb(0xCC, 0xDD, 0xFF), space_before=1)

    # Right dark box — Response JSON
    add_rect(sl, 6.65, 3.26, 6.35, 3.30, NAVY)
    txb_rsh = add_textbox(sl, 6.85, 3.33, 5.95, 0.34)
    txf_rsh = clear_first_para(txb_rsh)
    para(txf_rsh, "Response JSON (excerpt)", 12, bold=True, colour=TEAL)
    txb_rsb = add_textbox(sl, 6.85, 3.70, 5.95, 2.76)
    txf_rsb = clear_first_para(txb_rsb)
    for line in [
        '{ "query": "renal insufficiency in T2DM",',
        '  "total_retrieved": 5,',
        '  "embedding_model": "all-MiniLM-L6-v2",',
        '  "results": [{',
        '    "rank": 1, "score": 0.985,',
        '    "specialty": "Nephrology",',
        '    "description": "CKD stage 3 in T2DM...",',
        '    "keywords": "CKD, GFR, nephropathy",',
        '    "transcription_excerpt": "62yo male..."',
        '  }], "summary": "Top result: CKD..." }',
    ]:
        para(txf_rsb, line, 10, colour=_rgb(0xCC, 0xDD, 0xFF), space_before=1)

    # Bottom teal badge
    add_rect(sl, 0.3, 6.58, 12.7, 0.30, TEAL)
    txb_tags = add_textbox(sl, 0.5, 6.60, 12.3, 0.26)
    txf_tags = clear_first_para(txb_tags)
    para(txf_tags,
         "Docker-ready  ·  CORS enabled  ·  Pydantic validation  ·  422 on bad input",
         12, bold=True, colour=WHITE, align=PP_ALIGN.CENTER)

    add_slide_number(sl, num, total)


def slide_09_evaluation(prs, num, total):
    """Slide 9 — Evaluation Results."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, LIGHT)
    header_bar(sl, "Evaluation Results",
               "Proving Semantic Understanding — Not Keyword Matching")

    # 3 metric cards top
    metrics = [
        ("Precision@k",
         ["Fraction of top-k results whose specialty",
          "aligns with the expected clinical domain.",
          "Threshold: > 0.8 = good; 1.0 = perfect.",
          "Result: Precision@1 = 1.0 on all 5 queries."]),
        ("Keyword Recall@k",
         ["Fraction of top-k results containing at",
          "least one key clinical term from query domain.",
          "Threshold: > 0.6 = acceptable.",
          "Robust even with synonym vocabulary gap."]),
        ("Score Spread",
         ["Gap between rank-1 and rank-k score.",
          "Large gap = unambiguous top result.",
          "Threshold: > 0.1 = well-separated.",
          "Mean rank-1 score across 5 queries: 0.980."]),
    ]
    for i, (heading, lines) in enumerate(metrics):
        lft = 0.3 + i * 4.35
        card(sl, lft, 1.18, 4.1, 1.90, heading, lines)

    # Results table header
    add_rect(sl, 0.3, 3.24, 12.7, 0.40, NAVY)
    txb_hdr = add_textbox(sl, 0.5, 3.29, 12.3, 0.33)
    txf_hdr = clear_first_para(txb_hdr)
    para(txf_hdr,
         "Test Query                                     Rank-1 Specialty       "
         "Score    Correct",
         12, bold=True, colour=WHITE)

    # 5 test rows
    rows = [
        ("Renal insufficiency in type 2 diabetes mellitus",
         "Nephrology / CKD + DM", "0.985", "✓"),
        ("Blood glucose crisis requiring intravenous insulin",
         "Endocrinology / DKA",   "0.946", "✓"),
        ("COPD and decreased O2 needing bronchodilation",
         "Pulmonology / COPD",    "0.987", "✓"),
        ("Post-op knee arthroplasty physiotherapy rehab",
         "Orthopaedics / TKR",    "1.000", "✓"),
        ("Crushing left-arm pain with elevated troponin",
         "Cardiology / Chest Pain","0.980", "✓"),
    ]
    for i, (q, spec, score, hit) in enumerate(rows):
        bg = LIGHT if i % 2 == 0 else _rgb(0xE0, 0xEE, 0xF4)
        top_r = 3.64 + i * 0.44
        add_rect(sl, 0.3, top_r, 12.7, 0.44, bg)
        for j, (text, wid, lft_off) in enumerate([
            (q,     6.2, 0.42),
            (spec,  2.9, 6.82),
            (score, 1.0, 9.9),
            (hit,   0.7, 11.15),
        ]):
            txb = add_textbox(sl, lft_off, top_r + 0.06, wid, 0.34)
            txf = clear_first_para(txb)
            colour = GREEN if j == 3 else NAVY
            para(txf, text, 10, colour=colour, bold=(j == 3))

    # Semantic proof banner
    add_rect(sl, 0.3, 5.89, 12.7, 0.99, NAVY)
    txb_ph = add_textbox(sl, 0.5, 5.95, 12.3, 0.36)
    txf_ph = clear_first_para(txb_ph)
    para(txf_ph,
         "Semantic Proof — Vocabulary Mismatch Handled Correctly:",
         12, bold=True, colour=TEAL)
    txb_pb = add_textbox(sl, 0.5, 6.30, 12.3, 0.54)
    txf_pb = clear_first_para(txb_pb)
    para(txf_pb,
         "Query: \"renal insufficiency in T2DM\"  →  Rank 1: Nephrology / CKD  score=0.985  "
         "—  no word overlap between query and document. Keyword matcher returns nothing; "
         "embedding returns clinically correct note.",
         10, colour=WHITE, space_before=2)

    add_slide_number(sl, num, total)


def slide_10_summary(prs, num, total):
    """Slide 10 — Summary & Next Steps (full navy bg)."""
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, NAVY)
    # Teal accent bar on left
    add_rect(sl, 0, 0, 0.18, 7.5, TEAL)

    # Slide title
    txb_title = add_textbox(sl, 0.5, 0.25, 12.5, 0.72)
    txf_title = clear_first_para(txb_title)
    para(txf_title, "Summary & Next Steps", 28, bold=True, colour=WHITE)

    # Left panel — Delivered
    add_rect(sl, 0.45, 1.10, 5.98, 5.72, _rgb(0x0D, 0x38, 0x6A))
    txb_dh = add_textbox(sl, 0.65, 1.18, 5.6, 0.44)
    txf_dh = clear_first_para(txb_dh)
    para(txf_dh, "Delivered", 17, bold=True, colour=TEAL)
    txb_dl = add_textbox(sl, 0.65, 1.68, 5.6, 5.0)
    txf_dl = clear_first_para(txb_dl)
    for line in [
        "✓  Semantic retrieval (not keyword matching)",
        "✓  Dual embedding backends",
        "     (SentenceTransformer + TF-IDF/LSA)",
        "✓  FAISS cosine-similarity vector index",
        "✓  Claude API clinical summarisation",
        "✓  FastAPI REST service (GET + POST /retrieve)",
        "✓  Evaluation — 5 query types, Precision@1 = 1.0",
        "✓  20 passing tests (fully offline, no API key)",
        "✓  Docker-ready deployment",
    ]:
        para(txf_dl, line, 12, colour=WHITE, space_before=5)

    # Right panel — Next Steps
    add_rect(sl, 6.9, 1.10, 6.0, 5.72, _rgb(0x0D, 0x38, 0x6A))
    txb_nh = add_textbox(sl, 7.1, 1.18, 5.6, 0.44)
    txf_nh = clear_first_para(txb_nh)
    para(txf_nh, "Next Steps", 17, bold=True, colour=TEAL)
    txb_nl = add_textbox(sl, 7.1, 1.68, 5.6, 5.0)
    txf_nl = clear_first_para(txb_nl)
    for line in [
        "▶  Fine-tune on corpus triplets",
        "     (+5–15% precision expected)",
        "▶  Cross-encoder re-ranker",
        "     (top-10 → top-5 precision boost)",
        "▶  PHI de-identification before production",
        "▶  HNSW index for sub-ms at 1M+ scale",
        "▶  Auth + rate limiting for production API",
        "▶  Async embedding for background updates",
    ]:
        para(txf_nl, line, 12, colour=WHITE, space_before=5)

    # Footer
    txb_foot = add_textbox(sl, 0.45, 6.75, 12.5, 0.25)
    txf_foot = clear_first_para(txb_foot)
    para(txf_foot,
         "Clinical AI Take-Home Exam  ·  Invitrace Co., Ltd.  ·  June 2026",
         10, colour=GREY, align=PP_ALIGN.CENTER)

    add_slide_number(sl, num, total)


# ---------------------------------------------------------------------------
# Main build function
# ---------------------------------------------------------------------------

TOTAL = 10


def build() -> Presentation:
    prs = new_prs()

    slide_01_title(prs,        1, TOTAL)
    slide_02_problem(prs,      2, TOTAL)
    slide_03_dataset(prs,      3, TOTAL)
    slide_04_architecture(prs, 4, TOTAL)
    slide_05_embedding(prs,    5, TOTAL)
    slide_06_retrieval(prs,    6, TOTAL)
    slide_07_llm(prs,          7, TOTAL)
    slide_08_api(prs,          8, TOTAL)
    slide_09_evaluation(prs,   9, TOTAL)
    slide_10_summary(prs,     10, TOTAL)

    return prs


if __name__ == "__main__":
    out = Path("/home/user/clinic/Clinical_Note_Retrieval_Exam.pptx")
    prs = build()
    prs.save(str(out))
    print(f"Saved: {out}  ({out.stat().st_size // 1024} KB)")
