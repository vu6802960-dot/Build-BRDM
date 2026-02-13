import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import platform
import os
import csv
import io

# Ép quyền Android một lần nữa tại tầng hệ thống
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

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
    Label:
        text: root.audit
        size_hint_x: 0.15
        font_size: '8sp'
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
            height: '60dp'
            color: (0.05, 0.3, 0.5, 1)
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
            bg_color: (0.12, 0.45, 0.7, 1)
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
    user_info = StringProperty("HỆ THỐNG: SẴN SÀNG\nVUI LÒNG CHỌN FILE")
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
            self.user_info = f"LỖI EXPLORER: {str(e)}"

    def handle_selection(self, selection):
        if not selection:
            self.user_info = "BẠN ĐÃ HỦY CHỌN FILE."
            return
        
        path = selection[0] if isinstance(selection, list) else selection
        self.user_info = f"ĐANG NẠP: {os.path.basename(path)}..."
        
        # Dùng Clock để giải phóng UI thread
        Clock.schedule_once(lambda dt: self.final_load_method(path), 0.3)

    def final_load_method(self, path):
        try:
            # 1. Đọc thô toàn bộ file bất chấp encoding
            raw_content = ""
            for encoding in ['utf-8-sig', 'latin-1', 'utf-8']:
                try:
                    with open(path, 'r', encoding=encoding, errors='replace') as f:
                        raw_content = f.read()
                    if raw_content: break
                except:
                    continue

            if not raw_content:
                self.user_info = "LỖI: KHÔNG THỂ ĐỌC DỮ LIỆU TỪ FILE NÀY."
                return

            # 2. Làm sạch nội dung: Bỏ các dòng trống ở đầu/cuối và khoảng trắng rác
            clean_content = raw_content.strip()
            
            # 3. Tìm vị trí thực sự của Header "Single ID"
            if "Single ID" not in clean_content:
                self.user_info = "LỖI: FILE KHÔNG ĐÚNG CẤU TRÚC\n(KHÔNG TÌM THẤY 'SINGLE ID')"
                return

            # Cắt bỏ mọi thứ nằm trước "Single ID" (Xử lý dòng trống đầu file)
            start_pos = clean_content.find("Single ID")
            final_csv_text = clean_content[start_pos:]

            # 4. Dùng DictReader để xử lý chuỗi CSV này
            f_stream = io.StringIO(final_csv_text)
            reader = csv.DictReader(f_stream)
            
            # Dọn dẹp tên cột (loại bỏ \n, \t, khoảng trắng)
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames if fn]

            temp_data = []
            for i, row in enumerate(reader, 1):
                # Lưu thông tin User từ dòng đầu
                if i == 1:
                    self.current_user_id = row.get('Single ID', 'N/A').strip()
                    self.current_user_name = row.get('Name', 'Unknown').strip()

                # Ánh xạ cột cực kỳ an toàn
                temp_data.append({
                    'stt': str(i),
                    'model': row.get('Model Name', 'N/A').strip(),
                    'imei': row.get('IMEI', 'N/A').strip(),
                    'status': row.get('Status', 'N/A').strip(),
                    'audit': row.get('Last Audit', '').strip()
                })

            # 5. Cập nhật giao diện
            if temp_data:
                self.devices_data = temp_data
                self.user_info = f"ID: {self.current_user_id} | {self.current_user_name}\nNẠP THÀNH CÔNG: {len(temp_data)} MÁY"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "CẢNH BÁO: FILE HỢP LỆ NHƯNG KHÔNG CÓ DỮ LIỆU."

        except Exception as e:
            self.user_info = f"LỖI PHÂN TÍCH: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        try:
            container = self.root.get_screen('main').ids.get('table_content')
            if not container: return
            container.clear_widgets()
            
            # Tính toán Model thiếu (Xanh/Trắng)
            model_missing = {}
            for d in self.devices_data:
                if d['status'] in ['Occupied', 'Mượn']:
                    model_missing[d['model']] = True

            from kivy.factory import Factory
            for dev in self.devices_data:
                is_fail = model_missing.get(dev['model'], False)
                
                # Lọc theo nút Status
                if self.filter_mode == "du" and is_fail: continue
                if self.filter_mode == "thieu" and not is_fail: continue

                bg = (1, 1, 1, 1) if is_fail else (0.1, 0.6, 0.2, 0.8)
                txt = (0, 0, 0, 1) if is_fail else (1, 1, 1, 1)

                container.add_widget(Factory.DataRow(
                    stt=dev['stt'], model=dev['model'], imei=dev['imei'],
                    status=dev['status'], audit=dev['audit'],
                    bg_color=bg, text_color=txt
                ))
        except: pass

    def toggle_filter(self):
        modes = ["all", "du", "thieu"]
        self.filter_mode = modes[(modes.index(self.filter_mode) + 1) % 3]
        self.refresh_table()

    def export_data(self):
        # Xuất file (cần thêm logic filechooser.save_file nếu muốn chuyên nghiệp)
        pass

    def play_beep(self, type_name):
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound: sound.play()
        except: pass

if __name__ == '__main__':
    DeviceApp().run()
