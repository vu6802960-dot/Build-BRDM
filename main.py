import os
from datetime import datetime

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.clock import Clock

# Local imports (Đảm bảo các file này nằm cùng thư mục)
from scan_processor import MLKitScanner
from utils import save_to_csv

class MainScreen(BoxLayout):
    """Lớp giao diện chính định nghĩa trong brdmtracker.kv"""
    pass

class BRDMTrackerPro(App):
    def build(self):
        # Khởi tạo kho lưu trữ dữ liệu tạm thời
        self.data_records = []
        self.scanner = MLKitScanner()
        self.root_ui = MainScreen()
        return self.root_ui

    def on_start(self):
        """Chạy khi ứng dụng bắt đầu: Xin quyền và Khóa hướng màn hình"""
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.CAMERA, 
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
            
            # Khóa màn hình dọc để tránh lỗi xoay đen màn hình
            from plyer import orientation
            try:
                orientation.set_portrait()
            except Exception as e:
                print(f"Orientation Error: {e}")

    def start_scan(self):
        """Kích hoạt Camera Popup"""
        person = self.root_ui.ids.user_input.text.strip()
        if not person:
            self.show_popup("Thông báo", "Vui lòng nhập tên người thực hiện trước khi quét!")
            return
        
        # Sử dụng Clock để tạo độ trễ nhỏ, giúp UI mượt mà hơn khi mở phần cứng Camera
        Clock.schedule_once(self._open_camera_popup, 0.1)

    def _open_camera_popup(self, dt):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Thiết lập camera với độ phân giải tối ưu cho OCR
        self.cam = Camera(play=True, resolution=(640, 480))
        
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        cap_btn = Button(text="QUÉT NHÃN", background_color=(0.2, 0.7, 0.3, 1), bold=True)
        cap_btn.bind(on_press=self.process_ocr)
        
        can_btn = Button(text="HỦY", background_color=(0.8, 0.2, 0.2, 1))
        can_btn.bind(on_press=lambda x: self.scan_popup.dismiss())
        
        btn_layout.add_widget(cap_btn)
        btn_layout.add_widget(can_btn)
        
        content.add_widget(self.cam)
        content.add_widget(btn_layout)
        
        self.scan_popup = Popup(
            title="Đưa nhãn thiết bị vào khung hình", 
            content=content, 
            size_hint=(0.95, 0.9),
            auto_dismiss=False
        )
        self.scan_popup.open()

    def process_ocr(self, instance):
        """Chụp ảnh và gọi ML Kit xử lý"""
        try:
            if not self.cam.texture:
                return

            # Trích xuất dữ liệu ảnh từ Camera Texture
            from PIL import Image
            pix = self.cam.texture.pixels
            size = self.cam.texture.size
            img = Image.frombytes('RGBA', size, pix).convert('RGB')
            # Kivy texture bị ngược trục Y nên cần lật lại
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            # Lưu file tạm vào thư mục dữ liệu của App
            temp_path = os.path.join(self.user_data_dir, "last_capture.jpg")
            img.save(temp_path)

            # Gọi ML Kit Scanner
            raw_text = self.scanner.run_inference(temp_path)
            info = self.scanner.extract_info(raw_text)
            
            # Thêm vào danh sách kết quả
            self.add_record(info['model'], info['imei'])
            
            # Đóng camera
            self.scan_popup.dismiss()
            
        except Exception as e:
            self.show_popup("Lỗi Xử Lý", f"Không thể quét: {str(e)}")

    def add_record(self, model, imei):
        """Cập nhật dữ liệu vào bộ nhớ và giao diện"""
        record = {
            'time': datetime.now().strftime('%H:%M:%S'),
            'user': self.root_ui.ids.user_input.text.strip(),
            'status': self.root_ui.ids.status_spinner.text,
            'model': model,
            'imei': imei
        }
        self.data_records.append(record)
        
        # Tạo nhãn hiển thị mới trong danh sách
        display_text = (
            f"[b]{record['time']} - {record['status']}[/b]\n"
            f"Model: {model} | IMEI: {imei}\n"
            f"Người thực hiện: {record['user']}"
        )
        
        lbl = Label(
            text=display_text, 
            markup=True,
            size_hint_y=None, 
            height=100, 
            color=(0.2, 0.2, 0.2, 1),
            halign='left',
            valign='middle'
        )
        lbl.bind(size=lbl.setter('text_size'))
        
        self.root_ui.ids.result_list.add_widget(lbl)
        self.root_ui.ids.log_label.text = f"Tổng cộng: {len(self.data_records)} bản ghi"

    def export_data(self):
        """Gọi hàm lưu file CSV từ utils.py"""
        success, message = save_to_csv(self.data_records, self.user_data_dir)
        if success:
            self.show_popup("Thành công", f"Dữ liệu đã xuất ra file CSV!\nĐường dẫn: {message}")
        else:
            self.show_popup("Lỗi Xuất File", message)

    def show_popup(self, title, msg):
        """Hàm tiện ích hiển thị thông báo"""
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=msg, halign='center'))
        btn = Button(text="ĐÓNG", size_hint_y=None, height=50)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

if __name__ == '__main__':
    BRDMTrackerPro().run()