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

# Xin quyền truy cập bộ nhớ mức cao nhất có thể cho ứng dụng
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE, 
        Permission.WRITE_EXTERNAL_STORAGE
    ])

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
                rgba: (0.96, 0.96, 0.96, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.user_info
            size_hint_y: None
            height: '70dp'
            color: (0.05, 0.25, 0.45, 1)
            bold: True
            font_size: '12sp'
            halign: 'center'
            valign: 'middle'
            text_size: self.width, None

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
    user_info = StringProperty("V1.6.8: SẴN SÀNG\nVUI LÒNG NHẬN FILE")
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")
    current_user_id = ""
    current_user_name = ""

    def build(self):
        return Builder.load_string(KV)

    def open_file_explorer(self):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            self.user_info = f"LỖI KHỞI ĐỘNG CHỌN FILE: {str(e)}"

    def handle_selection(self, selection):
        if not selection:
            self.user_info = "BẠN ĐÃ HỦY CHỌN FILE."
            return
        
        # Lấy đường dẫn file
        path = selection[0]
        self.user_info = f"ĐANG XỬ LÝ:\n{os.path.basename(path)}"
        
        # Sử dụng Clock để tách biệt quá trình đọc file khỏi UI Thread
        Clock.schedule_once(lambda dt: self.parse_binary_v168(path), 0.1)

    def parse_binary_v168(self, path):
        try:
            # 1. ĐỌC NHỊ PHÂN TRỰC TIẾP (Bỏ qua mọi rào cản Text Mode)
            if not os.path.exists(path):
                # Thử fix đường dẫn ảo trên Android
                self.user_info = "LỖI: KHÔNG TÌM THẤY TỆP.\nHãy thử để file trong thư mục DOWNLOAD."
                return

            with open(path, 'rb') as f:
                raw_bytes = f.read()

            if len(raw_bytes) == 0:
                self.user_info = "LỖI: TỆP TRỐNG (0 BYTES)."
                return

            # 2. GIẢI MÃ THỦ CÔNG
            content = ""
            for codec in ['utf-8-sig', 'utf-8', 'latin-1']:
                try:
                    content = raw_bytes.decode(codec)
                    break
                except: continue

            if not content:
                self.user_info = "LỖI: KHÔNG THỂ GIẢI MÃ TỆP."
                return

            # 3. LỌC DỮ LIỆU THỰC SỰ
            lines = content.splitlines()
            valid_lines = [l.strip() for l in lines if l.strip()] # Loại bỏ dòng trống

            # Tìm dòng tiêu đề
            header_idx = -1
            for i, line in enumerate(valid_lines):
                if "Single ID" in line and "Model Name" in line:
                    header_idx = i
                    break
            
            if header_idx == -1:
                self.user_info = "LỖI: KHÔNG TÌM THẤY TIÊU ĐỀ 'Single ID'."
                return

            # 4. TRÍCH XUẤT CỘT
            headers = [h.strip() for h in valid_lines[header_idx].split(',')]
            try:
                i_id = headers.index("Single ID")
                i_name = headers.index("Name")
                i_model = headers.index("Model Name")
                i_imei = headers.index("IMEI")
                i_status = headers.index("Status")
                i_audit = headers.index("Last Audit")
            except ValueError as e:
                self.user_info = f"LỖI THIẾU CỘT: {str(e)}"
                return

            temp_list = []
            data_rows = valid_lines[header_idx + 1:]
            
            for idx, line in enumerate(data_rows, 1):
                cols = [c.strip() for c in line.split(',')]
                if len(cols) < i_status: continue

                if idx == 1:
                    self.current_user_id = cols[i_id]
                    self.current_user_name = cols[i_name]
                
                # Gộp cột Audit nếu bị lệch do dấu phẩy
                audit_str = ", ".join(cols[i_audit:]) if i_audit < len(cols) else ""

                temp_list.append({
                    'stt': str(idx),
                    'model': cols[i_model],
                    'imei': cols[i_imei],
                    'status': cols[i_status],
                    'audit': audit_str
                })

            # 5. CẬP NHẬT GIAO DIỆN
            if temp_list:
                self.devices_data = temp_list
                self.user_info = f"ID: {self.current_user_id} | {self.current_user_name}\nĐÃ NẠP THÀNH CÔNG: {len(temp_list)} MÁY"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "LỖI: KHÔNG CÓ DỮ LIỆU HỢP LỆ."

        except Exception as e:
            self.user_info = f"LỖI HỆ THỐNG: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        try:
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
        except: pass

    def toggle_filter(self):
        modes = ["all", "du", "thieu"]
        self.filter_mode = modes[(modes.index(self.filter_mode) + 1) % 3]
        self.refresh_table()

    def export_data(self):
        pass

    def play_beep(self, type_name):
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound: sound.play()
        except: pass

if __name__ == '__main__':
    DeviceApp().run()
