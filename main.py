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
        text: "DEVICE MANAGER PRO v4.9"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '40dp'

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
            id: cam_status
            text: "Màn hình Camera"
            color: (0.5, 0.5, 0.5, 1)

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.5
        spacing: '5dp'
        
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
            text: "Thông báo hệ thống"
            color: (0.1, 0.1, 0.1, 1)
            text_size: self.width, None
            halign: 'center'

    Button:
        id: main_btn
        text: "BƯỚC 1: CẤP QUYỀN"
        background_color: (0.1, 0.5, 0.8, 1)
        size_hint_y: None
        height: '60dp'
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
                request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
            self.root.ids.main_btn.text = "BƯỚC 2: MỞ CAMERA"
            self.step = 2
        elif self.step == 2:
            self.start_camera()

    def start_camera(self):
        try:
            self.root.ids.cam_container.clear_widgets()
            # Thử mở camera với tham số tối giản để Samsung dễ nhận
            self.cam = Camera(play=True, index=0, resolution=(640, 480))
            
            # Ép xoay texture
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
                
            self.root.ids.cam_container.add_widget(self.cam)
            
            # QUAN TRỌNG: Gọi lệnh play sau khi add vào layout 0.5 giây
            Clock.schedule_once(self.force_play, 0.5)
            
            self.root.ids.main_btn.text = "HỆ THỐNG SẴN SÀNG"
            self.root.ids.result_data.text = "Nếu vẫn đen, hãy nhấn lại Bước 2"
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi Cam: {str(e)}"

    def force_play(self, dt):
        self.cam.play = False
        self.cam.play = True

    def export_data(self):
        name = self.root.ids.user_input.text
        if not name:
            self.root.ids.result_data.text = "Lỗi: Nhập tên người mượn!"
            return

        # SỬA LỖI GHI FILE: Dùng thư mục nội bộ của App (Tránh lỗi Permission)
        if platform == 'android':
            from android.storage import primary_external_storage_path
            # Thay vì ghi trực tiếp vào root, ta ghi vào thư mục Documents của máy
            base_path = primary_external_storage_path()
            dir_path = os.path.join(base_path, "Documents")
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        else:
            dir_path = os.path.expanduser("~")

        file_name = "NhatKy_ThietBi.csv"
        full_path = os.path.join(dir_path, file_name)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            exists = os.path.isfile(full_path)
            with open(full_path, 'a', encoding='utf-8') as f:
                if not exists:
                    f.write("ThoiGian,NguoiMuon,CheDo\n")
                f.write(f"{now},{name},{self.mode}\n")
            self.root.ids.result_data.text = f"LƯU THÀNH CÔNG!\nTại: Documents/{file_name}"
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi ghi file: {str(e)}"

if __name__ == '__main__':
    DeviceApp().run()
