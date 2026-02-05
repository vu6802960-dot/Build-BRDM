[app]
title = Device Pro 4.9
package.name = samsungdm
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 4.9.0
requirements = python3, kivy==2.3.0, pillow, android, pyjnius
orientation = portrait
android.api = 33
android.build_tools_version = 33.0.0
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Thêm quyền quản lý file cho Android 11+
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.apptheme = @android:style/Theme.NoTitleBar
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True

[buildozer]
log_level = 2
