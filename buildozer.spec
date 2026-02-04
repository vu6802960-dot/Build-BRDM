[app]

# (str) Tiêu đề ứng dụng
title = Device Manager Pro

# (str) Tên gói (Không dấu, không khoảng cách)
package.name = devicemanager

# (str) Tên miền gói
package.domain = org.vudot

# (str) Thư mục chứa code (mặc định là thư mục hiện tại)
source.dir = .

# (list) Các định dạng file cần đóng gói
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Phiên bản ứng dụng (Nâng lên 1.7.0 để cập nhật bản mới nhất)
version = 1.7.0

# (list) Các thư viện Python bắt buộc
# Thêm 'requests' và 'certifi' để gọi API OCR mượt mà hơn
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, urllib3, charset-normalizer, idna

# (str) Hướng màn hình (portrait - dọc)
orientation = portrait

# (list) Quyền hạn hệ thống
# Quan trọng: Đủ quyền để Camera và lưu file không bị chặn 
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) API mục tiêu (API 33 là ổn định nhất cho Java 17 và Gradle hiện tại)
android.api = 33

# (int) API tối thiểu hỗ trợ
android.minapi = 21

# (str) Phiên bản NDK (Sử dụng bản 25b để tránh lỗi biên dịch)
android.ndk = 25b

# (str) Phiên bản Build-tools
android.build_tools_version = 33.0.0

# (bool) Sử dụng lưu trữ dữ liệu riêng (True giúp tránh lỗi Scoped Storage trên Android 11+)
android.private_storage = True

# (str) Điểm khởi chạy của ứng dụng
android.entrypoint = org.kivy.android.PythonActivity

# (list) Kiến trúc chip hỗ trợ (Thêm cả 2 để chạy được trên mọi loại máy Android)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Bật hỗ trợ AndroidX (Bắt buộc cho các thư viện KivyMD mới)
android.enable_androidx = True

# (bool) Tự động đồng ý các điều khoản SDK
android.accept_sdk_license = True

# (str) Định dạng file APK (debug để kiểm tra lỗi dễ hơn)
android.debug_artifact = apk

# (int) Cấp độ log (2 = debug, giúp xem chi tiết lỗi trong logcat)
log_level = 2

# (int) Cảnh báo nếu chạy build với quyền root
warn_on_root = 1

[buildozer]
# (str) Thư mục chứa file APK sau khi build xong
bin_dir = ./bin
