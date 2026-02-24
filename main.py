import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import platform
import os
import io
import csv

class MainScreen(Screen):
    pass

class ScanScreen(Screen):
    pass

KV = r'''
<DataRow@BoxLayout>:
    stt: ''
    model: ''
    imei: ''
    status: ''
    audit: ''
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
        font_size: '10sp'
    Label:
        text: root.model
        size_hint_x: 0.25
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
    Label:
        text: root.audit
        size_hint_x: 0.15
        font_size: '7sp'
        color: root.text_color

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '8dp'
        canvas.before:
            Color:
                rgba: (0.96, 0.96, 0.96, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.user_info
            size_hint_y: None
            height: '80dp'
            color: (0, 0.2, 0.5, 1)
            bold: True
            font_size: '11sp'
            halign: 'center'
            valign: 'middle'
            text_size: self.width, None

        BoxLayout:
            size_hint_y: None
            height: '45dp'
            spacing: '5dp'
            Button:
                text: 'NHẬP FILE'
                on_release: app.open_file_explorer()
            Button:
                text: 'QUÉT'
                background_color: (0.1, 0.6, 0.2, 1)
                on_release: root.manager.current = 'scan'
            Button:
                text: 'STATUS'
                on_release: app.toggle_filter()
            Button:
                text: 'XUẤT'
                on_release: app.export_data()

        DataRow:
            stt: 'STT'
            model: 'MODEL'
            imei: 'IMEI'
            status: 'T.THÁI'
            audit: 'AUDIT'
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
    ScanScreen:
'''

class DeviceApp(App):
    user_info = StringProperty("PHIÊN BẢN 1.7.0\nVUI LÒNG CHỌN FILE MY_DEVICE.TXT")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")
    current_user_id = ""
    current_user_name = ""

    def build(self):
        return Builder.load_string(KV)

    def open_file_explorer(self):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            self.user_info = f"LỖI HỆ THỐNG: {str(e)}"

    def handle_selection(self, selection):
        if not selection: return
        path = selection[0]
        self.user_info = f"ĐANG XỬ LÝ DỮ LIỆU..."
        # Gọi hàm xử lý sau 300ms để đảm bảo UI không bị đứng
        Clock.schedule_once(lambda dt: self.parse_v170(path), 0.3)

    def parse_v170(self, path):
        try:
            # 1. Đọc file dưới dạng nhị phân để an toàn tuyệt đối
            with open(path, 'rb') as f:
                raw_bytes = f.read()
            
            # 2. Giải mã bằng utf-8-sig (để tự loại bỏ mã BOM nếu có)
            content = raw_bytes.decode('utf-8-sig', errors='replace')
            
            # 3. Làm sạch dữ liệu thô: Xóa bỏ dòng trống đầu và cuối file
            content = content.strip()
            
            # 4. Tìm vị trí chính xác của "Single ID" để bắt đầu đọc
            start_index = content.find("Single ID")
            if start_index == -1:
                self.user_info = "LỖI: FILE KHÔNG CÓ TIÊU ĐỀ ĐÚNG MẪU."
                return
            
            data_content = content[start_index:]
            
            # 5. Sử dụng thư viện CSV chuẩn để xử lý dấu phẩy thông minh
            f_stream = io.StringIO(data_content)
            reader = csv.DictReader(f_stream)
            
            # Chuẩn hóa tên cột
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames]
            
            new_data = []
            for i, row in enumerate(reader, 1):
                # Lấy thông tin User từ dòng đầu tiên
                if i == 1:
                    self.current_user_id = row.get('Single ID', 'N/A')
                    self.current_user_name = row.get('Name', 'Unknown')
                
                new_data.append({
                    'stt': str(i),
                    'model': row.get('Model Name', 'N/A'),
                    'imei': row.get('IMEI', 'N/A'),
                    'status': row.get('Status', 'N/A'),
                    'audit': row.get('Last Audit', '')
                })

            if new_data:
                self.devices_data = new_data
                self.user_info = f"ĐÃ NẠP: {len(new_data)} MÁY\nUSER: {self.current_user_id} - {self.current_user_name}"
                # Gọi vẽ bảng
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "LỖI: FILE HỢP LỆ NHƯNG KHÔNG CÓ DỮ LIỆU MÁY."

        except Exception as e:
            self.user_info = f"LỖI PHÂN TÍCH: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        # Lấy container từ màn hình 'main'
        main_screen = self.root.get_screen('main')
        container = main_screen.ids.table_content
        container.clear_widgets()
        
        # Xác định Model nào có máy đang bị 'Occupied/Mượn'
        model_missing = {}
        for d in self.devices_data:
            if d['status'] in ['Occupied', 'Mượn']:
                model_missing[d['model']] = True

        from kivy.factory import Factory
        for dev in self.devices_data:
            is_fail = model_missing.get(dev['model'], False)
            
            # Lọc dữ liệu theo chế độ Status
            if self.filter_mode == "du" and is_fail: continue
            if self.filter_mode == "thieu" and not is_fail: continue

            # Màu sắc: Xanh (Đủ), Trắng (Thiếu/Cần trả)
            bg = (1, 1, 1, 1) if is_fail else (0.1, 0.6, 0.2, 0.8)
            txt = (0, 0, 0, 1) if is_fail else (1, 1, 1, 1)

            container.add_widget(Factory.DataRow(
                stt=dev['stt'], model=dev['model'], imei=dev['imei'],
                status=dev['status'], audit=dev['audit'],
                bg_color=bg, text_color=txt
            ))

    def toggle_filter(self):
        modes = ["all", "du", "thieu"]
        self.filter_mode = modes[(modes.index(self.filter_mode) + 1) % 3]
        self.refresh_table()

    def export_data(self):
        pass

    def play_beep(self, type_name):
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound: sound.play()
        except: pass

if __name__ == '__main__':
    DeviceApp().run()
