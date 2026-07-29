"""Parse dissertation Markdown into stable section/paragraph IDs."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")
FIGURE_MARKER_RE = re.compile(r"^\[\[FIGURE:.+\]\]\s*$")
LIST_RE = re.compile(r"^([-*]|\d+\.)\s+")
SKIP_LINE_PATTERNS = [
    re.compile(r"^\*\*Status:\*\*"),
    re.compile(r"^\*\*Title \(suggested\):\*\*"),
    re.compile(r"^---$"),
    re.compile(r"^\*\*Figure references:\*\*"),
    re.compile(r"^\*\*Note:\*\* Do not"),
    re.compile(r"^\*\*Title:\*\*"),
    re.compile(r"^\*.*(?:Draft|Sources:|Paste into).*\*$"),
]

FILE_SLUGS = {
    "ABSTRACT.md": "abstract",
    "CHAPTER_1_INTRODUCTION.md": "ch1",
    "CHAPTER_2_LITERATURE.md": "ch2",
    "CHAPTER_3_METHODS.md": "ch3",
    "CHAPTER_4_RESULTS.md": "ch4",
    "CHAPTER_5_DISCUSSION.md": "ch5",
    "REFERENCES.md": "refs",
}


@dataclass
class Block:
    block_type: str
    text: str
    start_line: int
    end_line: int
    section_path: str
    editable: bool
    paragraph_id: str | None = None
    heading_level: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FileInventory:
    path: str
    slug: str
    blocks: list[Block] = field(default_factory=list)

    @property
    def editable_blocks(self) -> list[Block]:
        return [b for b in self.blocks if b.editable and b.paragraph_id]

    @property
    def editable_count(self) -> int:
        return len(self.editable_blocks)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "slug": self.slug,
            "block_count": len(self.blocks),
            "editable_count": self.editable_count,
            "blocks": [b.to_dict() for b in self.blocks],
        }


def file_slug(path: Path) -> str:
    return FILE_SLUGS.get(path.name, path.stem.lower().replace(" ", "_"))


def _should_skip_line(stripped: str) -> bool:
    if not stripped:
        return False
    if stripped.startswith("## Draft checklist"):
        return True
    return any(p.match(stripped) for p in SKIP_LINE_PATTERNS)


def _section_key_from_heading(title: str) -> str:
    """Extract leading section number if present (e.g. '3.9', '5.3.6')."""
    match = re.match(r"^(\d+(?:\.\d+)*)\b", title.strip())
    if match:
        return match.group(1)
    # Unnumbered chapter labels / Abstract
    cleaned = re.sub(r"[^\w]+", "_", title.strip().lower()).strip("_")
    return cleaned or "body"


def _section_matches_filter(section_path: str, filters: Iterable[str]) -> bool:
    """True if section_path matches any filter token (* = all)."""
    tokens = list(filters)
    if not tokens or "*" in tokens:
        return True
    # section_path like ch3/3.9 or ch5/5.3.6
    parts = section_path.split("/")
    section = parts[-1] if parts else section_path
    for token in tokens:
        if section == token or section.startswith(token + "."):
            return True
        # also allow token contained as path segment
        if token in parts:
            return True
    return False


def inventory_file(path: Path, *, relative_to: Path | None = None) -> FileInventory:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    slug = file_slug(path)
    display = str(path.relative_to(relative_to)) if relative_to else str(path)

    blocks: list[Block] = []
    section_stack: list[str] = [slug]
    editable_ordinal = 0
    i = 0
    in_checklist = False
    in_fence = False

    def current_section() -> str:
        return "/".join(section_stack)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        line_no = i + 1

        if stripped.startswith("```"):
            in_fence = not in_fence
            blocks.append(
                Block(
                    block_type="fence_marker",
                    text=line,
                    start_line=line_no,
                    end_line=line_no,
                    section_path=current_section(),
                    editable=False,
                )
            )
            i += 1
            continue

        if in_fence:
            blocks.append(
                Block(
                    block_type="fence",
                    text=line,
                    start_line=line_no,
                    end_line=line_no,
                    section_path=current_section(),
                    editable=False,
                )
            )
            i += 1
            continue

        if stripped.startswith("## Draft checklist"):
            in_checklist = True
            blocks.append(
                Block(
                    block_type="skip",
                    text=line,
                    start_line=line_no,
                    end_line=line_no,
                    section_path=current_section(),
                    editable=False,
                )
            )
            i += 1
            continue

        if in_checklist:
            blocks.append(
                Block(
                    block_type="skip",
                    text=line,
                    start_line=line_no,
                    end_line=line_no,
                    section_path=current_section(),
                    editable=False,
                )
            )
            i += 1
            continue

        if _should_skip_line(stripped):
            blocks.append(
                Block(
                    block_type="skip",
                    text=line,
                    start_line=line_no,
                    end_line=line_no,
                    section_path=current_section(),
                    editable=False,
                )
            )
            i += 1
            continue

        if not stripped:
            blocks.append(
                Block(
                    block_type="blank",
                    text="",
                    start_line=line_no,
                    end_line=line_no,
                    section_path=current_section(),
                    editable=False,
                )
            )
            i += 1
            continue

        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            key = _section_key_from_heading(title)
            # section_stack[0] is always file slug; headings push numbered keys.
            if level == 1:
                section_stack = [slug] if key in {slug, "abstract", "references"} else [slug, key]
            else:
                # Keep slug + keys for heading levels 2..level
                section_stack = [slug] + section_stack[1 : level - 1] + [key]

            blocks.append(
                Block(
                    block_type="heading",
                    text=line,
                    start_line=line_no,
                    end_line=line_no,
                    section_path="/".join(section_stack),
                    editable=False,
                    heading_level=level,
                )
            )
            i += 1
            continue

        if FIGURE_MARKER_RE.match(stripped):
            blocks.append(
                Block(
                    block_type="figure_marker",
                    text=stripped,
                    start_line=line_no,
                    end_line=line_no,
                    section_path=current_section(),
                    editable=False,
                )
            )
            i += 1
            continue

        if stripped.startswith("|"):
            start = i
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            blocks.append(
                Block(
                    block_type="table",
                    text="\n".join(table_lines),
                    start_line=start + 1,
                    end_line=i,
                    section_path=current_section(),
                    editable=False,
                )
            )
            continue

        if stripped.startswith(">"):
            start = i
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i])
                i += 1
            blocks.append(
                Block(
                    block_type="blockquote",
                    text="\n".join(quote_lines),
                    start_line=start + 1,
                    end_line=i,
                    section_path=current_section(),
                    editable=False,
                )
            )
            continue

        if LIST_RE.match(stripped):
            blocks.append(
                Block(
                    block_type="list_item",
                    text=stripped,
                    start_line=line_no,
                    end_line=line_no,
                    section_path=current_section(),
                    editable=False,  # pilot: lists not editable
                )
            )
            i += 1
            continue

        # Prose paragraph: single non-empty line (dissertation MD is one line per para)
        editable_ordinal += 1
        para_id = f"{current_section()}/p{editable_ordinal:03d}"
        blocks.append(
            Block(
                block_type="paragraph",
                text=stripped,
                start_line=line_no,
                end_line=line_no,
                section_path=current_section(),
                editable=True,
                paragraph_id=para_id,
            )
        )
        i += 1

    return FileInventory(path=display, slug=slug, blocks=blocks)


def inventory_paths(
    paths: list[Path],
    *,
    relative_to: Path | None = None,
    section_filters: dict[str, list[str]] | None = None,
) -> list[FileInventory]:
    inventories = [inventory_file(p, relative_to=relative_to) for p in paths]
    if not section_filters:
        return inventories

    # Annotate editable flag down if section filter excludes
    for inv in inventories:
        filters = section_filters.get(inv.slug)
        if filters is None:
            # file not in filter map → no editable targets for this mode
            for b in inv.blocks:
                if b.editable:
                    b.editable = False
                    b.paragraph_id = None
            continue
        for b in inv.blocks:
            if not b.editable:
                continue
            if not _section_matches_filter(b.section_path, filters):
                b.editable = False
                b.paragraph_id = None
    return inventories


def batch_editable(
    inventories: list[FileInventory],
    *,
    batch_size: int = 4,
) -> list[list[Block]]:
    """Non-overlapping contiguous batches of editable paragraphs (3–5 preferred)."""
    size = max(3, min(5, batch_size))
    editable: list[Block] = []
    for inv in inventories:
        editable.extend(inv.editable_blocks)
    batches: list[list[Block]] = []
    for idx in range(0, len(editable), size):
        batches.append(editable[idx : idx + size])
    return batches


def neighbour_context(
    inventories: list[FileInventory],
    target_ids: set[str],
    *,
    neighbors: int = 1,
) -> dict[str, dict[str, list[dict]]]:
    """Read-only neighbouring blocks (any type) around each target, by paragraph_id."""
    all_blocks: list[Block] = []
    for inv in inventories:
        all_blocks.extend(inv.blocks)

    id_to_index = {
        b.paragraph_id: i
        for i, b in enumerate(all_blocks)
        if b.paragraph_id
    }
    out: dict[str, dict[str, list[dict]]] = {}
    for pid in target_ids:
        idx = id_to_index.get(pid)
        if idx is None:
            continue
        before = []
        after = []
        # walk backwards/forwards collecting up to N non-blank blocks
        j = idx - 1
        while j >= 0 and len(before) < neighbors:
            b = all_blocks[j]
            if b.block_type != "blank":
                before.append(
                    {
                        "block_type": b.block_type,
                        "paragraph_id": b.paragraph_id,
                        "text": b.text,
                    }
                )
            j -= 1
        j = idx + 1
        while j < len(all_blocks) and len(after) < neighbors:
            b = all_blocks[j]
            if b.block_type != "blank":
                after.append(
                    {
                        "block_type": b.block_type,
                        "paragraph_id": b.paragraph_id,
                        "text": b.text,
                    }
                )
            j += 1
        out[pid] = {
            "before": list(reversed(before)),
            "after": after,
        }
    return out
