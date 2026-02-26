"""
Pydantic schemas for validating AI output.

Every LLM response is parsed into one of these models before being
returned to the caller.  This eliminates manual json.loads() / KeyError
handling and guarantees a consistent contract between the AI layer and
the Django views.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from typing import List, Literal


# ── 1. Improve Description ──────────────────────────────────────────
class ImprovedDescription(BaseModel):
    """Schema returned by the improve-description chain."""
    improved_description: str = Field(
        ...,
        min_length=10,
        description="The rewritten, actionable task description.",
    )


# ── 2. Suggest Priority ─────────────────────────────────────────────
class PrioritySuggestion(BaseModel):
    """Schema returned by the suggest-priority chain."""
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        ...,
        description="Suggested priority level.",
    )
    reason: str = Field(
        ...,
        min_length=5,
        description="Brief explanation for the chosen priority.",
    )

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v: str) -> str:
        return v.strip().upper()


# ── 3. Generate Subtasks (v2 — with time estimates) ─────────────────
class SubtaskItem(BaseModel):
    """A single subtask with an optional time estimate."""
    title: str = Field(..., min_length=2, description="Subtask title.")
    time_estimate_minutes: int = Field(
        default=30,
        ge=5,
        le=480,
        description="Estimated minutes to complete this subtask.",
    )


class SubtaskList(BaseModel):
    """Schema returned by the generate-subtasks chain."""
    subtasks: List[SubtaskItem] = Field(
        ...,
        min_length=1,
        description="List of generated subtasks.",
    )


# ── 4. Productivity Coach ───────────────────────────────────────────
class CoachTip(BaseModel):
    """A single productivity coaching tip."""
    category: Literal["TIME_MANAGEMENT", "PRIORITIZATION", "FOCUS", "PLANNING", "MOTIVATION"] = Field(
        ...,
        description="Category of the tip.",
    )
    tip: str = Field(
        ...,
        min_length=10,
        description="Actionable productivity tip.",
    )
    reasoning: str = Field(
        ...,
        min_length=10,
        description="Why this tip is relevant based on the user's data.",
    )

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        return v.strip().upper().replace(" ", "_")


class ProductivityCoachResponse(BaseModel):
    """Schema returned by the productivity-coach chain."""
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Productivity score from 0 to 100.",
    )
    summary: str = Field(
        ...,
        min_length=10,
        description="Brief overall assessment of productivity.",
    )
    tips: List[CoachTip] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Personalized coaching tips.",
    )


# ── 5. Smart Search ─────────────────────────────────────────────────
class SearchFilter(BaseModel):
    """Structured search filter extracted from natural language query."""
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords to search in title/description.",
    )
    status: List[str] = Field(
        default_factory=list,
        description="Status filters: pending, in_progress, completed, cancelled.",
    )
    priority: List[str] = Field(
        default_factory=list,
        description="Priority filters: high, medium, low.",
    )
    overdue: bool = Field(
        default=False,
        description="Whether to filter for overdue tasks only.",
    )
    sort_by: Literal["relevance", "deadline", "priority", "created_at"] = Field(
        default="relevance",
        description="How to sort results.",
    )

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, list):
            return [s.strip().lower() for s in v]
        return v

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v):
        if isinstance(v, list):
            return [p.strip().lower() for p in v]
        return v
