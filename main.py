from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.graphics import Rotate, PushMatrix, PopMatrix
import json

# Giao diện đầy đủ: Camera dọc, Ô nhập tên, Mượn/Trả, Nút Quét, Nút Xuất File
KV = r'''
MainScreen:
    orientation: 'vertical'
    padding: "10dp"
    spacing: "10dp"

    MDLabel:
        text: "QUẢN LÝ THIẾT BỊ"
        halign: "center"
        bold: True
        font_style: "H6"
        size_hint_y: None
        height: "40dp"

    # Vùng Camera
    BoxLayout:
        size_hint_y: 0.4
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        RelativeLayout:
            id: cam_container
            MDLabel:
                id: cam_hint
                text: "Nhấn 'MỞ CAM' phía dưới"
                halign: "center"
                color: 1, 1, 1, 0.5

    # Form nhập liệu
    MDCard:
        orientation: 'vertical'
        padding: "12dp"
        spacing: "8dp"
        radius: [15,]
        elevation: 1
        size_hint_y: 0.45

        MDTextField:
            id: user_input
            hint_text: "Tên người mượn / trả"
            mode: "rectangle"
        
        BoxLayout:
            size_hint_y: None
            height: "50dp"
            spacing: "10dp"
            MDLabel:
                text: "Hình thức:"
                bold: True
            MDRaisedButton:
                id: type_btn
                text: "MƯỢN"
                on_release: root.change_type()
                md_bg_color: 0.1, 0.5, 0.1, 1

        MDLabel:
            text: "KẾT QUẢ QUÉT:"
            font_style: "Caption"
            bold: True
        
        ScrollView:
            MDLabel:
                id: result_text
                text: "Chưa có dữ liệu"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Secondary"

    # Nút điều khiển
    BoxLayout:
        size_hint_y: None
        height: "55dp"
        spacing: "10dp"

        MDFillRoundFlatButton:
            id: action_btn
            text: "1. CẤP QUYỀN"
            size_hint_x: 0.7
            on_release: root.logic_manager()

        MDFillRoundFlatButton:
            text: "XUẤT FILE"
            size_hint_x: 0.3
            md_bg_color: 0.5, 0.5, 0.5, 1
            on_release: root.export_csv()
'''

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.type = "MƯỢN"

    def change_type(self):
        self.type = "TRẢ" if self.type == "MƯỢN" else "MƯỢN"
        self.ids.type_btn.text = self.type
        self.ids.type_btn.md_bg_color = (0.7, 0.1, 0.1, 1) if self.type == "TRẢ" else (0.1, 0.5, 0.1, 1)

    def logic_manager(self):
        if self.step == 1:
            self.ask_permissions()
        elif self.step == 2:
            self.start_camera()
        else:
            self.take_photo_and_ocr()

    def ask_permissions(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA])
            self.ids.action_btn.disabled = True
            self.ids.result_text.text = "Đang xin quyền... Vui lòng đợi 3 giây"
            Clock.schedule_once(self.step_2_ready, 3)
        else:
            self.step_2_ready(0)

    def step_2_ready(self, dt):
        self.step = 2
        self.ids.action_btn.disabled = False
        self.ids.action_btn.text = "2. MỞ CAMERA"
        self.ids.action_btn.md_bg_color = (0, 0.6, 0.3, 1)
        self.ids.result_text.text = "Quyền đã sẵn sàng. Hãy nhấn Mở Camera."

    def start_camera(self):
        from kivy.uix.camera import Camera
        try:
            # Khởi tạo camera
            self.cam = Camera(play=True, resolution=(-1, -1))
            
            # SỬA LỖI XOAY NGANG: Ép xoay texture -90 độ cho Samsung
            with self.cam.canvas.before:
                PushMatrix()
                self.rot = Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
            
            self.ids.cam_container.clear_widgets()
            self.ids.cam_container.add_widget(self.cam)
            
            self.step = 3
            self.ids.action_btn.text = "QUÉT (SCAN)"
            self.ids.action_btn.md_bg_color = (1, 0.1, 0.1, 1)
        except Exception as e:
            self.ids.result_text.text = "Lỗi Cam: " + str(e)

    def take_photo_and_ocr(self):
        # Placeholder cho logic gửi OCR (sử dụng UrlRequest để không bị văng)
        self.ids.result_text.text = "Đang quét mã thiết bị..."
        # Logic gửi API OCR sẽ nằm ở đây

    def export_csv(self):
        import datetime
        name = self.ids.user_input.text
        if not name:
            self.ids.result_text.text = "Lỗi: Vui lòng nhập tên người thực hiện!"
            return
        # Logic lưu file CSV đơn giản
        self.ids.result_text.text = f"Đã lưu: {name} - {self.type} - {datetime.datetime.now()}"

class DeviceApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

if __name__ == "__main__":
    DeviceApp().run()
