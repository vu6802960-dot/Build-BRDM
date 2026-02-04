[app]

# (str) Tiêu đề ứng dụng
title = Samsung Device Manager

# (str) Tên gói (Không chứa ký tự đặc biệt)
package.name = devicemanager

# (str) Tên miền gói
package.domain = org.vudot

# (str) Thư mục chứa code
source.dir = .

# (list) Các định dạng file cần đóng gói
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Phiên bản ứng dụng
version = 2.0.0

# (list) Thư viện Python bắt buộc cho Samsung & Android đời cao
# Thêm 'openssl' để xử lý kết nối HTTPS an toàn của Samsung
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, openssl, urllib3

# (str) Hướng màn hình
orientation = portrait

# (list) Quyền hạn hệ thống
# Samsung Android 11+ yêu cầu khai báo quyền đọc/ghi bộ nhớ rõ ràng
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) API mục tiêu (33 là bản ổn định nhất cho Samsung Android 11-14)
android.api = 33

# (int) API tối thiểu hỗ trợ
android.minapi = 21

# (str) Phiên bản NDK (Sử dụng 25b để tương thích hoàn toàn với Java 17)
android.ndk = 25b

# (str) Phiên bản Build-tools
android.build_tools_version = 33.0.0

# (bool) Sử dụng lưu trữ dữ liệu riêng
android.private_storage = True

# (list) Kiến trúc chip hỗ trợ
# Bắt buộc có arm64-v8a cho các dòng Samsung đời mới (S21, S22, S23, S24...)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Bật hỗ trợ AndroidX (Bắt buộc để không bị lỗi giao diện trên One UI)
android.enable_androidx = True

# (bool) Tự động đồng ý các điều khoản SDK (Sửa lỗi 'Broken pipe' khi build)
android.accept_sdk_license = True

# (list) Thư viện nền tảng (SDL2 cho đồ họa Samsung)
android.bootstrap = sdl2

# (int) Cấp độ log (2 = debug chi tiết)
log_level = 2

# (int) Cảnh báo nếu chạy build với quyền root
warn_on_root = 1

[buildozer]
# (str) Thư mục chứa file APK sau khi build xong
bin_dir = ./bin
