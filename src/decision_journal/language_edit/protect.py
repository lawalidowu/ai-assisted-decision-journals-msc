"""Extract and compare protected elements for language-edit validation."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Iterable

# Author-year citations in parentheses or narrative form
CITATION_PAREN_RE = re.compile(
    r"\((?:[A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+)?(?:\s+et\s+al\.)?(?:\s*&?\s*[A-Z][A-Za-z'’-]+)?(?:,\s*)?)+(?:\s*\d{4}[a-z]?)(?:;\s*[^)]+)?\)"
)
CITATION_NARRATIVE_RE = re.compile(
    r"\b([A-Z][A-Za-z'’-]+(?:\s+et\s+al\.)?)\s*\((\d{4}[a-z]?)\)"
)

NUMBER_RE = re.compile(
    r"(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?(?![\w.])"
)
SAMPLE_N_RE = re.compile(r"\bn\s*=\s*\d+\b", re.I)
TEMPERATURE_RE = re.compile(r"\btemperature\s+[0-9.]+", re.I)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
CROSS_REF_RE = re.compile(
    r"\b(?:Chapter|Section|Figure|Table|Phase)\s+\d+(?:\.\d+[a-z]?)*(?:\.[a-z])?\b"
    r"|\b§\s*\d+(?:\.\d+)*\b",
    re.I,
)
FIGURE_MARKER_RE = re.compile(r"\[\[FIGURE:[^\]]+\]\]")
GREEK_STATS_RE = re.compile(
    r"[καβγδθμσρτωχφψΩα]|κ\s*≈\s*[0-9.]+(?:\s*[–-]\s*[0-9.]+)?|χ²|p\s*[<≤=]\s*[0-9.]+",
    re.I,
)
MARKDOWN_MARKER_RE = re.compile(
    r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))"
)
NO_HIGH_CELL_RE = re.compile(r"\bno\s*[×x]\s*high\b", re.I)


@dataclass
class ProtectedBundle:
    citations: list[str] = field(default_factory=list)
    numbers: list[str] = field(default_factory=list)
    sample_sizes: list[str] = field(default_factory=list)
    years: list[str] = field(default_factory=list)
    cross_refs: list[str] = field(default_factory=list)
    model_names: list[str] = field(default_factory=list)
    artefact_names: list[str] = field(default_factory=list)
    glossary_terms: list[str] = field(default_factory=list)
    greek_stats: list[str] = field(default_factory=list)
    markdown_markers: list[str] = field(default_factory=list)
    figure_markers: list[str] = field(default_factory=list)
    special_phrases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def as_counters(self) -> dict[str, Counter]:
        return {
            "citations": Counter(self.citations),
            "numbers": Counter(self.numbers),
            "sample_sizes": Counter(self.sample_sizes),
            "years": Counter(self.years),
            "cross_refs": Counter(self.cross_refs),
            "model_names": Counter(self.model_names),
            "artefact_names": Counter(self.artefact_names),
            "glossary_terms": Counter(self.glossary_terms),
            "greek_stats": Counter(self.greek_stats),
            "markdown_markers": Counter(self.markdown_markers),
            "figure_markers": Counter(self.figure_markers),
            "special_phrases": Counter(self.special_phrases),
        }


def _find_configured(text: str, items: Iterable[str]) -> list[str]:
    found: list[str] = []
    for item in items:
        if not item:
            continue
        if item in text:
            start = 0
            while True:
                idx = text.find(item, start)
                if idx < 0:
                    break
                found.append(item)
                start = idx + len(item)
    return found


def extract_protected(
    text: str,
    *,
    model_names: Iterable[str] | None = None,
    artefact_names: Iterable[str] | None = None,
    glossary: Iterable[str] | None = None,
) -> ProtectedBundle:
    model_names = list(model_names or [])
    artefact_names = list(artefact_names or [])
    glossary = list(glossary or [])

    citations = [m.group(0) for m in CITATION_PAREN_RE.finditer(text)]
    citations.extend(
        f"{m.group(1)} ({m.group(2)})" for m in CITATION_NARRATIVE_RE.finditer(text)
    )

    sample_sizes = [m.group(0).replace(" ", "") for m in SAMPLE_N_RE.finditer(text)]
    sample_sizes = [re.sub(r"\s+", "", s, flags=re.I) for s in sample_sizes]

    numbers: list[str] = []
    for m in NUMBER_RE.finditer(text):
        token = m.group(0)
        if re.fullmatch(r"(?:19|20)\d{2}", token) and "%" not in token:
            continue
        numbers.append(token)

    for m in TEMPERATURE_RE.finditer(text):
        numbers.append(m.group(0).lower())

    years = YEAR_RE.findall(text)
    cross_refs = [m.group(0) for m in CROSS_REF_RE.finditer(text)]
    greek_stats = [m.group(0) for m in GREEK_STATS_RE.finditer(text)]
    markdown_markers = [m.group(0) for m in MARKDOWN_MARKER_RE.finditer(text)]
    figure_markers = FIGURE_MARKER_RE.findall(text)
    special = [m.group(0) for m in NO_HIGH_CELL_RE.finditer(text)]

    return ProtectedBundle(
        citations=citations,
        numbers=numbers,
        sample_sizes=sample_sizes,
        years=years,
        cross_refs=cross_refs,
        model_names=_find_configured(text, model_names),
        artefact_names=_find_configured(text, artefact_names),
        glossary_terms=_find_configured(text, glossary),
        greek_stats=greek_stats,
        markdown_markers=markdown_markers,
        figure_markers=figure_markers,
        special_phrases=special,
    )


def compare_protected(
    original: str,
    revised: str,
    *,
    model_names: Iterable[str] | None = None,
    artefact_names: Iterable[str] | None = None,
    glossary: Iterable[str] | None = None,
) -> dict:
    """Return ok flag and per-category mismatches (missing/extra)."""
    kwargs = dict(
        model_names=model_names,
        artefact_names=artefact_names,
        glossary=glossary,
    )
    left = extract_protected(original, **kwargs)
    right = extract_protected(revised, **kwargs)
    mismatches: dict[str, dict[str, list[str]]] = {}
    ok = True
    for category, left_c in left.as_counters().items():
        right_c = right.as_counters()[category]
        missing: list[str] = []
        extra: list[str] = []
        for token, count in left_c.items():
            diff = count - right_c.get(token, 0)
            if diff > 0:
                missing.extend([token] * diff)
        for token, count in right_c.items():
            diff = count - left_c.get(token, 0)
            if diff > 0:
                extra.extend([token] * diff)
        if missing or extra:
            ok = False
            mismatches[category] = {"missing": missing, "extra": extra}
    return {
        "ok": ok,
        "mismatches": mismatches,
        "original": left.to_dict(),
        "revised": right.to_dict(),
    }


def markdown_structure_issues(original: str, revised: str) -> list[str]:
    """Lightweight structure checks for a single prose paragraph revision."""
    issues: list[str] = []
    if re.search(r"^#{1,4}\s", revised, re.M):
        issues.append("introduced_heading_marker")
    if "```" in revised and "```" not in original:
        issues.append("introduced_fence")
    if re.search(r"^\|", revised, re.M) and not re.search(r"^\|", original, re.M):
        issues.append("introduced_table_row")
    if "[[FIGURE:" in revised:
        orig_markers = set(FIGURE_MARKER_RE.findall(original))
        new_markers = set(FIGURE_MARKER_RE.findall(revised))
        if new_markers != orig_markers:
            issues.append("figure_marker_changed")
    if "\n\n" in revised.strip():
        issues.append("split_into_multiple_blocks")
    if revised.count("**") % 2 != 0:
        issues.append("unbalanced_bold_markers")
    return issues


def _phrase_in(text: str, phrase: str) -> bool:
    return phrase.casefold() in text.casefold()


def find_missing_qualifiers(
    original: str,
    revised: str,
    qualifiers: Iterable[str],
) -> list[str]:
    """Qualifiers present in original must remain in revised (case-insensitive)."""
    missing: list[str] = []
    for phrase in qualifiers:
        if not phrase:
            continue
        if _phrase_in(original, phrase) and not _phrase_in(revised, phrase):
            missing.append(phrase)
    return missing


def find_us_spellings(text: str, us_to_uk: dict[str, str]) -> list[dict[str, str]]:
    """Return US spellings found that should be UK forms."""
    hits: list[dict[str, str]] = []
    for us, uk in (us_to_uk or {}).items():
        us_token = us.strip()
        if not us_token:
            continue
        if us_token.isalpha():
            pattern = re.compile(rf"\b{re.escape(us_token)}\b", re.I)
            if pattern.search(text):
                hits.append({"us": us_token, "uk": uk.strip()})
        elif us_token.casefold() in text.casefold():
            hits.append({"us": us_token, "uk": uk.strip()})
    return hits


def check_faithful_not_replaced_by_accurate(
    original: str,
    revised: str,
    *,
    forbidden_substitutes: Iterable[str] | None = None,
) -> list[str]:
    """Reject swapping fidelity language for 'accurate' when original used faithful."""
    issues: list[str] = []
    if _phrase_in(original, "faithful") and not _phrase_in(revised, "faithful"):
        if _phrase_in(revised, "accurate"):
            issues.append("faithful_replaced_by_accurate")
    for phrase in forbidden_substitutes or ():
        if _phrase_in(revised, phrase) and not _phrase_in(original, phrase):
            if _phrase_in(original, "faithful"):
                issues.append(f"forbidden_substitute:{phrase}")
    return issues


def check_interleaved_meaning(original: str, revised: str) -> list[str]:
    """If original uses interleaved, revised must keep mixed-together sense."""
    if not _phrase_in(original, "interleaved"):
        return []
    if _phrase_in(revised, "interleaved"):
        return []
    mix_cues = ("mixed", "mixes", "interwoven", "interweav", "woven together")
    if not any(_phrase_in(revised, cue) for cue in mix_cues):
        return ["interleaved_meaning_lost"]
    return []


def check_scope_boundaries(
    original: str,
    revised: str,
    scope_phrases: Iterable[str],
) -> list[str]:
    """Sample/population boundary phrases in original must not disappear."""
    return find_missing_qualifiers(original, revised, scope_phrases)


def check_whether_preserved(original: str, revised: str) -> list[str]:
    """Preserve 'whether' in formal research questions / investigation statements."""
    orig_count = len(re.findall(r"\bwhether\b", original, flags=re.I))
    rev_count = len(re.findall(r"\bwhether\b", revised, flags=re.I))
    if orig_count > rev_count:
        return ["whether_replaced"]
    return []


def language_policy_issues(
    original: str,
    revised: str,
    *,
    qualifiers: Iterable[str] | None = None,
    scope_phrases: Iterable[str] | None = None,
    us_to_uk: dict[str, str] | None = None,
    forbidden_faithful_substitutes: Iterable[str] | None = None,
) -> dict:
    """Aggregate methodological, spelling, fidelity and scope checks."""
    missing_qualifiers = find_missing_qualifiers(original, revised, qualifiers or [])
    missing_scope = check_scope_boundaries(original, revised, scope_phrases or [])
    us_hits = find_us_spellings(revised, us_to_uk or {})
    faithful_issues = check_faithful_not_replaced_by_accurate(
        original,
        revised,
        forbidden_substitutes=forbidden_faithful_substitutes,
    )
    interleaved_issues = check_interleaved_meaning(original, revised)
    whether_issues = check_whether_preserved(original, revised)

    reasons: list[str] = []
    if missing_qualifiers:
        reasons.append("methodological_qualifier_missing")
    if missing_scope:
        reasons.append("scope_boundary_missing")
    if us_hits:
        reasons.append("american_spelling")
    reasons.extend(faithful_issues)
    reasons.extend(interleaved_issues)
    reasons.extend(whether_issues)

    return {
        "ok": not reasons,
        "reasons": reasons,
        "missing_qualifiers": missing_qualifiers,
        "missing_scope_phrases": missing_scope,
        "us_spellings": us_hits,
        "faithful_issues": faithful_issues,
        "interleaved_issues": interleaved_issues,
        "whether_issues": whether_issues,
    }
