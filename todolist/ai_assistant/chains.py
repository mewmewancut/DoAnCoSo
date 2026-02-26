"""
LCEL chains — the public API of the ai_assistant app.

Each function builds a LangChain Expression Language (LCEL) chain:

    prompt | llm | parser

and invokes it with the caller's data.  The parser is either:

* ``StrOutputParser``      → for free-text responses.
* ``PydanticOutputParser``  → for structured JSON validated by Pydantic.

If the LLM returns malformed JSON the chain retries once with a
``OutputFixingParser`` before raising.

Usage from anywhere in the project::

    from ai_assistant.chains import improve_description, suggest_priority, generate_subtasks

    text = improve_description(title="Buy groceries", description="")
    prio = suggest_priority(title="Fix prod bug", description="...", deadline=None)
    subs = generate_subtasks(title="Launch MVP", description="...", count=5)
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

from langchain_core.output_parsers import StrOutputParser
from pydantic import ValidationError

from .llm_client import get_llm
from .prompts import (
    IMPROVE_DESCRIPTION_PROMPT,
    SUGGEST_PRIORITY_PROMPT,
    GENERATE_SUBTASKS_PROMPT,
    PRODUCTIVITY_COACH_PROMPT,
    SMART_SEARCH_PROMPT,
)
from .schemas import (
    ImprovedDescription,
    PrioritySuggestion,
    SubtaskList,
    ProductivityCoachResponse,
    SearchFilter,
)

logger = logging.getLogger(__name__)


# ── helpers ──────────────────────────────────────────────────────────

def _safe_parse_json(text: str) -> dict:
    """
    Extract and parse JSON from LLM output that may contain markdown
    fences or trailing commentary.
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = cleaned.strip().rstrip("`")
    return json.loads(cleaned)


def _friendly_error(exc: Exception) -> str:
    """Map common LLM errors to user-facing messages."""
    msg = str(exc).lower()
    if "api key" in msg or "authentication" in msg or "unauthorized" in msg:
        return "API key error. Please check your LLM configuration."
    if "rate limit" in msg or "quota" in msg:
        return "Rate limit exceeded — please try again in a moment."
    if "timeout" in msg:
        return "Request timed out — please try again."
    return f"AI service error: {exc}"


# ── 1.  Improve Description ─────────────────────────────────────────

def improve_description(title: str, description: str = "") -> str:
    """
    Return an improved, actionable task description (plain text).

    Chain: IMPROVE_DESCRIPTION_PROMPT | llm | StrOutputParser
    Post-validation: must be ≥ 10 chars (via Pydantic schema).
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty.")

    try:
        llm = get_llm()
        chain = IMPROVE_DESCRIPTION_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({
            "title": title.strip(),
            "description": description.strip() or "No description provided.",
        })

        # Validate length via Pydantic (reuses the schema contract)
        validated = ImprovedDescription(improved_description=raw.strip())
        return validated.improved_description

    except ValidationError:
        raise ValueError("AI returned a response that was too short. Please try again.")
    except Exception as exc:
        raise Exception(_friendly_error(exc))


# ── 2.  Suggest Priority ────────────────────────────────────────────

def suggest_priority(
    title: str,
    description: str = "",
    deadline: Optional[object] = None,
) -> dict:
    """
    Return ``{"priority": "HIGH|MEDIUM|LOW", "reason": "..."}``.

    Chain: SUGGEST_PRIORITY_PROMPT | llm | StrOutputParser → json.loads → Pydantic
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty.")

    deadline_str = (
        deadline.strftime("%Y-%m-%d %H:%M") if deadline else "No deadline"
    )

    try:
        llm = get_llm()
        chain = SUGGEST_PRIORITY_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({
            "title": title.strip(),
            "description": description.strip() or "No description provided.",
            "deadline": deadline_str,
        })

        parsed = _safe_parse_json(raw)
        validated = PrioritySuggestion(**parsed)
        return validated.model_dump()

    except (json.JSONDecodeError, ValidationError):
        raise Exception("Failed to parse AI response. Please try again.")
    except Exception as exc:
        raise Exception(_friendly_error(exc))


# ── 3.  Generate Subtasks (v2 — with time estimates) ─────────────────

def generate_subtasks(
    title: str,
    description: str = "",
    count: int = 5,
) -> list[dict]:
    """
    Return a list of dicts: ``[{"title": "...", "time_estimate_minutes": 30}, ...]``.

    Chain: GENERATE_SUBTASKS_PROMPT | llm | StrOutputParser → json.loads → Pydantic
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty.")

    count = max(3, min(10, int(count)))

    try:
        llm = get_llm()
        chain = GENERATE_SUBTASKS_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({
            "title": title.strip(),
            "description": description.strip() or "No description provided.",
            "count": str(count),
        })

        parsed = _safe_parse_json(raw)
        validated = SubtaskList(**parsed)

        # Return as plain dicts, capped at requested count
        return [item.model_dump() for item in validated.subtasks[:count]]

    except (json.JSONDecodeError, ValidationError):
        raise Exception("Failed to parse AI response. Please try again.")
    except Exception as exc:
        raise Exception(_friendly_error(exc))


# ── 4.  Productivity Coach ──────────────────────────────────────────

def productivity_coach(stats: dict) -> dict:
    """
    Analyze user's task statistics and return personalized coaching.

    Returns ``{"score": 75, "summary": "...", "tips": [{"category": "...", "tip": "...", "reasoning": "..."}]}``.

    Chain: PRODUCTIVITY_COACH_PROMPT | llm | StrOutputParser → json.loads → Pydantic
    """
    try:
        llm = get_llm()
        chain = PRODUCTIVITY_COACH_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({
            "total_tasks": str(stats.get("total_tasks", 0)),
            "completed_tasks": str(stats.get("completed_tasks", 0)),
            "pending_tasks": str(stats.get("pending_tasks", 0)),
            "in_progress_tasks": str(stats.get("in_progress_tasks", 0)),
            "overdue_tasks": str(stats.get("overdue_tasks", 0)),
            "completion_rate": str(stats.get("completion_rate", 0)),
            "avg_completion_days": str(stats.get("avg_completion_days", "N/A")),
            "created_this_week": str(stats.get("created_this_week", 0)),
            "completed_this_week": str(stats.get("completed_this_week", 0)),
            "high_priority": str(stats.get("high_priority", 0)),
            "medium_priority": str(stats.get("medium_priority", 0)),
            "low_priority": str(stats.get("low_priority", 0)),
        })

        parsed = _safe_parse_json(raw)
        validated = ProductivityCoachResponse(**parsed)
        return validated.model_dump()

    except (json.JSONDecodeError, ValidationError):
        raise Exception("Failed to parse AI coaching response. Please try again.")
    except Exception as exc:
        raise Exception(_friendly_error(exc))


# ── 5.  Smart Search ────────────────────────────────────────────────

def smart_search(query: str) -> dict:
    """
    Interpret a natural language search query into structured filters.

    Returns ``{"keywords": [...], "status": [...], "priority": [...], "overdue": bool, "sort_by": "..."}``.

    Chain: SMART_SEARCH_PROMPT | llm | StrOutputParser → json.loads → Pydantic
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    try:
        llm = get_llm()
        chain = SMART_SEARCH_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({"query": query.strip()})

        parsed = _safe_parse_json(raw)
        validated = SearchFilter(**parsed)
        return validated.model_dump()

    except (json.JSONDecodeError, ValidationError):
        raise Exception("Failed to parse search query. Please try again.")
    except Exception as exc:
        raise Exception(_friendly_error(exc))
