[app]
title = DeviceManager
package.name = devicemanager
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,txt,csv
version = 1.0

# Quyền hạn cực kỳ quan trọng cho Android 13+
android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

requirements = python3, kivy==2.2.1, pillow, pyzbar, requests

orientation = portrait
fullscreen = 1
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
