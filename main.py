import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.uix.stencilview import StencilView
from kivy.utils import platform, get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Rotate, PushMatrix, PopMatrix
from kivy.core.audio import SoundLoader 
import os, datetime, requests, re

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
        text: "DEVICE MANAGER PRO v7.0"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '35dp'

    StencilView:
        id: cam_stencil
        size_hint_y: 0.35
        canvas.before:
            Color:
                rgba: (0, 0, 0, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            id: cam_container
            size: self.parent.size
            pos: self.parent.pos

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
                text: "Sẵn sàng quét..."
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
        self.api_key = "K89370347288957" # Thay key của bạn
        self.beep_ok = SoundLoader.load('success.wav') 
        self.beep_error = SoundLoader.load('error.wav') # Tích hợp file âm thanh bạn gửi
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

    def start_camera_full(self):
        self.root.ids.cam_container.clear_widgets()
        self.cam = Camera(play=True, index=0, resolution=(1920, 1080), allow_stretch=True, keep_ratio=True)
        self.root.ids.cam_container.add_widget(self.cam)
        Clock.schedule_once(self.apply_rotation_full, 1.0)

    def apply_rotation_full(self, dt):
        try:
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
            self.cam.size = self.root.ids.cam_stencil.size
            self.cam.pos = self.root.ids.cam_stencil.pos
            self.root.ids.main_btn.text = "BƯỚC 3: QUÉT NHÃN"
            self.root.ids.main_btn.background_color = (0.2, 0.6, 0.2, 1)
            self.step = 3
        except: pass

    def scan_with_ocr(self):
        # Reset camera để tránh lưu ảnh cũ
        self.cam.play = False
        self.cam.play = True
        temp_path = os.path.join(self.user_data_dir, "temp.jpg")
        # Đợi camera ổn định ánh sáng ở khoảng cách 25cm
        Clock.schedule_once(lambda dt: self._capture_logic(temp_path), 0.2)

    def _capture_logic(self, path):
        self.cam.export_to_png(path)
        self.root.ids.cam_stencil.opacity = 0.5
        self.process_ocr_v7(path)

    def process_ocr_v7(self, path):
        try:
            with open(path, 'rb') as f:
                payload = {
                    'apikey': self.api_key,
                    'OCREngine': 2,
                    'scale': True,
                    'detectOrientation': True,
                    'language': 'eng'
                }
                r = requests.post('https://api.ocr.space/parse/image', files={'image': f}, data=payload, timeout=15)
            
            result = r.json()
            if result.get('OCRExitCode') == 1:
                raw_text = result['ParsedResults'][0]['ParsedText'].upper()
                
                # --- TRÍCH XUẤT DỮ LIỆU ---
                model_match = re.search(r'SM-[A-Z0-9]+', raw_text)
                imei_match = re.search(r'\d{15}', raw_text)
                sn_match = re.search(r'S/N:?\s*([A-Z0-9]{11})', raw_text) or re.search(r'\b[A-Z0-9]{11}\b', raw_text)

                res_model = model_match.group(0) if model_match else None
                res_imei = imei_match.group(0) if imei_match else None
                res_sn = sn_match.group(1) if (sn_match and hasattr(sn_match, 'group') and len(sn_match.groups()) > 0) else (sn_match.group(0) if sn_match else None)

                # --- RÀNG BUỘC HIỂN THỊ CHẶT CHẼ ---
                # Chỉ hiển thị nếu có Model VÀ (có IMEI HOẶC có SN)
                if res_model and (res_imei or res_sn):
                    if self.beep_ok: self.beep_ok.play()
                    t = datetime.datetime.now().strftime("%H:%M:%S")
                    u = self.root.ids.user_input.text.strip()
                    
                    final_imei = res_imei if res_imei else "N/A"
                    final_sn = res_sn if res_sn else "N/A"
                    
                    new_line = f"• {t} | {res_model}\n  IMEI: {final_imei} | SN: {final_sn}\n"
                    self.history_display = new_line + self.history_display
                    self.root.ids.result_data.text = self.history_display
                    
                    full_dt = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    self.history_list.append([full_dt, u, self.mode, res_model, final_imei, final_sn])
                else:
                    # Phát âm thanh báo lỗi khi thiếu thông tin
                    if self.beep_error: self.beep_error.play()
                    
                    msg = "❌ QUÉT THẤT BẠI: THÔNG TIN CHƯA ĐỦ!\n"
                    if not res_model: msg += "- Thiếu Model (SM-...)\n"
                    if not (res_imei or res_sn): msg += "- Thiếu IMEI/SN\n"
                    msg += "Gợi ý: Nghiêng máy tránh lóa đèn văn phòng."
                    self.root.ids.result_data.text = msg + "\n---\n" + self.history_display
            else:
                if self.beep_error: self.beep_error.play()
                self.root.ids.result_data.text = "⚠️ LỖI PHẢN HỒI OCR! THỬ LẠI."
        except:
            if self.beep_error: self.beep_error.play()
            self.root.ids.result_data.text = "⚠️ LỖI MẠNG! KIỂM TRA WIFI/4G."
        
        self.root.ids.cam_stencil.opacity = 1

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
                if self.beep_error: self.beep_error.play()
                self.root.ids.result_data.text = "LỖI: CHƯA NHẬP TÊN!"
                return
            self.scan_with_ocr()

    def export_data(self):
        if not self.history_list:
            self.root.ids.result_data.text = "⚠️ KHÔNG CÓ DỮ LIỆU ĐỂ XUẤT!"
            return
        if platform == 'android':
            from android.storage import primary_external_storage_path
            f_path = os.path.join(primary_external_storage_path(), "Documents", "NhatKy_v70.csv")
        else: f_path = "NhatKy_v70.csv"
        try:
            exists = os.path.isfile(f_path)
            with open(f_path, 'a', encoding='utf-8') as f:
                if not exists: f.write("Thoi Gian,Nguoi Dung,Che Do,Model,IMEI,SN\n")
                for row in self.history_list: f.write(",".join(row) + "\n")
            self.history_display = ""; self.history_list = []
            self.root.ids.result_data.text = "✅ ĐÃ LƯU FILE CSV THÀNH CÔNG!"; self.root.ids.user_input.text = "" 
        except: self.root.ids.result_data.text = "LỖI KHI LƯU FILE!"

if __name__ == '__main__':
    DeviceApp().run()
