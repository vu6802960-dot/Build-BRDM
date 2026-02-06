[app]
title = Device Pro 5.3
package.name = samsungdm
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 5.3.0

# THÊM CÁC THƯ VIỆN MẠNG QUAN TRỌNG: requests, charset-normalizer, idna, urllib3, certifi
requirements = python3, kivy==2.3.0, pillow, android, pyjnius, requests, charset-normalizer, idna, urllib3, certifi

orientation = portrait
fullscreen = 0

# CẤP QUYỀN INTERNET ĐỂ GỌI API
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.build_tools_version = 33.0.0
android.private_storage = True
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.accept_sdk_license = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
