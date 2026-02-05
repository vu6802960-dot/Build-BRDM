[app]

# (str) Tiêu đề ứng dụng
title = Samsung Device Manager

# (str) Tên gói (Không dấu, không khoảng cách)
package.name = samsungdm

# (str) Tên miền gói
package.domain = org.vudot

# (str) Thư mục chứa code nguồn
source.dir = .

# (list) Các định dạng file cần đóng gói
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Phiên bản
version = 3.3.0

# (list) Các thư viện Python cần thiết
# Đã thêm openssl để đảm bảo kết nối mạng an toàn trên Android 11+
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, openssl

# (str) Hướng màn hình
orientation = portrait

# (list) Quyền hạn hệ thống
# Chỉ giữ lại Camera và Internet để tối ưu hóa việc xác thực quyền trên Samsung
android.permissions = CAMERA, INTERNET

# (int) Target API (33 là chuẩn cho Samsung Android 11-14)
android.api = 33

# (int) API tối thiểu hỗ trợ
android.minapi = 21

# (str) Phiên bản NDK ổn định nhất
android.ndk = 25b

# (int) NDK API (Sử dụng 21 để tương thích rộng)
android.ndk_api = 21

# (bool) Tự động chấp nhận SDK License để tránh lỗi 'Broken pipe'
android.accept_sdk_license = True

# (list) Kiến trúc chip
# Bắt buộc phải có arm64-v8a cho các dòng Samsung Galaxy mới
android.archs = arm64-v8a, armeabi-v7a

# (str) Theme ứng dụng
# FIX: Tuyệt đối KHÔNG để dấu ngoặc kép ở đây (Tránh lỗi ManifestMerger)
android.apptheme = @android:style/Theme.NoTitleBar

# (bool) Bật AndroidX để tương thích với One UI của Samsung
android.enable_androidx = True

# (bool) Copy các thư viện native
android.copy_libs = 1

# (str) Hoạt động chính của ứng dụng
android.entrypoint = org.kivy.android.PythonActivity

# (int) Cấp độ Log (2 là hiển thị đầy đủ để kiểm tra lỗi)
log_level = 2

# (int) Cảnh báo nếu build với quyền root
warn_on_root = 1

[buildozer]

# (str) Thư mục chứa file APK sau khi xuất bản
bin_dir = ./bin
