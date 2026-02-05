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
        text: "DEVICE MANAGER PRO v4.9.1"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '40dp'

    BoxLayout:
        id: cam_container
        size_hint_y: 0.45
        canvas.before:
            Color:
                rgba: (0, 0, 0, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            id: cam_status
            text: "Chưa có tín hiệu Camera"
            color: (0.5, 0.5, 0.5, 1)

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.45
        spacing: '8dp'
        
        TextInput:
            id: user_input
            multiline: False
            size_hint_y: None
            height: '45dp'
            hint_text: "Tên người mượn/trả..."

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
            self.root.ids.main_btn.text = "BƯỚC 2: MỞ CAMERA (NHẤN LẠI NẾU ĐEN)"
            self.root.ids.main_btn.background_color = (0.2, 0.6, 0.2, 1)
            self.step = 2
        elif self.step == 2:
            self.start_camera()

    def start_camera(self):
        try:
            # Xóa widget cũ để giải phóng tài nguyên trước khi mở lại
            self.root.ids.cam_container.clear_widgets()
            
            # TỰ ĐỘNG THÍCH ỨNG: Không ép resolution, để mặc định để Samsung tự chọn
            self.cam = Camera(play=True, index=0) 
            
            # Xoay dọc camera
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
                
            self.root.ids.cam_container.add_widget(self.cam)
            self.root.ids.result_data.text = "Đang kết nối ống kính... Vui lòng đợi"
            
            # Buộc hệ thống cập nhật lại luồng sau 1 giây
            Clock.schedule_once(self.refresh_cam, 1.0)
            
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi: {str(e)}"

    def refresh_cam(self, dt):
        if hasattr(self, 'cam'):
            self.cam.play = False
            self.cam.play = True
            self.root.ids.result_data.text = "Camera đã kích hoạt. Nhấn lại nút xanh nếu vẫn đen."

    def export_data(self):
        name = self.root.ids.user_input.text
        if not name:
            self.root.ids.result_data.text = "Nhập tên trước khi xuất!"
            return

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
            self.root.ids.result_data.text = f"LƯU OK: {now}\nTrong mục Documents"
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi file: {str(e)}"

if __name__ == '__main__':
    DeviceApp().run()
