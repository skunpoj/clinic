"""Load and preprocess the mtsamples medical transcription dataset."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


def load_mtsamples(csv_path: str | Path) -> pd.DataFrame:
    """
    Load mtsamples.csv and return cleaned records.

    Expected columns: description, medical_specialty, sample_name,
                      transcription, keywords
    """
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Drop rows without transcription text
    df = df[df["transcription"].notna() & (df["transcription"].str.strip() != "")]

    # Clean text
    df["transcription"] = df["transcription"].apply(_clean_text)
    df["medical_specialty"] = df["medical_specialty"].str.strip()
    df["description"] = df["description"].fillna("").str.strip()
    df["sample_name"] = df["sample_name"].fillna("").str.strip()
    df["keywords"] = df["keywords"].fillna("").str.strip()

    df = df.reset_index(drop=True)
    return df


def build_documents(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convert DataFrame rows to document dicts suitable for embedding.
    Each document combines the description and full transcription.
    """
    docs = []
    for i, row in df.iterrows():
        # Context text used for embedding: specialty + description + transcription
        text_for_embedding = _build_embedding_text(row)
        docs.append(
            {
                "id": int(i),
                "specialty": row.get("medical_specialty", ""),
                "sample_name": row.get("sample_name", ""),
                "description": row.get("description", ""),
                "keywords": row.get("keywords", ""),
                "transcription": row.get("transcription", ""),
                "text_for_embedding": text_for_embedding,
            }
        )
    return docs


def _build_embedding_text(row: pd.Series) -> str:
    parts = []
    if row.get("medical_specialty"):
        parts.append(f"Specialty: {row['medical_specialty'].strip()}")
    if row.get("description"):
        parts.append(f"Description: {row['description'].strip()}")
    if row.get("transcription"):
        # Use first 512 tokens worth of chars (~2000 chars) to keep embeddings manageable
        trx = row["transcription"].strip()[:2000]
        parts.append(trx)
    return " | ".join(parts)


def _clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_sample_documents() -> list[dict[str, Any]]:
    """Return a small set of synthetic documents for testing without real data."""
    return [
        {
            "id": 0,
            "specialty": "Nephrology",
            "sample_name": "CKD with Diabetes",
            "description": "Chronic kidney disease in a diabetic patient",
            "keywords": "CKD, diabetes, nephropathy, kidney failure",
            "transcription": (
                "HISTORY: The patient is a 62-year-old male with longstanding type 2 diabetes mellitus "
                "and chronic kidney disease stage 3. He presents with worsening edema and elevated "
                "creatinine. HbA1c is 8.9%. GFR is 38 mL/min. He is on metformin which has been "
                "discontinued given renal impairment. Started on insulin. Nephrology follow-up arranged."
            ),
            "text_for_embedding": (
                "Specialty: Nephrology | Description: Chronic kidney disease in a diabetic patient | "
                "HISTORY: The patient is a 62-year-old male with longstanding type 2 diabetes mellitus "
                "and chronic kidney disease stage 3."
            ),
        },
        {
            "id": 1,
            "specialty": "Cardiology",
            "sample_name": "Chest Pain Evaluation",
            "description": "Acute chest pain, rule out MI",
            "keywords": "chest pain, myocardial infarction, troponin, EKG",
            "transcription": (
                "CHIEF COMPLAINT: Chest pain. The patient is a 55-year-old male who presents with "
                "sudden onset crushing substernal chest pain radiating to the left arm. Troponin I "
                "elevated at 2.3. EKG shows ST elevation in leads II, III, aVF. Emergent catheterization "
                "performed. RCA stent placed. Patient stabilised in CCU."
            ),
            "text_for_embedding": (
                "Specialty: Cardiology | Description: Acute chest pain, rule out MI | "
                "CHIEF COMPLAINT: Chest pain. The patient is a 55-year-old male."
            ),
        },
        {
            "id": 2,
            "specialty": "Pulmonology",
            "sample_name": "COPD Exacerbation",
            "description": "Acute exacerbation of chronic obstructive pulmonary disease",
            "keywords": "COPD, dyspnea, bronchodilator, oxygen therapy",
            "transcription": (
                "HISTORY: 68-year-old female, 40 pack-year smoker, with known COPD presenting with "
                "worsening dyspnea and productive cough with yellow sputum for 3 days. O2 sat 88% on "
                "room air. CXR shows hyperinflation. Started on albuterol nebulizers, ipratropium, "
                "systemic steroids and azithromycin. Pulmonology consulted."
            ),
            "text_for_embedding": (
                "Specialty: Pulmonology | Description: Acute exacerbation of COPD | "
                "HISTORY: 68-year-old female with COPD presenting with worsening dyspnea."
            ),
        },
        {
            "id": 3,
            "specialty": "Orthopedic Surgery",
            "sample_name": "Total Knee Replacement",
            "description": "Right total knee arthroplasty for severe osteoarthritis",
            "keywords": "knee replacement, arthroplasty, osteoarthritis, orthopedics",
            "transcription": (
                "PROCEDURE: Right total knee arthroplasty. The patient is a 71-year-old female with "
                "severe right knee osteoarthritis refractory to conservative management. Under spinal "
                "anesthesia, medial parapatellar approach used. Cruciate-retaining implant placed. "
                "Blood loss 300 mL. Post-op PT initiated. DVT prophylaxis with enoxaparin."
            ),
            "text_for_embedding": (
                "Specialty: Orthopedic Surgery | Description: Right total knee arthroplasty | "
                "PROCEDURE: Right total knee arthroplasty for severe osteoarthritis."
            ),
        },
        {
            "id": 4,
            "specialty": "Endocrinology",
            "sample_name": "Diabetic Ketoacidosis",
            "description": "DKA in a type 1 diabetic patient",
            "keywords": "DKA, insulin, type 1 diabetes, ketoacidosis, hyperglycemia",
            "transcription": (
                "HISTORY: 24-year-old female with type 1 diabetes mellitus presents with nausea, "
                "vomiting and abdominal pain for 12 hours. Blood glucose 480 mg/dL, pH 7.18, "
                "bicarbonate 8, ketones 4+. Diagnosis: diabetic ketoacidosis. IV insulin infusion "
                "started, aggressive fluid resuscitation with normal saline. Potassium supplementation. "
                "ICU admission. Glucose normalised within 18 hours."
            ),
            "text_for_embedding": (
                "Specialty: Endocrinology | Description: DKA in type 1 diabetic | "
                "HISTORY: 24-year-old female with type 1 diabetes presents with DKA."
            ),
        },
    ]
