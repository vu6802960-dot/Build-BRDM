import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import os

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
    height: '45dp'
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
            height: '40dp'
            color: (0.12, 0.45, 0.7, 1)
            bold: True
            font_size: '13sp'
            halign: 'center'
            valign: 'middle'
            text_size: self.size

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
    user_info = StringProperty("VUI LÒNG CHỌN FILE .TXT")
    current_user_id = ""
    current_user_name = ""
    devices_data = ListProperty([])
    filter_mode = StringProperty("all")

    def build(self):
        return Builder.load_string(KV)

    def open_file_explorer(self):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            self.user_info = f"Lỗi khởi động chọn file: {str(e)}"

    def handle_selection(self, selection):
        if not selection:
            self.user_info = "Bạn chưa chọn file nào."
            return
        # Cập nhật trạng thái đang xử lý để người dùng biết app không bị treo
        self.user_info = "Đang xử lý dữ liệu..."
        Clock.schedule_once(lambda dt: self.process_file_v160(selection[0]), 0.2)

    def process_file_v160(self, path):
        try:
            # 1. Đọc file thủ công với chế độ bảo vệ ký tự
            if not os.path.exists(path):
                # Thử fix đường dẫn nếu trên Android
                if path.startswith('content://'):
                    self.user_info = "Lỗi: Android chặn truy cập file này (URI Content)."
                    return

            with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
                raw_lines = f.readlines()
            
            # 2. Lọc bỏ dòng trống và làm sạch ký tự lạ
            clean_lines = [l.strip() for l in raw_lines if l.strip()]
            
            if not clean_lines:
                self.user_info = "File không chứa nội dung."
                return

            # 3. Tìm Header "Single ID"
            header_idx = -1
            header_cols = []
            for i, line in enumerate(clean_lines):
                if "Single ID" in line:
                    header_idx = i
                    header_cols = [h.strip() for h in line.split(',')]
                    break
            
            if header_idx == -1:
                self.user_info = "Không tìm thấy tiêu đề 'Single ID'."
                return

            # 4. Tìm chỉ mục các cột quan trọng
            try:
                i_id = header_cols.index("Single ID")
                i_name = header_cols.index("Name")
                i_model = header_cols.index("Model Name")
                i_imei = header_cols.index("IMEI")
                i_status = header_cols.index("Status")
                i_audit = header_cols.index("Last Audit")
            except ValueError as e:
                self.user_info = f"File thiếu cột: {str(e)}"
                return

            # 5. Phân tích dữ liệu
            temp_data = []
            data_rows = clean_lines[header_idx + 1:]
            
            for idx, line in enumerate(data_rows, 1):
                # Tách cột (xử lý trường hợp Last Audit chứa dấu phẩy)
                cols = [c.strip() for c in line.split(',')]
                
                # Nếu số lượng cột nhiều hơn header, gộp phần thừa vào Last Audit
                if len(cols) > len(header_cols):
                    extra = ", ".join(cols[i_audit:])
                    cols[i_audit] = extra

                if len(cols) >= 5:
                    if idx == 1:
                        self.current_user_id = cols[i_id]
                        self.current_user_name = cols[i_name]
                    
                    temp_data.append({
                        'stt': str(idx),
                        'model': cols[i_model],
                        'imei': cols[i_imei],
                        'status': cols[i_status],
                        'audit': cols[i_audit] if i_audit < len(cols) else ""
                    })

            # 6. Hiển thị kết quả
            if temp_data:
                self.devices_data = temp_data
                self.user_info = f"ID: {self.current_user_id} | User: {self.current_user_name} ({len(temp_data)} máy)"
                self.refresh_table()
                self.play_beep('success')
            else:
                self.user_info = "Đọc file thành công nhưng không có dữ liệu máy."

        except Exception as e:
            self.user_info = f"Lỗi hệ thống: {str(e)}"
            self.play_beep('error')

    def refresh_table(self, *args):
        try:
            container = self.root.get_screen('main').ids.get('table_content')
            if not container: return
            container.clear_widgets()
            
            # Logic trạng thái Model
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
        # Giữ nguyên logic xuất file
        pass

    def play_beep(self, type_name):
        try:
            sound = SoundLoader.load(f"{type_name}.wav")
            if sound: sound.play()
        except: pass

if __name__ == '__main__':
    DeviceApp().run()
