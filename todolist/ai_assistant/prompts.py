"""
Prompt templates cho AI Assistant.

Triết lý thiết kế
──────────────────
Mỗi prompt tuân theo cấu trúc **Vai trò -> Ngữ cảnh -> Nhiệm vụ -> Định dạng -> Quy tắc**:

1. **Vai trò**: Cho LLM biết *nó là ai* (chuyên gia quản lý công việc).
2. **Ngữ cảnh**: Đưa vào dữ liệu người dùng (tiêu đề, mô tả, hạn chót …).
3. **Nhiệm vụ**: Mô tả chính xác đầu ra mong muốn.
4. **Định dạng**: Với chuỗi có cấu trúc, định dạng do Pydantic kiểm soát,
                  nên chỉ yêu cầu "JSON khớp với schema".
                  Với chuỗi văn bản tự do, mô tả cấu trúc mong đợi.
5. **Quy tắc**: Ràng buộc cứng (ngôn ngữ, giới hạn độ dài, v.v.).

Tại sao LCEL?
─────────────
Sử dụng LangChain Expression Language (prompt | llm | parser) để xây dựng
chuỗi một cách khai báo.  Mỗi prompt là ``ChatPromptTemplate`` —
parser được gắn trong ``chains.py``, không phải ở đây.
"""

from langchain_core.prompts import ChatPromptTemplate


# -- 1. Cải thiện mô tả (đầu ra văn bản tự do) -----------------------
IMPROVE_DESCRIPTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Bạn là chuyên gia trợ lý quản lý công việc. "
     "Mục tiêu của bạn là viết lại mô tả công việc sao cho rõ ràng, "
     "chi tiết và có thể thực hiện ngay. "
     "LUÔN LUÔN trả lời bằng tiếng Việt."),
    ("human",
     "Tiêu đề công việc: {title}\n"
     "Mô tả hiện tại: {description}\n\n"
     "Viết lại mô tả theo cấu trúc sau:\n"
     "1. **Mục tiêu** – cần đạt được điều gì.\n"
     "2. **Các bước** – hành động cụ thể để hoàn thành.\n"
     "3. **Kết quả mong đợi** – làm sao biết công việc đã hoàn thành.\n\n"
     "QUY TẮC ĐỊNH DẠNG:\n"
     "- Chỉ trả về mô tả đã cải thiện — không bình luận thêm.\n"
     "- LUÔN trả lời bằng tiếng Việt.\n"
     "- Ngắn gọn nhưng đầy đủ (100-300 từ).\n"
     "- KHÔNG thêm khoảng trắng ở đầu dòng.\n"
     "- Đánh số tuần tự: 1. 2. 3. (không lặp lại số 1).\n"
     "- Dùng **text** cho chữ in đậm."),
])


# -- 2. Gợi ý mức ưu tiên (đầu ra JSON có cấu trúc) -----------------
SUGGEST_PRIORITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Bạn là chuyên gia trợ lý quản lý công việc, đánh giá mức độ "
     "khẩn cấp và quan trọng để đề xuất mức ưu tiên. "
     "LUÔN LUÔN trả lời bằng tiếng Việt."),
    ("human",
     "Tiêu đề công việc: {title}\n"
     "Mô tả: {description}\n"
     "Hạn chót: {deadline}\n\n"
     "Phân loại mức ưu tiên: HIGH, MEDIUM hoặc LOW.\n"
     "HIGH = quan trọng VÀ khẩn cấp (hạn chót gấp, tác động lớn).\n"
     "MEDIUM = quan trọng nhưng chưa cần ngay.\n"
     "LOW = không bắt buộc, không áp lực thời gian.\n\n"
     "Trả về JSON:\n"
     '{{"priority": "HIGH|MEDIUM|LOW", "reason": "giải thích 1-2 câu bằng tiếng Việt"}}\n\n'
     "QUY TẮC:\n"
     "- Chỉ trả về JSON hợp lệ, không thêm văn bản.\n"
     "- Viết lý do bằng tiếng Việt."),
])


# -- 3. Tạo công việc con v2 (JSON có cấu trúc + ước tính thời gian) -
#    {count} được truyền vào tại thời điểm xây dựng chuỗi qua partial_variables.
GENERATE_SUBTASKS_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Bạn là chuyên gia trợ lý quản lý công việc, chuyên chia nhỏ "
     "các công việc phức tạp thành các bước nhỏ có thể hoàn thành "
     "với ước tính thời gian thực tế. "
     "LUÔN LUÔN trả lời bằng tiếng Việt."),
    ("human",
     "Tiêu đề công việc: {title}\n"
     "Mô tả: {description}\n\n"
     "Chia công việc thành đúng {count} công việc con.\n"
     "Với mỗi công việc con, cung cấp:\n"
     '  - "title": câu hành động ngắn gọn bằng tiếng Việt\n'
     '  - "time_estimate_minutes": ước tính số phút (5-480)\n\n'
     "Trả về JSON:\n"
     '{{"subtasks": [{{"title": "...", "time_estimate_minutes": 30}}, ...]}}\n\n'
     "QUY TẮC:\n"
     "- Chỉ trả về JSON hợp lệ.\n"
     "- Sắp xếp công việc con theo thứ tự logic (bước 1 -> 2 -> ...).\n"
     "- LUÔN viết bằng tiếng Việt."),
])


