import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock
from kivy.utils import platform
import os
import io
import csv

# Giao diện ứng dụng (Kivy Language)
KV = r'''
<DataRow@BoxLayout>:
    stt: ''
    model: ''
    imei: ''
    status: ''
    bg_color: (1, 1, 1, 1)
    text_color: (0, 0, 0, 1)
    size_hint_y: None
    height: '48dp'
    padding: ['5dp', '2dp']
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [3,]
    Label:
        text: root.stt
        size_hint_x: 0.1
        color: root.text_color
    Label:
        text: root.model
        size_hint_x: 0.4
        color: root.text_color
        font_size: '9sp'
    Label:
        text: root.imei
        size_hint_x: 0.35
        color: root.text_color
        font_size: '9sp'
    Label:
        text: root.status
        size_hint_x: 0.15
        bold: True
        color: (0.8, 0.1, 0.1, 1) if root.status in ['Occupied', 'Mượn'] else (0.1, 0.5, 0.1, 1)

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '8dp'
        canvas.before:
            Color:
                rgba: (0.95, 0.95, 0.95, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.user_info
            size_hint_y: None
            height: '100dp'
            color: (0.1, 0.3, 0.6, 1)
            bold: True
            font_size: '11sp'
            halign: 'center'
            valign: 'middle'
            text_size: self.width, None

        Button:
            text: 'BẤM ĐỂ NẠP FILE TỪ MỤC DOWNLOAD'
            size_hint_y: None
            height: '60dp'
            background_color: (0.1, 0.5, 0.2, 1)
            on_release: app.scan_download_folder()

        BoxLayout:
            size_hint_y: None
            height: '40dp'
            spacing: '10dp'
            Button:
                text: 'LỌC MÁY THIẾU'
                on_release: app.toggle_filter()
            Button:
                text: 'XÓA BẢNG'
                on_release: app.clear_data()

        DataRow:
            stt: 'STT'
            model: 'MODEL NAME'
            imei: 'IMEI'
            status: 'TT'
            bg_color: (0.1, 0.4, 0.6, 1)
            text_color: (1, 1, 1, 1)

        ScrollView:
            BoxLayout:
                id: table_content
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '2dp'

ScreenManager:
    MainScreen:
'''

class DeviceApp(App):
    user_info = StringProperty("BẢN v1.8.1: NẠP FILE TRỰC TIẾP\n1. Copy file 'my_device.txt' vào thư mục Download\n2. Nhấn nút xanh để nạp dữ liệu.")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")
    
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        # Yêu cầu quyền truy cập khi App bắt đầu
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

    def scan_download_folder(self):
        """Tự động quét file mà không cần mở trình chọn của Android"""
        try:
            # Các đường dẫn phổ biến trên Android
            if platform == 'android':
                paths_to_check = [
                    "/storage/emulated/0/Download/my_device.txt",
                    "/sdcard/Download/my_device.txt"
                ]
            else:
                # Dành cho việc test trên máy tính
                paths_to_check = ["my_device.txt", "Download/my_device.txt"]

            target_file = None
            for p in paths_to_check:
                if os.path.exists(p):
                    target_file = p
                    break
            
            if target_file:
                self.user_info = f"ĐÃ TÌM THẤY FILE!\nĐang nạp dữ liệu..."
                Clock.schedule_once(lambda dt: self.process_data_v181(target_file), 0.5)
            else:
                self.user_info = "LỖI: KHÔNG TÌM THẤY FILE!\nHãy đảm bảo file tên là: my_device.txt\nvà đã copy vào thư mục Download."
        except Exception as e:
            self.user_info = f"LỖI HỆ THỐNG: {str(e)}"

    def process_data_v181(self, path):
        try:
            with open(path, 'rb') as f:
                raw = f.read()
            
            # Giải mã hỗ trợ UTF-8 có BOM
            text = raw.decode('utf-8-sig', errors='replace')
            
            # Tìm header Single ID
            marker = "Single ID"
            start_pos = text.find(marker)
            
            if start_pos == -1:
                self.user_info = "LỖI: File không đúng định dạng ERP (Thiếu Single ID)."
                return

            clean_csv = text[start_pos:].strip()
            f_stream = io.StringIO(clean_csv)
            reader = csv.DictReader(f_stream)
            
            # Chuẩn hóa tên cột (loại bỏ khoảng trắng)
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames if fn]

            new_list = []
            for i, row in enumerate(reader, 1):
                new_list.append({
                    'stt': str(i),
                    'model': str(row.get('Model Name', 'N/A')).strip(),
                    'imei': str(row.get('IMEI', 'N/A')).strip(),
                    'status': str(row.get('Status', 'N/A')).strip()
                })

            if new_list:
                self.devices_data = new_list
                self.user_info = f"NẠP THÀNH CÔNG: {len(new_list)} MÁY.\nFile: {os.path.basename(path)}"
                self.refresh_table()
            else:
                self.user_info = "LỖI: File tìm thấy nhưng không có dữ liệu máy."
                
        except Exception as e:
            self.user_info = f"LỖI PHÂN TÍCH: {str(e)}"

    def refresh_table(self):
        try:
            container = self.root.get_screen('main').ids.table_content
            container.clear_widgets()
            
            from kivy.factory import Factory
            for dev in self.devices_data:
                # Chế độ lọc
                if self.filter_mode == "occupied" and dev['status'] not in ['Occupied', 'Mượn']:
                    continue
                
                # Màu sắc hiển thị
                is_fail = dev['status'] in ['Occupied', 'Mượn']
                bg = (1, 1, 1, 1) if is_fail else (0.1, 0.6, 0.2, 0.8)
                txt = (0, 0, 0, 1) if is_fail else (1, 1, 1, 1)

                container.add_widget(Factory.DataRow(
                    stt=dev['stt'], model=dev['model'], imei=dev['imei'],
                    status=dev['status'], bg_color=bg, text_color=txt
                ))
        except:
            pass

    def toggle_filter(self):
        self.filter_mode = "occupied" if self.filter_mode == "all" else "all"
        self.refresh_table()

    def clear_data(self):
        self.devices_data = []
        self.refresh_table()
        self.user_info = "ĐÃ XÓA DỮ LIỆU TẠM THỜI."

if __name__ == '__main__':
    DeviceApp().run()
