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

# Giao diện tối giản để tránh lỗi đồ họa
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
            height: '110dp'
            color: (0.1, 0.2, 0.5, 1)
            bold: True
            font_size: '11sp'
            halign: 'center'
            valign: 'middle'
            text_size: self.width, None

        Button:
            text: 'NẠP FILE TỪ DOWNLOAD'
            size_hint_y: None
            height: '60dp'
            background_color: (0.1, 0.4, 0.8, 1)
            on_release: app.safe_scan()

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
            model: 'MODEL'
            imei: 'IMEI'
            status: 'TT'
            bg_color: (0.2, 0.2, 0.2, 1)
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
    user_info = StringProperty("v1.8.2: HƯỚNG DẪN QUAN TRỌNG\n1. Chép 'my_device.txt' vào thư mục Download\n2. Cấp quyền 'QUẢN LÝ TẤT CẢ TỆP' trong cài đặt máy\n3. Nhấn nút NẠP FILE bên dưới.")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")
    
    def build(self):
        return Builder.load_string(KV)

    def safe_scan(self):
        """Hàm quét file có bọc bảo vệ chống Crash"""
        self.user_info = "ĐANG KIỂM TRA BỘ NHỚ..."
        Clock.schedule_once(self.execute_scan, 0.5)

    def execute_scan(self, dt):
        try:
            # Đường dẫn tuyệt đối an toàn nhất trên Android
            target = "/storage/emulated/0/Download/my_device.txt"
            
            if not os.path.exists(target):
                # Thử đường dẫn phụ
                target = "/sdcard/Download/my_device.txt"
                if not os.path.exists(target):
                    self.user_info = "LỖI: KHÔNG TÌM THẤY FILE!\nHãy kiểm tra file 'my_device.txt' trong mục Download."
                    return

            with open(target, 'rb') as f:
                raw = f.read()
            
            text = raw.decode('utf-8-sig', errors='replace')
            marker = "Single ID"
            start_pos = text.find(marker)
            
            if start_pos == -1:
                self.user_info = "LỖI: File tìm thấy nhưng sai định dạng ERP."
                return

            clean_csv = text[start_pos:].strip()
            f_stream = io.StringIO(clean_csv)
            reader = csv.DictReader(f_stream)
            
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
                self.user_info = f"THÀNH CÔNG: NẠP {len(new_list)} MÁY!"
                self.refresh_table()
            else:
                self.user_info = "LỖI: File không có dữ liệu."

        except PermissionError:
            self.user_info = "LỖI QUYỀN TRUY CẬP!\nHãy vào Cài đặt điện thoại -> Ứng dụng -> Quyền\nBật 'Quản lý tất cả các tệp'."
        except Exception as e:
            self.user_info = f"LỖI: {str(e)}"

    def refresh_table(self):
        container = self.root.get_screen('main').ids.table_content
        container.clear_widgets()
        from kivy.factory import Factory
        for dev in self.devices_data:
            if self.filter_mode == "occupied" and dev['status'] not in ['Occupied', 'Mượn']:
                continue
            is_fail = dev['status'] in ['Occupied', 'Mượn']
            bg = (1, 1, 1, 1) if is_fail else (0.1, 0.6, 0.2, 0.8)
            txt = (0, 0, 0, 1) if is_fail else (1, 1, 1, 1)
            container.add_widget(Factory.DataRow(
                stt=dev['stt'], model=dev['model'], imei=dev['imei'],
                status=dev['status'], bg_color=bg, text_color=txt
            ))

    def toggle_filter(self):
        self.filter_mode = "occupied" if self.filter_mode == "all" else "all"
        self.refresh_table()

    def clear_data(self):
        self.devices_data = []
        self.refresh_table()
        self.user_info = "ĐÃ XÓA BẢNG."

if __name__ == '__main__':
    DeviceApp().run()
