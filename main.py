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
                rgba: (0.95, 0.95, 0.95, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.user_info
            size_hint_y: None
            height: '80dp'
            color: (0, 0.2, 0.5, 1)
            bold: True
            font_size: '12sp'
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
    user_info = StringProperty("V1.7.1: SẴN SÀNG\nNHẤN 'NHẬP FILE' ĐỂ BẮT ĐẦU")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")
    current_user_id = ""
    current_user_name = ""

    def build(self):
        return Builder.load_string(KV)

    def open_file_explorer(self):
        # Reset trạng thái trước khi chọn
        self.user_info = "HỆ THỐNG ĐANG MỞ BỘ NHỚ..."
        try:
            from plyer import filechooser
            # Không dùng filter để tránh lỗi Android nhận diện sai mime type
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            self.user_info = f"LỖI KHỞI CHẠY: {str(e)}"

    def handle_selection(self, selection):
        # Nếu hàm này được gọi, dòng chữ chắc chắn phải đổi
        if not selection:
            self.user_info = "BẠN ĐÃ THOÁT MÀ CHƯA CHỌN FILE."
            return

        path = selection[0]
        self.user_info = f"ĐÃ NHẬN TÍN HIỆU FILE:\n{os.path.basename(path)}"
        
        # Ép hệ thống chạy parse ngay lập tức
        Clock.schedule_once(lambda dt: self.parse_final_v171(path), 0.1)

    def parse_final_v171(self, path):
        try:
            # 1. Đọc file ở mức nhị phân thấp nhất
            if not os.path.exists(path):
                # Thủ thuật cho Android: Nếu không thấy file, thử tìm trong cache
                self.user_info = f"LỖI: Android chặn đường dẫn trực tiếp.\nHãy thử Copy file vào thư mục DOWNLOAD."
                return

            with open(path, 'rb') as f:
                content_bytes = f.read()

            if not content_bytes:
                self.user_info = "LỖI: Tệp tin rỗng."
                return

            # 2. Giải mã và chuẩn hóa dòng
            text = content_bytes.decode('utf-8-sig', errors='replace')
            # Tìm header Single ID bất kể nó nằm ở đâu
            idx = text.find("Single ID")
            if idx == -1:
                self.user_info = "LỖI: File không chứa dữ liệu Single ID."
                return

            clean_csv = text[idx:].strip()
            f_stream = io.StringIO(clean_csv)
            reader = csv.DictReader(f_stream)
            
            # Làm sạch header
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames if fn]

            temp_list = []
            for i, row in enumerate(reader, 1):
                if i == 1:
                    self.current_user_id = row.get('Single ID', 'N/A').strip()
                    self.current_user_name = row.get('Name', 'Unknown').strip()

                temp_list.append({
                    'stt': str(i),
                    'model': row.get('Model Name', 'N/A').strip(),
                    'imei': row.get('IMEI', 'N/A').strip(),
                    'status': row.get('Status', 'N/A').strip(),
                    'audit': row.get('Last Audit', '').strip()
                })

            if temp_list:
                self.devices_data = temp_list
                self.user_info = f"THÀNH CÔNG! NẠP {len(temp_list)} MÁY\nUSER: {self.current_user_id}"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "LỖI: Cấu trúc CSV đúng nhưng không có dữ liệu."

        except Exception as e:
            self.user_info = f"LỖI XỬ LÝ: {str(e)}"

    def refresh_table(self, *args):
        container = self.root.get_screen('main').ids.table_content
        container.clear_widgets()
        
        model_missing = {}
        for d in self.devices_data:
            if d['status'] in ['Occupied', 'Mượn']:
                model_missing[d['model']] = True

        from kivy.factory import Factory
        for dev in self.devices_data:
            is_fail = model_missing.get(dev['model'], False)
            if self.filter_mode == "du" and is_fail: continue
            if self.filter_mode == "thieu" and not is_fail: continue

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
