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
