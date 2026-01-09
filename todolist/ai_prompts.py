"""
AI Prompt Templates for TodoList Application
"""

from langchain_core.prompts import PromptTemplate


# ============================================
# 1. IMPROVE TASK DESCRIPTION
# ============================================
IMPROVE_DESCRIPTION_TEMPLATE = """Bạn là một trợ lý quản lý công việc thông minh.

Nhiệm vụ của bạn là cải thiện mô tả công việc (task) để nó rõ ràng, chi tiết và dễ thực hiện hơn.

Task hiện tại:
Tiêu đề: {title}
Mô tả: {description}

Hãy viết lại mô tả task theo cấu trúc sau:
1. Mục tiêu: Làm rõ mục tiêu cần đạt được
2. Các bước thực hiện: Liệt kê các bước cụ thể (nếu cần)
3. Kết quả mong đợi: Mô tả rõ output/kết quả

Chỉ trả về mô tả đã cải thiện, không cần giải thích thêm.
Giữ nguyên ngôn ngữ của task gốc (Tiếng Việt hoặc English).
"""

improve_description_prompt = PromptTemplate(
    input_variables=["title", "description"],
    template=IMPROVE_DESCRIPTION_TEMPLATE
)


# ============================================
# 2. SUGGEST PRIORITY
# ============================================
SUGGEST_PRIORITY_TEMPLATE = """Bạn là một trợ lý quản lý công việc thông minh.

Hãy phân tích task sau và đề xuất mức độ ưu tiên (priority):

Tiêu đề: {title}
Mô tả: {description}
Deadline: {deadline}

Các mức độ ưu tiên:
- HIGH: Công việc quan trọng và khẩn cấp, cần làm ngay
- MEDIUM: Công việc quan trọng nhưng không quá gấp
- LOW: Công việc có thể làm sau

Hãy trả về JSON với format:
{{
    "priority": "HIGH|MEDIUM|LOW",
    "reason": "Giải thích ngắn gọn lý do (1-2 câu)"
}}

Chỉ trả về JSON, không thêm text nào khác.
"""

suggest_priority_prompt = PromptTemplate(
    input_variables=["title", "description", "deadline"],
    template=SUGGEST_PRIORITY_TEMPLATE
)


# ============================================
# 3. GENERATE SUBTASKS
# ============================================
GENERATE_SUBTASKS_TEMPLATE = """Bạn là một trợ lý quản lý công việc thông minh.

Hãy chia nhỏ task phức tạp sau thành các subtasks cụ thể, dễ thực hiện:

Tiêu đề: {title}
Mô tả: {description}

Yêu cầu:
- Mỗi subtask phải là một bước cụ thể, có thể hoàn thành
- Sắp xếp theo thứ tự logic (bước 1 -> 2 -> 3...)
- Tối đa 5-8 subtasks
- Mỗi subtask nên ngắn gọn (1 câu)

Trả về JSON format:
{{
    "subtasks": [
        "Subtask 1",
        "Subtask 2",
        ...
    ]
}}

Chỉ trả về JSON, không thêm text nào khác.
"""

generate_subtasks_prompt = PromptTemplate(
    input_variables=["title", "description"],
    template=GENERATE_SUBTASKS_TEMPLATE
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
