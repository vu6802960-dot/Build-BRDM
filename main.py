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

# Tự động xin quyền truy cập bộ nhớ trên Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

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
        font_size: '10sp'
        halign: 'center'
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
            height: '65dp'
            color: (0.05, 0.3, 0.5, 1)
            bold: True
            font_size: '11sp'
            halign: 'center'
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
    user_info = StringProperty("V1.6.6: HỆ THỐNG SẴN SÀNG\nVUI LÒNG CHỌN FILE")
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
            self.user_info = f"LỖI: {str(e)}"

    def handle_selection(self, selection):
        if not selection: return
        path = selection[0]
        self.user_info = f"ĐANG ĐỌC FILE:\n{os.path.basename(path)}"
        # Giải phóng luồng giao diện để hiện chữ "Đang đọc"
        Clock.schedule_once(lambda dt: self.parse_engine_v166(path), 0.2)

    def parse_engine_v166(self, path):
        try:
            # Bước 1: Đọc dưới dạng Binary để không bị kẹt bởi đường dẫn URI hoặc Encoding
            if not os.path.exists(path):
                self.user_info = f"LỖI: Android chặn truy cập đường dẫn này.\nHãy thử chép file vào thư mục Download."
                return

            with open(path, 'rb') as f:
                raw_data = f.read()

            # Bước 2: Decode linh hoạt
            text = ""
            for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
                try:
                    text = raw_data.decode(enc)
                    break
                except: continue
            
            if not text:
                self.user_info = "LỖI: Không thể giải mã định dạng file."
                return

            # Bước 3: Tiền xử lý dữ liệu - Tìm Header Single ID
            # Cách này giúp bỏ qua dòng trống đầu file my_device.txt
            lines = text.splitlines()
            header_idx = -1
            for i, line in enumerate(lines):
                if "Single ID" in line and "Model Name" in line:
                    header_idx = i
                    break
            
            if header_idx == -1:
                self.user_info = "LỖI: Cấu trúc file không đúng (Thiếu tiêu đề Single ID)."
                return

            # Bước 4: Tách cột thủ công để đảm bảo độ chính xác tuyệt đối
            header_line = lines[header_idx].split(',')
            try:
                # Tìm vị trí các cột dựa trên file thực tế
                idx_id = header_line.index("Single ID")
                idx_name = header_line.index("Name")
                idx_model = header_line.index("Model Name")
                idx_imei = header_line.index("IMEI")
                idx_status = header_line.index("Status")
                idx_audit = header_line.index("Last Audit")
            except ValueError as ve:
                self.user_info = f"LỖI: File thiếu cột bắt buộc: {str(ve)}"
                return

            final_list = []
            data_lines = lines[header_idx + 1:]
            
            for i, line in enumerate(data_lines, 1):
                if not line.strip(): continue
                cols = [c.strip() for c in line.split(',')]
                
                # Nếu dòng dữ liệu đủ cột
                if len(cols) >= idx_status:
                    if i == 1:
                        self.current_user_id = cols[idx_id]
                        self.current_user_name = cols[idx_name]
                    
                    # Xử lý trường hợp cột Audit có dấu phẩy bên trong
                    audit_val = ""
                    if idx_audit < len(cols):
                        audit_val = ", ".join(cols[idx_audit:])

                    final_list.append({
                        'stt': str(i),
                        'model': cols[idx_model],
                        'imei': cols[idx_imei],
                        'status': cols[idx_status],
                        'audit': audit_val
                    })

            # Bước 5: Cập nhật UI
            if final_list:
                self.devices_data = final_list
                self.user_info = f"ID: {self.current_user_id} | {self.current_user_name}\nĐÃ NẠP THÀNH CÔNG {len(final_list)} MÁY"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "LỖI: Không đọc được dòng dữ liệu nào."

        except Exception as e:
            self.user_info = f"LỖI HỆ THỐNG: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        try:
            container = self.root.get_screen('main').ids.table_content
            container.clear_widgets()
            
            # Logic tính toán Model xanh/trắng
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
        # Sẽ bổ sung ở bản nâng cao
        pass

    def play_beep(self, type_name):
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound: sound.play()
        except: pass

if __name__ == '__main__':
    DeviceApp().run()
