"""Core extraction logic for decision journal entries."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROMPT_TEMPLATE = """
You are analysing emergency policy discussion text.

Task:
Identify decisions or recommendations and their supporting evidence.

Rules:
- Only use information present in the text.
- Do not invent decisions.
- Do not add outside knowledge.
- Return valid JSON only.
- Do not wrap the JSON in markdown code fences.
- Each decision must have supporting evidence.
- Each decision must include both "source_location" and "source_quote" fields.
- "source_location" must point to the exact location of evidence in the provided text using sentence numbering (e.g., "sentence_2" or "sentences_2-3").
- "source_quote" must be an exact quote copied from the provided text that supports the decision.
- Do not use generic labels such as "Input text", "Discussion text", or "Transcript" when sentence-level location can be provided.
- If no clear decision/recommendation exists, return [].
- Do NOT extract suggestions/proposals/options when text states no final agreement/decision was reached.

Return this format:
[
  {{
    "decision": "...",
    "evidence": "...",
    "source_location": "...",
    "source_quote": "..."
  }}
]

TEXT:
{text}
"""

INQUIRY_PROMPT_TEMPLATE = """
You are analysing a UK public inquiry hearing transcript.

Task:
Identify formal decisions, recommendations, or agreed actions announced during the hearing.

Rules:
- Only use information present in the text.
- Only extract formal decisions, recommendations, directions, or agreed actions — NOT routine witness testimony or factual answers.
- Do not extract background statements, procedural exchanges, or answers to questions unless they record a formal decision.
- Do not invent decisions.
- Do not add outside knowledge.
- Return valid JSON only.
- Do not wrap the JSON in markdown code fences.
- Each decision must have supporting evidence.
- Each decision must include both "source_location" and "source_quote" fields.
- "source_location" must point to the exact location of evidence in the provided text using sentence numbering (e.g., "sentence_2" or "sentences_2-3").
- "source_quote" must be an exact quote copied from the provided text that supports the decision.
- Do not use generic labels such as "Input text", "Discussion text", or "Transcript" when sentence-level location can be provided.
- If no formal decision/recommendation exists in this excerpt, return [].
- Do NOT extract suggestions/proposals/options when text states no final agreement/decision was reached.

Return this format:
[
  {{
    "decision": "...",
    "evidence": "...",
    "source_location": "...",
    "source_quote": "..."
  }}
]

