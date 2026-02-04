from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock
# Lưu ý: Các thư viện nặng được import bên trong hàm để tránh crash khi mở App

KV = r'''
MainScreen:
    orientation: 'vertical'
    padding: "10dp"
    spacing: "5dp"
    
    MDLabel:
        text: "SAMSUNG MANAGER v3.1"
        halign: "center"
        bold: True
        font_style: "H6"
        size_hint_y: None
        height: "45dp"

    BoxLayout:
        id: cam_container
        size_hint_y: 0.35
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        MDLabel:
            id: cam_hint
            text: "Camera sẽ hiển thị tại Bước 2"
            halign: "center"
            color: 1, 1, 1, 0.5

    MDCard:
        orientation: 'vertical'
        padding: "12dp"
        spacing: "8dp"
        size_hint_y: 0.65
        radius: [15,]
        elevation: 1

        MDTextField:
            id: user_name
            hint_text: "Tên người mượn/trả"
            mode: "rectangle"
            size_hint_y: None
            height: "50dp"

        BoxLayout:
            size_hint_y: None
            height: "50dp"
            spacing: "10dp"
            MDRaisedButton:
                id: btn_muon
                text: "MƯỢN"
                md_bg_color: 0, 0.5, 0.8, 1
                on_release: root.set_status("MUON")
            MDRaisedButton:
                id: btn_tra
                text: "TRẢ"
                md_bg_color: 0.5, 0.5, 0.5, 1
                on_release: root.set_status("TRA")

        MDScrollView:
            MDLabel:
                id: data_display
                text: "Trạng thái: Sẵn sàng thực hiện"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Secondary"
                font_style: "Caption"

        MDFillRoundFlatButton:
            id: main_btn
            text: "BƯỚC 1: CẤP QUYỀN"
            size_hint_x: 1
            height: "50dp"
            on_release: root.logic_controller()

        MDRectangleFlatIconButton:
            icon: "file-export"
            text: "XUẤT DỮ LIỆU (LOG)"
            size_hint_x: 1
            on_release: root.export_log()
'''

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.status = "MUON"

    def set_status(self, mode):
        self.status = mode
        if mode == "MUON":
            self.ids.btn_muon.md_bg_color = (0, 0.5, 0.8, 1)
            self.ids.btn_tra.md_bg_color = (0.5, 0.5, 0.5, 1)
        else:
            self.ids.btn_muon.md_bg_color = (0.5, 0.5, 0.5, 1)
            self.ids.btn_tra.md_bg_color = (0.8, 0.2, 0.2, 1)

    def logic_controller(self):
        if self.step == 1:
            self.ask_perms()
        elif self.step == 2:
            self.start_cam()
        else:
            self.capture_ocr()

    def ask_perms(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            self.ids.main_btn.disabled = True
            Clock.schedule_once(lambda dt: self.enable_step2(), 3)
        else:
            self.enable_step2()

    def enable_step2(self):
        self.step = 2
        self.ids.main_btn.disabled = False
        self.ids.main_btn.text = "BƯỚC 2: MỞ CAMERA"
        self.ids.main_btn.md_bg_color = (0, 0.6, 0.3, 1)

    def start_cam(self):
        from kivy.uix.camera import Camera
        from kivy.graphics import Rotate, PushMatrix, PopMatrix
        try:
            self.cam = Camera(play=True, allow_stretch=True, keep_ratio=True)
            # Sửa lỗi xoay màn hình trên Samsung
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
                
            self.ids.cam_container.clear_widgets()
            self.ids.cam_container.add_widget(self.cam)
            self.step = 3
            self.ids.main_btn.text = "BƯỚC 3: QUÉT NHÃN NGAY"
        except Exception as e:
            self.ids.data_display.text = "Lỗi khởi tạo Cam: " + str(e)

    def capture_ocr(self):
        import io, base64, urllib.parse
        from PIL import Image
        from kivy.network.urlrequest import UrlRequest
        
        if not hasattr(self, 'cam') or not self.cam.texture: return
        
        self.ids.data_display.text = "Đang xử lý hình ảnh..."
        try:
            pixels = self.cam.texture.pixels
            img = Image.frombytes('RGBA', self.cam.texture.size, pixels).convert('RGB')
            # Xoay ảnh PIL đứng lại trước khi gửi API
            img = img.rotate(-90, expand=True)
            
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            payload = urllib.parse.urlencode({
                'apikey': 'helloworld', # Nên thay bằng key cá nhân của bạn
                'base64Image': "data:image/jpg;base64," + b64
            })
            UrlRequest("https://api.ocr.space/parse/image", req_body=payload, on_success=self.ocr_success)
        except Exception as e:
            self.ids.data_display.text = "Lỗi OCR: " + str(e)

    def ocr_success(self, req, res):
        try:
            text = res['ParsedResults'][0]['ParsedText']
            self.ids.data_display.text = "DỮ LIỆU QUÉT ĐƯỢC:\n" + text
        except:
            self.ids.data_display.text = "Không tìm thấy nội dung chữ trong ảnh."

    def export_log(self):
        from datetime import datetime
        user = self.ids.user_name.text
        if not user or user.strip() == "":
            self.ids.data_display.text = "LỖI: BẠN CHƯA NHẬP TÊN!"
            return
            
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = self.ids.data_display.text.replace('\n', ' ')
        log_line = f"[{now}] | {user} | {self.status} | {content}\n"
        
        try:
            # Đường dẫn an toàn cho Samsung
            path = "/sdcard/Documents/device_logs.txt" if platform == 'android' else "logs.txt"
            with open(path, "a", encoding="utf-8") as f:
                f.write(log_line)
            self.ids.data_display.text = "ĐÃ LƯU LOG VÀO THƯ MỤC DOCUMENTS!"
        except Exception as e:
            self.ids.data_display.text = "Lỗi xuất file: " + str(e)

class LabelApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

if __name__ == "__main__":
    LabelApp().run()
