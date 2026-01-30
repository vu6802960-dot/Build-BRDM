[app]
title = BRDM Tracker
package.name = brdmtracker
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.5.0

# Ép sử dụng bản Master để fix lỗi AndroidX
p4a.branch = master

requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, numpy, pyjnius, android, plyer

# Cấu hình AndroidX và Java cực kỳ quan trọng
android.enable_androidx = True
android.desugar_libs = True
# Sử dụng phiên bản ổn định nhất của ML Kit để tránh xung đột Gradle
android.gradle_dependencies = "com.google.mlkit:text-recognition:16.0.0"

android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

orientation = portrait
fullscreen = 0

# Thêm metadata để tải module OCR từ Google Play Services
android.meta_data = com.google.android.gms.vision.DEPENDENCIES=ocr

[buildozer]
log_level = 2
warn_on_root = 1
