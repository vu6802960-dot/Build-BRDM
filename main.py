from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock

KV = r'''
MainScreen:
    orientation: 'vertical'
    padding: "20dp"
    
    MDLabel:
        text: "SAMSUNG STABILITY v3.4"
        halign: "center"
        bold: True
        size_hint_y: None
        height: "50dp"

    BoxLayout:
        id: cam_container
        size_hint_y: 0.4
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        MDLabel:
            text: "Giao diện đã tải xong"
            halign: "center"
            color: 1, 1, 1, 0.5

    MDCard:
        padding: "15dp"
        size_hint_y: 0.4
        MDLabel:
            id: status_log
            text: "Nhấn nút để xin quyền và mở Cam"
            halign: "center"

    MDFillRoundFlatButton:
        id: btn
        text: "KÍCH HOẠT HỆ THỐNG"
        size_hint_x: 1
        on_release: root.start_process()
'''

class MainScreen(BoxLayout):
    def start_process(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA])
            self.ids.status_log.text = "Đang xin quyền...\nĐợi 3 giây..."
            Clock.schedule_once(self.open_camera, 3)
        else:
            self.open_camera(0)

    def open_camera(self, dt):
        from kivy.uix.camera import Camera
        try:
            self.cam = Camera(play=True, resolution=(-1, -1))
            self.ids.cam_container.clear_widgets()
            self.ids.cam_container.add_widget(self.cam)
            self.ids.status_log.text = "CAMERA SẴN SÀNG!"
        except Exception as e:
            self.ids.status_log.text = "Lỗi: " + str(e)

class LabelApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == "__main__":
    LabelApp().run()