TEXT:
{text}
"""


def clean_inquiry_text(text: str) -> str:
    """Normalize inquiry transcript text extracted from PDFs."""
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_for_quote_match(text: str) -> str:
    """Alphanumeric fold for fuzzy quote matching (handles PDF spacing glitches)."""
    text = text.lower()
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"[^a-z0-9]+", "", text)


def quote_found_in_text(quote: str, source_text: str) -> bool:
    """Check if quote appears in source text, tolerating PDF extraction glitches."""
    if not quote or not source_text:
        return False
    if quote in source_text:
        return True
    norm_quote = normalize_for_quote_match(quote)
    norm_source = normalize_for_quote_match(source_text)
    return bool(norm_quote) and norm_quote in norm_source


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env or set the variable in your shell."
        )
    return OpenAI(api_key=api_key)


def split_sentences(text: str) -> List[str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]


def chunk_text_by_sentences(text: str, chunk_size: int = 7, overlap: int = 2) -> List[str]:
    sentences = split_sentences(text)
    if len(sentences) <= chunk_size:
        return [text]
    chunks = []
    step = max(1, chunk_size - overlap)
    for idx in range(0, len(sentences), step):
        chunk = " ".join(sentences[idx : idx + chunk_size])
        if chunk:
            chunks.append(chunk)
        if idx + chunk_size >= len(sentences):
            break
    return chunks


def normalize_json_output(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return s

    fence_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, flags=re.IGNORECASE | re.DOTALL)
    if fence_match:
        s = fence_match.group(1).strip()

    start_candidates = [idx for idx in (s.find("["), s.find("{")) if idx != -1]
    if start_candidates:
        start = min(start_candidates)
        end = max(s.rfind("]"), s.rfind("}"))
        if end >= start:
            s = s[start : end + 1].strip()

    return s


def call_extractor(
    text: str,
    model: str,
    client: OpenAI | None = None,
    prompt_template: str = PROMPT_TEMPLATE,
    temperature: float = 0,
) -> Tuple[str, List[dict], str]:
    client = client or get_client()
    prompt = prompt_template.format(text=text)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    output = (response.choices[0].message.content or "").strip()
    normalized_output = normalize_json_output(output)
    try:
        parsed = json.loads(normalized_output)
        if not isinstance(parsed, list):
            return output, [], "invalid_json_shape"
        return output, parsed, ""
    except json.JSONDecodeError:
        return output, [], "invalid_json"


def dedupe_decisions(items: List[dict]) -> List[dict]:
    seen = set()
    deduped = []
    for item in items:
        decision = item.get("decision", "").strip().lower()
        evidence = item.get("evidence", "").strip().lower()
        key = f"{decision}|{evidence}"
        if key and key not in seen:
            deduped.append(item)
            seen.add(key)
    return deduped


def validate_traceability(items: List[dict], source_text: str) -> List[str]:
    issues = []
    location_pattern = re.compile(r"^sentence_\d+$|^sentences_\d+-\d+$")
    for idx, item in enumerate(items, start=1):
        location = str(item.get("source_location", "")).strip()
        quote = str(item.get("source_quote", "")).strip()
        if not location_pattern.match(location):
            issues.append(f"item_{idx}: bad_source_location")
        if not quote:
            issues.append(f"item_{idx}: missing_source_quote")
        elif not quote_found_in_text(quote, source_text):
            issues.append(f"item_{idx}: source_quote_not_found_in_text")
    return issues


def extract_decisions(
    text: str,
    model: str = "gpt-4o-mini",
    chunk_size: int = 7,
    chunk_overlap: int = 2,
    client: OpenAI | None = None,
    inquiry_mode: bool = False,
    normalize_text: bool = False,
) -> dict:
    """Extract decisions from text, chunking long inputs and deduplicating."""
    if inquiry_mode or normalize_text:
        text = clean_inquiry_text(text)

    prompt_template = INQUIRY_PROMPT_TEMPLATE if inquiry_mode else PROMPT_TEMPLATE
    chunks = chunk_text_by_sentences(text, chunk_size=chunk_size, overlap=chunk_overlap)
    merged: List[dict] = []
    chunk_errors: List[str] = []
    raw_outputs: List[str] = []

    for chunk_idx, chunk in enumerate(chunks, start=1):
        raw, parsed, error = call_extractor(
            chunk, model=model, client=client, prompt_template=prompt_template
        )
        raw_outputs.append(raw)
        if error:
            chunk_errors.append(f"chunk_{chunk_idx}:{error}")
            continue
        for item in parsed:
            item["source_chunk"] = chunk
        merged.extend(parsed)

    decisions = dedupe_decisions(merged)
    traceability_issues: List[str] = []
    pass_count = 0
    fail_count = 0

    for idx, item in enumerate(decisions, start=1):
        chunk_text = item.pop("source_chunk", "")
        item_issues = validate_traceability([item], chunk_text)
        item["traceability_ok"] = not item_issues
        if item_issues:
            for issue in item_issues:
                suffix = issue.split(":", 1)[-1]
                traceability_issues.append(f"item_{idx}:{suffix}")
            fail_count += 1
        else:
            pass_count += 1

    return {
        "decisions": decisions,
        "chunk_count": len(chunks),
        "chunk_errors": chunk_errors,
        "traceability_issues": traceability_issues,
        "traceability_pass_count": pass_count,
        "traceability_fail_count": fail_count,
        "raw_outputs": raw_outputs,
    }


def load_text_file(file_path: str | Path) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".txt":
        text = path.read_text(encoding="utf-8").strip()
    elif suffix == ".docx":
        from docx import Document

        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .txt or .docx, or convert PDF first.")

    if not text:
        raise ValueError(f"File is empty: {path}")
    return text
