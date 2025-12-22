# Nghiên cứu tích hợp AI cho TodoList

## So sánh các LLM APIs

### 1. OpenAI (GPT-3.5/GPT-4)
**Ưu điểm:**
- Chất lượng output tốt nhất
- Documentation đầy đủ
- Hỗ trợ tốt với LangChain

**Nhược điểm:**
- Có phí, tốn tiền nếu dùng nhiều
- API key phải trả tiền

**Giá:** ~$0.002/1K tokens (GPT-3.5-turbo)

### 2. Google Gemini
**Ưu điểm:**
- Free tier khá cao
- Tốc độ nhanh
- Tiếng Việt tốt

**Nhược điểm:**
- API còn mới, ít tài liệu hơn
- Rate limit thấp cho free tier

### 3. Groq
**Ưu điểm:**
- SIÊU NHANH (inference speed cao nhất)
- Free tier khá rộng
- Dùng được nhiều models

**Nhược điểm:**
- Rate limit strict
- Chưa phổ biến lắm

## Quyết định: Dùng gì?

**Chọn OpenAI** cho demo và development vì:
- Có free trial $5 credit
- Quality tốt nhất cho các task phức tạp
- Dễ implement nhất

Sau này có thể chuyển sang Gemini để tiết kiệm chi phí.

## Các tính năng AI cần làm

1. **Cải thiện mô tả task** - Độ khó: Dễ
   - Input: Task description ngắn
   - Output: Task description chi tiết, rõ ràng hơn
   
2. **Đề xuất priority** - Độ khó: Trung bình
   - Input: Task info (title, description, deadline)
   - Output: Priority level (High/Medium/Low) + lý do
   
3. **Chia nhỏ task** - Độ khó: Khó
   - Input: Task phức tạp
   - Output: Danh sách subtasks cụ thể
   
4. **Lập kế hoạch** - Độ khó: Khó nhất
   - Input: Danh sách tasks + user schedule
   - Output: Planning theo ngày/tuần

## Cách tích hợp

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7
)

# Ví dụ prompt
prompt = PromptTemplate(
    input_variables=["task_description"],
    template="Improve this task description: {task_description}"
)
```

## Next steps
- [ ] Setup OpenAI API key
- [ ] Test kết nối với API
- [ ] Viết helper functions
- [ ] Tạo prompt templates
