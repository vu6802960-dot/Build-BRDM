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
        text: "DEVICE MANAGER PRO v5.1"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '40dp'

    # Vùng chứa Camera
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
            text: "Dữ liệu: Đang chờ quét..."
            color: (0, 0.5, 0, 1)
            bold: True
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
        self.last_scan = "Chưa có dữ liệu"
        return Builder.load_string(KV)

    def toggle_mode(self):
        self.mode = "TRA" if self.mode == "MUON" else "MUON"
        self.root.ids.type_btn.text = f"CHẾ ĐỘ: {self.mode}"

    def handle_logic(self):
        if self.step == 1:
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            self.root.ids.main_btn.text = "BƯỚC 2: MỞ CAMERA"
            self.step = 2
        elif self.step == 2:
            self.start_camera_full()
        elif self.step == 3:
            self.scan_now()

    def start_camera_full(self):
        self.root.ids.cam_container.clear_widgets()
        # Khởi tạo camera với size lớn hơn để khi xoay nó không bị hở trắng
        self.cam = Camera(play=True, index=0, resolution=(640, 480))
        self.root.ids.cam_container.add_widget(self.cam)
        
        Clock.schedule_once(self.apply_rotation_full, 1.0)

    def apply_rotation_full(self, dt):
        try:
            # 1. Thực hiện xoay
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
            
            # 2. ÉP SIZE: Đảo ngược chiều rộng/cao để lấp đầy khung
            # Một số máy cần tăng size lên 1.5 lần để bù đắp khoảng trống khi xoay
            self.cam.size = (self.root.ids.cam_container.height, self.root.ids.cam_container.width)
            self.cam.center = self.root.ids.cam_container.center
            
            self.root.ids.result_data.text = "Đã tối ưu hiển thị. Sẵn sàng quét!"
            self.root.ids.main_btn.text = "BƯỚC 3: NHẤN ĐỂ QUÉT MÃ"
            self.root.ids.main_btn.background_color = (0.8, 0.5, 0, 1)
            self.step = 3
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi hiển thị: {e}"

    def scan_now(self):
        # Logic giả lập quét (Snapshot)
        # Trong thực tế, đây là nơi ta gọi thư viện phân tích hình ảnh
        now = datetime.datetime.now().strftime("%H%M%S")
        self.last_scan = f"DEV-{now}" # Tạo mã thiết bị giả lập dựa trên thời gian
        self.root.ids.result_data.text = f"QUÉT THÀNH CÔNG: {self.last_scan}"
        
        # Nháy màn hình để báo hiệu đã quét
        self.root.ids.cam_container.opacity = 0.5
        Clock.schedule_once(lambda dt: setattr(self.root.ids.cam_container, 'opacity', 1), 0.1)

    def export_data(self):
        name = self.root.ids.user_input.text
        if not name:
            self.root.ids.result_data.text = "CẦN NHẬP TÊN!"
            return
        
        if platform == 'android':
            from android.storage import primary_external_storage_path
            dir_path = os.path.join(primary_external_storage_path(), "Documents")
        else:
            dir_path = os.path.expanduser("~")

        if not os.path.exists(dir_path): os.makedirs(dir_path)
        full_path = os.path.join(dir_path, "NhatKy_ThietBi.csv")
        dt = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")

        try:
            with open(full_path, 'a', encoding='utf-8') as f:
                # Lưu cả Mã Thiết Bị vừa quét được
                f.write(f"{dt},{name},{self.mode},{self.last_scan}\n")
            self.root.ids.result_data.text = f"ĐÃ LƯU: {self.last_scan}\nTại Documents"
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi lưu: {str(e)}"

if __name__ == '__main__':
    DeviceApp().run()
