[app]

# (str) Title of your application
title = Device Pro 4.9.1

# (str) Package name
package.name = samsungdm

# (str) Package domain (needed for android packaging)
package.domain = org.vudot

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning (method 1)
version = 4.9.1

# (list) Application requirements
# CHỈ DÙNG Kivy thuần, KHÔNG dùng kivymd để chống văng trên Samsung
requirements = python3, kivy==2.3.0, pillow, android, pyjnius

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be monitor for orientation changes
# android.screen_orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# Bổ sung các quyền Media cho Android 13+ (S22, S23, A-series)
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support.
android.ndk_api = 21

# (str) Android Build Tools version to use
android.build_tools_version = 33.0.0

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) The Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) allow backup
android.allow_backup = True

# (str) The Android app theme
android.apptheme = @android:style/Theme.NoTitleBar

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Copy libraries to the libs/ folder
android.copy_libs = 1

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Logcat filters to use
android.logcat_filters = *:S python:D

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = no, 1 = yes)
warn_on_root = 1
