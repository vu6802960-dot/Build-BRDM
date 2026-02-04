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
        text: "DEVICE MANAGER v1.8.1"
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
                rgba: 0.15, 0.15, 0.15, 1
            Rectangle:
                pos: self.pos
                size: self.size
        MDLabel:
            id: cam_placeholder
            text: "Nhấn 'SCAN NHÃN' để mở Camera"
            halign: "center"
            theme_text_color: "Hint"

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
            text: "Trạng thái: Đã sẵn sàng"
            theme_text_color: "Secondary"
            font_style: "Body2"

    MDBoxLayout:
        size_hint_y: None
        height: "55dp"
        spacing: "10dp"
        MDRaisedButton:
            id: btn_scan
            text: "SCAN NHÃN"
            size_hint_x: 0.6
            on_release: root.handle_scan_logic()
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
        self.camera_active = False

    def set_status_type(self, s_type):
        self.status_type = s_type
        self.ids.btn_muon.md_bg_color = (0, 0.5, 0.8, 1) if s_type == "MUON" else (0.5, 0.5, 0.5, 1)
        self.ids.btn_tra.md_bg_color = (0.8, 0.2, 0.2, 1) if s_type == "TRA" else (0.5, 0.5, 0.5, 1)

    def handle_scan_logic(self):
        if not self.camera_active:
            self.enable_camera_widget()
        else:
            self.capture_and_read()

    def enable_camera_widget(self):
        from kivy.uix.camera import Camera
        try:
            # Khởi tạo camera không resolution để tối ưu độ tương thích
            self.camera_widget = Camera(play=True, allow_stretch=True)
            self.ids.camera_container.clear_widgets()
            self.ids.camera_container.add_widget(self.camera_widget)
            self.camera_active = True
            self.ids.btn_scan.text = "CHỤP & QUÉT"
            self.ids.data_display.text = "Camera đã sẵn sàng."
        except Exception as e:
            self.ids.data_display.text = f"Lỗi mở Camera: {str(e)}"

    def capture_and_read(self):
        if not self.camera_widget.texture:
            return
        try:
            pixels = self.camera_widget.texture.pixels
            pil_image = Image.frombytes('RGBA', self.camera_widget.texture.size, pixels).convert('RGB')
            buf = io.BytesIO()
            pil_image.save(buf, format='JPEG', quality=85)
            self.ids.data_display.text = "Đang gửi dữ liệu OCR..."
            
            base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
            payload = urllib.parse.urlencode({
                'apikey': 'helloworld', 
                'base64Image': f"data:image/jpg;base64,{base64_image}",
                'language': 'eng'
            })
            UrlRequest("https://api.ocr.space/parse/image", req_body=payload, on_success=self.on_ocr_success)
        except Exception as e:
            self.ids.data_display.text = f"Lỗi xử lý: {str(e)}"

    def on_ocr_success(self, request, result):
        try:
            text = result['ParsedResults'][0]['ParsedText']
            imei = re.search(r'\d{15}', text)
            model = re.search(r'(SM-[A-Z0-9]+)', text)
            m_val = model.group(0) if model else 'N/A'
            i_val = imei.group(0) if imei else 'N/A'
            self.ids.data_display.text = f"Model: {m_val}\\nIMEI: {i_val}"
        except:
            self.ids.data_display.text = "Kết quả: Không tìm thấy dữ liệu"

    def export_data(self):
        # Lấy tên người dùng an toàn
        user = self.user_input.text if hasattr(self, 'user_input') else ""
        if not user:
            self.ids.data_display.text = "VUI LÒNG NHẬP TÊN NGƯỜI LÀM!"
            return
        
        # CÁCH 1: Xử lý chuỗi xuống dòng TRƯỚC khi đưa vào f-string để tránh SyntaxError
        display_text = self.ids.data_display.text.replace('\\n', ' | ').replace('\n', ' | ')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # f-string sạch, không chứa dấu gạch chéo ngược trong biểu thức { }
        log_entry = f"[{timestamp}] | {user} | {self.status_type} | {display_text}\n"
        
        try:
            if platform == 'android':
                from jnius import autoclass
                context = autoclass('org.kivy.android.PythonActivity').mActivity
                storage_dir = context.getExternalFilesDir(None).getAbsolutePath()
            else:
                storage_dir = "."
            
            file_path = os.path.join(storage_dir, "device_logs.txt")
            with open(file_path, "a", encoding='utf-8') as f:
                f.write(log_entry)
            self.ids.data_display.text = "LƯU LOG THÀNH CÔNG!"
        except Exception as e:
            self.ids.data_display.text = f"Lỗi lưu file: {str(e)}"

class LabelApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.screen = Builder.load_string(KV)
        return self.screen

    def on_start(self):
        # Nạp widget input sau khi App đã khởi tạo xong giao diện chính
        Clock.schedule_once(self.create_input_field, 0.2)
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.CAMERA, 
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.READ_EXTERNAL_STORAGE
            ])

    def create_input_field(self, dt):
        from kivymd.uix.textfield import MDTextField
        self.screen.user_input = MDTextField(
            hint_text="Tên người thực hiện", 
            mode="rectangle"
        )
        self.screen.ids.input_container.add_widget(self.screen.user_input)

if __name__ == "__main__":
    LabelApp().run()
