import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.factory import Factory
import os, datetime, csv

# Giao diện hiện đại với phong cách Card View và bo góc
KV = r'''
<DataRow@BoxLayout>:
    stt: ''; model: ''; imei: ''; status: ''; audit: ''; is_header: False
    size_hint_y: None
    height: '50dp'
    padding: ['5dp', '2dp']
    canvas.before:
        Color:
            rgba: (0.12, 0.45, 0.7, 1) if self.is_header else (1, 1, 1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [5,]
        Color:
            rgba: (0.9, 0.9, 0.9, 1) if not self.is_header else (0,0,0,0)
        Line:
            width: 1
            rectangle: (self.x, self.y, self.width, self.height)
            
    Label:
        text: root.stt
        size_hint_x: 0.1
        bold: root.is_header
        color: (1,1,1,1) if root.is_header else (0,0,0,1)
    Label:
        text: root.model
        size_hint_x: 0.25
        bold: root.is_header
        color: (1,1,1,1) if root.is_header else (0,0,0,1)
    Label:
        text: root.imei
        size_hint_x: 0.35
        bold: root.is_header
        color: (1,1,1,1) if root.is_header else (0.2, 0.2, 0.2, 1)
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

<ModelStatusRow>:
    size_hint_y: None
    height: '60dp'
    padding: '10dp'
    spacing: '10dp'
    canvas.before:
        Color:
            rgba: (0.95, 0.95, 0.95, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
    Label:
        text: root.model_name
        color: (0,0,0,1)
        bold: True
        halign: 'left'
        text_size: self.size
        valign: 'middle'
    Label:
        text: root.status_text
        color: (0.1, 0.5, 0.1, 1) if root.is_full else (0.8, 0, 0, 1)
        size_hint_x: 0.3
        bold: True

<MainScreen>:
    name: 'main'
    canvas.before:
        Color:
            rgba: (0.98, 0.98, 0.98, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        
        # Top Bar
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            canvas.before:
                Color:
                    rgba: (0.12, 0.45, 0.7, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [0, 0, 15, 15]
            Label:
                text: app.user_info
                bold: True
                color: (1,1,1,1)

        # Action Buttons
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '5dp'
            Button:
                text: 'IMPORT'
                background_color: (0.2, 0.6, 0.2, 1)
                on_release: app.import_data()
            Button:
                text: 'STATUS'
                on_release: root.manager.current = 'status'
            Button:
                text: 'SCAN'
                background_color: (0.1, 0.5, 0.8, 1)
                on_release: root.manager.current = 'scan'
            Button:
                text: 'EXPORT'
                on_release: app.export_data()

        TextInput:
            id: search_input
            hint_text: '🔍 Search IMEI...'
            size_hint_y: None
            height: '45dp'
            multiline: False
            padding: [10, 10]
            on_text: app.search_imei(self.text)

        DataRow:
            stt: 'STT'; model: 'MODEL'; imei: 'IMEI/SN'; status: 'TRẠNG THÁI'; audit: 'AUDIT'; is_header: True

        ScrollView:
            BoxLayout:
                id: main_table
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '2dp'

<StatusScreen>:
    name: 'status'
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'
        Label:
            text: "BÁO CÁO TỔNG KHO"
            size_hint_y: None
            height: '40dp'
            bold: True
            font_size: '18sp'
            color: (0.1, 0.3, 0.5, 1)
        ScrollView:
            BoxLayout:
                id: status_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '8dp'
        Button:
            text: 'QUAY LẠI'
            size_hint_y: None
            height: '50dp'
            on_release: root.manager.current = 'main'

<ScanScreen>:
    name: 'scan'
    on_enter: app.start_continuous_scan()
    on_leave: app.stop_continuous_scan()
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        BoxLayout:
            id: camera_preview
            size_hint_y: 0.5
            canvas.before:
                Color:
                    rgba: (0, 0, 0, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
        BoxLayout:
            size_hint_y: None
            height: '45dp'
            spacing: '5dp'
            TextInput:
                id: scan_user
                hint_text: 'Tên người thực hiện...'
            Spinner:
                id: scan_mode
                text: 'Kho'
                values: ('Kho', 'Mượn')
                size_hint_x: 0.3
        DataRow:
            stt: 'STT'; model: 'Model'; imei: 'IMEI'; status: 'Status'; audit: 'Audit'; is_header: True
        ScrollView:
            BoxLayout:
                id: scan_table
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'THOÁT CAMERA'
            size_hint_y: None
            height: '50dp'
            on_release: root.manager.current = 'main'

ScreenManager:
    MainScreen:
    StatusScreen:
    ScanScreen:
'''

