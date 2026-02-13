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

# Tự động xin quyền trên Android
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
            height: '55dp'
            color: (0, 0.3, 0.6, 1)
            bold: True
            font_size: '12sp'
            halign: 'center'
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
    user_info = StringProperty("HỆ THỐNG: SẴN SÀNG\nVUI LÒNG NHẤN 'NHẬP FILE'")
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
            self.user_info = f"LỖI KHỞI CHẠY: {str(e)}"

    def handle_selection(self, selection):
        if not selection:
            self.user_info = "THÔNG BÁO: BẠN ĐÃ THOÁT CHỌN FILE."
            return
        
        # Đảm bảo lấy đúng đường dẫn chuỗi
        path = selection[0] if isinstance(selection, list) else selection
        self.user_info = f"ĐANG ĐỌC FILE:\n{os.path.basename(path)}"
        
        # Đợi một chút để UI cập nhật thông báo
        Clock.schedule_once(lambda dt: self.load_data_v163(path), 0.5)

    def load_data_v163(self, path):
        try:
            # 1. Đọc nội dung thô
            content = ""
            # Thử các loại encoding khác nhau
            for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
                try:
                    with open(path, 'r', encoding=enc, errors='replace') as f:
                        content = f.read()
                    break
                except:
                    continue
            
            if not content:
                self.user_info = "LỖI: KHÔNG THỂ ĐỌC NỘI DUNG FILE."
                return

            # 2. Xử lý dòng trống và tìm Header
            lines = content.splitlines()
            valid_start = -1
            for i, line in enumerate(lines):
                if "Single ID" in line and "Model Name" in line:
                    valid_start = i
                    break
            
            if valid_start == -1:
                self.user_info = "LỖI: CẤU TRÚC FILE KHÔNG ĐÚNG\n(THIẾU CỘT TIÊU ĐỀ)"
                return

            # 3. Sử dụng bộ lọc CSV cho phần nội dung từ Header trở đi
            csv_data = "\n".join(lines[valid_start:])
            f_stream = io.StringIO(csv_data)
            reader = csv.DictReader(f_stream)
            
            # Làm sạch tên cột
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames]

            temp_list = []
            for i, row in enumerate(reader, 1):
                if i == 1:
                    self.current_user_id = row.get('Single ID', 'N/A')
                    self.current_user_name = row.get('Name', 'Unknown')

                temp_list.append({
                    'stt': str(i),
                    'model': row.get('Model Name', 'N/A'),
                    'imei': row.get('IMEI', 'N/A'),
                    'status': row.get('Status', 'N/A'),
                    'audit': row.get('Last Audit', '')
                })

            # 4. Hiển thị lên màn hình
            if temp_list:
                self.devices_data = temp_list
                self.user_info = f"ID: {self.current_user_id} | {self.current_user_name}\nĐÃ NẠP {len(temp_list)} MÁY THÀNH CÔNG"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "LỖI: FILE CÓ TIÊU ĐỀ NHƯNG KHÔNG CÓ DỮ LIỆU."

        except Exception as e:
            self.user_info = f"LỖI XỬ LÝ: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        container = self.root.get_screen('main').ids.get('table_content')
        if not container: return
        container.clear_widgets()
        
        # Kiểm tra trạng thái máy theo Model
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
        # Xuất file (cần thêm quyền ghi file Android)
        pass

    def play_beep(self, type_name):
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound: sound.play()
        except: pass

if __name__ == '__main__':
    DeviceApp().run()
