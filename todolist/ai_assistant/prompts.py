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


# ── 4. Productivity Coach (structured JSON output) ──────────────────
PRODUCTIVITY_COACH_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert productivity coach who analyzes a user's task "
     "management patterns and provides personalized, actionable advice. "
     "You must be encouraging but honest."),
    ("human",
     "Here is my task management data:\n\n"
     "Total tasks: {total_tasks}\n"
     "Completed: {completed_tasks}\n"
     "Pending: {pending_tasks}\n"
     "In Progress: {in_progress_tasks}\n"
     "Overdue: {overdue_tasks}\n"
     "Completion rate: {completion_rate}%\n"
     "Average completion time: {avg_completion_days} days\n"
     "Tasks created this week: {created_this_week}\n"
     "Tasks completed this week: {completed_this_week}\n"
     "Priority breakdown — High: {high_priority}, Medium: {medium_priority}, Low: {low_priority}\n\n"
     "Based on this data, give me a productivity score (0-100) and "
     "up to 3 personalized tips to improve.\n\n"
     "Return JSON:\n"
     '{{"score": 75, "summary": "...", "tips": [{{"category": "TIME_MANAGEMENT|PRIORITIZATION|FOCUS|PLANNING|MOTIVATION", "tip": "...", "reasoning": "..."}}]}}\n\n'
     "RULES:\n"
     "- Return ONLY valid JSON, no extra text.\n"
     "- Score must reflect the data objectively.\n"
     "- Tips must be specific to the user's patterns, not generic.\n"
     "- Use the SAME language as any task titles if provided, otherwise English."),
])


# ── 5. Smart Search (structured JSON output) ────────────────────────
SMART_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a search query interpreter for a task management app. "
     "Your job is to convert natural language queries into structured "
     "search filters. The app has tasks with: title, description, "
     "status (pending/in_progress/completed/cancelled), "
     "priority (high/medium/low), and deadline."),
    ("human",
     "Convert this search query into structured filters:\n\n"
     "Query: \"{query}\"\n\n"
     "Return JSON:\n"
     '{{"keywords": ["word1", "word2"], "status": ["pending", "in_progress"], '
     '"priority": ["high"], "overdue": false, "sort_by": "relevance|deadline|priority|created_at"}}\n\n'
     "RULES:\n"
     "- Return ONLY valid JSON.\n"
     "- Only include filters that are clearly implied by the query.\n"
     "- If the query mentions 'urgent' or 'important', map to priority=['high'].\n"
     "- If the query mentions 'overdue' or 'late', set overdue=true.\n"
     "- If the query mentions 'done' or 'finished', map to status=['completed'].\n"
     "- If the query mentions 'not started' or 'todo', map to status=['pending'].\n"
     "- Extract actual search keywords from the remaining content."),
])


# ── 6. Auto-Tag (structured JSON output) ────────────────────────────
AUTO_TAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert task-management assistant that categorises tasks "
     "into short, reusable tags. Tags help users filter and group related "
     "tasks."),
    ("human",
     "Task title: {title}\n"
     "Description: {description}\n\n"
     "Suggest 1 to 5 short tags (1-2 words each) that best categorise "
     "this task.  Choose from common categories like: work, personal, "
     "study, health, finance, shopping, coding, design, meeting, email, "
     "research, writing, planning, bug-fix, feature, devops, marketing, etc.\n"
     "You may also invent new tags if none of the above fit.\n\n"
     "Return JSON:\n"
     '{{"tags": ["tag1", "tag2"]}}\n\n'
     "RULES:\n"
     "- Return ONLY valid JSON, no extra text.\n"
     "- Tags must be lowercase, hyphen-separated (no spaces).\n"
     "- Keep tags concise (max 20 characters each).\n"
     "- Be specific but not overly narrow."),
])
