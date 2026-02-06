[app]

# (str) Title of your application
title = Device Pro 553

# (str) Package name
package.name = samsungdm

# (str) Package domain (needed for android packaging)
package.domain = org.vudot

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (QUAN TRỌNG: Phải có đuôi wav để đóng gói âm thanh)
source.include_exts = py,png,jpg,kv,atlas,ttf,wav

# (str) Application versioning
version = 5.5.3

# (list) Application requirements
# Bổ sung ffpyplayer để xử lý âm thanh success.wav ổn định trên Android
requirements = python3, kivy==2.3.0, pillow, android, pyjnius, requests, certifi, charset-normalizer, idna, urllib3, ffpyplayer

# (str) Supported orientation
orientation = portrait

# (list) Permissions
# INTERNET: Để gọi API OCR.space
# CAMERA & STORAGE: Để chụp ảnh nhãn và lưu file CSV
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API (Samsung đời mới thường dùng 33)
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android Build Tools version to use
android.build_tools_version = 33.0.0

# (list) The Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support (Cần thiết cho các API hiện đại)
android.enable_androidx = True

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Logcat filters
android.logcat_filters = *:S python:D

[buildozer]
# (int) Log level (2 để xem chi tiết lỗi nếu có)
log_level = 2
