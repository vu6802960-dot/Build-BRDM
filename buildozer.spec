[app]

# (str) Title of your application
title = Device Pro 5.0

# (str) Package name
package.name = samsungdm

# (str) Package domain (needed for android packaging)
package.domain = org.vudot

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning (method 1)
version = 5.0.0

# (list) Application requirements
# Chỉ dùng Kivy thuần và Pillow để xử lý ảnh nhẹ nhàng nhất
requirements = python3, kivy==2.3.0, pillow, android, pyjnius

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be monitor for orientation changes
fullscreen = 0

# (list) Permissions 
# Bổ sung đầy đủ quyền ghi file và camera cho Android 11-14
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES

# (int) Target Android API, nên để 33 cho Samsung đời mới
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use.
android.ndk_api = 21

# (str) Android Build Tools version to use
android.build_tools_version = 33.0.0

# (bool) Use --private data storage (True) 
android.private_storage = True

# (list) The Android architectures to build for
# arm64-v8a là kiến trúc chính của các dòng Samsung S/A hiện nay
android.archs = arm64-v8a, armeabi-v7a

# (str) The Android app theme
android.apptheme = @android:style/Theme.NoTitleBar

# (bool) Enable AndroidX support (Cần thiết cho camera hiện đại)
android.enable_androidx = True

# (bool) Copy libraries to the libs/ folder
android.copy_libs = 1

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Logcat filters to use
android.logcat_filters = *:S python:D

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = no, 1 = yes)
warn_on_root = 1
