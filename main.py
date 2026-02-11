import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import os, datetime, csv

KV = r'''
<DataRow@BoxLayout>:
    stt: ''; model: ''; imei: ''; status: ''; audit: ''; is_header: False
    size_hint_y: None
    height: '45dp'
    canvas.before:
        Color:
            rgba: (0.2, 0.2, 0.2, 1) if self.is_header else ((0.9, 1, 0.9, 1) if self.status == 'Kho' else (1, 0.9, 0.9, 1))
        Rectangle:
            pos: self.pos
            size: self.size
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
        size_hint_x: 0.3
        bold: root.is_header
        color: (1,1,1,1) if root.is_header else (0,0,0,1)
    Label:
        text: root.status
        size_hint_x: 0.15
        bold: root.is_header
        color: (1,1,1,1) if root.is_header else ((0, 0.6, 0, 1) if root.status == 'Kho' else (0.8, 0, 0, 1))
    Label:
        text: root.audit
        size_hint_x: 0.2
        bold: root.is_header
        font_size: '9sp'
        color: (1,1,1,1) if root.is_header else (0,0,0,1)

<ModelStatusRow@ButtonBehavior+BoxLayout>:
    model_name: ''; status_text: ''; is_full: True
    size_hint_y: None
    height: '50dp'
    padding: '10dp'
    canvas.before:
        Color:
            rgba: (0.1, 0.8, 0.1, 0.2) if self.is_full else (1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: (0.8, 0.8, 0.8, 1)
        Line:
            points: self.x, self.y, self.x + self.width, self.y
    Label:
        text: root.model_name
        color: (0,0,0,1)
    Label:
        text: root.status_text
        color: (0, 0.5, 0, 1) if root.is_full else (0.8, 0, 0, 1)
        size_hint_x: 0.3
        bold: True

ScreenManager:
    MainScreen:
    StatusScreen:
    ScanScreen:

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '5dp'
        Label:
            text: app.user_info
            size_hint_y: None
            height: '40dp'
            bold: True
            color: (0,0,0,1)
        BoxLayout:
            size_hint_y: None
            height: '45dp'
            spacing: '5dp'
            Button:
                text: 'IMPORT'
                on_release: app.import_data()
            Button:
                text: 'STATUS'
                on_release: root.manager.current = 'status'
            Button:
                text: 'CAMERA SCAN'
                on_release: root.manager.current = 'scan'
            Button:
                text: 'EXPORT'
                on_release: app.export_data()
        TextInput:
            id: search_input
            hint_text: 'Search IMEI...'
            size_hint_y: None
            height: '40dp'
            multiline: False
            on_text: app.search_imei(self.text)
        DataRow:
            stt: 'STT'; model: 'Model'; imei: 'IMEI/SN'; status: 'Status'; audit: 'Last Audit'; is_header: True
        ScrollView:
            BoxLayout:
                id: main_table
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height

<StatusScreen>:
    name: 'status'
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        Label:
            text: "TRẠNG THÁI MODEL"
            size_hint_y: None
            height: '40dp'
            bold: True
            color: (0,0,0,1)
        ScrollView:
            BoxLayout:
                id: status_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'QUAY LẠI'
            size_hint_y: None
            height: '45dp'
            on_release: root.manager.current = 'main'

<ScanScreen>:
    name: 'scan'
    on_enter: app.start_continuous_scan()
    on_leave: app.stop_continuous_scan()
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '5dp'
        BoxLayout:
            id: camera_preview
            size_hint_y: 0.4
            canvas.before:
                Color: rgba: (0,0,0,1)
                Rectangle: pos: self.pos, size: self.size
        BoxLayout:
            size_hint_y: None
            height: '40dp'
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
            stt: 'STT'; model: 'Model'; imei: 'IMEI/SN'; status: 'Status'; audit: 'Last Audit'; is_header: True
        ScrollView:
            BoxLayout:
                id: scan_table
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'ĐÓNG CAMERA'
            size_hint_y: None
            height: '45dp'
            on_release: root.manager.current = 'main'
'''

