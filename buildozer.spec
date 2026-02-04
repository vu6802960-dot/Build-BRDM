[app]
title = Device Manager Pro
package.name = devicemanager
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 3.1.0

# Thêm pillow, openssl, urllib3 để phục vụ OCR và xoay ảnh
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, openssl, urllib3

orientation = portrait
android.api = 33
android.minapi = 21
android.ndk = 25b

# Quyền hạn đầy đủ cho Camera và Bộ nhớ Samsung
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# Kiến trúc 64-bit bắt buộc cho Samsung mới
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.accept_sdk_license = True
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
