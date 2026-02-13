import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import os
import shutil
import tempfile

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
        halign: 'center'
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
            height: '45dp'
            color: (0.12, 0.45, 0.7, 1)
            bold: True
            font_size: '13sp'
            text_size: self.width, None
            halign: 'center'

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
    user_info = StringProperty("VUI LÒNG NHẤN 'NHẬP FILE'")
    current_user_id = ""
    current_user_name = ""
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")

    def build(self):
        return Builder.load_string(KV)

    def open_file_explorer(self):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            self.user_info = f"Lỗi: {str(e)}"

    def handle_selection(self, selection):
        if not selection:
            return
        self.user_info = "Đang nạp file..."
        # Gọi hàm xử lý file sau một khoảng thời gian ngắn để UI kịp cập nhật
        Clock.schedule_once(lambda dt: self.load_data_safely(selection[0]), 0.1)

    def load_data_safely(self, path):
        try:
            # BƯỚC 1: Sao chép file vào thư mục nội bộ của App để tránh lỗi URI
            temp_dir = tempfile.gettempdir()
            local_path = os.path.join(temp_dir, "data_temp.txt")
            
            if path.startswith('content://') or not os.path.exists(path):
                # Nếu là đường dẫn ảo, chúng ta thử đọc trực tiếp qua shutil (nếu plyer hỗ trợ)
                # Hoặc thông báo cho người dùng
                shutil.copy2(path, local_path)
            else:
                shutil.copy2(path, local_path)

            # BƯỚC 2: Đọc file từ thư mục nội bộ
            with open(local_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]

            if not lines:
                self.user_info = "File trống hoặc không thể đọc!"
                return

            # BƯỚC 3: Tìm Header và chỉ số cột
            header_idx = -1
            for i, line in enumerate(lines):
                if "Single ID" in line and "Model Name" in line:
                    header_idx = i
                    break
            
            if header_idx == -1:
                self.user_info = "Cấu trúc file không đúng (Thiếu Single ID)!"
                return

            cols_name = [c.strip() for c in lines[header_idx].split(',')]
            idx_map = {
                'id': cols_name.index("Single ID"),
                'name': cols_name.index("Name"),
                'model': cols_name.index("Model Name"),
                'imei': cols_name.index("IMEI"),
                'status': cols_name.index("Status"),
                'audit': cols_name.index("Last Audit")
            }

            # BƯỚC 4: Parse dữ liệu
            parsed_list = []
            for i, line in enumerate(lines[header_idx + 1:], 1):
                raw_cols = [c.strip() for c in line.split(',')]
                if len(raw_cols) < 5: continue

                # Gộp các cột thừa vào Last Audit (do nội dung chứa dấu phẩy)
                if len(raw_cols) > len(cols_name):
                    audit_val = ", ".join(raw_cols[idx_map['audit']:])
                else:
                    audit_val = raw_cols[idx_map['audit']] if idx_map['audit'] < len(raw_cols) else ""

                if i == 1:
                    self.current_user_id = raw_cols[idx_map['id']]
                    self.current_user_name = raw_cols[idx_map['name']]

                parsed_list.append({
                    'stt': str(i),
                    'model': raw_cols[idx_map['model']],
                    'imei': raw_cols[idx_map['imei']],
                    'status': raw_cols[idx_map['status']],
                    'audit': audit_val
                })

            if parsed_list:
                self.devices_data = parsed_list
                self.user_info = f"ID: {self.current_user_id} | {self.current_user_name} ({len(parsed_list)} máy)"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "Không tìm thấy dòng dữ liệu hợp lệ."

        except Exception as e:
            self.user_info = f"Lỗi: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        container = self.root.get_screen('main').ids.get('table_content')
        if not container: return
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
        # Logic xuất CSV kèm ID & User
        if not self.devices_data: return
        try:
            with open('audit_export.csv', 'w', newline='', encoding='utf-8-sig') as f:
                f.write(f"ID: {self.current_user_id}, User: {self.current_user_name}\n")
                f.write("STT,Model,IMEI,Status,Audit\n")
                for d in self.devices_data:
                    f.write(f"{d['stt']},{d['model']},{d['imei']},{d['status']},{d['audit']}\n")
            self.user_info = "Đã xuất file audit_export.csv"
            self.play_beep('success')
        except Exception as e:
            self.user_info = f"Lỗi xuất file: {str(e)}"

    def play_beep(self, type_name):
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound: sound.play()
        except: pass

if __name__ == '__main__':
    DeviceApp().run()
