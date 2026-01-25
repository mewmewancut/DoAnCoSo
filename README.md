# DoAnCoSo — TodoList tích hợp AI

Một ứng dụng TodoList phát triển bằng Django, tích hợp các tính năng AI (OpenAI/LangChain) để tự động cải thiện mô tả task, đề xuất độ ưu tiên và tách task phức tạp thành subtasks.

## Mục tiêu

- Xây dựng hệ thống quản lý công việc (tasks) cơ bản: CRUD, phân loại, lọc, sắp xếp và phân trang.
- Tích hợp các tính năng AI hỗ trợ người dùng: cải thiện mô tả, đề xuất priority, chia nhỏ task.
- Cung cấp giao diện dashboard, calendar và thống kê tiến độ.

## Công nghệ

- Backend: Python 3.x, Django 4/5
- AI: LangChain + OpenAI (có thể chuyển sang Google Gemini/Groq)
- Frontend: Bootstrap 5, FullCalendar.js
- DB: SQLite (dev), có thể đổi sang PostgreSQL cho production

## Cấu trúc dự án (chính)

- `todolist/` - Django project
- `tasks/` - App quản lý tasks, views, templates, APIs
- `accounts/` - App authentication (signup, activation, reset password)
- `ai_prompts.py` - Prompt templates cho AI
- `ai_utils.py` - Wrapper gọi LLM và helper functions
- `test_ai.py` - Script kiểm thử các hàm AI

## Cài đặt & Chạy (local)

1. Tạo virtualenv và cài dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Tạo file `.env` từ `.env.example` và đặt `OPENAI_API_KEY`:

```
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
```

3. Migrate và tạo superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Chạy server:

```bash
python manage.py runserver
```

## API endpoints (AI)

- `POST /tasks/api/improve-description/` — Body: `{ "title": "...", "description": "..." }` → Trả về mô tả đã cải thiện
- `POST /tasks/api/suggest-priority/` — Body: `{ "title": "...", "description": "...", "deadline": "ISO" }` → Trả về priority + lý do
- (sắp tới) `POST /tasks/api/generate-subtasks/` — Body: `{ "title": "...", "description": "..." }` → Trả về list subtasks

> Các endpoint yêu cầu người dùng đăng nhập (login required). Thử nghiệm có thể dùng `curl` hoặc fetch từ frontend.

## Models chính

- `Task` — `id (UUID), user (FK), title, description, deadline, priority, status, created_at, updated_at, completed_at`
- `AISuggestion` — lưu lịch sử các gợi ý AI (loại suggestion, input, output, user, timestamp)

## Hướng dẫn test AI (local)

Chạy script test nhanh:

```bash
python todolist/test_ai.py
```

Lưu ý: Cần `OPENAI_API_KEY` trong `.env` để các test gọi LLM.

## Contributor & Liên hệ

- Sơn: mewmewancut <23010313@st.phenikaa-uni.edu.vn> — Backend core & Authentication
- Dũng: aduoke33 <23010329@st.phenikaa-uni.edu.vn> — AI Integration & Logic
- Minh: doanquangminh14 — Frontend & UI/UX

## Commit / Branching

- Main branch: code ổn định
- Các feature branch: `feature/<name>` hoặc `user/<name>/feature`

## Ghi chú triển khai

- Đối với production: chuyển SQLite → PostgreSQL, cấu hình `ALLOWED_HOSTS`, thiết lập SMTP thực tế, và bảo mật API keys (Secrets manager).

---

_README tự động cập nhật bởi trợ lý phát triển dự án (dành cho đồ án)._
