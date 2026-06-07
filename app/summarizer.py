"""LLM-powered summarization of retrieved clinical notes via Claude API."""
from __future__ import annotations

import logging
from typing import Any

import anthropic

from app.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, SUMMARY_MAX_TOKENS

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a senior clinical decision-support assistant helping a doctor quickly \
review retrieved patient notes. You write clear, accurate, concise summaries \
targeted at a physician audience.

When summarising, you:
1. Lead with the most clinically salient findings across all notes.
2. Highlight patterns, shared diagnoses, or relevant differentials.
3. Note any red-flag findings explicitly.
4. Keep the summary under 300 words unless the complexity demands more.
5. Do NOT fabricate findings that are not present in the provided notes.
"""

_USER_TEMPLATE = """\
Doctor's query: {query}

The system retrieved the following {n} clinical notes (ordered by relevance):

{notes_block}

Please provide a concise clinical summary that directly addresses the doctor's \
query based on these notes.\
"""


def build_notes_block(results: list[dict[str, Any]]) -> str:
    parts = []
    for r in results:
        part = (
            f"--- Note {r['rank']} (score={r['score']:.3f}) ---\n"
            f"Specialty: {r.get('specialty', 'N/A')}\n"
            f"Sample: {r.get('sample_name', 'N/A')}\n"
            f"Description: {r.get('description', 'N/A')}\n"
            f"Keywords: {r.get('keywords', 'N/A')}\n\n"
            f"{r.get('transcription', '')[:1500]}\n"
        )
        parts.append(part)
    return "\n".join(parts)


def summarize(query: str, results: list[dict[str, Any]]) -> str:
    """
    Call Claude to generate a doctor-facing summary of retrieved notes.

    Falls back to a structured plain-text summary if the API key is absent
    (useful for local dev / evaluation without spending API credits).
    """
    if not results:
        return "No relevant clinical notes were retrieved for this query."

    notes_block = build_notes_block(results)
    user_message = _USER_TEMPLATE.format(
        query=query, n=len(results), notes_block=notes_block
    )

    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set — returning rule-based summary.")
        return _fallback_summary(query, results)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=SUMMARY_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def _fallback_summary(query: str, results: list[dict[str, Any]]) -> str:
    """Rule-based summary when no API key is available."""
    specialties = list({r.get("specialty", "") for r in results if r.get("specialty")})
    descriptions = [r.get("description", "") for r in results if r.get("description")]

    lines = [
        f"Query: {query}",
        f"\nRetrieved {len(results)} relevant clinical note(s).",
        f"Specialties covered: {', '.join(specialties) or 'N/A'}",
        "\nTop findings:",
    ]
    for r in results[:3]:
        lines.append(
            f"  [{r['rank']}] {r.get('description', '')} "
            f"(score: {r['score']:.3f})"
        )
    if descriptions:
        lines.append(
            "\nNote: Set ANTHROPIC_API_KEY for an AI-generated clinical summary."
        )
    return "\n".join(lines)
