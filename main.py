import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.utils import platform
from kivy.clock import Clock
from kivy.graphics import Rotate, PushMatrix, PopMatrix
import os
import datetime

# Giao diện Native Kivy siêu nhẹ, chống văng tuyệt đối
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
        text: "DEVICE MANAGER PRO v4.8.1"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '40dp'

    # Khung hiển thị Camera
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
            text: "Đang đợi khởi động Camera..."
            color: (0.5, 0.5, 0.5, 1)

    # Vùng nhập liệu và hiển thị trạng thái
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.5
        spacing: '5dp'
        
        TextInput:
            id: user_input
            multiline: False
            size_hint_y: None
            height: '45dp'
            hint_text: "Nhập tên người thực hiện..."
            padding: [10, 10]

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            Button:
                id: type_btn
                text: "CHẾ ĐỘ: MƯỢN"
                background_normal: ''
                background_color: (0.1, 0.5, 0.8, 1)
                on_release: app.toggle_mode()
            Button:
                text: "XUẤT FILE CSV"
                background_normal: ''
                background_color: (0.5, 0.5, 0.5, 1)
                on_release: app.export_data()

        # Vùng hiển thị thông báo/dữ liệu quét
        ScrollView:
            canvas.before:
                Color:
                    rgba: (0.9, 0.9, 0.9, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                id: result_data
                text: "Trạng thái: Sẵn sàng"
                color: (0.1, 0.1, 0.1, 1)
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'center'
                padding: [10, 10]

    # Nút điều khiển chính
    Button:
        id: main_btn
        text: "BƯỚC 1: CẤP QUYỀN CAMERA"
        background_normal: ''
        background_color: (0.2, 0.6, 0.2, 1)
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
        if self.mode == "MUON":
            self.mode = "TRA"
            self.root.ids.type_btn.text = "CHẾ ĐỘ: TRẢ"
            self.root.ids.type_btn.background_color = (0.8, 0.2, 0.2, 1)
        else:
            self.mode = "MUON"
            self.root.ids.type_btn.text = "CHẾ ĐỘ: MƯỢN"
            self.root.ids.type_btn.background_color = (0.1, 0.5, 0.8, 1)

    def handle_logic(self):
        if self.step == 1:
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.CAMERA, 
                    Permission.WRITE_EXTERNAL_STORAGE, 
                    Permission.READ_EXTERNAL_STORAGE
                ])
            self.root.ids.main_btn.text = "BƯỚC 2: KHỞI CHẠY CAMERA"
            self.root.ids.result_data.text = "Đã xin quyền. Hãy nhấn Bước 2."
            self.step = 2
        elif self.step == 2:
            self.start_camera()

    def start_camera(self):
        try:
            # Sử dụng độ phân giải phổ biến để Samsung dễ chấp nhận
            self.cam = Camera(play=True, resolution=(640, 480), index=0)
            
            # Xoay dọc Texture cho Samsung
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
                
            self.root.ids.cam_container.clear_widgets()
            self.root.ids.cam_container.add_widget(self.cam)
            
            self.root.ids.main_btn.text = "BƯỚC 3: QUÉT DỮ LIỆU"
            self.root.ids.result_data.text = "Camera đã bật thành công!"
            self.step = 3
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi khởi tạo Camera: {str(e)}"

    def export_data(self):
        name = self.root.ids.user_input.text
        if not name:
            self.root.ids.result_data.text = "LỖI: Vui lòng nhập tên người thực hiện!"
            return

        # Lấy thời gian thực
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        # Xác định đường dẫn lưu file
        if platform == 'android':
            from android.storage import primary_external_storage_path
            dir_path = primary_external_storage_path()
        else:
            dir_path = os.path.expanduser("~")

        file_name = "Log_ThietBi.csv"
        full_path = os.path.join(dir_path, file_name)

        try:
            file_exists = os.path.isfile(full_path)
            with open(full_path, 'a', encoding='utf-8') as f:
                if not file_exists:
                    f.write("Thoi Gian,Nguoi Thuc Hien,Che Do,Du Lieu Quet\n")
                
                # Ghi dòng dữ liệu
                scan_val = "N/A" # Sẽ thay bằng giá trị quét mã ở bản sau
                f.write(f"{dt_string},{name},{self.mode},{scan_val}\n")
            
            self.root.ids.result_data.text = f"ĐÃ LƯU: {dt_string}\nTại: {full_path}"
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi lưu file: {str(e)}"

if __name__ == '__main__':
    DeviceApp().run()
