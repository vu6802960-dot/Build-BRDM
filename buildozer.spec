[app]
title = Device Manager Pro
package.name = devicemanager
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.8.0

# Đã bổ sung 'openssl' và 'urllib3'
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius, requests, certifi, openssl, urllib3

orientation = portrait
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.0
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.allow_backup = True
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
