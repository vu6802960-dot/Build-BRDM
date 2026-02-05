[app]
# (str) Tiêu đề ứng dụng
title = Device Manager Pro

# (str) Tên gói
package.name = samsungdm
package.domain = org.vudot

# (str) Thư mục nguồn
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 4.1.0

# Requirements: Giữ tối giản để tránh văng app trên Samsung
# Dùng UrlRequest tích hợp sẵn thay vì requests/openssl
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius

orientation = portrait

# Cấu hình Android SDK/NDK
android.api = 33
# KHÓA PHIÊN BẢN BUILD TOOLS TẠI 33.0.0 ĐỂ TRÁNH LỖI LICENSE 36.1
android.build_tools_version = 33.0.0
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Quyền hạn
android.permissions = CAMERA, INTERNET

# (str) Theme ứng dụng (Đã fix lỗi dấu ngoặc kép)
android.apptheme = @android:style/Theme.NoTitleBar

# (list) Kiến trúc chip (Bắt buộc cho Samsung mới)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Chấp nhận license
android.accept_sdk_license = True

# Tương thích Samsung One UI
android.enable_androidx = True
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
