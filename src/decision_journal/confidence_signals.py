"""Phase 2b candidate confidence signals (rule baseline + optional LLM second pass).

Compared against human Rubric B (quote-to-decision support) — not Rubric A validity.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import OpenAI

from decision_journal.extraction import get_client, normalize_for_quote_match, normalize_json_output

CONFIDENCE_LEVELS = ("low", "medium", "high")
LEVEL_TO_ORD = {"low": 0, "medium": 1, "high": 2}
ORD_TO_LEVEL = {0: "low", 1: "medium", 2: "high"}

HEDGING_PATTERN = re.compile(
    r"\b(should|must|need to|ought to|might|could|perhaps|arguably|immediately|urgently)\b",
    re.I,
)

LLM_CONFIDENCE_PROMPT = """
You assess extraction evidence strength only — NOT whether the entry is a valid government policy decision.

Given DECISION and SOURCE_QUOTE, rate how strongly the quote supports the decision text.

Rules:
- high: quote clearly supports the decision text with minimal inference
- medium: partial or indirect support; some inference or wording mismatch
- low: quote missing, unreadable, or does not support the decision text

Do not penalize procedural or narrative content — only judge quote-to-decision support.

Return JSON only (no markdown):
{{"confidence": "high" or "medium" or "low", "reasoning": "one short sentence"}}

DECISION:
{decision}

SOURCE_QUOTE:
{quote}
"""


def quote_readable(quote: str | None) -> bool:
    q = (quote or "").strip()
    if len(q) < 12:
        return False
    if q in {"...", "…", '""', "''"}:
        return False
    return True


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in STOPWORDS}


STOPWORDS = {
    "that",
    "this",
    "with",
    "from",
    "have",
    "were",
    "been",
    "they",
    "their",
    "there",
    "which",
    "would",
    "could",
    "should",
    "about",
    "into",
    "than",
    "then",
    "when",
    "what",
    "your",
    "also",
    "very",
    "more",
    "some",
    "such",
    "only",
    "other",
    "being",
    "made",
    "said",
    "will",
    "government",
    "decision",
}


def quote_supports_decision_heuristic(decision: str, quote: str | None) -> bool:
    """Rule-based [2]: does quote support decision text (not topic-only)?"""
    q = (quote or "").strip()
    d = (decision or "").strip()
    if not q or not d:
        return False

    nd = normalize_for_quote_match(d)
    nq = normalize_for_quote_match(q)
    if nd and nq and (nd in nq or nq in nd):
        return True

    d_words = _content_words(d)
    q_words = _content_words(q)
    if not d_words:
        return False
    overlap = len(d_words & q_words) / len(d_words)
    if overlap >= 0.55:
        return True

    # Decision adds hedge/intensifier not in quote → partial support at best
    for match in HEDGING_PATTERN.finditer(d):
        token = match.group(1).lower()
        if token not in q.lower():
            return False

    return overlap >= 0.35


def score_to_confidence(points: int) -> str:
    if points >= 2:
        return "high"
    if points == 1:
        return "medium"
    return "low"


def rule_based_confidence(item: dict[str, Any]) -> dict[str, Any]:
    """Checklist-style rule baseline aligned with Rubric B checklist (0/1/2 → L/M/H)."""
    quote = item.get("source_quote")
    decision = item.get("decision") or ""

    checks = {
        "quote_readable": quote_readable(quote),
        "quote_supports_decision": quote_supports_decision_heuristic(decision, quote),
    }
    points = sum(1 for v in checks.values() if v)
    confidence = score_to_confidence(points)

    details: dict[str, Any] = {
        "points": points,
        "checks": checks,
    }
    trace = item.get("traceability_ok")
    if trace is False and confidence == "high":
        details["traceability_note"] = "high_support_despite_trace_fail"
    elif trace is True:
        details["traceability_ok"] = True

    return {
        "rule_confidence": confidence,
        "rule_details": details,
    }


def call_llm_confidence(
    decision: str,
    quote: str | None,
    *,
    model: str,
    client: OpenAI | None = None,
) -> dict[str, Any]:
    client = client or get_client()
    prompt = LLM_CONFIDENCE_PROMPT.format(
        decision=decision or "(none)",
        quote=quote or "(none)",
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    raw = (response.choices[0].message.content or "").strip()
    normalized = normalize_json_output(raw)
    try:
        parsed = json.loads(normalized)
    except json.JSONDecodeError as exc:
        return {
            "llm_confidence": None,
            "llm_reasoning": None,
            "llm_error": f"invalid_json: {exc}",
            "llm_raw": raw,
        }

    level = str(parsed.get("confidence", "")).strip().lower()
    if level not in CONFIDENCE_LEVELS:
        return {
            "llm_confidence": None,
            "llm_reasoning": parsed.get("reasoning"),
            "llm_error": f"invalid_level: {level}",
            "llm_raw": raw,
        }

    return {
        "llm_confidence": level,
        "llm_reasoning": parsed.get("reasoning"),
        "llm_error": None,
        "llm_raw": raw,
    }


def linear_weighted_kappa(y_true: list[int], y_pred: list[int], n_classes: int = 3) -> float:
    """Cohen's kappa with linear weights for ordinal 0..n_classes-1."""
    n = len(y_true)
    if n == 0:
        return float("nan")

    conf = [[0] * n_classes for _ in range(n_classes)]
    for t, p in zip(y_true, y_pred, strict=True):
        if 0 <= t < n_classes and 0 <= p < n_classes:
            conf[t][p] += 1

    weights = [[abs(i - j) / (n_classes - 1) for j in range(n_classes)] for i in range(n_classes)]

    obs = sum(weights[i][j] * conf[i][j] for i in range(n_classes) for j in range(n_classes)) / n

    row_marg = [sum(conf[i][j] for j in range(n_classes)) / n for i in range(n_classes)]
    col_marg = [sum(conf[i][j] for i in range(n_classes)) / n for j in range(n_classes)]
    exp = sum(weights[i][j] * row_marg[i] * col_marg[j] for i in range(n_classes) for j in range(n_classes))

    if exp == 1.0:
        return 1.0 if obs == 1.0 else 0.0
    return 1.0 - (obs / exp) if exp else float("nan")


