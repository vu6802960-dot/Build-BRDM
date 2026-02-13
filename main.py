import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.label import Label
import os

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
    height: '45dp'
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
            height: '40dp'
            color: (0.12, 0.45, 0.7, 1)
            bold: True
            font_size: '14sp'

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
    user_info = StringProperty("CHỜ NHẬP FILE...")
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
        if selection:
            Clock.schedule_once(lambda dt: self.process_file_manual(selection[0]), 0.1)

    def process_file_manual(self, path):
        try:
            new_data = []
            with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]

            if not lines:
                self.user_info = "File không có dữ liệu!"
                return

            # Tìm dòng tiêu đề (Header)
            header = []
            start_index = 0
            for idx, line in enumerate(lines):
                if "Single ID" in line and "Model Name" in line:
                    header = [h.strip() for h in line.split(',')]
                    start_index = idx + 1
                    break
            
            if not header:
                self.user_info = "Sai cấu trúc file (Thiếu tiêu đề)!"
                return

            # Chỉ số các cột cần lấy dựa trên Header thực tế của file my_device.txt
            try:
                idx_id = header.index("Single ID")
                idx_name = header.index("Name")
                idx_model = header.index("Model Name")
                idx_imei = header.index("IMEI")
                idx_status = header.index("Status")
                idx_audit = header.index("Last Audit")
            except ValueError as ve:
                self.user_info = f"Thiếu cột: {str(ve)}"
                return

            # Đọc dữ liệu từ các dòng còn lại
            for i, line in enumerate(lines[start_index:], 1):
                cols = [c.strip() for c in line.split(',')]
                if len(cols) < len(header): continue # Bỏ qua dòng thiếu cột

                if i == 1:
                    self.current_user_id = cols[idx_id]
                    self.current_user_name = cols[idx_name]
                    self.user_info = f"ID: {self.current_user_id} | User: {self.current_user_name}"

                item = {
                    'stt': str(i),
                    'model': cols[idx_model],
                    'imei': cols[idx_imei],
                    'status': cols[idx_status],
                    'audit': cols[idx_audit] if idx_audit < len(cols) else ""
                }
                new_data.append(item)

            if new_data:
                self.devices_data = new_data
                self.user_info += f" | Tổng: {len(new_data)} máy"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "Không đọc được dòng dữ liệu nào!"

        except Exception as e:
            self.user_info = f"Lỗi: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        if not self.root: return
        container = self.root.get_screen('main').ids.get('table_content')
        if not container: return
        container.clear_widgets()
        
        # Check model status
        model_missing = {}
        for d in self.devices_data:
            m = d['model']
            if d['status'] in ['Occupied', 'Mượn']:
                model_missing[m] = True

        from kivy.factory import Factory
        for dev in self.devices_data:
            m = dev['model']
            is_fail = model_missing.get(m, False)
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
        # Logic xuất file tương tự
        pass

    def play_beep(self, type_name):
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound: sound.play()
        except: pass

if __name__ == '__main__':
    DeviceApp().run()
