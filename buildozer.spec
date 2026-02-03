[app]
title = SMSN Scanner
package.name = smsnscanner
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0.1

requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius

android.api = 31
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 30.0.3
android.permissions = CAMERA, INTERNET

# 4. CHẶN XOAY MÀN HÌNH: Chỉ cho phép Portrait (Dọc)
orientation = portrait

android.archs = arm64-v8a
# Tự động yêu cầu quyền khi mở app
android.entrypoint = main.py

[buildozer]
log_level = 2
warn_on_root = 1
