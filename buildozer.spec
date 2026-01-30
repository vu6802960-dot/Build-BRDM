[app]
title = BRDM Tracker
package.name = brdmtracker
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.5.0

# Pillow dùng để xử lý ảnh đệm, pyjnius để gọi ML Kit
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, numpy, pyjnius, android, plyer

# KHAI BÁO THƯ VIỆN GOOGLE ML KIT (Bắt buộc)
android.gradle_dependencies = "com.google.mlkit:text-recognition:16.0.0"

android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
orientation = portrait
