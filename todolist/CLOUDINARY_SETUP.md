# 📸 Hướng dẫn cài đặt Cloudinary cho Django - Upload Avatar

## 🎯 Tổng quan
Cloudinary là dịch vụ lưu trữ ảnh trên cloud miễn phí, giúp bạn không cần lưu ảnh trên server local.

---

## 📋 Bước 1: Cài đặt Packages (Đã làm)

Các package đã được cài đặt:
- `django-cloudinary-storage` - Django integration cho Cloudinary
- `pillow` - Xử lý ảnh trong Python

---

## 🌐 Bước 2: Tạo tài khoản Cloudinary (MIỄN PHÍ)

1. **Truy cập**: https://cloudinary.com/users/register/free
2. **Đăng ký** bằng:
   - Email
   - Google Account
   - GitHub Account
3. Sau khi đăng ký, bạn sẽ được chuyển đến **Dashboard**

---

## 🔑 Bước 3: Lấy Cloudinary Credentials

1. Trong **Dashboard**, tìm phần **Account Details** (thường ở góc trên bên phải)
2. Bạn sẽ thấy 3 thông tin quan trọng:
   - **Cloud name**: Tên cloud của bạn (ví dụ: `dxyz123456`)
   - **API Key**: Key để xác thực (ví dụ: `123456789012345`)
   - **API Secret**: Secret key (ví dụ: `abcdefghijklmnopqrstuvwxyz`)

3. **Copy 3 thông tin này lại** (sẽ cần dùng ở bước sau)

   💡 **Lưu ý**: API Secret là thông tin nhạy cảm, không chia sẻ công khai!

## ⚙️ Bước 4: Cấu hình trong Django

### 🔒 Cách 1: Sử dụng Environment Variables (KHUYẾN NGHỊ - Bảo mật hơn)

**Ưu điểm**: Bảo mật, không commit credentials lên Git

1. **Cài đặt python-decouple**:
```bash
pip install python-decouple
```

2. **Tạo file `.env`** trong thư mục gốc của project (cùng cấp với `manage.py`):
a
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

3. **Thêm `.env` vào `.gitignore`** (nếu chưa có):
```
.env
```

4. **Cập nhật `todolist/settings.py`**:
```python
from decouple import config

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}
```

### ⚡ Cách 2: Đặt trực tiếp trong settings.py (Chỉ dùng cho development)

**Lưu ý**: Chỉ dùng khi phát triển local, KHÔNG commit lên Git!

Cập nhật trong `todolist/settings.py` (đã được thêm sẵn, chỉ cần thay thế giá trị):

```python
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'your_cloud_name',      # Thay bằng Cloud name của bạn
    'API_KEY': 'your_api_key',            # Thay bằng API Key của bạn
    'API_SECRET': 'your_api_secret',       # Thay bằng API Secret của bạn
}
```

**Ví dụ thực tế**:
```python
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dxyz123456',
    'API_KEY': '123456789012345',
    'API_SECRET': 'abcdefghijklmnopqrstuvwxyz',
}
```

## 🗄️ Bước 5: Tạo Migration và Chạy Migration

Sau khi đã cấu hình Cloudinary credentials, chạy migration để thêm field `avatar` vào database:

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

**Lưu ý**: Nếu có lỗi, có thể cần xóa migration cũ hoặc reset database (chỉ trong development).

---

## ✅ Bước 6: Kiểm tra và Sử dụng

1. **Chạy server**:
```bash
python manage.py runserver
```

2. **Đăng nhập** vào tài khoản của bạn

3. **Vào trang Profile**: `/accounts/profile/`

4. **Chỉnh sửa hồ sơ**: Click "Chỉnh sửa hồ sơ"

5. **Upload avatar**: 
   - Chọn file ảnh (JPG, PNG, GIF)
   - Xem preview ngay lập tức
   - Click "Lưu thay đổi"

6. **Kiểm tra trong Cloudinary**:
   - Vào https://console.cloudinary.com/
   - Click **Media Library**
   - Bạn sẽ thấy ảnh đã được upload vào thư mục `avatars/`

---

## ⚠️ Lưu ý quan trọng về Bảo mật:

### 🔐 KHÔNG commit credentials lên GitHub!

1. **Nếu dùng `.env`**:
   - Đảm bảo `.env` đã có trong `.gitignore`
   - Tạo file `.env.example` với format (không có giá trị thật):
   ```env
   CLOUDINARY_CLOUD_NAME=
   CLOUDINARY_API_KEY=
   CLOUDINARY_API_SECRET=
   ```

2. **Nếu dùng cách 2 (trong settings.py)**:
   - ⚠️ **NHỚ XÓA** credentials trước khi commit
   - Hoặc sử dụng environment variables

---

## 🐛 Troubleshooting (Xử lý lỗi):

### ❌ Lỗi "Invalid credentials"
- **Nguyên nhân**: Cloud name, API Key, hoặc API Secret sai
- **Giải pháp**: 
  - Kiểm tra lại trong Cloudinary Dashboard
  - Đảm bảo không có khoảng trắng thừa
  - Copy lại từ Dashboard

### ❌ Ảnh không hiển thị
- **Nguyên nhân**: CLOUDINARY_STORAGE chưa được cấu hình đúng
- **Giải pháp**:
  - Kiểm tra `INSTALLED_APPS` có `cloudinary_storage` và `cloudinary`
  - Kiểm tra `DEFAULT_FILE_STORAGE` đã được set
  - Restart server sau khi thay đổi settings

### ❌ Upload thất bại
- **Nguyên nhân**: File quá lớn hoặc định dạng không hỗ trợ
- **Giải pháp**:
  - Cloudinary free plan giới hạn **10MB/file**
  - Chỉ hỗ trợ: JPG, PNG, GIF, WebP
  - Nén ảnh trước khi upload

### ❌ Lỗi "ModuleNotFoundError: No module named 'cloudinary_storage'"
- **Giải pháp**: 
```bash
pip install django-cloudinary-storage pillow
```

---

## 📚 Tài liệu tham khảo:

- **Cloudinary Dashboard**: https://console.cloudinary.com/
- **Cloudinary Documentation**: https://cloudinary.com/documentation
- **Django Cloudinary Storage**: https://github.com/klis87/django-cloudinary-storage
- **Pillow Documentation**: https://pillow.readthedocs.io/

---

## ✨ Tính năng đã được tích hợp:

✅ Upload avatar từ Profile Edit page  
✅ Preview avatar trước khi lưu  
✅ Hiển thị avatar trong Profile page  
✅ Tự động resize và optimize ảnh (Cloudinary tự động)  
✅ Lưu trữ trên Cloudinary cloud (không tốn dung lượng server)  
✅ URL ảnh tự động từ Cloudinary CDN  

---

## 🎉 Hoàn thành!

Sau khi hoàn thành các bước trên, bạn đã có thể:
- Upload avatar cho user
- Ảnh được lưu trên Cloudinary
- Hiển thị avatar ở mọi nơi trong ứng dụng

**Chúc bạn thành công!** 🚀

