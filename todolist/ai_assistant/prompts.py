"""
Prompt templates for the AI Assistant.

Design Philosophy
─────────────────
Each prompt follows a **Role → Context → Task → Format → Rules** structure:

1. **Role**:   Tell the LLM *who it is* (task-management expert).
2. **Context**: Inject the user's data (title, description, deadline …).
3. **Task**:   Precisely describe the desired output.
4. **Format**: For structured chains the format is enforced by Pydantic,
               so we only ask for "JSON matching the schema".
               For free-text chains we describe the expected structure.
5. **Rules**:  Hard constraints (language matching, length limits, etc.).

Why LCEL?
─────────
We use LangChain Expression Language (prompt | llm | parser) to compose
chains declaratively.  Each prompt is a plain ``ChatPromptTemplate`` —
the parser is attached in ``chains.py``, not here.
"""

from langchain_core.prompts import ChatPromptTemplate


# ── 1. Improve Description (free-text output) ───────────────────────
IMPROVE_DESCRIPTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert task-management assistant. "
     "Your goal is to rewrite a task description so it becomes clear, "
     "detailed, and immediately actionable."),
    ("human",
     "Task title: {title}\n"
     "Current description: {description}\n\n"
     "Rewrite the description using this structure:\n"
     "1. **Objective** – what exactly must be achieved.\n"
     "2. **Steps** – concrete actions to complete the task.\n"
     "3. **Expected Result** – how to know the task is done.\n\n"
     "RULES:\n"
     "- Return ONLY the improved description — no commentary.\n"
     "- Match the language of the input (Vietnamese → Vietnamese, etc.).\n"
     "- Keep it concise but comprehensive (100-300 words)."),
])


# ── 2. Suggest Priority (structured JSON output) ────────────────────
SUGGEST_PRIORITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert task-management assistant that evaluates "
     "urgency and importance to recommend a priority level."),
    ("human",
     "Task title: {title}\n"
     "Description: {description}\n"
     "Deadline: {deadline}\n\n"
     "Classify the priority as HIGH, MEDIUM, or LOW.\n"
     "HIGH = important AND urgent (tight deadline, critical impact).\n"
     "MEDIUM = important but not immediately urgent.\n"
     "LOW = nice-to-have, no time pressure.\n\n"
     "Return JSON:\n"
     '{{"priority": "HIGH|MEDIUM|LOW", "reason": "1-2 sentence explanation"}}\n\n'
     "RULES:\n"
     "- Return ONLY valid JSON, no extra text.\n"
     "- Write the reason in the SAME language as the input."),
])


# ── 3. Generate Subtasks v2 (structured JSON with time estimates) ───
#    {count} is injected at chain-build time via partial_variables.
GENERATE_SUBTASKS_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert task-management assistant that breaks down "
     "complex tasks into small, completable steps with realistic "
     "time estimates."),
    ("human",
     "Task title: {title}\n"
     "Description: {description}\n\n"
     "Break this into exactly {count} subtasks.\n"
     "For each subtask provide:\n"
     '  - "title": a concise action sentence\n'
     '  - "time_estimate_minutes": estimated minutes (5–480)\n\n'
     "Return JSON:\n"
     '{{"subtasks": [{{"title": "...", "time_estimate_minutes": 30}}, ...]}}\n\n'
     "RULES:\n"
     "- Return ONLY valid JSON.\n"
     "- Order subtasks logically (step 1 → 2 → …).\n"
     "- Use the SAME language as the input."),
])
