"""
AI Prompt Templates for TodoList Application
"""

from langchain_core.prompts import PromptTemplate


# ============================================
# 1. IMPROVE TASK DESCRIPTION
# ============================================
IMPROVE_DESCRIPTION_TEMPLATE = """You are an intelligent task management assistant.

Your job is to improve the task description to make it clearer, more detailed, and actionable.

Current Task:
Title: {title}
Description: {description}

Rewrite the task description with this structure:
1. Objective: Clarify the goal to be achieved
2. Steps: List specific steps to complete (if needed)
3. Expected Result: Describe the output/result clearly

IMPORTANT RULES:
- Return ONLY the improved description, no explanations
- RESPOND IN THE SAME LANGUAGE AS THE INPUT
- If the title/description is in Vietnamese, respond in Vietnamese
- If the title/description is in English, respond in English
- Keep the response format clean without markdown headers
"""

improve_description_prompt = PromptTemplate(
    input_variables=["title", "description"],
    template=IMPROVE_DESCRIPTION_TEMPLATE
)


# ============================================
# 2. SUGGEST PRIORITY
# ============================================
SUGGEST_PRIORITY_TEMPLATE = """You are an intelligent task management assistant.

Analyze the following task and suggest a priority level:

Title: {title}
Description: {description}
Deadline: {deadline}

Priority levels:
- HIGH: Important and urgent, needs immediate attention
- MEDIUM: Important but not very urgent
- LOW: Can be done later

Return JSON with this format:
{{
    "priority": "HIGH|MEDIUM|LOW",
    "reason": "Brief explanation (1-2 sentences)"
}}

IMPORTANT RULES:
- Return ONLY valid JSON, no extra text
- The "reason" MUST BE IN THE SAME LANGUAGE AS THE INPUT
- If title/description is Vietnamese, write reason in Vietnamese
- If title/description is English, write reason in English
"""

suggest_priority_prompt = PromptTemplate(
    input_variables=["title", "description", "deadline"],
    template=SUGGEST_PRIORITY_TEMPLATE
)


# ============================================
# 3. GENERATE SUBTASKS
# ============================================
GENERATE_SUBTASKS_TEMPLATE = """You are an intelligent task management assistant.

Break down the following complex task into specific, actionable subtasks:

Title: {title}
Description: {description}

Requirements:
- Generate exactly {count} subtasks
- Each subtask must be a concrete, completable step
- Arrange in logical order (step 1 -> 2 -> 3...)
- Each subtask should be concise (1 sentence)

Return JSON format:
{{
    "subtasks": [
        "Subtask 1",
        "Subtask 2",
        ...
    ]
}}

IMPORTANT RULES:
- Return ONLY valid JSON, no extra text
- Generate EXACTLY {count} subtasks
- Subtasks MUST BE IN THE SAME LANGUAGE AS THE INPUT
- If title/description is Vietnamese, write subtasks in Vietnamese
- If title/description is English, write subtasks in English
"""

generate_subtasks_prompt = PromptTemplate(
    input_variables=["title", "description"],
    template=GENERATE_SUBTASKS_TEMPLATE.replace("{count}", "5")  # Default count
)


def get_generate_subtasks_prompt(count=5):
    """
    Get the subtasks prompt template with dynamic count
    
    Args:
        count (int): Number of subtasks to generate (3-10)
    
    Returns:
        PromptTemplate: Prompt template with count value
    """
    count = max(3, min(10, int(count)))
    template = GENERATE_SUBTASKS_TEMPLATE.replace("{count}", str(count))
    return PromptTemplate(
        input_variables=["title", "description"],
        template=template
    )


# ============================================
# 4. DAILY/WEEKLY PLANNING (Sẽ làm sau)
# ============================================
DAILY_PLANNING_TEMPLATE = """Bạn là một trợ lý lập kế hoạch công việc thông minh.

Hãy tạo kế hoạch công việc cho ngày {date}.

Danh sách tasks cần làm:
{tasks_list}

Thời gian làm việc: {work_hours} giờ

Hãy:
1. Sắp xếp thứ tự ưu tiên các tasks
2. Phân bổ thời gian hợp lý
3. Đề xuất task nào nên làm trước

Trả về JSON format với kế hoạch chi tiết.
"""

# TODO: Sẽ implement sau khi có đủ dữ liệu tasks
