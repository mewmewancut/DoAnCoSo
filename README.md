# DoAnCoSo — TodoList tích hợp AI

Một ứng dụng TodoList phát triển bằng Django, tích hợp các tính năng AI (LangChain LCEL + Pydantic v2) để tự động cải thiện mô tả task, đề xuất độ ưu tiên, chia nhỏ task thành subtasks, coaching năng suất và tìm kiếm thông minh.

## Mục tiêu

- Xây dựng hệ thống quản lý công việc (tasks) cơ bản: CRUD, phân loại, lọc, sắp xếp và phân trang.
- Tích hợp các tính năng AI hỗ trợ người dùng: cải thiện mô tả, đề xuất priority, chia nhỏ task, coaching năng suất, smart search.
- Cung cấp giao diện dashboard, calendar và thống kê tiến độ.

## Sơ đồ kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client (Browser)                        │
│              Bootstrap 5 · FullCalendar.js · Fetch API          │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP
┌──────────────────────────────▼──────────────────────────────────┐
│                        Django 6.0 (WSGI)                        │
│                                                                 │
│  ┌───────────┐  ┌───────────┐  ┌────────────────┐              │
│  │ accounts  │  │   tasks   │  │  ai_assistant   │              │
│  │           │  │           │  │                 │              │
│  │ • Auth    │  │ • CRUD    │  │ • LLM Client    │              │
│  │ • Profile │  │ • SubTask │  │ • LCEL Chains   │              │
│  │ • Reset   │  │ • Calendar│  │ • Pydantic v2   │              │
│  │           │  │ • PDF     │  │ • Prompt Templ. │              │
│  └─────┬─────┘  └─────┬─────┘  └───────┬────────┘              │
│        │              │                 │                        │
│  ┌─────▼──────────────▼─────┐  ┌───────▼────────┐              │
│  │   Service Layer          │  │  LLM Providers  │              │
│  │ (business logic, N+1 fix)│  │ Gemini / Groq / │              │
│  └─────────────┬────────────┘  │    OpenAI       │              │
│                │               └────────────────┘               │
│  ┌─────────────▼────────────┐                                   │
│  │   SQLite (dev)           │                                   │
│  │   PostgreSQL (prod)      │                                   │
│  └──────────────────────────┘                                   │
│                                                                 │
│  External: Cloudinary (avatar) · SMTP (email activation)        │
└─────────────────────────────────────────────────────────────────┘
```

## Công nghệ

| Layer    | Công nghệ                                             |
| -------- | ----------------------------------------------------- |
| Backend  | Python 3.14, Django 6.0.1                             |
| AI       | LangChain LCEL + Pydantic v2 (Gemini / Groq / OpenAI) |
| Frontend | Bootstrap 5, Bootstrap Icons, FullCalendar.js         |
| Database | SQLite (dev), PostgreSQL (prod)                       |
| Storage  | Cloudinary (avatar images)                            |
| Secrets  | python-decouple (`.env`)                              |
| PDF      | weasyprint                                            |
| Testing  | Django TestCase — 87 unit tests                       |

## Cấu trúc dự án (chính)

```
DoAnCoSo/
├── requirements.txt
├── todolist/                  # Django project root
│   ├── manage.py
│   ├── todolist/              # Project config (settings, urls, wsgi)
│   ├── accounts/              # Authentication app
│   │   ├── models.py          #   Custom User (UUID pk, Cloudinary avatar)
│   │   ├── views.py           #   Register, login, profile, password reset
│   │   ├── services/          #   Business logic layer
│   │   └── templates/accounts/
│   ├── tasks/                 # Task management app
│   │   ├── models.py          #   Task, SubTask, Tag, AISuggestion
│   │   ├── views.py           #   CRUD, dashboard, calendar, PDF download
│   │   ├── ai_views.py        #   AI API endpoints
│   │   ├── forms.py           #   TaskForm with deadline validation
│   │   ├── services/          #   TaskService, SubtaskService, CalendarService...
│   │   └── templates/tasks/
│   ├── ai_assistant/          # AI integration app
│   │   ├── llm_client.py      #   LLM factory (Gemini/Groq/OpenAI)
│   │   ├── chains.py          #   LCEL chains
│   │   ├── schemas.py         #   Pydantic v2 output schemas
│   │   └── prompts.py         #   Prompt templates
│   ├── templates/             # Shared templates (base, home, 404, 500)
│   └── static/                # Static assets
```

## Screenshots

| Trang        | Mô tả                                                     |
| ------------ | --------------------------------------------------------- |
| Home         | Landing page với giới thiệu tính năng và CTA              |
| Dashboard    | Tổng quan task: thống kê, biểu đồ tiến độ                 |
| Task List    | Danh sách task với filter, sort, phân trang               |
| AI Assistant | 6 tab: Improve, Priority, Subtasks, Coach, Search, Wizard |
| Calendar     | Lịch FullCalendar hiển thị deadline task                  |
| Profile      | Thông tin cá nhân, avatar, thống kê hoạt động             |

> _Chụp screenshot khi chạy `python manage.py runserver` và thêm ảnh vào thư mục `docs/screenshots/`._

## Cài đặt & Chạy (local)

1. Tạo virtualenv và cài dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Tạo file `.env` trong thư mục `todolist/` và cấu hình:

```
SECRET_KEY=your-django-secret-key
DEBUG=True
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-key-here
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
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

