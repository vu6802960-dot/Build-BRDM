from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from PIL import Image
import io
import base64
import urllib.parse

# 1. Chống xoay màn hình: Khóa cứng hướng dọc (Portrait) ngay khi khởi động
Window.softinput_mode = "below_target"

# 2. Giao diện tích hợp Camera
KV = '''
MainScreen:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size
            
    Camera:
        id: cam
        resolution: (1280, 720)
        play: True
        allow_stretch: True
        keep_ratio: True
        index: 0 # Đảm bảo mở camera sau

    MDLabel:
        id: status_label
        text: "HƯỚNG CAMERA VÀO NHÃN VÀ NHẤN QUÉT"
        halign: "center"
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        size_hint_y: None
        height: "60dp"

    MDRaisedButton:
        text: "QUÉT SMSN"
        pos_hint: {"center_x": .5}
        size_hint: (0.8, 0.1)
        md_bg_color: 0.1, 0.5, 0.9, 1
        on_release: root.capture_and_read()
'''

class MainScreen(BoxLayout):
    def capture_and_read(self):
        camera = self.ids.cam
        # Chống văng: Kiểm tra camera đã sẵn sàng chưa trước khi lấy texture
        if not camera.texture:
            self.ids.status_label.text = "LỖI: CAMERA CHƯA SẴN SÀNG"
            return

        try:
            pixels = camera.texture.pixels
            pil_image = Image.frombytes('RGBA', camera.texture.size, pixels).convert('RGB')
            
            # Pillow: Tăng chất lượng ảnh để đọc SMSN chính xác hơn
            buf = io.BytesIO()
            pil_image.save(buf, format='JPEG', quality=90)
            image_bytes = buf.getvalue()

            self.ids.status_label.text = "ĐANG GỬI DỮ LIỆU..."
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            payload = urllib.parse.urlencode({
                'apikey': 'helloworld', 
                'base64Image': f"data:image/jpg;base64,{base64_image}",
                'language': 'eng'
            })
            
            UrlRequest("https://api.ocr.space/parse/image", 
                       req_body=payload, 
                       req_headers={'Content-type': 'application/x-www-form-urlencoded'},
                       on_success=self.on_ocr_success,
                       on_failure=lambda req, err: self.set_status("LỖI MẠNG"),
                       timeout=10)
        except Exception as e:
            self.set_status(f"LỖI HỆ THỐNG: {str(e)}")

    def on_ocr_success(self, request, result):
        try:
            parsed_text = result['ParsedResults'][0]['ParsedText']
            self.ids.status_label.text = f"SMSN: {parsed_text.strip()}"
        except:
            self.ids.status_label.text = "KHÔNG TÌM THẤY CHỮ"

    def set_status(self, msg):
        self.ids.status_label.text = msg

class LabelApp(MDApp):
    def build(self):
        # 3. Chống tắt màn hình: Sử dụng lệnh hệ thống Android (Wake Lock)
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.INTERNET])
            # Giữ màn hình luôn sáng thông qua thiết lập Window
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            WindowManager = autoclass('android.view.WindowManager$LayoutParams')
            activity.getWindow().addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
            
        return Builder.load_string(KV)

if __name__ == "__main__":
    LabelApp().run()
