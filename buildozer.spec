[app]
# (Bản ghi tên ứng dụng)
title = BRDM Tracker
package.name = brdmtracker
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.5.0

# Sử dụng bản master của python-for-android để hỗ trợ tốt nhất cho AndroidX
p4a.branch = master

# Các thư viện cần thiết cho ML Kit và Kivy
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, numpy, pyjnius, android, plyer

# --- CẤU HÌNH QUAN TRỌNG ĐỂ SỬA LỖI GRADLE ---
android.enable_androidx = True
android.desugar_libs = True
android.gradle_dependencies = "com.google.mlkit:text-recognition:16.0.0"

# Cấu hình SDK/NDK và Quyền truy cập
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

# Khóa portrait để tránh lỗi treo/xoay màn hình đen
orientation = portrait
fullscreen = 0

# Thêm metadata để Google Play Services chuẩn bị sẵn bộ OCR
android.meta_data = com.google.android.gms.vision.DEPENDENCIES=ocr

[buildozer]
log_level = 2
warn_on_root = 1
