[app]
title = BRDM Tracker Pro
package.name = brdmpro
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 2.0.0

# Sử dụng master branch để có bản vá AndroidX mới nhất
p4a.branch = master

requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, numpy, pyjnius, android, plyer

# --- CẤU HÌNH FIX LỖI BUILD GRADLE ---
android.enable_androidx = True
android.desugar_libs = True
android.gradle_dependencies = "com.google.mlkit:text-recognition:16.0.0"
# Fix lỗi libc++_shared.so trùng lặp khiến gradlew failed
android.packaging_options = "exclude:lib/**/libc++_shared.so"

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Khóa cứng hướng màn hình dọc
orientation = portrait
android.meta_data = com.google.android.gms.vision.DEPENDENCIES=ocr