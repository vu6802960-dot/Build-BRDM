[app]
title = Device Pro 5.5
package.name = samsungdm
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 5.5.0
requirements = python3, kivy==2.3.0, pillow, android, pyjnius, requests, charset-normalizer, idna, urllib3, certifi
orientation = portrait
fullscreen = 0
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.accept_sdk_license = True
android.logcat_filters = *:S python:D
