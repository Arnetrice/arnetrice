"""Pydantic schemas for content frontmatter, plus loaded-document wrappers."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CaseState = Literal["draft", "queued", "live"]
Channel = Literal["SYS", "WKF", "GOV", "VIS"]
TopicCategory = Literal["systems", "workflow", "governance", "visibility", "ai-assisted"]


class SystemCase(BaseModel):
    """Frontmatter for a case study under /systems/{slug}.

    Long-form narrative (challenge/architecture/outcome) lives in the
    markdown body, split by H2 headings.
    """

    slug: str
    id: str = Field(description="Display identifier, e.g. 'SYS-001'.")
    title: str
    role: str
    timeframe: str
    summary: str
    channel: Channel
    state: CaseState = "live"
    stack: list[str] = Field(default_factory=list)
    published: date | None = None
    featured: bool = False
    order: int = 0


class SystemCaseDoc(BaseModel):
    """A loaded case study: frontmatter + rendered body sections."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    case: SystemCase
    sections: dict[str, str] = Field(default_factory=dict)

    @property
    def url(self) -> str:
        return f"/systems/{self.case.slug}"

    def section(self, key: str) -> str:
        return self.sections.get(key.lower(), "")


class ArchitectureTopic(BaseModel):
    """Frontmatter for an architecture deep-dive under /architecture/{slug}."""

    slug: str
    id: str = Field(description="Display identifier, e.g. 'ARC-001'.")
    title: str
    summary: str
    channel: Channel
    category: TopicCategory
    state: CaseState = "live"
    primitives: list[str] = Field(default_factory=list)
    published: date | None = None
    featured: bool = False
    order: int = 0


class ArchitectureTopicDoc(BaseModel):
    """A loaded topic: frontmatter + rendered body sections."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    topic: ArchitectureTopic
    sections: dict[str, str] = Field(default_factory=dict)

    @property
    def url(self) -> str:
        return f"/architecture/{self.topic.slug}"

    def section(self, key: str) -> str:
        return self.sections.get(key.lower(), "")


class Insight(BaseModel):
    """Frontmatter for a writing piece under /insights/{slug}.

    Unlike case studies and architecture topics, insights are flat essays —
    the body is rendered as a single HTML blob (no enforced sections).
    """

    slug: str
    id: str = Field(description="Display identifier, e.g. 'INS-001'.")
    title: str
    summary: str
    channel: Channel
    state: CaseState = "live"
    topic: str = Field(description="Free-form topic tag, e.g. 'design', 'operations'.")
    published: date
    reading_time_min: int = 5
    featured: bool = False


class InsightDoc(BaseModel):
    """A loaded insight: frontmatter + rendered body HTML."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    insight: Insight
    body_html: str = ""

    @property
    def url(self) -> str:
        return f"/insights/{self.insight.slug}"
