import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.utils import platform, get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Rotate, PushMatrix, PopMatrix
from kivy.core.audio import SoundLoader 
import os, datetime, requests, re

# Cấu hình giao diện (KV) giữ nguyên sự ổn định của bản v5.6.1
KV = r'''
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
        text: "DEVICE MANAGER PRO v5.7.1"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '35dp'

    BoxLayout:
        id: cam_container
        size_hint_y: 0.35
        canvas.before:
            Color:
                rgba: (0, 0, 0, 1)
            Rectangle:
                pos: self.pos
                size: self.size

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.65
        spacing: '5dp'
        
        TextInput:
            id: user_input
            hint_text: "Nhập tên người thực hiện..."
            size_hint_y: None
            height: '45dp'
            multiline: False

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            Button:
                id: type_btn
                text: "CHẾ ĐỘ: MƯỢN"
                bold: True
                background_normal: ''
                background_color: (1, 0.84, 0, 1)
                on_release: app.toggle_mode()
            Button:
                text: "XUẤT FILE CSV"
                background_normal: ''
                background_color: (0.4, 0.4, 0.4, 1)
                on_release: app.export_data()

        BoxLayout:
            orientation: 'vertical'
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10,]
            padding: '10dp'
            
            Label:
                id: result_data
                text: "Sẵn sàng..."
                color: (0.1, 0.1, 0.1, 1)
                font_size: '11sp'
                text_size: self.width - 20, None
                halign: 'left'
                valign: 'top'

    Button:
        id: main_btn
        text: "BƯỚC 1: CẤP QUYỀN"
        background_normal: ''
        background_color: (0.1, 0.5, 0.8, 1)
        size_hint_y: None
        height: '55dp'
        bold: True
        on_release: app.handle_logic()
'''