def confusion_matrix(
    y_true: list[str],
    y_pred: list[str],
    labels: tuple[str, ...] = CONFIDENCE_LEVELS,
) -> dict[str, dict[str, int]]:
    matrix: dict[str, dict[str, int]] = {t: {p: 0 for p in labels} for t in labels}
    for t, p in zip(y_true, y_pred, strict=True):
        if t in matrix and p in matrix[t]:
            matrix[t][p] += 1
    return matrix


def compare_signals(
    items: list[dict[str, Any]],
    *,
    human_key: str = "human_confidence",
    pred_key: str,
) -> dict[str, Any]:
    pairs = [
        (item[human_key], item[pred_key])
        for item in items
        if item.get(human_key) in CONFIDENCE_LEVELS and item.get(pred_key) in CONFIDENCE_LEVELS
    ]
    if not pairs:
        return {"n": 0, "exact_agreement": None, "weighted_kappa": None, "confusion": {}}

    y_true = [LEVEL_TO_ORD[t] for t, _ in pairs]
    y_pred = [LEVEL_TO_ORD[p] for _, p in pairs]
    labels_true = [t for t, _ in pairs]
    labels_pred = [p for _, p in pairs]

    exact = sum(1 for t, p in pairs if t == p) / len(pairs)
    return {
        "n": len(pairs),
        "exact_agreement": round(exact, 4),
        "weighted_kappa": round(linear_weighted_kappa(y_true, y_pred), 4),
        "confusion": confusion_matrix(labels_true, labels_pred),
    }


def default_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
