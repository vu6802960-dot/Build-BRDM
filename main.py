import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.utils import platform
import os
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
    is_header: False
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
    Label:
        text: root.imei
        size_hint_x: 0.35
        color: root.text_color
    Label:
        text: root.status
        size_hint_x: 0.15
        bold: True
        color: (0.9, 0.1, 0.1, 1) if root.status in ['Occupied', 'Mượn'] else root.text_color
    Label:
        text: root.audit
        size_hint_x: 0.15
        font_size: '9sp'
        color: root.text_color

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '8dp'
        canvas.before:
            Color: rgba: (0.95, 0.95, 0.95, 1)
            Rectangle: pos: self.pos; size: self.size

        Label:
            text: app.user_info
            size_hint_y: None
            height: '40dp'
            color: (0.12, 0.45, 0.7, 1)
            bold: True
            font_size: '15sp'

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
            stt: 'STT'; model: 'MODEL'; imei: 'IMEI'; status: 'T.THÁI'; audit: 'AUDIT'
            is_header: True
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
    user_info = StringProperty("CHƯA CÓ DỮ LIỆU")
    current_user_id = ""
    current_user_name = ""
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")

    def build(self):
        try:
            return Builder.load_string(KV)
        except Exception as e:
            return Label(text=f"Lỗi khởi tạo: {str(e)}")

    def open_file_explorer(self):
        """Lazy import để tránh crash lúc mở app"""
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            self.user_info = f"Lỗi mở FileExplorer: {str(e)}"

    def handle_selection(self, selection):
        if selection:
            self.process_file(selection[0])

    def process_file(self, path):
        try:
            new_data = []
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    if i == 1:
                        self.current_user_id = row.get('Single ID', 'Unknown')
                        self.current_user_name = row.get('Name', 'User')
                        self.user_info = f"ID: {self.current_user_id} | User: {self.current_user_name}"
                    
                    item = {
                        'stt': str(i),
                        'model': row.get('Model Name', ''),
                        'imei': row.get('IMEI', ''),
                        'status': row.get('Status', ''),
                        'audit': row.get('Last Audit', '')
                    }
                    new_data.append(item)

            self.devices_data = new_data
            self.refresh_table()
            self.play_beep('success')
        except Exception as e:
            self.user_info = f"Lỗi đọc dữ liệu: {str(e)}"
            self.play_beep('error')

    def refresh_table(self):
        try:
            container = self.root.get_screen('main').ids.table_content
            container.clear_widgets()
            
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

                row = Factory.DataRow(
                    stt=dev['stt'], model=dev['model'], imei=dev['imei'],
                    status=dev['status'], audit=dev['audit'],
                    bg_color=bg, text_color=txt
                )
                container.add_widget(row)
        except:
            pass

    def toggle_filter(self):
        modes = ["all", "du", "thieu"]
        self.filter_mode = modes[(modes.index(self.filter_mode) + 1) % 3]
        self.refresh_table()

    def export_data(self):
        if not self.devices_data: return
        try:
            with open('audit_export.csv', 'w', newline='', encoding='utf-8-sig') as f:
                f.write(f"ID: {self.current_user_id}, User: {self.current_user_name}\n")
                writer = csv.DictWriter(f, fieldnames=['stt', 'model', 'imei', 'status', 'audit'])
                writer.writeheader()
                writer.writerows(self.devices_data)
            self.play_beep('success')
        except:
            self.play_beep('error')

    def play_beep(self, type_name):
        """Xử lý âm thanh an toàn"""
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound:
                sound.play()
        except:
            pass

if __name__ == '__main__':
    DeviceApp().run()
