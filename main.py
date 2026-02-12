import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.utils import platform
import os
import csv

# Thêm plyer để mở file explorer của điện thoại
try:
    from plyer import filechooser
except:
    filechooser = None

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
    is_missing: False  # Trạng thái thiếu (nền trắng)
    size_hint_y: None
    height: '45dp'
    padding: ['5dp', '2dp']
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1) if self.is_missing else ((0.12, 0.45, 0.7, 1) if self.is_header else (0.1, 0.6, 0.2, 0.8))
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [3,]
            
    Label:
        text: root.stt
        size_hint_x: 0.1
        color: (0,0,0,1) if root.is_missing else (1,1,1,1)
    Label:
        text: root.model
        size_hint_x: 0.25
        color: (0,0,0,1) if root.is_missing else (1,1,1,1)
    Label:
        text: root.imei
        size_hint_x: 0.35
        color: (0,0,0,1) if root.is_missing else (1,1,1,1)
    Label:
        text: root.status
        size_hint_x: 0.15
        bold: True
        color: (0.9, 0.1, 0.1, 1) if root.status == 'Mượn' else (1,1,1,1)
    Label:
        text: root.audit
        size_hint_x: 0.15
        font_size: '10sp'
        color: (0.3, 0.3, 0.3, 1) if root.is_missing else (1,1,1,1)

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

        # Thông tin User
        Label:
            text: app.user_info
            size_hint_y: None
            height: '30dp'
            color: (0,0,0,1)
            bold: True

        # Hàng nút chức năng chính (Đồng bộ cùng hàng)
        BoxLayout:
            size_hint_y: None
            height: '45dp'
            spacing: '5dp'
            Button:
                text: 'MỞ FILE'
                on_release: app.open_file_explorer()
            Button:
                text: 'QUÉT'
                background_color: (0.1, 0.6, 0.2, 1)
                on_release: root.manager.current = 'scan'
            Button:
                text: 'LỌC STATUS'
                on_release: app.toggle_filter()
            Button:
                text: 'XUẤT'
                on_release: app.export_data()

        DataRow:
            stt: 'STT'; model: 'MODEL'; imei: 'IMEI'; status: 'TRẠNG THÁI'; audit: 'AUDIT'; is_header: True

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
    user_info = StringProperty("Chưa có dữ liệu")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all") # all, đủ (xanh), thiếu (trắng)

    def build(self):
        try:
            self.root_widget = Builder.load_string(KV)
            return self.root_widget
        except Exception as e:
            return Label(text=f"Lỗi: {str(e)}")

    def open_file_explorer(self):
        """Mở trình chọn file trên Android/PC"""
        if filechooser:
            filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self, selection):
        """Xử lý sau khi chọn file"""
        if selection:
            file_path = selection[0]
            # Cập nhật User từ tên file
            file_name = os.path.basename(file_path)
            self.user_info = f"File: {file_name}"
            self.import_data(file_path)

    def import_data(self, path):
        try:
            self.devices_data = []
            with open(path, 'r', encoding='utf-8') as f:
                # Logic đọc file linh hoạt TXT hoặc CSV
                if path.endswith('.csv'):
                    reader = csv.DictReader(f)
                else:
                    # Giả định txt ngăn cách bởi dấu phẩy hoặc tab
                    reader = csv.DictReader(f, delimiter=',')
                
                for i, row in enumerate(reader, 1):
                    row['stt'] = str(i)
                    self.devices_data.append(row)
            
            self.refresh_table()
            self.play_beep('success')
        except:
            self.play_beep('error')

    def toggle_filter(self):
        """Chuyển đổi giữa các chế độ lọc"""
        modes = ["all", "đủ", "thiếu"]
        current_idx = modes.index(self.filter_mode)
        self.filter_mode = modes[(current_idx + 1) % 3]
        self.refresh_table()

    def refresh_table(self):
        container = self.root_widget.get_screen('main').ids.table_content
        container.clear_widgets()
        
        from kivy.factory import Factory
        for dev in self.devices_data:
            status = dev.get('status', '')
            
            # Logic lọc
            if self.filter_mode == "đủ" and status == "Mượn": continue
            if self.filter_mode == "thiếu" and status == "Kho": continue
            
            row = Factory.DataRow(
                stt=dev.get('stt', ''),
                model=dev.get('model', ''),
                imei=dev.get('imei', ''),
                status=status,
                audit=dev.get('audit', ''),
                is_missing=True if status == "Mượn" else False
            )
            container.add_widget(row)

    def play_beep(self, status):
        # (Giữ nguyên logic âm thanh của v1.4.6)
        pass

if __name__ == '__main__':
    DeviceApp().run()
