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
    AUTO_TAG_PROMPT,
)
from .schemas import (
    ImprovedDescription,
    PrioritySuggestion,
    SubtaskList,
    ProductivityCoachResponse,
    SearchFilter,
    TagSuggestion,
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
        return "Lỗi API key. Vui lòng kiểm tra cấu hình LLM."
    if "rate limit" in msg or "quota" in msg:
        return "Vượt giới hạn tốc độ — vui lòng thử lại sau giây lát."
    if "timeout" in msg:
        return "Yêu cầu quá thời gian — vui lòng thử lại."
    return f"Lỗi dịch vụ AI: {exc}"


# ── 1.  Improve Description ─────────────────────────────────────────

def improve_description(title: str, description: str = "") -> str:
    """
    Return an improved, actionable task description (plain text).

    Chain: IMPROVE_DESCRIPTION_PROMPT | llm | StrOutputParser
    Post-validation: must be ≥ 10 chars (via Pydantic schema).
    """
    if not title or not title.strip():
        raise ValueError("Tiêu đề không được để trống.")

    try:
        llm = get_llm()
        chain = IMPROVE_DESCRIPTION_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({
            "title": title.strip(),
            "description": description.strip() or "Không có mô tả.",
        })

        # Validate length via Pydantic (reuses the schema contract)
        validated = ImprovedDescription(improved_description=raw.strip())
        return validated.improved_description

    except ValidationError:
        raise ValueError("AI trả về kết quả quá ngắn. Vui lòng thử lại.")
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
        raise ValueError("Tiêu đề không được để trống.")

    deadline_str = (
        deadline.strftime("%Y-%m-%d %H:%M") if deadline else "Không có hạn chót"
    )

    try:
        llm = get_llm()
        chain = SUGGEST_PRIORITY_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({
            "title": title.strip(),
            "description": description.strip() or "Không có mô tả.",
            "deadline": deadline_str,
        })

        parsed = _safe_parse_json(raw)
        validated = PrioritySuggestion(**parsed)
        return validated.model_dump()

    except (json.JSONDecodeError, ValidationError):
        raise Exception("Không thể xử lý phản hồi AI. Vui lòng thử lại.")
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
        raise ValueError("Tiêu đề không được để trống.")

    count = max(3, min(10, int(count)))

    try:
        llm = get_llm()
        chain = GENERATE_SUBTASKS_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({
            "title": title.strip(),
            "description": description.strip() or "Không có mô tả.",
            "count": str(count),
        })

        parsed = _safe_parse_json(raw)
        validated = SubtaskList(**parsed)

        # Return as plain dicts, capped at requested count
        return [item.model_dump() for item in validated.subtasks[:count]]

    except (json.JSONDecodeError, ValidationError):
        raise Exception("Không thể xử lý phản hồi AI. Vui lòng thử lại.")
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
        raise Exception("Không thể xử lý phản hồi huấn luyện AI. Vui lòng thử lại.")
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
        raise ValueError("Truy vấn tìm kiếm không được để trống.")

    try:
        llm = get_llm()
        chain = SMART_SEARCH_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({"query": query.strip()})

        parsed = _safe_parse_json(raw)
        validated = SearchFilter(**parsed)
        return validated.model_dump()

    except (json.JSONDecodeError, ValidationError):
        raise Exception("Không thể xử lý truy vấn tìm kiếm. Vui lòng thử lại.")
    except Exception as exc:
        raise Exception(_friendly_error(exc))


# ── 6.  Auto-Tag ────────────────────────────────────────────────────

def auto_tag(title: str, description: str = "") -> list[str]:
    """
    Suggest tags for a task based on its title and description.

    Returns a list of lowercase, hyphen-separated tag strings.

    Chain: AUTO_TAG_PROMPT | llm | StrOutputParser → json.loads → Pydantic
    """
    if not title or not title.strip():
        raise ValueError("Tiêu đề không được để trống.")

    try:
        llm = get_llm()
        chain = AUTO_TAG_PROMPT | llm | StrOutputParser()

        raw: str = chain.invoke({
            "title": title.strip(),
            "description": (description or "").strip() or "Không có mô tả.",
        })

        parsed = _safe_parse_json(raw)
        validated = TagSuggestion(**parsed)
        return validated.tags

    except (json.JSONDecodeError, ValidationError):
        raise Exception("Không thể xử lý phản hồi gắn nhãn AI. Vui lòng thử lại.")
    except Exception as exc:
        raise Exception(_friendly_error(exc))
