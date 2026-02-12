[app]
title = Device Manager Pro
package.name = devicemanager
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,csv,txt
version = 1.4.1

# Requirements đầy đủ để xử lý ảnh và âm thanh
requirements = python3, kivy==2.2.1, pillow, requests, ffpyplayer

# Icon và Presplash (Hãy đảm bảo tên file là icon.png viết thường)
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

orientation = portrait
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
