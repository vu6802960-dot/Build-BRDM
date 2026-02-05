import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.uix.textinput import TextInput
from kivy.utils import platform
from kivy.clock import Clock
from kivy.graphics import Rotate, PushMatrix, PopMatrix

# Giao diện dùng Kivy thuần (Native) để đảm bảo không bị văng trên Samsung
KV = r'''
<CustomButton@Button>:
    background_normal: ''
    background_color: (0.1, 0.5, 0.8, 1)
    font_size: '16sp'
    size_hint_y: None
    height: '50dp'

BoxLayout:
    orientation: 'vertical'
    padding: '10dp'
    spacing: '10dp'
    canvas.before:
        Color:
            rgba: (0.95, 0.95, 0.95, 1)
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "DEVICE MANAGER PRO v4.7"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '40dp'

    # Khung Camera
    BoxLayout:
        id: cam_container
        size_hint_y: 0.4
        canvas.before:
            Color:
                rgba: (0, 0, 0, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Camera Preview"
            color: (0.5, 0.5, 0.5, 1)

    # Vùng nhập liệu
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.5
        spacing: '5dp'
        
        Label:
            text: "Tên người mượn/trả:"
            color: (0, 0, 0, 1)
            halign: 'left'
            text_size: self.size
            size_hint_y: None
            height: '25dp'
        
        TextInput:
            id: user_input
            multiline: False
            size_hint_y: None
            height: '45dp'
            hint_text: "Nhập tên tại đây..."

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            Button:
                id: type_btn
                text: "CHẾ ĐỘ: MƯỢN"
                on_release: app.toggle_mode()
            Button:
                text: "XUẤT FILE CSV"
                background_color: (0.5, 0.5, 0.5, 1)
                on_release: app.export_data()

        Label:
            text: "DỮ LIỆU QUÉT ĐƯỢC:"
            color: (0, 0, 0, 1)
            bold: True
            size_hint_y: None
            height: '25dp'
        
        Label:
            id: result_data
            text: "Đang chờ quét..."
            color: (0.2, 0.2, 0.2, 1)
            valign: 'top'
            text_size: self.size

    CustomButton:
        id: main_btn
        text: "1. CẤP QUYỀN & MỞ CAM"
        on_release: app.handle_logic()
'''

class DeviceApp(App):
    def build(self):
        self.step = 1
        self.mode = "MƯỢN"
        return Builder.load_string(KV)

    def toggle_mode(self):
        if self.mode == "MƯỢN":
            self.mode = "TRẢ"
            self.root.ids.type_btn.background_color = (0.8, 0.2, 0.2, 1)
        else:
            self.mode = "MƯỢN"
            self.root.ids.type_btn.background_color = (0.1, 0.5, 0.8, 1)
        self.root.ids.type_btn.text = f"CHẾ ĐỘ: {self.mode}"

    def handle_logic(self):
        if self.step == 1:
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA])
            self.root.ids.main_btn.text = "2. KHỞI CHẠY CAMERA"
            self.step = 2
        elif self.step == 2:
            self.start_camera()

    def start_camera(self):
        try:
            cam = Camera(play=True, resolution=(-1, -1))
            
            # XOAY DỌC CAMERA CHO SAMSUNG
            with cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=cam.center)
            with cam.canvas.after:
                PopMatrix()
                
            self.root.ids.cam_container.clear_widgets()
            self.root.ids.cam_container.add_widget(cam)
            self.root.ids.main_btn.text = "QUÉT DỮ LIỆU (SCAN)"
            self.step = 3
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi: {e}"

    def export_data(self):
        name = self.root.ids.user_input.text
        if not name:
            self.root.ids.result_data.text = "Vui lòng nhập tên!"
            return
        self.root.ids.result_data.text = f"Đã xuất dữ liệu cho {name}"

if __name__ == '__main__':
    DeviceApp().run()
