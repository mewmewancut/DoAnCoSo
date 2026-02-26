# DoAnCoSo — TodoList tích hợp AI

Một ứng dụng TodoList phát triển bằng Django, tích hợp các tính năng AI (LangChain LCEL + Pydantic v2) để tự động cải thiện mô tả task, đề xuất độ ưu tiên, chia nhỏ task thành subtasks, coaching năng suất và tìm kiếm thông minh.

## Mục tiêu

- Xây dựng hệ thống quản lý công việc (tasks) cơ bản: CRUD, phân loại, lọc, sắp xếp và phân trang.
- Tích hợp các tính năng AI hỗ trợ người dùng: cải thiện mô tả, đề xuất priority, chia nhỏ task, coaching năng suất, smart search.
- Cung cấp giao diện dashboard, calendar và thống kê tiến độ.

## Công nghệ

- Backend: Python 3.14, Django 5/6
- AI: LangChain LCEL + Pydantic v2 (OpenAI / Google Gemini / Groq — switchable)
- Secrets: python-decouple (`.env`)
- Frontend: Bootstrap 5, FullCalendar.js
- DB: SQLite (dev), có thể đổi sang PostgreSQL cho production

## Cấu trúc dự án (chính)

- `todolist/` — Django project root
- `todolist/ai_assistant/` — AI app (LCEL chains, Pydantic schemas, prompt templates, LLM client factory)
- `todolist/tasks/` — App quản lý tasks, views, templates, APIs, services
- `todolist/accounts/` — App authentication (signup, activation, reset password)

## Cài đặt & Chạy (local)

1. Tạo virtualenv và cài dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Tạo file `.env` từ `.env.example` và cấu hình API keys:

```
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-key-here
SECRET_KEY=your-django-secret-key
```

3. Migrate và tạo superuser:

```bash
cd todolist
python manage.py migrate
python manage.py createsuperuser
```

4. Chạy server:

```bash
python manage.py runserver
```

## API endpoints (AI)

| Method | Endpoint                          | Mô tả                                            |
| ------ | --------------------------------- | ------------------------------------------------ |
| POST   | `/tasks/api/improve-description/` | Cải thiện mô tả task                             |
| POST   | `/tasks/api/suggest-priority/`    | Đề xuất priority + lý do                         |
| POST   | `/tasks/api/generate-subtasks/`   | Chia nhỏ task thành subtasks (kèm time estimate) |
| POST   | `/tasks/api/productivity-coach/`  | Phân tích năng suất + lời khuyên cá nhân         |
| POST   | `/tasks/api/smart-search/`        | Tìm kiếm task bằng ngôn ngữ tự nhiên             |
| GET    | `/tasks/api/ai-history/`          | Lịch sử sử dụng AI                               |

> Các endpoint yêu cầu người dùng đăng nhập (login required).

## Models chính

- `Task` — `id (UUID), user (FK), title, description, deadline, priority, status, created_at, updated_at, completed_at`
- `SubTask` — `id (UUID), task (FK), title, description, status, order, completed_at`
- `AISuggestion` — lưu lịch sử các gợi ý AI (description, priority, subtasks, coach, search)

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
