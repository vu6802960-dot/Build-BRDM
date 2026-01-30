import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.utils import platform

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

    def on_status_change(self, instance):
        if instance.state == 'down':
            self.current_status = instance.text

    def on_scan(self):
        if not self.root_ui.ids.person_input.text.strip():
            self.show_popup("Error", "Please enter person name first!")
            return
        self.camera_handler.open_camera()

    def on_scan_complete(self, result):
        if not result or not result.get('imei'):
            self.show_popup("OCR Failed", "Could not read IMEI. Try better lighting.")
            return

        record = {
            'datetime': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'model': result.get('model', 'Unknown'),
            'imei': result.get('imei', ''),
            'smsn': result.get('smsn', 'N/A'),
            'status': self.current_status,
            'person': self.root_ui.ids.person_input.text.strip()
        }
        self.scanned_data.append(record)
        self.update_ui(record)

    def update_ui(self, record):
        info = f"{record['datetime']} - {record['person']}\n{record['model']} | {record['imei']}"
        lbl = Label(text=info, size_hint_y=None, height=80, color=(0,0,0,1), halign='left')
        lbl.bind(size=lbl.setter('text_size'))
        self.root_ui.ids.display_layout.add_widget(lbl)
        self.root_ui.ids.counter_label.text = f"Records: {len(self.scanned_data)}"

    def on_export(self):
        if export_to_csv(self.scanned_data):
            self.show_popup("Success", "Data exported successfully!")

    def on_clear_all(self):
        self.scanned_data.clear()
        self.root_ui.ids.display_layout.clear_widgets()
        self.root_ui.ids.counter_label.text = "Records: 0"

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height=50)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

if __name__ == '__main__':
    BRDMTrackerApp().run()