from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock
import os

# Sử dụng r''' để tránh lỗi escape character trong chuỗi KV
KV = r'''
MainScreen:
    orientation: 'vertical'
    padding: "20dp"
    spacing: "10dp"
    
    MDLabel:
        text: "SAMSUNG STABILITY v2.3"
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
            text: "Camera chờ nạp..."
            halign: "center"
            color: 1, 1, 1, 0.5

    MDCard:
        orientation: 'vertical'
        padding: "15dp"
        size_hint_y: 0.5
        radius: [15,]
        
        MDLabel:
            id: status_log
            text: "HƯỚNG DẪN:\n1. Nhấn CẤP QUYỀN\n2. Đợi 3 giây hệ thống ổn định\n3. Nhấn MỞ CAMERA"
            halign: "center"
            theme_text_color: "Secondary"

    MDFillRoundFlatButton:
        id: action_btn
        text: "BƯỚC 1: CẤP QUYỀN TRUY CẬP"
        size_hint_x: 1
        height: "56dp"
        md_bg_color: 0, 0.4, 0.8, 1
        on_release: root.samsung_logic_flow()
'''

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1

    def samsung_logic_flow(self):
        if self.step == 1:
            self.request_samsung_permissions()
        elif self.step == 2:
            self.activate_camera()

    def request_samsung_permissions(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            # Xin quyền không dùng callback để tránh văng App trên Samsung
            request_permissions([
                Permission.CAMERA, 
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.READ_EXTERNAL_STORAGE
            ])
            
            # Xử lý chuỗi thông báo an toàn
            msg = "HỆ THỐNG ĐANG XÁC THỰC...\nVUI LÒNG ĐỢI 3 GIÂY"
            self.ids.status_log.text = msg
            self.ids.action_btn.disabled = True
            Clock.schedule_once(self.prepare_step_2, 3)
        else:
            self.prepare_step_2(0)

    def prepare_step_2(self, dt):
        self.step = 2
        self.ids.action_btn.disabled = False
        self.ids.action_btn.text = "BƯỚC 2: KÍCH HOẠT CAMERA"
        self.ids.action_btn.md_bg_color = (0, 0.6, 0.3, 1)
        
        # Tránh dùng f-string chứa dấu gạch chéo ngược
        msg = "HỆ THỐNG ĐÃ SẴN SÀNG\nNhấn nút để bắt đầu quét"
        self.ids.status_log.text = msg

    def activate_camera(self):
        from kivy.uix.camera import Camera
        try:
            # Khởi tạo tối giản để Samsung tự chọn driver phù hợp
            self.cam = Camera(play=True, allow_stretch=True)
            self.ids.cam_box.clear_widgets()
            self.ids.cam_box.add_widget(self.cam)
            
            self.ids.status_log.text = "CAMERA ĐÃ CHẠY THÀNH CÔNG!"
            self.ids.action_btn.text = "QUÉT NHÃN NGAY"
            self.step = 3
        except Exception as e:
            # Chuyển lỗi thành chuỗi an toàn trước khi hiển thị
            err_msg = "Lỗi nạp phần cứng: " + str(e)
            self.ids.status_log.text = err_msg

class LabelApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        # Tránh lỗi compile khi load string KV
        return Builder.load_string(KV)

if __name__ == "__main__":
    LabelApp().run()
