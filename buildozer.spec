[app]

# (str) Title of your application
title = Device Manager Pro

# (str) Package name
package.name = devicemanager

# (str) Package domain (needed for android packaging)
package.domain = org.vudot

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,wav,csv,txt

# (str) Application version
version = 1.4

# (list) Application requirements
# Đã bao gồm các thư viện cần thiết cho Kivy, xử lý ảnh và mạng
requirements = python3, kivy==2.2.1, pillow, requests, chardet, idna, urllib3

# (str) Custom source folders for requirements
# source.include_dirs = assets,bin

# (str) Presplash of the application
# Hình ảnh hiện lên khi app đang load (thay cho màn hình đen)
presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (list) Supported orientations
orientation = portrait

# -----------------------------------------------------------------------------
# Android specific
# -----------------------------------------------------------------------------

# (list) Permissions
# Cấp quyền Camera để quét mã và Storage để xuất/nhập file CSV/TXT
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API
# Hạ xuống 31 để tránh lỗi "API 33 not available" trên GitHub Actions
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
# android.sdk = 31

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) The Android arch to build for.
# Build cho cả 2 kiến trúc phổ biến nhất hiện nay
android.archs = arm64-v8a, armeabi-v7a

# (bool) allows Android to handle screen rotation
android.allow_rotation = false

# (bool) Accept SDK license
android.accept_sdk_license = True

# -----------------------------------------------------------------------------
# Buildozer section
# -----------------------------------------------------------------------------

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1

# (str) Path to build artifact storage, can be a variable name, or relative path
bin_dir = ./bin