5. Chạy unit tests:

```bash
python manage.py test tasks accounts --verbosity=2
```

## API endpoints (AI)

| Method | Endpoint                          | Mô tả                                            |
| ------ | --------------------------------- | ------------------------------------------------ |
| POST   | `/tasks/api/improve-description/` | Cải thiện mô tả task                             |
| POST   | `/tasks/api/suggest-priority/`    | Đề xuất priority + lý do                         |
| POST   | `/tasks/api/generate-subtasks/`   | Chia nhỏ task thành subtasks (kèm time estimate) |
| POST   | `/tasks/api/productivity-coach/`  | Phân tích năng suất + lời khuyên cá nhân         |
| POST   | `/tasks/api/smart-search/`        | Tìm kiếm task bằng ngôn ngữ tự nhiên             |
| POST   | `/tasks/api/auto-tag/`            | Tự động gắn tag cho task                         |
| POST   | `/tasks/api/ai-create-task/`      | AI Wizard — tạo task hoàn chỉnh từng bước        |
| GET    | `/tasks/api/ai-history/`          | Lịch sử sử dụng AI                               |

> Các endpoint yêu cầu người dùng đăng nhập (login required).

## Models chính

- `User` — `id (UUID), username, email, avatar (Cloudinary), is_active`
- `Task` — `id (UUID), user (FK), title, description, tags (M2M), deadline, priority, status, created_at, updated_at, completed_at`
- `SubTask` — `id (UUID), task (FK), title, description, status, order, completed_at`
- `Tag` — `id (UUID), name, slug, color`
- `AISuggestion` — `id (UUID), task (FK), user (FK), suggestion_type, input_data (JSON), output_data (JSON), applied`

## Unit Tests

| Module   | Loại test                                      | Số lượng |
| -------- | ---------------------------------------------- | -------- |
| tasks    | Model tests (Task, SubTask, Tag, AISuggestion) | 15       |
| tasks    | Form tests (TaskForm validation)               | 6        |
| tasks    | View tests (auth, CRUD, filter, AJAX)          | 18       |
| tasks    | Service tests (TaskService, SubtaskService)    | 13       |
| accounts | Model tests (User)                             | 8        |
| accounts | Form tests (Register, ProfileEdit)             | 6        |
| accounts | View tests (login, register, profile)          | 11       |
| **Tổng** |                                                | **87**   |

## Contributor & Liên hệ

- Sơn: mewmewancut <23010313@st.phenikaa-uni.edu.vn> — Backend core & Authentication
- Dũng: aduoke33 <23010329@st.phenikaa-uni.edu.vn> — AI Integration & Logic
- Minh: doanquangminh14 — Frontend & UI/UX

## Commit / Branching

- Main branch: code ổn định
- Các feature branch: `feature/<name>` hoặc `user/<name>/feature`

## Ghi chú triển khai

- Đối với production: chuyển SQLite → PostgreSQL, cấu hình `ALLOWED_HOSTS`, thiết lập SMTP thực tế, và bảo mật API keys (Secrets manager).
- Chạy `python manage.py collectstatic` để thu thập static files vào `staticfiles/`.
- Custom error pages (404, 500) đã được cấu hình.
