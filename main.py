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
        text: "QUẢN LÝ THIẾT BỊ v1.4"
        halign: "center"
        bold: True
        font_style: "H6"
        size_hint_y: None
        height: "40dp"

    Camera:
        id: cam
        resolution: (1280, 720)
        play: False 
        allow_stretch: True
        size_hint_y: 0.4

    MDCard:
        orientation: 'vertical'
        padding: "12dp"
        spacing: "8dp"
        size_hint_y: 0.5
        elevation: 2
        radius: [15, ]

        MDTextField:
            id: user_input
            hint_text: "Tên người thực hiện"
            mode: "rectangle"

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
            text: "Trạng thái: Đang khởi động..."
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
        if s_type == "MUON":
            self.ids.btn_muon.md_bg_color = (0, 0.5, 0.8, 1)
            self.ids.btn_tra.md_bg_color = (0.5, 0.5, 0.5, 1)
        else:
            self.ids.btn_tra.md_bg_color = (0.8, 0.2, 0.2, 1)
            self.ids.btn_muon.md_bg_color = (0.5, 0.5, 0.5, 1)

    def capture_and_read(self):
        camera = self.ids.cam
        if not camera.play or not camera.texture:
            self.ids.data_display.text = "Lỗi: Camera chưa sẵn sàng"
            return
        try:
            pixels = camera.texture.pixels
            pil_image = Image.frombytes('RGBA', camera.texture.size, pixels).convert('RGB')
            buf = io.BytesIO()
            pil_image.save(buf, format='JPEG', quality=85)
            self.ids.data_display.text = "Đang nhận diện..."
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
            lines = text.split('\n')
            smsn_val = next((l.strip() for l in lines if 8 <= len(l.strip()) <= 12 and any(c.isalpha() for c in l.strip())), "N/A")
            self.ids.data_display.text = f"Model: {model.group(0) if model else 'N/A'}\nIMEI: {imei.group(0) if imei else 'N/A'}\nSMSN: {smsn_val}"
        except:
            self.ids.data_display.text = "Lỗi đọc nhãn"

    def export_data(self):
        user = self.ids.user_input.text
        if not user:
            self.ids.data_display.text = "VUI LÒNG NHẬP TÊN!"
            return
        
        data_text = self.ids.data_display.text.replace('\n', ' | ')
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | {user} | {self.status_type} | {data_text}\n"
        
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
            self.ids.data_display.text = f"ĐÃ LƯU!\nĐường dẫn: Android/data/.../files/"
        except Exception as e:
            self.ids.data_display.text = f"Lỗi lưu: {str(e)}"

class LabelApp(MDApp):
    def build(self):
        self.screen = Builder.load_string(KV)
        return self.screen

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], self.check_permissions)
        else:
            self.screen.ids.cam.play = True

    def check_permissions(self, permissions, results):
        if all(results):
            Clock.schedule_once(lambda dt: self.enable_features(), 0.5)
        else:
            self.screen.ids.data_display.text = "LỖI: Chưa cấp quyền Camera/Bộ nhớ"

    def enable_features(self):
        self.screen.ids.cam.play = True
        self.screen.ids.data_display.text = "Sẵn sàng."
        from jnius import autoclass
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        activity.getWindow().addFlags(autoclass('android.view.WindowManager$LayoutParams').FLAG_KEEP_SCREEN_ON)

if __name__ == "__main__":
    LabelApp().run()
