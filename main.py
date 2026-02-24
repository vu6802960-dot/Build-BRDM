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

# Xin quyền truy cập toàn diện trên Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE, 
        Permission.WRITE_EXTERNAL_STORAGE,
        # Quyền này giúp Android 11+ dễ thở hơn khi đọc file txt
        "android.permission.MANAGE_EXTERNAL_STORAGE" 
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
            height: '75dp'
            color: (0, 0.2, 0.5, 1)
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
    user_info = StringProperty("V1.6.9: HỆ THỐNG SẴN SÀNG\nHÃY CHỌN FILE .TXT")
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
            self.user_info = f"KHÔNG MỞ ĐƯỢC TRÌNH CHỌN FILE: {str(e)}"

    def handle_selection(self, selection):
        if not selection:
            self.user_info = "BẠN CHƯA CHỌN FILE NÀO."
            return
        
        path = selection[0]
        self.user_info = f"ĐANG PHÂN TÍCH FILE:\n{os.path.basename(path)}"
        # Đợi 0.5 giây để UI cập nhật chữ "Đang phân tích"
        Clock.schedule_once(lambda dt: self.ultimate_parse_v169(path), 0.5)

    def ultimate_parse_v169(self, path):
        try:
            raw_data = None
            
            # Kỹ thuật đọc cưỡng ép: Nếu open(path) thất bại, thử tìm file trong Download
            try:
                with open(path, 'rb') as f:
                    raw_data = f.read()
            except Exception as e:
                # Nếu không đọc được từ đường dẫn ảo, thử tìm trong thư mục Download thật
                filename = os.path.basename(path)
                alt_path = f"/storage/emulated/0/Download/{filename}"
                if os.path.exists(alt_path):
                    with open(alt_path, 'rb') as f:
                        raw_data = f.read()
                else:
                    self.user_info = f"LỖI TRUY CẬP: Android chặn đọc file này.\nThử chép file vào Download & chọn lại."
                    return

            if not raw_data or len(raw_data) < 10:
                self.user_info = "LỖI: FILE KHÔNG CÓ DỮ LIỆU HOẶC QUÁ NHỎ."
                return

            # Giải mã nhị phân
            decoded_content = ""
            for codec in ['utf-8-sig', 'utf-8', 'latin-1']:
                try:
                    decoded_content = raw_data.decode(codec)
                    break
                except: continue

            if not decoded_content:
                self.user_info = "LỖI: ĐỊNH DẠNG VĂN BẢN KHÔNG HỢP LỆ."
                return

            # Xử lý nội dung (Loại bỏ dòng trống đầu file my_device.txt)
            lines = [l.strip() for l in decoded_content.splitlines() if l.strip()]
            
            # Tìm Header "Single ID"
            header_idx = -1
            for i, line in enumerate(lines):
                if "Single ID" in line and "Model Name" in line:
                    header_idx = i
                    break
            
            if header_idx == -1:
                self.user_info = "LỖI: FILE THIẾU CỘT TIÊU ĐỀ 'Single ID'."
                return

            # Phân tích các cột
            headers = [h.strip() for h in lines[header_idx].split(',')]
            try:
                i_id = headers.index("Single ID")
                i_name = headers.index("Name")
                i_model = headers.index("Model Name")
                i_imei = headers.index("IMEI")
                i_status = headers.index("Status")
                i_audit = headers.index("Last Audit")
            except ValueError as ve:
                self.user_info = f"LỖI CẤU TRÚC: Thiếu cột {str(ve)}"
                return

            temp_list = []
            data_rows = lines[header_idx + 1:]
            
            for idx, line in enumerate(data_rows, 1):
                cols = [c.strip() for c in line.split(',')]
                if len(cols) <= i_status: continue

                if idx == 1:
                    self.current_user_id = cols[i_id]
                    self.current_user_name = cols[i_name]
                
                # Gộp cột audit nếu có dấu phẩy
                audit_str = ", ".join(cols[i_audit:]) if i_audit < len(cols) else ""

                temp_list.append({
                    'stt': str(idx),
                    'model': cols[i_model],
                    'imei': cols[i_imei],
                    'status': cols[i_status],
                    'audit': audit_str
                })

            if temp_list:
                self.devices_data = temp_list
                self.user_info = f"ID: {self.current_user_id} | {self.current_user_name}\nĐÃ NẠP {len(temp_list)} THIẾT BỊ THÀNH CÔNG!"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "CẢNH BÁO: Không tìm thấy máy nào trong file."

        except Exception as e:
            self.user_info = f"LỖI PHÁT SINH: {str(e)}"
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
