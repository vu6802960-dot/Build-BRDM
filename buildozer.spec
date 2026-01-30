[app]
title = BRDM Tracker
package.name = brdmtracker
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.4.0
requirements = python3, kivy==2.3.0, kivymd==1.1.1, opencv, numpy, pillow, pyjnius, android, plyer
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a