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
version = 3.2.0

# (list) Thư viện bắt buộc. 
# QUAN TRỌNG: Thêm openssl để tránh lỗi mạng trên Samsung
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, openssl

# (str) Hướng màn hình
orientation = portrait

# (list) Quyền hạn hệ thống. 
# TỐI GIẢN: Chỉ xin Camera và Internet để tránh bộ lọc Knox của Samsung chặn App
android.permissions = CAMERA, INTERNET

# (int) Target API (33 là con số ổn định nhất cho Samsung Android 11-14)
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version (Nên dùng 25b cho ổn định)
android.ndk = 25b

# (str) Android NDK path (để trống để buildozer tự tải)
#android.ndk_path = 

# (str) Android SDK path (để trống để buildozer tự tải)
#android.sdk_path = 

# (bool) Chấp nhận license tự động (Sửa lỗi Broken Pipe trên Github Actions)
android.accept_sdk_license = True

# (list) Kiến trúc chip hỗ trợ. 
# BẮT BUỘC: arm64-v8a cho điện thoại Samsung mới
android.archs = arm64-v8a, armeabi-v7a

# (bool) Bật AndroidX (Bắt buộc cho Samsung One UI)
android.enable_androidx = True

# (bool) Copy các thư viện bổ trợ
android.copy_libs = 1

# (str) Tên hoạt động chính
android.entrypoint = org.kivy.android.PythonActivity

# (list) Các dịch vụ chạy ngầm (Nếu có)
#services = 

# (str) App theme (Dùng NoTitleBar để tránh lỗi hiển thị tầng Native)
android.apptheme = "@android:style/Theme.NoTitleBar"

# (int) Cấp độ Log
log_level = 2

# (int) Cảnh báo nếu build bằng root
warn_on_root = 1

[buildozer]

# (str) Đường dẫn đến thư mục bin
bin_dir = ./bin
