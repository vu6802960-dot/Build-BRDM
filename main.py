import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.utils import platform
from kivy.clock import Clock
from kivy.graphics import Rotate, PushMatrix, PopMatrix
import os
import datetime

KV = r'''
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
        text: "DEVICE MANAGER PRO v5.0"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '40dp'

    # Vùng Camera chiếm diện tích lớn để dễ quan sát
    BoxLayout:
        id: cam_container
        size_hint_y: 0.55
        canvas.before:
            Color:
                rgba: (0, 0, 0, 1)
            Rectangle:
                pos: self.pos
                size: self.size

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.35
        spacing: '8dp'
        
        TextInput:
            id: user_input
            hint_text: "Tên người mượn/trả..."
            size_hint_y: None
            height: '45dp'
            multiline: False

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
                on_release: app.export_data()

        Label:
            id: result_data
            text: "Trạng thái: Sẵn sàng"
            color: (0.1, 0.1, 0.1, 1)
            text_size: self.width, None
            halign: 'center'

    Button:
        id: main_btn
        text: "BƯỚC 1: CẤP QUYỀN"
        background_color: (0.1, 0.5, 0.8, 1)
        size_hint_y: None
        height: '60dp'
        bold: True
        on_release: app.handle_logic()
'''

class DeviceApp(App):
    def build(self):
        self.step = 1
        self.mode = "MUON"
        return Builder.load_string(KV)

    def toggle_mode(self):
        self.mode = "TRA" if self.mode == "MUON" else "MUON"
        self.root.ids.type_btn.text = f"CHẾ ĐỘ: {self.mode}"

    def handle_logic(self):
        if self.step == 1:
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            self.root.ids.main_btn.text = "BƯỚC 2: KÍCH HOẠT CAMERA"
            self.step = 2
        elif self.step == 2:
            self.start_camera_safe()

    def start_camera_safe(self):
        self.root.ids.cam_container.clear_widgets()
        self.root.ids.result_data.text = "Đang mở ống kính..."
        
        # Mở camera ở độ phân giải an toàn, CHƯA XOAY để tránh crash
        self.cam = Camera(play=True, index=0, resolution=(640, 480))
        self.root.ids.cam_container.add_widget(self.cam)
        
        # Đợi 1.5 giây cho hình ảnh hiện lên ổn định rồi mới ra lệnh xoay
        Clock.schedule_once(self.apply_rotation, 1.5)

    def apply_rotation(self, dt):
        try:
            # Thực hiện xoay 90 độ (hoặc -90 tùy máy) để đưa về chiều dọc
            with self.cam.canvas.before:
                PushMatrix()
                # Origin đặt tại tâm của camera widget
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
            
            self.root.ids.result_data.text = "Camera đã xoay dọc thành công!"
            self.root.ids.main_btn.text = "NHẤN ĐỂ QUÉT LẠI (NẾU CẦN)"
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi xoay: {e}"

    def export_data(self):
        name = self.root.ids.user_input.text
        if not name: return
        
        if platform == 'android':
            from android.storage import primary_external_storage_path
            dir_path = os.path.join(primary_external_storage_path(), "Documents")
            if not os.path.exists(dir_path): os.makedirs(dir_path)
        else:
            dir_path = os.path.expanduser("~")

        full_path = os.path.join(dir_path, "NhatKy_ThietBi.csv")
        now = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")

        try:
            with open(full_path, 'a', encoding='utf-8') as f:
                f.write(f"{now},{name},{self.mode}\n")
            self.root.ids.result_data.text = f"Đã lưu vào Documents/NhatKy_ThietBi.csv"
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi file: {str(e)}"

if __name__ == '__main__':
    DeviceApp().run()
