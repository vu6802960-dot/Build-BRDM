[app]
title = Device Manager Pro
package.name = samsungdm
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 4.0.0

# LOẠI BỎ requests, openssl để tránh văng trên Samsung
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius

orientation = portrait
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Fix lỗi Manifest từ bản 3.3
android.apptheme = @android:style/Theme.NoTitleBar
android.permissions = CAMERA, INTERNET

# Bắt buộc cho Samsung mới
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.copy_libs = 1

[buildozer]
log_level = 2
