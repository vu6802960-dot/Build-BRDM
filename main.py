from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock
from kivy.graphics import Rotate, PushMatrix, PopMatrix
from kivy.network.urlrequest import UrlRequest
from PIL import Image
import io, base64, urllib.parse, os, re
from datetime import datetime

# Sử dụng r''' để bảo vệ các ký tự đặc biệt trong giao diện
KV = r'''
MainScreen:
    orientation: 'vertical'
    padding: "10dp"
    spacing: "5dp"
    
    MDLabel:
        text: "DEVICE MANAGER PRO v3.0"
        halign: "center"
        bold: True
        font_style: "H6"
        size_hint_y: None
        height: "40dp"

    BoxLayout:
        id: cam_container
        size_hint_y: 0.35
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size

    MDCard:
        orientation: 'vertical'
        padding: "12dp"
        spacing: "10dp"
        size_hint_y: 0.65
        radius: [15,]
        elevation: 1

        MDTextField:
            id: user_name
            hint_text: "Tên người thực hiện"
            mode: "rectangle"
            size_hint_y: None
            height: "52dp"

        BoxLayout:
            size_hint_y: None
            height: "50dp"
            spacing: "15dp"
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
                text: "KẾT QUẢ QUÉT SẼ HIỂN THỊ TẠI ĐÂY"
                theme_text_color: "Secondary"
                font_style: "Caption"
                size_hint_y: None
                height: self.texture_size[1]
                halign: "left"

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
            height: "45dp"
            on_release: root.export_log()
'''

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.status = "MUON"
        self.cam = None

    def set_status(self, mode):
        self.status = mode
        # Cập nhật màu nút bấm
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
        try:
            # Khởi tạo camera
            self.cam = Camera(play=True, allow_stretch=True, keep_ratio=True)
            
            # Xoay Texture 90 độ để sửa lỗi camera bị ngang trên Samsung
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
                
            self.ids.cam_container.clear_widgets()
            self.ids.cam_container.add_widget(self.cam)
            self.step = 3
            self.ids.main_btn.text = "BƯỚC 3: QUÉT NHÃN (OCR)"
        except Exception as e:
            self.ids.data_display.text = "Lỗi Camera: " + str(e)

    def capture_ocr(self):
        if not self.cam or not self.cam.texture:
            return
        
        self.ids.data_display.text = "Đang xử lý ảnh..."
        try:
            # Trích xuất pixels từ texture
            pixels = self.cam.texture.pixels
            img = Image.frombytes('RGBA', self.cam.texture.size, pixels).convert('RGB')
            
            # Xoay ảnh PIL cho đúng chiều đứng trước khi gửi đi quét
            img = img.rotate(-90, expand=True)
            
            # Chuyển ảnh sang Base64
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=85)
            b64_data = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            # Chuẩn bị tham số cho API
            raw_payload = {
                'apikey': 'helloworld',
                'base64Image': "data:image/jpg;base64," + b64_data
            }
            payload = urllib.parse.urlencode(raw_payload)
            UrlRequest("https://api.ocr.space/parse/image", req_body=payload, on_success=self.ocr_success)
        except Exception as e:
            self.ids.data_display.text = "Lỗi xử lý OCR: " + str(e)

    def ocr_success(self, req, res):
        try:
            parsed_text = res['ParsedResults'][0]['ParsedText']
            # Hiển thị kết quả an toàn
            self.ids.data_display.text = "DỮ LIỆU ĐỌC ĐƯỢC:\n" + parsed_text
        except:
            self.ids.data_display.text = "Lỗi: Không tìm thấy nội dung chữ."

    def export_log(self):
        user = self.ids.user_name.text
        # Làm sạch chuỗi trước khi lưu
        raw_content = self.ids.data_display.text
        clean_content = raw_content.replace('\n', ' | ')
        
        if not user or user.strip() == "":
            self.ids.data_display.text = "VUI LÒNG NHẬP TÊN NGƯỜI LÀM!"
            return
            
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # f-string đơn giản không chứa dấu gạch chéo ngược
        log_line = f"[{now}] | {user} | {self.status} | {clean_content}\n"
        
        try:
            # Đường dẫn an toàn trên Samsung Android 11+
            if platform == 'android':
                path = "/sdcard/Documents/device_logs.txt"
            else:
                path = "device_logs.txt"
                
            with open(path, "a", encoding="utf-8") as f:
                f.write(log_line)
            self.ids.data_display.text = "LƯU THÀNH CÔNG VÀO THƯ MỤC DOCUMENTS!"
        except Exception as e:
            self.ids.data_display.text = "Lỗi lưu file: " + str(e)

class LabelApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

if __name__ == "__main__":
    LabelApp().run()
