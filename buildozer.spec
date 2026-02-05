[app]
title = Device Manager Pro
package.name = samsungdm
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 4.3.0

requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius

orientation = portrait
android.api = 33
android.build_tools_version = 33.0.0
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

android.permissions = CAMERA, INTERNET
android.accept_sdk_license = True
android.apptheme = @android:style/Theme.NoTitleBar
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
