import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import platform
import os
import shutil

# Xin quyền đặc biệt cho Android 11+
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
                rgba: (0.95, 0.95, 0.95, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.user_info
            size_hint_y: None
            height: '70dp'
            color: (0, 0.2, 0.4, 1)
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
    user_info = StringProperty("V1.6.7: CHỜ NHẬP FILE...")
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
            self.user_info = f"LỖI KHỞI ĐỘNG: {str(e)}"

    def handle_selection(self, selection):
        if not selection:
            self.user_info = "BẠN ĐÃ HỦY CHỌN FILE."
            return
        
        path = selection[0]
        # Hiển thị thông báo đang xử lý để người dùng biết App không treo
        self.user_info = f"ĐANG ĐỌC:\n{os.path.basename(path)}"
        Clock.schedule_once(lambda dt: self.process_file_v167(path), 0.2)

    def process_file_v167(self, path):
        try:
            # 1. KỸ THUẬT COPY FILE VÀO CACHE (Vượt qua Scoped Storage)
            temp_path = os.path.join(self.user_data_dir, "cached_device.txt")
            try:
                shutil.copy2(path, temp_path)
            except:
                # Nếu không copy được, thử đọc trực tiếp (dành cho PC)
                temp_path = path

            # 2. ĐỌC NHỊ PHÂN VÀ GIẢI MÃ (Vượt qua lỗi Encoding/BOM)
            with open(temp_path, 'rb') as f:
                raw_bytes = f.read()
            
            # Thử giải mã với các bảng mã phổ biến nhất
            decoded_text = ""
            for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
                try:
                    decoded_text = raw_bytes.decode(enc)
                    break
                except: continue
            
            if not decoded_text:
                self.user_info = "LỖI: KHÔNG THỂ GIẢI MÃ NỘI DUNG FILE."
                return

            # 3. LÀM SẠCH VÀ TÌM TIÊU ĐỀ (Vượt qua dòng trống đầu file)
            lines = [l.strip() for l in decoded_text.splitlines() if l.strip()]
            header_idx = -1
            for i, line in enumerate(lines):
                if "Single ID" in line and "Model Name" in line:
                    header_idx = i
                    break
            
            if header_idx == -1:
                self.user_info = "LỖI: FILE KHÔNG ĐÚNG CẤU TRÚC ERP."
                return

            # 4. PHÂN TÍCH CỘT THỦ CÔNG (Vượt qua lỗi dấu phẩy trong dữ liệu)
            headers = [h.strip() for h in lines[header_idx].split(',')]
            try:
                idx_id = headers.index("Single ID")
                idx_name = headers.index("Name")
                idx_model = headers.index("Model Name")
                idx_imei = headers.index("IMEI")
                idx_status = headers.index("Status")
                idx_audit = headers.index("Last Audit")
            except ValueError as e:
                self.user_info = f"THIẾU CỘT: {str(e)}"
                return

            parsed_data = []
            for i, line in enumerate(lines[header_idx+1:], 1):
                cols = [c.strip() for c in line.split(',')]
                if len(cols) < idx_status: continue

                # Lấy thông tin User từ dòng đầu tiên có dữ liệu
                if i == 1:
                    self.current_user_id = cols[idx_id]
                    self.current_user_name = cols[idx_name]

                # Gộp các phần dư vào Audit (nếu nội dung audit có dấu phẩy)
                audit_val = ""
                if idx_audit < len(cols):
                    audit_val = ", ".join(cols[idx_audit:])

                parsed_data.append({
                    'stt': str(i),
                    'model': cols[idx_model],
                    'imei': cols[idx_imei],
                    'status': cols[idx_status],
                    'audit': audit_val
                })

            # 5. HIỂN THỊ KẾT QUẢ
            if parsed_data:
                self.devices_data = parsed_data
                self.user_info = f"ID: {self.current_user_id} | {self.current_user_name}\nĐÃ NẠP: {len(parsed_data)} MÁY"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "CẢNH BÁO: FILE KHÔNG CÓ DỮ LIỆU MÁY."

        except Exception as e:
            self.user_info = f"LỖI HỆ THỐNG: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        try:
            container = self.root.get_screen('main').ids.table_content
            container.clear_widgets()
            
            # Logic lọc và tô màu
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
