import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import os
import csv

# KV Language - ĐÃ SỬA LỖI CÚ PHÁP TẠI DataRow 
KV = r'''
<DataRow@BoxLayout>:
    stt: ''; model: ''; imei: ''; status: ''; audit: ''; is_header: False
    size_hint_y: None
    height: '45dp'
    padding: ['5dp', '2dp']
    canvas.before:
        Color:
            rgba: (0.12, 0.45, 0.7, 1) if self.is_header else (1, 1, 1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [3,]
            
    Label:
        text: root.stt
        size_hint_x: 0.1
        color: (1,1,1,1) if root.is_header else (0,0,0,1)
    Label:
        text: root.model
        size_hint_x: 0.25
        color: (1,1,1,1) if root.is_header else (0,0,0,1)
    Label:
        text: root.imei
        size_hint_x: 0.35
        color: (1,1,1,1) if root.is_header else (0,0,0,1)
    Label:
        text: root.status
        size_hint_x: 0.15
        bold: True
        color: (1,1,1,1) if root.is_header else ((0.1, 0.6, 0.2, 1) if root.status == 'Kho' else (0.9, 0.2, 0.2, 1))
    Label:
        text: root.audit
        size_hint_x: 0.15
        font_size: '10sp'
        color: (1,1,1,1) if root.is_header else (0.4, 0.4, 0.4, 1)

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        canvas.before:
            Color:
                rgba: (0.92, 0.92, 0.92, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.user_info
            size_hint_y: None
            height: '30dp'
            color: (0,0,0,1)
            bold: True

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            Button:
                text: 'NHẬP FILE'
                on_release: app.import_data()
            Button:
                text: 'QUÉT IMEI'
                background_color: (0.1, 0.6, 0.2, 1)
                on_release: root.manager.current = 'scan'
            Button:
                text: 'XUẤT FILE'
                on_release: app.export_data()

        DataRow:
            stt: 'STT'; model: 'MODEL'; imei: 'IMEI'; status: 'T.THÁI'; audit: 'AUDIT'; is_header: True

        ScrollView:
            BoxLayout:
                id: table_content
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '2dp'

<ScanScreen>:
    name: 'scan'
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'DỪNG QUÉT & QUAY LẠI'
            size_hint_y: None
            height: '60dp'
            on_release: root.manager.current = 'main'
        Label:
            text: 'Giao diện Camera'
            color: (0,0,0,1)

ScreenManager:
    MainScreen:
    ScanScreen:
'''

class DeviceApp(App):
    user_info = StringProperty("ID: 6802960 | User: VU-DOT")
    devices_data = ListProperty([])

    def build(self):
        # Nạp giao diện an toàn
        try:
            self.root_widget = Builder.load_string(KV)
            return self.root_widget
        except Exception as e:
            print(f"Lỗi nạp giao diện: {e}")
            return None

    def play_beep(self, status='success'):
        """Phát âm thanh an toàn, tránh lỗi NoneType từ Logcat"""
        try:
            file = 'success.wav' if status == 'success' else 'error.wav'
            sound_path = os.path.join(os.path.dirname(__file__), file)
            sound = SoundLoader.load(sound_path)
            if sound:
                sound.play()
        except:
            pass

    def import_data(self):
        """Logic xử lý dữ liệu từ file txt/csv"""
        source_file = 'my_device.txt'
        if not os.path.exists(source_file):
            self.play_beep('error')
            return

        try:
            self.devices_data = []
            with open(source_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    row['stt'] = str(i)
                    self.devices_data.append(row)
            
            self.refresh_table()
            self.play_beep('success')
        except Exception as e:
            print(f"Lỗi Import: {e}")
            self.play_beep('error')

    def refresh_table(self):
        """Cập nhật giao diện bảng"""
        try:
            container = self.root.get_screen('main').ids.table_content
            container.clear_widgets()
            from kivy.factory import Factory
            for dev in self.devices_data:
                row_widget = Factory.DataRow(
                    stt=dev.get('stt', ''),
                    model=dev.get('model', ''),
                    imei=dev.get('imei', ''),
                    status=dev.get('status', ''),
                    audit=dev.get('audit', '')
                )
                container.add_widget(row_widget)
        except Exception as e:
            print(f"Lỗi hiển thị bảng: {e}")

    def export_data(self):
        """Xuất file kết quả"""
        if not self.devices_data:
            self.play_beep('error')
            return
            
        try:
            with open('export_devices.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['stt', 'model', 'imei', 'status', 'audit'])
                writer.writeheader()
                writer.writerows(self.devices_data)
            self.play_beep('success')
        except:
            self.play_beep('error')

if __name__ == '__main__':
    DeviceApp().run()
