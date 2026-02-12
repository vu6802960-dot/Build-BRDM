import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import os
import csv

# KV Language - Đã kiểm tra kỹ cú pháp để tránh SyntaxError
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
        font_size: '11sp'
    Label:
        text: root.imei
        size_hint_x: 0.35
        color: (1,1,1,1) if root.is_header else (0,0,0,1)
        font_size: '11sp'
    Label:
        text: root.status
        size_hint_x: 0.15
        bold: True
        color: (1,1,1,1) if root.is_header else ((0.1, 0.6, 0.2, 1) if 'In' in root.status else (0.9, 0.2, 0.2, 1))
    Label:
        text: root.audit
        size_hint_x: 0.15
        font_size: '9sp'
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
            text: 'Camera Interface'
            color: (1,1,1,1)

ScreenManager:
    MainScreen:
    ScanScreen:
'''

class DeviceApp(App):
    user_info = StringProperty("ID: 6802960 | User: VU-DOT")
    devices_data = ListProperty([])

    def build(self):
        try:
            return Builder.load_string(KV)
        except Exception as e:
            print(f"Lỗi KV: {e}")
            return None

    def play_beep(self, status='success'):
        """Sửa lỗi NoneType từ Logcat cũ"""
        try:
            file = 'success.wav' if status == 'success' else 'error.wav'
            sound_path = os.path.join(os.path.dirname(__file__), file)
            sound = SoundLoader.load(sound_path)
            if sound:
                sound.play()
        except:
            pass

    def import_data(self):
        """Khớp chính xác với cột trong my_device.txt"""
        source_file = 'my_device.txt'
        if not os.path.exists(source_file):
            self.play_beep('error')
            return

        try:
            new_data = []
            with open(source_file, 'r', encoding='utf-8') as f:
                # Đọc file với DictReader
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    # Lấy dữ liệu theo đúng tên tiêu đề trong file của bạn
                    item = {
                        'stt': str(i),
                        'model': row.get('Model Name', 'N/A'),
                        'imei': row.get('IMEI', 'N/A'),
                        'status': row.get('Status', 'N/A'),
                        'audit': row.get('Last Audit', 'N/A')
                    }
                    new_data.append(item)
            
            self.devices_data = new_data
            self.refresh_table()
            self.play_beep('success')
        except Exception as e:
            print(f"Lỗi Import: {e}")
            self.play_beep('error')

    def refresh_table(self):
        """Cập nhật giao diện bảng"""
        try:
            # Truy cập đúng ID từ MainScreen
            container = self.root.get_screen('main').ids.table_content
            container.clear_widgets()
            
            from kivy.factory import Factory
            for dev in self.devices_data:
                row = Factory.DataRow(
                    stt=dev['stt'],
                    model=dev['model'],
                    imei=dev['imei'],
                    status=dev['status'],
                    audit=dev['audit']
                )
                container.add_widget(row)
        except Exception as e:
            print(f"Lỗi Refresh: {e}")

    def export_data(self):
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
