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
source.include_exts = py,png,jpg,kv,atlas,wav,csv,txt

# (str) Application versioning (method 1)
version = 1.5.3

# (list) Application requirements
# Cần plyer để chọn file, ffpyplayer để phát âm thanh
requirements = python3, kivy==2.2.1, pillow, requests, ffpyplayer, plyer

# (str) Presplash of the application
presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (list) Permissions
# Cần quyền Camera cho quét IMEI và Storage để nhập/xuất file
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API, should be as high as possible.
# API 30 là bản ổn định nhất cho môi trường GitHub hiện tại
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (list) Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow skip update of android sdk
android.skip_update = False

# (bool) Display warning if android sdk is not found
android.warn_on_missing_sdk = True

# (bool) Accept SDK license agreements
android.accept_sdk_license = True

# (str) The Android logcat filters to use
#android.logcat_filters = *:S python:D

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display build output in color (0 = False, 1 = True)
warn_on_root = 1


