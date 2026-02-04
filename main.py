from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from PIL import Image
from datetime import datetime
import io, base64, urllib.parse, re, os

Window.softinput_mode = "below_target"

KV = '''
MainScreen:
    orientation: 'vertical'
    padding: "10dp"
    spacing: "8dp"

    MDLabel:
        text: "QUẢN LÝ THIẾT BỊ v1.7"
        halign: "center"
        bold: True
        font_style: "H6"
        size_hint_y: None
        height: "40dp"

    BoxLayout:
        id: camera_container
        size_hint_y: 0.4
        canvas.before:
            Color:
                rgba: 0.2, 0.2, 0.2, 1
            Rectangle:
                pos: self.pos
                size: self.size

    MDCard:
        orientation: 'vertical'
        padding: "12dp"
        spacing: "8dp"
        size_hint_y: 0.5
        elevation: 2
        radius: [15, ]

        BoxLayout:
            id: input_container
            size_hint_y: None
            height: "60dp"

        MDBoxLayout:
            adaptive_height: True
            spacing: "15dp"
            MDRaisedButton:
                id: btn_muon
                text: "MƯỢN"
                md_bg_color: 0, 0.5, 0.8, 1
                on_release: root.set_status_type("MUON")
            MDRaisedButton:
                id: btn_tra
                text: "TRẢ"
                md_bg_color: 0.5, 0.5, 0.5, 1
                on_release: root.set_status_type("TRA")

        MDLabel:
            id: data_display
            text: "Trạng thái: Đang chờ cấp quyền..."
            theme_text_color: "Secondary"
            font_style: "Body2"

    MDBoxLayout:
        size_hint_y: None
        height: "55dp"
        spacing: "10dp"
        MDRaisedButton:
            text: "SCAN NHÃN"
            size_hint_x: 0.6
            on_release: root.capture_and_read()
        MDFillRoundFlatButton:
            text: "LƯU DỮ LIỆU"
            size_hint_x: 0.4
            md_bg_color: 0, .6, .2, 1
            on_release: root.export_data()
'''

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_type = "MUON"

    def set_status_type(self, s_type):
        self.status_type = s_type
        self.ids.btn_muon.md_bg_color = (0, 0.5, 0.8, 1) if s_type == "MUON" else (0.5, 0.5, 0.5, 1)
        self.ids.btn_tra.md_bg_color = (0.8, 0.2, 0.2, 1) if s_type == "TRA" else (0.5, 0.5, 0.5, 1)

    def capture_and_read(self):
        if not hasattr(self, 'camera_widget') or not self.camera_widget.play:
            self.ids.data_display.text = "Camera chưa sẵn sàng!"
            return
        try:
            pixels = self.camera_widget.texture.pixels
            pil_image = Image.frombytes('RGBA', self.camera_widget.texture.size, pixels).convert('RGB')
            buf = io.BytesIO()
            pil_image.save(buf, format='JPEG', quality=85)
            self.ids.data_display.text = "Đang quét OCR..."
            base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
            payload = urllib.parse.urlencode({
                'apikey': 'helloworld', 
                'base64Image': f"data:image/jpg;base64,{base64_image}",
                'language': 'eng'
            })
            UrlRequest("https://api.ocr.space/parse/image", req_body=payload, on_success=self.on_ocr_success)
        except Exception as e:
            self.ids.data_display.text = f"Lỗi: {str(e)}"

    def on_ocr_success(self, request, result):
        try:
            text = result['ParsedResults'][0]['ParsedText']
            imei = re.search(r'\d{15}', text)
            model = re.search(r'(SM-[A-Z0-9]+)', text)
            self.ids.data_display.text = f"Model: {model.group(0) if model else 'N/A'}\\nIMEI: {imei.group(0) if imei else 'N/A'}"
        except:
            self.ids.data_display.text = "Không tìm thấy dữ liệu trên nhãn"

    def export_data(self):
        user = self.user_input.text if hasattr(self, 'user_input') else ""
        if not user:
            self.ids.data_display.text = "HÃY NHẬP TÊN NGƯỜI LÀM!"
            return
        
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | {user} | {self.status_type} | {self.ids.data_display.text.replace('\\n', ' | ')}\\n"
        
        try:
            if platform == 'android':
                from jnius import autoclass
                context = autoclass('org.kivy.android.PythonActivity').mActivity
                storage_dir = context.getExternalFilesDir(None).getAbsolutePath()
            else:
                storage_dir = "."
            
            with open(os.path.join(storage_dir, "device_logs.txt"), "a", encoding='utf-8') as f:
                f.write(log_entry)
            self.ids.data_display.text = "LƯU THÀNH CÔNG!"
        except Exception as e:
            self.ids.data_display.text = f"Lỗi lưu: {str(e)}"

class LabelApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.screen = Builder.load_string(KV)
        return self.screen

    def on_start(self):
        Clock.schedule_once(self.create_input_field, 0.1)
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE], self.check_permissions)
        else:
            Clock.schedule_once(self.enable_camera, 1.0)

    def create_input_field(self, dt):
        from kivymd.uix.textfield import MDTextField
        self.screen.user_input = MDTextField(hint_text="Tên người thực hiện", mode="rectangle")
        self.screen.ids.input_container.add_widget(self.screen.user_input)

    def check_permissions(self, permissions, results):
        if all(results):
            # Tăng độ trễ lên 1.2 giây để tránh lỗi 'setParameters failed'
            Clock.schedule_once(self.enable_camera, 1.2)
        else:
            self.screen.ids.data_display.text = "LỖI: Chưa được cấp quyền!"

    def enable_camera(self, dt):
        from kivy.uix.camera import Camera
        try:
            # TỐI ƯU: Không chỉ định resolution để Android tự chọn bản phù hợp nhất
            self.screen.camera_widget = Camera(play=True, allow_stretch=True)
            self.screen.ids.camera_container.add_widget(self.screen.camera_widget)
            self.screen.ids.data_display.text = "Hệ thống sẵn sàng."
        except Exception as e:
            self.screen.ids.data_display.text = f"Lỗi kết nối Camera: {str(e)}"

if __name__ == "__main__":
    LabelApp().run()
