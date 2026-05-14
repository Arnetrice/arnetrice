"""Walks /content, parses markdown + frontmatter, caches in memory.

Content is loaded once at startup via `warm_caches()` (called from the
FastAPI lifespan). Routes read from in-memory caches — no I/O per request.

HTML is enabled in the markdown renderer so trusted content (committed by
the maintainer) can include inline SVG diagrams and other structural HTML.
"""
from pathlib import Path

import frontmatter
from markdown_it import MarkdownIt

from app.config import PROJECT_ROOT
from app.content.models import (
    ArchitectureTopic,
    ArchitectureTopicDoc,
    Insight,
    InsightDoc,
    SystemCase,
    SystemCaseDoc,
)


CONTENT_ROOT = PROJECT_ROOT / "content"

_md = MarkdownIt("commonmark", {"breaks": False, "html": True}).enable(["table"])


def _render_markdown(text: str) -> str:
    return _md.render(text or "")


def _split_sections(body: str) -> dict[str, str]:
    """Split markdown body on H2 headings. Returns {lowercase_heading: raw_md}."""
    out: dict[str, str] = {}
    current_key: str | None = None
    current: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_key is not None:
                out[current_key] = "\n".join(current).strip()
            current_key = line[3:].strip().lower()
            current = []
        else:
            current.append(line)
    if current_key is not None:
        out[current_key] = "\n".join(current).strip()
    return out


def _load_markdown(directory: Path) -> list[tuple[dict, str]]:
    if not directory.exists():
        return []
    out: list[tuple[dict, str]] = []
    for path in sorted(directory.glob("*.md")):
        post = frontmatter.load(path)
        meta = dict(post.metadata)
        meta.setdefault("slug", path.stem)
        out.append((meta, post.content))
    return out


# ---------- Caches ----------

_systems_cache: list[SystemCaseDoc] = []
_systems_by_slug: dict[str, SystemCaseDoc] = {}
_architecture_cache: list[ArchitectureTopicDoc] = []
_architecture_by_slug: dict[str, ArchitectureTopicDoc] = {}
_insights_cache: list[InsightDoc] = []
_insights_by_slug: dict[str, InsightDoc] = {}


def _build_systems() -> list[SystemCaseDoc]:
    docs: list[SystemCaseDoc] = []
    for meta, body in _load_markdown(CONTENT_ROOT / "systems"):
        case = SystemCase(**meta)
        sections_md = _split_sections(body)
        sections_html = {k: _render_markdown(v) for k, v in sections_md.items()}
        docs.append(SystemCaseDoc(case=case, sections=sections_html))
    return sorted(
        docs,
        key=lambda d: (d.case.published.toordinal() if d.case.published else 0, d.case.id),
        reverse=True,
    )


def _build_architecture() -> list[ArchitectureTopicDoc]:
    docs: list[ArchitectureTopicDoc] = []
    for meta, body in _load_markdown(CONTENT_ROOT / "architecture"):
        topic = ArchitectureTopic(**meta)
        sections_md = _split_sections(body)
        sections_html = {k: _render_markdown(v) for k, v in sections_md.items()}
        docs.append(ArchitectureTopicDoc(topic=topic, sections=sections_html))
    return sorted(docs, key=lambda d: (d.topic.order, d.topic.id))


def _build_insights() -> list[InsightDoc]:
    docs: list[InsightDoc] = []
    for meta, body in _load_markdown(CONTENT_ROOT / "insights"):
        insight = Insight(**meta)
        body_html = _render_markdown(body)
        docs.append(InsightDoc(insight=insight, body_html=body_html))
    # Newest first.
    return sorted(docs, key=lambda d: d.insight.published, reverse=True)


def warm_caches() -> None:
    """Called from FastAPI lifespan at startup."""
    global _systems_cache, _systems_by_slug
    global _architecture_cache, _architecture_by_slug
    global _insights_cache, _insights_by_slug

    _systems_cache = _build_systems()
    _systems_by_slug = {d.case.slug: d for d in _systems_cache}

    _architecture_cache = _build_architecture()
    _architecture_by_slug = {d.topic.slug: d for d in _architecture_cache}

    _insights_cache = _build_insights()
    _insights_by_slug = {d.insight.slug: d for d in _insights_cache}


def get_systems() -> list[SystemCaseDoc]:
    if not _systems_cache:
        warm_caches()
    return _systems_cache


def get_system(slug: str) -> SystemCaseDoc | None:
    if not _systems_by_slug:
        warm_caches()
    return _systems_by_slug.get(slug)


def get_architecture() -> list[ArchitectureTopicDoc]:
    if not _architecture_cache:
        warm_caches()
    return _architecture_cache


def get_topic(slug: str) -> ArchitectureTopicDoc | None:
    if not _architecture_by_slug:
        warm_caches()
    return _architecture_by_slug.get(slug)


def get_insights() -> list[InsightDoc]:
    if not _insights_cache:
        warm_caches()
    return _insights_cache


def get_insight(slug: str) -> InsightDoc | None:
    if not _insights_by_slug:
        warm_caches()
    return _insights_by_slug.get(slug)