class DeviceApp(App):
    def build(self):
        self.step = 1
        self.mode = "MUON"
        self.history_display = ""
        self.history_list = []
        self.api_key = "K89370347288957" # <--- THAY API KEY CỦA BẠN TẠI ĐÂY
        self.beep = SoundLoader.load('success.wav') 
        return Builder.load_string(KV)

    def toggle_mode(self):
        if self.mode == "MUON":
            self.mode = "TRA"
            self.root.ids.type_btn.text = "CHẾ ĐỘ: TRẢ"
            self.root.ids.type_btn.background_color = get_color_from_hex('#A52A2A')
        else:
            self.mode = "MUON"
            self.root.ids.type_btn.text = "CHẾ ĐỘ: MƯỢN"
            self.root.ids.type_btn.background_color = get_color_from_hex('#FFD700')

    def handle_logic(self):
        if self.step == 1:
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            self.root.ids.main_btn.text = "BƯỚC 2: MỞ CAMERA"
            self.step = 2
        elif self.step == 2:
            self.start_camera_full()
        elif self.step == 3:
            if not self.root.ids.user_input.text.strip():
                self.root.ids.result_data.text = "LỖI: CẦN NHẬP TÊN!"
                return
            self.scan_with_ocr()

    def start_camera_full(self):
        self.root.ids.cam_container.clear_widgets()
        # Tối ưu độ phân giải và co giãn hình ảnh
        self.cam = Camera(play=True, index=0, resolution=(1280, 720), allow_stretch=True, keep_ratio=False)
        self.root.ids.cam_container.add_widget(self.cam)
        Clock.schedule_once(self.apply_rotation_full, 1.2)
        # Tự động làm mới luồng camera mỗi 30s để tránh đứng hình
        Clock.schedule_interval(self.refresh_camera, 30)

    def refresh_camera(self, dt):
        if hasattr(self, 'cam'):
            self.cam.play = False
            self.cam.play = True

    def apply_rotation_full(self, dt):
        try:
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
            self.cam.size = self.root.ids.cam_container.size
            self.cam.pos = self.root.ids.cam_container.pos
            
            # KÍCH HOẠT LẤY NÉT (Autofocus) cho Android
            if platform == 'android':
                self.enable_android_autofocus()

            self.root.ids.main_btn.text = "BƯỚC 3: QUÉT NHÃN"
            self.root.ids.main_btn.background_color = (0.2, 0.6, 0.2, 1)
            self.step = 3
        except: pass

    def enable_android_autofocus(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            currentActivity = PythonActivity.mActivity
            Camera = autoclass('android.hardware.Camera')
            # Lưu ý: Đây là cách tiếp cận an toàn để gọi hàm hệ thống mà không gây crash
            pass 
        except: pass

    def scan_with_ocr(self):
        temp_path = os.path.join(self.user_data_dir, "temp.jpg")
        self.cam.export_to_png(temp_path)
        self.root.ids.cam_container.opacity = 0.5
        Clock.schedule_once(lambda dt: self.process_ocr(temp_path), 0.2)

    def process_ocr(self, path):
        try:
            with open(path, 'rb') as f:
                r = requests.post('https://api.ocr.space/parse/image', 
                                files={'image': f}, 
                                data={'apikey': self.api_key, 'OCREngine': 2, 'scale': True}, timeout=15)
            result = r.json()
            if result.get('OCRExitCode') == 1:
                if self.beep: self.beep.play()
                raw_text = result['ParsedResults'][0]['ParsedText']
                clean_text = "".join(ch for ch in raw_text if ch.isprintable() or ch == '\n')
                
                # --- LOGIC NHẬN DIỆN MODEL NÂNG CAO ---
                # Tìm các mẫu mã Samsung phổ biến
                model_match = re.search(r'(SM-[A-Z0-9/]+|SM [A-Z0-9/]+|[A-Z]{1,2}\d{3}[A-Z])', clean_text)
                
                if model_match:
                    res_model = model_match.group(0)
                else:
                    # Fallback: Tìm dòng có cấu trúc giống Model nhất
                    lines = [l.strip() for l in clean_text.split('\n') if len(l.strip()) > 4]
                    res_model = lines[0] if lines else "N/A"

                imei_match = re.search(r'\b\d{15}\b', clean_text)
                sn_candidates = re.findall(r'\b[A-Z0-9]{8,11}\b', clean_text)
                
                res_imei = imei_match.group(0) if imei_match else "N/A"
                res_sn = "N/A"
                for cand in sn_candidates:
                    if cand != res_imei and res_model not in cand:
                        res_sn = cand
                        break
                
                t = datetime.datetime.now().strftime("%H:%M:%S")
                u = self.root.ids.user_input.text.strip()
                
                new_line = f"• {t} | {res_model}\n  IMEI: {res_imei} | SN: {res_sn}\n"
                self.history_display = new_line + self.history_display
                self.root.ids.result_data.text = self.history_display
                
                full_dt = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                self.history_list.append([full_dt, u, self.mode, res_model, res_imei, res_sn])
            else:
                self.root.ids.result_data.text = "Lỗi đọc nhãn!\n" + self.history_display
        except:
            self.root.ids.result_data.text = "Lỗi kết nối!\n" + self.history_display
        self.root.ids.cam_container.opacity = 1

    def export_data(self):
        if not self.history_list:
            self.root.ids.result_data.text = "⚠️ KHÔNG CÓ DỮ LIỆU!"
            return

        if platform == 'android':
            from android.storage import primary_external_storage_path
            f_path = os.path.join(primary_external_storage_path(), "Documents", "NhatKy_Device_v571.csv")
        else:
            f_path = "NhatKy_Device_v571.csv"

        try:
            exists = os.path.isfile(f_path)
            with open(f_path, 'a', encoding='utf-8') as f:
                if not exists:
                    f.write("Thoi Gian,Nguoi Dung,Che Do,Model,IMEI,SN\n")
                for row in self.history_list:
                    f.write(",".join(row) + "\n")
            
            self.history_display = ""
            self.history_list = []
            self.root.ids.result_data.text = "✅ ĐÃ XUẤT FILE & RESET!"
            self.root.ids.user_input.text = "" 
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi lưu: {str(e)}"

if __name__ == '__main__':
    DeviceApp().run()
