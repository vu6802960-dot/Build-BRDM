from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from camera_handler import CameraHandler
from utils import export_to_csv

class BRDMTrackerLayout(BoxLayout):
    pass

class BRDMTrackerApp(App):
    def build(self):
        self.scanned_data = []
        self.current_status = "Borrow"
        self.root_ui = BRDMTrackerLayout()
        self.camera_handler = CameraHandler(self.on_scan_complete)
        return self.root_ui

    def on_start(self):
        # Khóa màn hình dọc và xin quyền
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
            try:
                from plyer import orientation
                orientation.set_portrait()
            except: pass

    def on_scan(self):
        if not self.root_ui.ids.person_input.text.strip():
            return
        # Delay nhỏ để hệ thống UI không bị lag khi mở Camera
        Clock.schedule_once(lambda dt: self.camera_handler.open_camera(), 0.2)

    def on_scan_complete(self, result):
        if result:
            record = {
                'datetime': datetime.now().strftime('%H:%M:%S'),
                'model': result.get('model'),
                'imei': result.get('imei'),
                'smsn': result.get('smsn'),
                'status': self.current_status,
                'person': self.root_ui.ids.person_input.text.strip()
            }
            self.scanned_data.append(record)
            self.update_ui(record)

    def update_ui(self, record):
        from kivy.uix.label import Label
        info = f"{record['model']} | {record['imei']}\n{record['person']}"
        self.root_ui.ids.display_layout.add_widget(Label(text=info, size_hint_y=None, height=60, color=(0,0,0,1)))
        self.root_ui.ids.counter_label.text = f"Records: {len(self.scanned_data)}"

    def on_export(self):
        export_to_csv(self.scanned_data)

    def on_clear_all(self):
        self.scanned_data.clear()
        self.root_ui.ids.display_layout.clear_widgets()
        self.root_ui.ids.counter_label.text = "Records: 0"
