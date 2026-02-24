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
            height: '85dp'
            color: (0.1, 0.3, 0.6, 1)
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
                background_color: (0.2, 0.4, 0.8, 1)
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
    user_info = StringProperty("V1.7.2: TRÌNH QUẢN LÝ THIẾT BỊ\nBẤM NHẬP FILE ĐỂ BẮT ĐẦU")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")
    current_user_id = ""
    current_user_name = ""
    
    # Biến để kiểm soát quá trình nạp
    is_processing = False

    def build(self):
        return Builder.load_string(KV)

    def open_file_explorer(self):
        if self.is_processing: return
        
        self.user_info = "ĐANG MỞ TRÌNH CHỌN FILE...\n(HÃY CHỌN ĐÚNG FILE .TXT)"
        self.is_processing = True
        
        try:
            from plyer import filechooser
            # Dùng tham số cực kỳ cơ bản để tránh lỗi filter của Android
            filechooser.open_file(on_selection=self.secure_callback)
            
            # Đề phòng callback bị treo, đặt một timer reset trạng thái sau 30 giây
            Clock.schedule_once(self.reset_processing_status, 30)
            
        except Exception as e:
            self.user_info = f"LỖI KHỞI ĐỘNG: {str(e)}"
            self.is_processing = False

    def reset_processing_status(self, dt):
        if self.is_processing and not self.devices_data:
            self.is_processing = False
            self.user_info = "QUÁ THỜI GIAN CHỜ.\nVUI LÒNG THỬ LẠI HOẶC CHỌN FILE KHÁC."

    def secure_callback(self, selection):
        # Ép thực hiện trong luồng Kivy để tránh lỗi đồng bộ
        Clock.schedule_once(lambda dt: self.handle_selection_v172(selection), 0)

    def handle_selection_v172(self, selection):
        self.is_processing = False
        
        if not selection:
            self.user_info = "BẠN CHƯA CHỌN FILE NÀO."
            return

        path = selection[0]
        # Hiển thị ngay tên file để người dùng biết app đã nhận được đường dẫn
        self.user_info = f"ĐÃ NHẬN FILE: {os.path.basename(path)}\nĐANG PHÂN TÍCH DỮ LIỆU..."
        
        # Gọi hàm đọc file
        Clock.schedule_once(lambda dt: self.ultimate_file_reader(path), 0.5)

    def ultimate_file_reader(self, path):
        try:
            # 1. Đọc thô Binary (Cách duy nhất để xuyên thủng rào cản Android)
            with open(path, 'rb') as f:
                raw = f.read()
            
            if not raw:
                self.user_info = "LỖI: FILE KHÔNG CÓ DỮ LIỆU (0 BYTES)."
                return

            # 2. Decode linh hoạt
            text = ""
            for codec in ['utf-8-sig', 'utf-8', 'latin-1']:
                try:
                    text = raw.decode(codec)
                    break
                except: continue
            
            if not text:
                self.user_info = "LỖI: KHÔNG THỂ GIẢI MÃ NỘI DUNG."
                return

            # 3. Kỹ thuật "Cắt lớp": Tìm Header Single ID
            start_point = text.find("Single ID")
            if start_point == -1:
                self.user_info = "LỖI: FILE SAI CẤU TRÚC ERP\n(KHÔNG TÌM THẤY 'SINGLE ID')"
                return
            
            clean_data = text[start_point:].strip()
            
            # 4. Parse CSV với cơ chế an toàn
            f_stream = io.StringIO(clean_csv)
            # Tự động đoán định dạng (delimiter)
            reader = csv.DictReader(f_stream)
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames if fn]

            parsed_list = []
            for i, row in enumerate(reader, 1):
                if i == 1:
                    self.current_user_id = row.get('Single ID', 'N/A').strip()
                    self.current_user_name = row.get('Name', 'Unknown').strip()

                parsed_list.append({
                    'stt': str(i),
                    'model': row.get('Model Name', 'N/A').strip(),
                    'imei': row.get('IMEI', 'N/A').strip(),
                    'status': row.get('Status', 'N/A').strip(),
                    'audit': row.get('Last Audit', '').strip()
                })

            if parsed_list:
                self.devices_data = parsed_list
                self.user_info = f"NẠP THÀNH CÔNG: {len(parsed_list)} MÁY\nID: {self.current_user_id} | {self.current_user_name}"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "CẢNH BÁO: FILE TRỐNG HOẶC SAI ĐỊNH DẠNG."

        except Exception as e:
            self.user_info = f"LỖI PHÂN TÍCH: {str(e)}"

    def refresh_table(self, *args):
        container = self.root.get_screen('main').ids.table_content
        container.clear_widgets()
        
        # Logic check thiếu/đủ
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
