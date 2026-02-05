from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock
import os

# Sử dụng r''' để bảo vệ chuỗi KV
KV = r'''
MainScreen:
    orientation: 'vertical'
    padding: "20dp"
    
    MDLabel:
        text: "SAMSUNG STABILITY v3.2"
        halign: "center"
        bold: True
        size_hint_y: None
        height: "50dp"

    BoxLayout:
        id: cam_container
        size_hint_y: 0.4
        canvas.before:
            Color: rgba: 0, 0, 0, 1
            Rectangle: pos: self.pos, size: self.size
        MDLabel:
            id: hint_text
            text: "Chờ kích hoạt..."
            halign: "center"
            color: 1, 1, 1, 0.5

    MDCard:
        orientation: 'vertical'
        padding: "15dp"
        size_hint_y: 0.6
        MDLabel:
            id: status_log
            text: "1. Nhấn CẤP QUYỀN\n2. Chọn 'Cho phép'\n3. Đợi App tự nạp (5 giây)"
            halign: "center"

    MDFillRoundFlatButton:
        id: main_btn
        text: "KÍCH HOẠT HỆ THỐNG"
        size_hint_x: 1
        on_release: root.start_samsung_flow()
'''

class MainScreen(BoxLayout):
    def start_samsung_flow(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            # CHỈ xin quyền Camera. Quyền bộ nhớ trên Android 11+ xử lý khác.
            request_permissions([Permission.CAMERA])
            
            self.ids.main_btn.disabled = True
            self.ids.status_log.text = "HỆ THỐNG ĐANG XỬ LÝ...\nVUI LÒNG ĐỢI 5 GIÂY"
            
            # Tăng thời gian chờ lên 5 giây để Samsung Knox hoàn tất kiểm tra
            Clock.schedule_once(self.delayed_camera_load, 5)
        else:
            self.delayed_camera_load(0)

    def delayed_camera_load(self, dt):
        from kivy.uix.camera import Camera
        try:
            # Tạo widget camera với cấu hình thấp nhất để an toàn
            self.cam = Camera(play=True, resolution=(-1, -1))
            self.ids.cam_container.clear_widgets()
            self.ids.cam_container.add_widget(self.cam)
            
            self.ids.status_log.text = "KÍCH HOẠT THÀNH CÔNG!"
            self.ids.main_btn.text = "QUÉT DỮ LIỆU"
            self.ids.main_btn.disabled = False
        except Exception as e:
            self.ids.status_log.text = "Lỗi phần cứng: " + str(e)

class LabelApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == "__main__":
    LabelApp().run()
