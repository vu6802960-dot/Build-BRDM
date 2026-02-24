import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import platform
import os
import io
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
        font_size: '9sp'
    Label:
        text: root.imei
        size_hint_x: 0.35
        color: root.text_color
        font_size: '9sp'
    Label:
        text: root.status
        size_hint_x: 0.15
        bold: True
        color: (0.8, 0.1, 0.1, 1) if root.status in ['Occupied', 'Mượn'] else (0.1, 0.5, 0.1, 1)
    Label:
        text: root.audit
        size_hint_x: 0.15
        font_size: '7sp'
        color: root.text_color

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '8dp'
        canvas.before:
            Color:
                rgba: (0.96, 0.96, 0.96, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.user_info
            size_hint_y: None
            height: '90dp'
            color: (0.1, 0.3, 0.6, 1)
            bold: True
            font_size: '11sp'
            halign: 'center'
            valign: 'middle'
            text_size: self.width, None

        BoxLayout:
            size_hint_y: None
            height: '45dp'
            spacing: '5dp'
            Button:
                text: 'CHỌN FILE .TXT'
                background_color: (0.2, 0.5, 0.9, 1)
                on_release: app.open_file_explorer()
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
            bg_color: (0.1, 0.4, 0.6, 1)
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
    user_info = StringProperty("BẢN v1.7.3: CƠ CHẾ ĐỌC CƯỠNG BỨC\nNHẤN NÚT ĐỂ CHỌN FILE")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")
    current_user_id = ""
    current_user_name = ""
    
    selected_path = None

    def build(self):
        return Builder.load_string(KV)

    def on_pause(self):
        # Lưu trạng thái khi app bị đẩy vào nền
        return True

    def on_resume(self):
        # Khi App quay lại từ trình chọn file, nếu có path thì xử lý ngay
        if self.selected_path:
            Clock.schedule_once(lambda dt: self.ultimate_parse_v173(self.selected_path), 0.5)
        return True

    def open_file_explorer(self):
        self.user_info = "ĐANG MỞ HỆ THỐNG...\n(HÃY CHỌN FILE VÀ ĐỢI 1 GIÂY)"
        try:
            from plyer import filechooser
            # Sử dụng tham số tối giản nhất
            filechooser.open_file(on_selection=self.internal_callback)
        except Exception as e:
            self.user_info = f"LỖI: {str(e)}"

    def internal_callback(self, selection):
        if selection:
            self.selected_path = selection[0]
            # Thử chạy ngay, nếu kẹt thì on_resume sẽ "cứu"
            Clock.schedule_once(lambda dt: self.ultimate_parse_v173(selection[0]), 0)

    def ultimate_parse_v173(self, path):
        if not path: return
        self.user_info = f"ĐANG ĐỌC:\n{os.path.basename(path)}"
        
        try:
            # Bước 1: Đọc Binary - KHÔNG dùng os.path.exists vì nó hay báo sai trên Android URI
            try:
                with open(path, 'rb') as f:
                    raw_bytes = f.read()
            except:
                # Nếu path URI thất bại, thử đoán path vật lý (Download)
                fname = os.path.basename(path)
                alt_path = f"/storage/emulated/0/Download/{fname}"
                with open(alt_path, 'rb') as f:
                    raw_bytes = f.read()

            if not raw_bytes:
                self.user_info = "LỖI: FILE KHÔNG CÓ DỮ LIỆU."
                return

            # Bước 2: Giải mã cực mạnh
            text = raw_bytes.decode('utf-8-sig', errors='replace')
            
            # Bước 3: Tìm điểm bắt đầu dữ liệu
            marker = "Single ID"
            start_pos = text.find(marker)
            if start_pos == -1:
                self.user_info = "LỖI: FILE KHÔNG ĐÚNG MẪU (THIẾU SINGLE ID)."
                return

            # Bước 4: Xử lý CSV thủ công để tránh lỗi DictReader trên dữ liệu bẩn
            lines = text[start_pos:].strip().splitlines()
            headers = [h.strip() for h in lines[0].split(',')]
            
            try:
                i_id = headers.index("Single ID")
                i_name = headers.index("Name")
                i_model = headers.index("Model Name")
                i_imei = headers.index("IMEI")
                i_status = headers.index("Status")
                i_audit = headers.index("Last Audit")
            except:
                self.user_info = "LỖI: FILE THIẾU CỘT QUAN TRỌNG."
                return

            temp_list = []
            for i, line in enumerate(lines[1:], 1):
                if not line.strip(): continue
                # Sử dụng csv.reader để xử lý dấu phẩy trong nội dung
                parts = list(csv.reader([line]))[0]
                if len(parts) <= i_status: continue

                if i == 1:
                    self.current_user_id = parts[i_id]
                    self.current_user_name = parts[i_name]

                temp_list.append({
                    'stt': str(i),
                    'model': parts[i_model],
                    'imei': parts[i_imei],
                    'status': parts[i_status],
                    'audit': parts[i_audit] if i_audit < len(parts) else ""
                })

            if temp_list:
                self.devices_data = temp_list
                self.user_info = f"NẠP THÀNH CÔNG: {len(temp_list)} MÁY\nUSER: {self.current_user_id}"
                self.refresh_table()
                self.selected_path = None # Reset sau khi xong
            else:
                self.user_info = "KHÔNG CÓ DỮ LIỆU TRONG FILE."

        except Exception as e:
            self.user_info = f"LỖI PHÂN TÍCH: {str(e)}"

    def refresh_table(self, *args):
        container = self.root.get_screen('main').ids.table_content
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
        pass

if __name__ == '__main__':
    DeviceApp().run()
