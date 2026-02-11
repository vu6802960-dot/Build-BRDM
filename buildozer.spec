[app]
title = Device Manager
package.name = devicemanager
package.domain = org.vudot

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,csv,txt

version = 1.4

# (list) Application requirements
# SỬA LỖI: Thêm đầy đủ các thư viện và khóa phiên bản
requirements = python3, kivy==2.2.1, pillow, requests, chardet, idna, urllib3

# (str) Icon of the application (Đảm bảo bạn có file icon.png 512x512)
icon.filename = %(source.dir)s/icon.png

# (str) Presplash of the application (Màn hình khởi động thay cho Loading)
presplash.filename = %(source.dir)s/presplash.png

# (list) Supported orientations
orientation = portrait

# (list) Permissions
# QUAN TRỌNG: Cấp quyền Camera và Ghi file để không bị crash
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API, nên dùng 33 cho độ ổn định cao nhất
android.api = 33
android.minapi = 21
android.ndk = 25b

# (bool) Chấp nhận license tự động
android.accept_sdk_license = True

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (str) The Android arch to build for.
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
