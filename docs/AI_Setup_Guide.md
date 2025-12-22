# Hướng dẫn setup AI features

## 1. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

## 2. Tạo file .env

Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```

## 3. Lấy OpenAI API Key

1. Vào https://platform.openai.com/
2. Đăng ký tài khoản (có $5 free credit)
3. Vào API Keys > Create new secret key
4. Copy key vào file `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

## 4. Test kết nối

```bash
cd todolist
python -c "from ai_utils import test_connection; test_connection()"
```

Nếu thấy "✓ LLM connection successful!" là ok!

## Lưu ý

- **KHÔNG** commit file `.env` lên git
- API key là bí mật, không share cho ai
- Free tier có giới hạn, dùng tiết kiệm
- Nếu hết credit, có thể dùng Gemini (free)

## Troubleshooting

**Lỗi: "OPENAI_API_KEY not found"**
- Kiểm tra đã tạo file `.env` chưa
- Kiểm tra đã điền API key đúng format chưa

**Lỗi: "Rate limit exceeded"**
- Đợi 1 phút rồi thử lại
- Hoặc chuyển sang dùng provider khác
