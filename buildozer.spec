[app]
title = Device Manager Pro
package.name = devicemanager
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 2.2.0

# Thêm openssl để tránh lỗi kết nối mạng trên Samsung
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, openssl

orientation = portrait
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.0

# Quyền hạn đầy đủ
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Bắt buộc kiến trúc 64-bit cho Samsung đời mới
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.accept_sdk_license = True
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
