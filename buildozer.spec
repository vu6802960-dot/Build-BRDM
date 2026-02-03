[app]
# (Tiêu đề và tên gói)
title = Device Manager
package.name = devicemanager
package.domain = org.vudot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.2.0

# (Yêu cầu thư viện)
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, android, pyjnius

# (Phần sửa lỗi quan trọng nhất)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.0
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (Cấu hình hiển thị)
orientation = portrait
android.allow_backup = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