# -- 4. Huấn luyện năng suất (đầu ra JSON có cấu trúc) ---------------
PRODUCTIVITY_COACH_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Bạn là chuyên gia huấn luyện năng suất, phân tích mô hình quản lý "
     "công việc của người dùng và đưa ra lời khuyên cá nhân hóa, "
     "có thể thực hiện được. Bạn phải khích lệ nhưng trung thực. "
     "LUÔN LUÔN trả lời bằng tiếng Việt."),
    ("human",
     "Đây là dữ liệu quản lý công việc của tôi:\n\n"
     "Tổng số công việc: {total_tasks}\n"
     "Đã hoàn thành: {completed_tasks}\n"
     "Đang chờ: {pending_tasks}\n"
     "Đang thực hiện: {in_progress_tasks}\n"
     "Quá hạn: {overdue_tasks}\n"
     "Tỷ lệ hoàn thành: {completion_rate}%\n"
     "Thời gian hoàn thành trung bình: {avg_completion_days} ngày\n"
     "Công việc tạo tuần này: {created_this_week}\n"
     "Công việc hoàn thành tuần này: {completed_this_week}\n"
     "Phân bổ ưu tiên — Cao: {high_priority}, Trung bình: {medium_priority}, Thấp: {low_priority}\n\n"
     "Dựa trên dữ liệu này, cho tôi điểm năng suất (0-100) và "
     "tối đa 3 lời khuyên cá nhân hóa để cải thiện.\n\n"
     "Trả về JSON:\n"
     '{{"score": 75, "summary": "...", "tips": [{{"category": "TIME_MANAGEMENT|PRIORITIZATION|FOCUS|PLANNING|MOTIVATION", "tip": "...", "reasoning": "..."}}]}}\n\n'
     "QUY TẮC:\n"
     "- Chỉ trả về JSON hợp lệ, không thêm văn bản.\n"
     "- Điểm số phải phản ánh dữ liệu một cách khách quan.\n"
     "- Lời khuyên phải cụ thể theo mô hình của người dùng, không chung chung.\n"
     "- LUÔN viết summary, tip và reasoning bằng tiếng Việt."),
])


# -- 5. Tìm kiếm thông minh (đầu ra JSON có cấu trúc) ----------------
SMART_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Bạn là trình thông dịch truy vấn tìm kiếm cho ứng dụng quản lý công việc. "
     "Công việc của bạn là chuyển đổi truy vấn ngôn ngữ tự nhiên thành "
     "bộ lọc tìm kiếm có cấu trúc dạng JSON. Ứng dụng có các công việc với: title, description, "
     "status (pending/in_progress/completed/cancelled), "
     "priority (high/medium/low), và deadline. "
     "Người dùng sẽ nhập truy vấn bằng tiếng Việt. "
     "LUÔN LUÔN trả lời bằng JSON hợp lệ."),
    ("human",
     "Chuyển đổi truy vấn tìm kiếm này thành bộ lọc có cấu trúc:\n\n"
     "Truy vấn: \"{query}\"\n\n"
     "Trả về ĐÚNG định dạng JSON này (không thêm text khác):\n"
     '{{\n'
     '  "keywords": ["tu1", "tu2"],\n'
     '  "status": [],\n'
     '  "priority": [],\n'
     '  "overdue": false,\n'
     '  "sort_by": "relevance"\n'
     '}}\n\n'
     "QUY TẮC:\n"
     "- CHỈ trả về JSON, KHÔNG thêm giải thích.\n"
     "- Chỉ bao gồm bộ lọc được ngụ ý rõ ràng từ truy vấn.\n"
     "- 'khẩn cấp', 'gấp', 'quan trọng' → priority=[\"high\"]\n"
     "- 'quá hạn', 'trễ', 'muộn' → overdue=true\n"
     "- 'xong', 'hoàn thành', 'đã làm' → status=[\"completed\"]\n"
     "- 'chưa làm', 'chờ', 'mới' → status=[\"pending\"]\n"
     "- 'đang làm' → status=[\"in_progress\"]\n"
     "- Trích xuất từ khóa tìm kiếm thực tế từ nội dung còn lại vào keywords.\n"
     "- sort_by phải là một trong: relevance, deadline, priority, created_at"),
])


# -- 6. Gắn nhãn tự động (đầu ra JSON có cấu trúc) -------------------
AUTO_TAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Bạn là chuyên gia trợ lý quản lý công việc, chuyên phân loại công việc "
     "thành các nhãn ngắn, có thể tái sử dụng. Nhãn giúp người dùng lọc "
     "và nhóm các công việc liên quan. "
     "LUÔN LUÔN trả lời bằng tiếng Việt."),
    ("human",
     "Tiêu đề công việc: {title}\n"
     "Mô tả: {description}\n\n"
     "Gợi ý 1 đến 5 nhãn ngắn (1-2 từ mỗi nhãn) phù hợp nhất để "
     "phân loại công việc này. Chọn từ các danh mục phổ biến như: "
     "cong-viec, ca-nhan, hoc-tap, suc-khoe, tai-chinh, mua-sam, "
     "lap-trinh, thiet-ke, hop, email, nghien-cuu, viet-bai, "
     "ke-hoach, sua-loi, tinh-nang, devops, marketing, v.v.\n"
     "Bạn cũng có thể tạo nhãn mới nếu không có nhãn nào phù hợp.\n\n"
     "Trả về JSON:\n"
     '{{"tags": ["nhan1", "nhan2"]}}\n\n'
     "QUY TẮC:\n"
     "- Chỉ trả về JSON hợp lệ, không thêm văn bản.\n"
     "- Nhãn phải viết thường, phân cách bằng dấu gạch ngang (không dùng dấu cách).\n"
     "- Nhãn ngắn gọn (tối đa 20 ký tự mỗi nhãn).\n"
     "- Cụ thể nhưng không quá hẹp."),
])
