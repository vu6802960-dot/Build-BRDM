[app]
title = Device Manager
package.name = samsungdm
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 3.4.0

# RÚT GỌN TỐI ĐA: Chỉ giữ lại những gì thực sự cần thiết
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius

orientation = portrait
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Dùng theme mặc định để giảm tải cho Manifest
android.apptheme = @android:style/Theme.NoTitleBar

# CHỈ xin quyền Camera
android.permissions = CAMERA, INTERNET

android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.copy_libs = 1