class ModelStatusRow(ButtonBehavior, BoxLayout):
    model_name = StringProperty('')
    status_text = StringProperty('')
    is_full = BooleanProperty(True)

class DeviceApp(App):
    user_info = StringProperty("ID: --- | Name: ---")
    all_devices = ListProperty([])
    filtered_devices = ListProperty([])

    def build(self):
        # Tải âm thanh an toàn
        self.beep_ok = SoundLoader.load('success.wav')
        self.beep_error = SoundLoader.load('error.wav')
        return Builder.load_string(KV)

    def import_data(self):
        csv_path = "export_devices.csv"
        txt_path = "my_device.txt"
        
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data = []
                    for row in reader:
                        data.append({
                            'stt': row.get('STT',''),
                            'model': row.get('Model',''),
                            'imei': row.get('IMEI',''),
                            'status': row.get('Status',''),
                            'audit': row.get('Audit','')
                        })
                    self.all_devices = data
                    self.filtered_devices = data
                    if os.path.exists(txt_path):
                        with open(txt_path, 'r', encoding='utf-8') as tf:
                            self.user_info = tf.readline().strip()
                    self.refresh_all_uis()
                    return
            except Exception as e: print(f"CSV Error: {e}")

        if os.path.exists(txt_path):
            try:
                with open(txt_path, "r", encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        self.user_info = lines[0].strip()
                        data = []
                        for line in lines[1:]:
                            if ',' in line:
                                p = [i.strip() for i in line.split(',')]
                                if len(p) >= 6:
                                    data.append({'stt': str(len(data)+1), 'model': p[4], 'imei': p[5], 'status': 'Kho', 'audit': 'Initial'})
                        self.all_devices = data
                        self.filtered_devices = data
                        self.refresh_all_uis()
            except Exception as e: print(f"TXT Error: {e}")

    def refresh_all_uis(self):
        for screen_name, table_id in [('main', 'main_table'), ('scan', 'scan_table')]:
            screen = self.root.get_screen(screen_name)
            table = screen.ids[table_id]
            table.clear_widgets()
            source = self.filtered_devices if screen_name == 'main' else self.all_devices
            for d in source:
                table.add_widget(Factory.DataRow(stt=d['stt'], model=d['model'], imei=d['imei'], status=d['status'], audit=d['audit']))
        self.update_status_screen()

    def update_status_screen(self):
        container = self.root.get_screen('status').ids.status_container
        container.clear_widgets()
        models = {}
        for d in self.all_devices:
            name = d['model']
            if name not in models: models[name] = True
            if d['status'] == 'Mượn': models[name] = False
        for name, is_full in models.items():
            row = ModelStatusRow(model_name=name, is_full=is_full, status_text="ĐỦ" if is_full else "THIẾU")
            row.bind(on_release=lambda instance, n=name: self.show_missing(n))
            container.add_widget(row)

    def show_missing(self, model_name):
        self.filtered_devices = [d for d in self.all_devices if d['model'] == model_name and d['status'] == 'Mượn']
        self.root.current = 'main'

    def search_imei(self, query):
        if not query:
            self.filtered_devices = self.all_devices
        else:
            self.filtered_devices = [d for d in self.all_devices if query.lower() in d['imei'].lower()]
        self.refresh_all_uis()

    def start_continuous_scan(self):
        try:
            if not hasattr(self, 'cam') or self.cam is None:
                from kivy.uix.camera import Camera
                self.cam = Camera(play=True, resolution=(1280, 720))
                self.root.get_screen('scan').ids.camera_preview.add_widget(self.cam)
            self.scan_event = Clock.schedule_interval(self.analyze_qr, 0.5)
        except Exception as e: print(f"Cam Error: {e}")

    def stop_continuous_scan(self):
        if hasattr(self, 'scan_event'): Clock.unschedule(self.scan_event)

    def analyze_qr(self, dt):
        pass # Tích hợp logic quét thực tế ở đây

    def export_data(self):
        try:
            with open("export_devices.csv", 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["STT", "Model", "IMEI", "Status", "Audit"])
                for d in self.all_devices:
                    writer.writerow([d['stt'], d['model'], d['imei'], d['status'], d['audit']])
            self.root.get_screen('main').ids.search_input.hint_text = "Data Saved Successfully!"
        except Exception as e: print(f"Export Error: {e}")

if __name__ == '__main__':
    DeviceApp().run()
