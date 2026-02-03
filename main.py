from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window
from kivy.utils import platform
from PIL import Image
from datetime import datetime
import io, base64, urllib.parse, re

# Cấu hình hệ thống: Chống xoay và hỗ trợ bàn phím
Window.softinput_mode = "below_target"

KV = '''
MainScreen:
    orientation: 'vertical'
    padding: "10dp"
    spacing: "8dp"

    MDLabel:
        text: "QUẢN LÝ THIẾT BỊ"
        halign: "center"
        bold: True
        font_style: "H6"
        size_hint_y: None
        height: "40dp"

    Camera:
        id: cam
        resolution: (1280, 720)
        play: True
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
            size_hint_y: None
            height: "50dp"

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

        MDSeparator:
            height: "1dp"

        MDLabel:
            id: data_display
            text: "Model: --\\nIMEI: --\\nSMSN: --"
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
        if not camera.texture: return
        try:
            pixels = camera.texture.pixels
            pil_image = Image.frombytes('RGBA', camera.texture.size, pixels).convert('RGB')
            buf = io.BytesIO()
            pil_image.save(buf, format='JPEG', quality=85)
            
            self.ids.data_display.text = "Đang nhận diện qua API..."
            base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            payload = urllib.parse.urlencode({
                'apikey': 'helloworld', 
                'base64Image': f"data:image/jpg;base64,{base64_image}",
                'language': 'eng'
            })
            UrlRequest("https://api.ocr.space/parse/image", 
                       req_body=payload, 
                       on_success=self.on_ocr_success,
                       on_failure=lambda req, res: self.on_error("Lỗi kết nối API"))
        except Exception as e:
            self.ids.data_display.text = f"Lỗi: {str(e)}"

    def on_ocr_success(self, request, result):
        try:
            text = result['ParsedResults'][0]['ParsedText']
            imei_match = re.search(r'\d{15}', text)
            imei_val = imei_match.group(0) if imei_match else "N/A"
            
            model_match = re.search(r'(SM-[A-Z0-9]+)', text)
            model_val = model_match.group(0) if model_match else "N/A"
            
            lines = text.split('\n')
            smsn_val = "N/A"
            for line in lines:
                clean = line.strip()
                if 8 <= len(clean) <= 12 and any(c.isalpha() for c in clean):
                    smsn_val = clean
                    break
                    
            self.ids.data_display.text = f"Model: {model_val}\nIMEI: {imei_val}\nSMSN: {smsn_val}"
        except:
            self.ids.data_display.text = "Không tìm thấy dữ liệu trên nhãn"

    def on_error(self, message):
        self.ids.data_display.text = message

    def export_data(self):
        user = self.ids.user_input.text
        if not user:
            self.ids.data_display.text = "LỖI: CHƯA NHẬP TÊN NGƯỜI LÀM!"
            return
            
        # Sửa lỗi f-string: Tách phần replace ra khỏi f-string
        raw_data = self.ids.data_display.text
        clean_data = raw_data.replace('\n', ' | ')
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Tạo nội dung log an toàn
        log_entry = f"[{timestamp}] | {user} | {self.status_type} | {clean_data}\n"
        
        try:
            # Lưu file vào thư mục nội bộ
            with open("device_logs.txt", "a", encoding='utf-8') as f:
                f.write(log_entry)
            self.ids.data_display.text = f"ĐÃ LƯU THÀNH CÔNG!\nUser: {user}"
        except Exception as e:
            self.ids.data_display.text = f"Lỗi lưu file: {str(e)}"

class LabelApp(MDApp):
    def build(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET])
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            activity.getWindow().addFlags(autoclass('android.view.WindowManager$LayoutParams').FLAG_KEEP_SCREEN_ON)
        return Builder.load_string(KV)

if __name__ == "__main__":
    LabelApp().run()
