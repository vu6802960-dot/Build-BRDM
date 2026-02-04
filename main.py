from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.utils import platform
from kivy.clock import Clock
from PIL import Image
from datetime import datetime
import io, base64, urllib.parse, re, os

# Giao diện tối giản, tập trung vào sự ổn định
KV = '''
MainScreen:
    orientation: 'vertical'
    padding: "15dp"
    spacing: "10dp"

    MDLabel:
        text: "SAMSUNG DEVICE MANAGER"
        halign: "center"
        bold: True
        font_style: "H6"
        size_hint_y: None
        height: "50dp"

    BoxLayout:
        id: cam_box
        size_hint_y: 0.4
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        MDLabel:
            id: cam_hint
            text: "1. Cấp quyền xong\\n2. Nhấn 'KÍCH HOẠT CAMERA'"
            halign: "center"
            color: 1, 1, 1, 1

    MDCard:
        orientation: 'vertical'
        padding: "15dp"
        size_hint_y: 0.6
        elevation: 1
        
        BoxLayout:
            id: input_box
            size_hint_y: None
            height: "60dp"

        MDLabel:
            id: status_log
            text: "Trạng thái: Chờ cấp quyền..."
            font_style: "Caption"

    MDRaisedButton:
        id: action_btn
        text: "KÍCH HOẠT CAMERA"
        size_hint_x: 1
        height: "56dp"
        md_bg_color: 0, 0.4, 0.8, 1
        on_release: root.manage_camera()
'''

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_cam_setup = False
        self.cam_obj = None

    def manage_camera(self):
        # Trên Samsung, việc kích hoạt thủ công sau khi mở app là an toàn nhất
        if not self.is_cam_setup:
            self.init_samsung_camera()
        else:
            self.do_ocr()

    def init_samsung_camera(self):
        from kivy.uix.camera import Camera
        try:
            self.ids.status_log.text = "Đang kết nối phần cứng Samsung..."
            # KHÔNG đặt resolution để tránh lỗi setParameters failed trên Android 11+
            self.cam_obj = Camera(play=True, allow_stretch=True)
            self.ids.cam_box.clear_widgets()
            self.ids.cam_box.add_widget(self.cam_obj)
            
            self.is_cam_setup = True
            self.ids.action_btn.text = "CHỤP & QUÉT NHÃN"
            self.ids.action_btn.md_bg_color = (0, 0.6, 0.3, 1)
            self.ids.status_log.text = "Camera đã sẵn sàng."
        except Exception as e:
            self.ids.status_log.text = f"Lỗi Samsung Cam: {str(e)}"

    def do_ocr(self):
        if not self.cam_obj or not self.cam_obj.texture:
            return
        
        try:
            self.ids.status_log.text = "Đang trích xuất ảnh..."
            pixels = self.cam_obj.texture.pixels
            img = Image.frombytes('RGBA', self.cam_obj.texture.size, pixels).convert('RGB')
            
            # Giảm chất lượng một chút để upload nhanh hơn trên mạng di động
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=80)
            
            b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            params = urllib.parse.urlencode({
                'apikey': 'helloworld',
                'base64Image': f"data:image/jpg;base64,{b64}"
            })
            UrlRequest("https://api.ocr.space/parse/image", req_body=params, on_success=self.ocr_done)
        except Exception as e:
            self.ids.status_log.text = f"Lỗi OCR: {str(e)}"

    def ocr_done(self, req, res):
        try:
            val = res['ParsedResults'][0]['ParsedText']
            self.ids.status_log.text = f"DỮ LIỆU ĐỌC ĐƯỢC:\\n{val}"
        except:
            self.ids.status_log.text = "Không nhận diện được chữ."

class LabelApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        Clock.schedule_once(self.prepare_ui, 1.0)
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            # Samsung yêu cầu danh sách quyền rõ ràng
            request_permissions([
                Permission.CAMERA, 
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.READ_EXTERNAL_STORAGE
            ])

    def prepare_ui(self, dt):
        from kivymd.uix.textfield import MDTextField
        self.root.u_input = MDTextField(hint_text="Tên người thực hiện", mode="rectangle")
        self.root.ids.input_box.add_widget(self.root.u_input)

if __name__ == "__main__":
    LabelApp().run()