class DeviceApp(App):
    user_info = StringProperty("ID: --- | Name: ---")
    all_devices = ListProperty([])
    filtered_devices = ListProperty([])

    def build(self):
        self.beep_ok = SoundLoader.load('success.wav')
        self.beep_error = SoundLoader.load('error.wav')
        return Builder.load_string(KV)

    def import_data(self):
        csv_path = "export_devices.csv"
        txt_path = "my_device.txt"
        
        # ƯU TIÊN 1: Nạp từ CSV đã xuất trước đó để kế thừa trạng thái mới nhất
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data = []
                    for row in reader:
                        data.append({
                            'stt': row['STT'],
                            'model': row['Model'],
                            'imei': row['IMEI'],
                            'status': row['Status'],
                            'audit': row['Audit']
                        })
                    self.all_devices = data
                    self.filtered_devices = data
                    # Cập nhật thông tin User từ dòng đầu file txt
                    if os.path.exists(txt_path):
                        with open(txt_path, 'r', encoding='utf-8') as tf:
                            self.user_info = tf.readline().strip()
                    self.refresh_all_uis()
                    return
            except Exception as e: print(f"CSV Import Error: {e}")

        # ƯU TIÊN 2: Nạp từ TXT (Chỉ dùng cho lần đầu tiên chạy app)
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
                                    # p[4] là Model Name, p[5] là IMEI dựa trên snippet của bạn
                                    data.append({'stt': str(len(data)+1), 'model': p[4], 'imei': p[5], 'status': 'Kho', 'audit': 'Initial'})
                        self.all_devices = data
                        self.filtered_devices = data
                        self.refresh_all_uis()
            except Exception as e: print(f"TXT Import Error: {e}")

    def refresh_all_uis(self):
        for screen_name, table_id in [('main', 'main_table'), ('scan', 'scan_table')]:
            table = self.root.get_screen(screen_name).ids[table_id]
            table.clear_widgets()
            source = self.filtered_devices if screen_name == 'main' else self.all_devices
            for d in source:
                from kivy.factory import Factory
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
            from kivy.factory import Factory
            row = Factory.ModelStatusRow(model_name=name, is_full=is_full, status_text="ĐỦ" if is_full else "THIẾU")
            row.on_release = lambda n=name, f=is_full: self.show_missing(n) if not f else None
            container.add_widget(row)

    def show_missing(self, model_name):
        self.filtered_devices = [d for d in self.all_devices if d['model'] == model_name and d['status'] == 'Mượn']
        self.root.current = 'main'

    def search_imei(self, query):
        self.filtered_devices = [d for d in self.all_devices if query.lower() in d['imei'].lower()] if query else self.all_devices
        self.refresh_all_uis()

    def start_continuous_scan(self):
        try:
            if not hasattr(self, 'cam') or self.cam is None:
                from kivy.uix.camera import Camera
                self.cam = Camera(play=True, resolution=(1920, 1080))
                self.root.get_screen('scan').ids.camera_preview.add_widget(self.cam)
            self.scan_event = Clock.schedule_interval(self.analyze_qr, 0.5)
            self.refresh_event = Clock.schedule_interval(self.refresh_cam, 60)
        except Exception as e: print(f"Cam Error: {e}")

    def refresh_cam(self, dt):
        if hasattr(self, 'cam'): self.cam.play = False; self.cam.play = True

    def stop_continuous_scan(self):
        if hasattr(self, 'scan_event'): Clock.unschedule(self.scan_event)
        if hasattr(self, 'refresh_event'): Clock.unschedule(self.refresh_event)

    def analyze_qr(self, dt):
        # Nơi tích hợp pyzbar để quét frame
        pass

    def apply_scan(self, imei):
        user = self.root.get_screen('scan').ids.scan_user.text.strip()
        mode = self.root.get_screen('scan').ids.scan_mode.text
        if not user: return
        found = False
        for d in self.all_devices:
            if d['imei'] == imei:
                d['status'] = mode
                d['audit'] = f"{datetime.datetime.now().strftime('%d/%m %H:%M')} - {user}"
                found = True; break
        if found:
            if self.beep_ok: self.beep_ok.play()
            self.refresh_all_uis()
        elif self.beep_error: self.beep_error.play()

    def export_data(self):
        try:
            # GHI ĐÈ FILE CSV (Chế độ 'w')
            with open("export_devices.csv", 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["STT", "Model", "IMEI", "Status", "Audit"])
                for d in self.all_devices:
                    writer.writerow([d['stt'], d['model'], d['imei'], d['status'], d['audit']])
            self.root.get_screen('main').ids.search_input.hint_text = "Dữ liệu mới nhất đã được ghi đè!"
        except Exception as e: print(f"Export Error: {e}")

if __name__ == '__main__':
    DeviceApp().run()
