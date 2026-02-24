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
        font_size: '10sp'
    Label:
        text: root.imei
        size_hint_x: 0.35
        color: root.text_color
        font_size: '10sp'
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
            font_size: '12sp'
            halign: 'center'
            valign: 'middle'
            text_size: self.width, None

        Button:
            text: 'BẤM VÀO ĐÂY ĐỂ NẠP FILE TỪ THƯ MỤC DOWNLOAD'
            size_hint_y: None
            height: '50dp'
            background_color: (0.2, 0.6, 0.3, 1)
            on_release: app.scan_download_folder()

        BoxLayout:
            size_hint_y: None
            height: '40dp'
            spacing: '5dp'
            Button:
                text: 'LỌC TRẠNG THÁI'
                on_release: app.toggle_filter()

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
    user_info = StringProperty("V1.8.0: CHẾ ĐỘ NẠP TRỰC TIẾP\nBƯỚC 1: Copy file my_device.txt vào mục Download\nBƯỚC 2: Nhấn nút xanh bên dưới")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")
    
    def build(self):
        return Builder.load_string(KV)

    def scan_download_folder(self):
        # Đường dẫn thư mục Download chuẩn trên mọi máy Android
        if platform == 'android':
            base_path = "/storage/emulated/0/Download"
        else:
            base_path = "." # Cho PC test

        target_file = os.path.join(base_path, "my_device.txt")
        
        self.user_info = f"ĐANG QUÉT FILE TẠI:\n{target_file}"
        
        if os.path.exists(target_file):
            Clock.schedule_once(lambda dt: self.direct_read_v180(target_file), 0.5)
        else:
            self.user_info = "LỖI: KHÔNG TÌM THẤY FILE!\nHãy đảm bảo file tên đúng là: my_device.txt\nvà nằm trong thư mục Download."

    def direct_read_v180(self, path):
        try:
            with open(path, 'rb') as f:
                raw = f.read()
            
            text = raw.decode('utf-8-sig', errors='replace')
            marker = "Single ID"
            start_pos = text.find(marker)
            
            if start_pos == -1:
                self.user_info = "LỖI: File tìm thấy nhưng sai cấu trúc ERP."
                return

            clean_csv = text[start_pos:].strip()
            f_stream = io.StringIO(clean_csv)
            reader = csv.DictReader(f_stream)
            
            temp_list = []
            for i, row in enumerate(reader, 1):
                temp_list.append({
                    'stt': str(i),
                    'model': row.get('Model Name', 'N/A').strip(),
                    'imei': row.get('IMEI', 'N/A').strip(),
                    'status': row.get('Status', 'N/A').strip()
                })

            if temp_list:
                self.devices_data = temp_list
                self.user_info = f"NẠP THÀNH CÔNG {len(temp_list)} MÁY!\nFile: {os.path.basename(path)}"
                self.refresh_table()
            else:
                self.user_info = "LỖI: File không có dữ liệu máy."

        except Exception as e:
            self.user_info = f"LỖI ĐỌC FILE: {str(e)}\nHãy kiểm tra quyền truy cập bộ nhớ của App."

    def refresh_table(self):
        container = self.root.get_screen('main').ids.table_content
        container.clear_widgets()
        
        from kivy.factory import Factory
        for dev in self.devices_data:
            # Logic lọc
            if self.filter_mode == "occupied" and dev['status'] not in ['Occupied', 'Mượn']: continue
            
            bg = (1, 1, 1, 1) if dev['status'] in ['Occupied', 'Mượn'] else (0.1, 0.6, 0.2, 0.8)
            txt = (0, 0, 0, 1) if dev['status'] in ['Occupied', 'Mượn'] else (1, 1, 1, 1)

            container.add_widget(Factory.DataRow(
                stt=dev['stt'], model=dev['model'], imei=dev['imei'],
                status=dev['status'], bg_color=bg, text_color=txt
            ))

    def toggle_filter(self):
        self.filter_mode = "occupied" if self.filter_mode == "all" else "all"
        self.refresh_table()

if __name__ == '__main__':
    DeviceApp().run()
