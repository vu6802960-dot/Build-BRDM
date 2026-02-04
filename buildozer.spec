[app]

# (str) Tiêu đề ứng dụng
title = Device Manager Pro

# (str) Tên gói (Không chứa ký tự đặc biệt)
package.name = devicemanager

# (str) Tên miền gói
package.domain = org.vudot

# (str) Thư mục chứa file main.py
source.dir = .

# (list) Các định dạng file bao gồm trong APK
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Phiên bản ứng dụng (Tăng lên 1.6.0 để cập nhật)
version = 1.6.0

# (list) CÁC THƯ VIỆN BẮT BUỘC
# Đã thêm 'requests' và 'certifi' để xử lý API OCR qua HTTPS an toàn 
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, urllib3, idna, charset-normalizer

# (str) Hướng màn hình (portrait - dọc)
orientation = portrait

# (list) QUYỀN HẠN ANDROID
# Giữ lại các quyền quan trọng để camera không bị lỗi 'Fail to connect' 
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API (Dùng API 34 cho Android 14)
android.api = 33

# (int) Minimum API hỗ trợ
android.minapi = 21

# (str) Phiên bản NDK và Build Tools phù hợp với Java 17
android.ndk = 25b
android.build_tools_version = 33.0.0

# (bool) Sử dụng lưu trữ dữ liệu riêng tư (Khuyên dùng cho Android 11+)
android.private_storage = True

# (str) Entry point của ứng dụng
android.entrypoint = org.kivy.android.PythonActivity

# (list) Các kiến trúc chip hỗ trợ (Đủ cho mọi dòng máy hiện nay)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Bật hỗ trợ AndroidX (Bắt buộc cho KivyMD đời mới) 
android.enable_androidx = True

# (bool) Tự động chấp nhận giấy phép SDK (Dành cho build tự động trên GitHub)
android.accept_sdk_license = True

# (bool) Copy thư viện thay vì tạo symlink (Giúp tránh lỗi link thư viện trên NDK mới)
android.copy_libs = 1

# (str) Cấu hình logcat để bắt lỗi hiệu quả
android.logcat_filters = *:S python:D

[buildozer]

# (int) Mức độ log (2 = debug để xem chi tiết quá trình build)
log_level = 2

# (int) Cảnh báo nếu chạy buildozer bằng quyền root
warn_on_root = 1

