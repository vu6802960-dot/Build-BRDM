[app]

# (str) Title of your application
title = Device Manager Pro

# (str) Package name
package.name = devicemanager

# (str) Package domain (needed for android packaging)
package.domain = org.vudot

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application version
version = 3.0.0

# (list) Application requirements
# Bắt buộc có pillow để xử lý xoay ảnh, openssl cho kết nối API OCR
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, openssl, urllib3

# (str) Supported orientation
orientation = portrait

# (list) Permissions
# Thêm quyền bộ nhớ để xuất file Log vào thư mục Documents
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
# API 33 ổn định nhất cho Samsung Android 11-14
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android NDK directory (if empty, it will be automatically downloaded)
android.ndk_path = 

# (str) Android SDK directory (if empty, it will be automatically downloaded)
android.sdk_path = 

# (str) ANT directory (if empty, it will be automatically downloaded)
android.ant_path = 

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (list) Android architectures to build for
# Bắt buộc arm64-v8a cho Samsung đời mới
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support (Bắt buộc cho KivyMD trên Samsung)
android.enable_androidx = True

# (list) Copy these libs to the extra-libs directory
android.copy_libs = 1

# (str) The Android arch to build for
android.bootstrap = sdl2

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
