import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.utils import platform, get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Rotate, PushMatrix, PopMatrix
import os
import datetime
import requests # Thư viện để gửi ảnh lên server OCR

KV = r'''
BoxLayout:
    orientation: 'vertical'
    padding: '12dp'
    spacing: '10dp'
    canvas.before:
        Color:
            rgba: (0.95, 0.95, 0.95, 1)
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "DEVICE MANAGER PRO v5.3 (OCR ONLINE)"
        color: (0, 0, 0, 1)
        bold: True
        size_hint_y: None
        height: '35dp'

    # VÙNG CAMERA: Thu nhỏ (chiếm 35% màn hình)
    BoxLayout:
        id: cam_container
        size_hint_y: 0.35
        canvas.before:
            Color:
                rgba: (0, 0, 0, 1)
            Rectangle:
                pos: self.pos
                size: self.size

    # VÙNG DỮ LIỆU & NGHIỆP VỤ: Mở rộng (chiếm 65% màn hình)
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.65
        spacing: '8dp'
        
        TextInput:
            id: user_input
            hint_text: "Bắt buộc: Nhập tên người mượn/trả..."
            size_hint_y: None
            height: '45dp'
            multiline: False
            padding: [10, 10]

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            Button:
                id: type_btn
                text: "CHẾ ĐỘ: MƯỢN"
                bold: True
                background_normal: ''
                background_color: (1, 0.84, 0, 1) # Vàng
                on_release: app.toggle_mode()
            Button:
                text: "XUẤT FILE CSV"
                background_normal: ''
                background_color: (0.4, 0.4, 0.4, 1)
                on_release: app.export_data()

        # Vùng hiển thị dữ liệu quét (LỚN HƠN)
        BoxLayout:
            orientation: 'vertical'
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10,]
            padding: '12dp'
            
            Label:
                text: "KẾT QUẢ QUÉT NHÃN (OCR):"
                color: (0.5, 0.5, 0.5, 1)
                font_size: '12sp'
                size_hint_y: None
                height: '20dp'
                halign: 'left'
                text_size: self.size

            Label:
                id: result_data
                text: "Sẵn sàng..."
                color: (0.1, 0.1, 0.1, 1)
                bold: True
                font_size: '15sp'
                text_size: self.width, None
                halign: 'center'
                valign: 'middle'

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
        self.last_scan = "None"
        # HÃY THAY MÃ API KEY CỦA BẠN VÀO ĐÂY
        self.api_key = "K89370347288957" 
        return Builder.load_string(KV)

    def toggle_mode(self):
        if self.mode == "MUON":
            self.mode = "TRA"
            self.root.ids.type_btn.text = "CHẾ ĐỘ: TRẢ"
            self.root.ids.type_btn.background_color = get_color_from_hex('#A52A2A') # Nâu
        else:
            self.mode = "MUON"
            self.root.ids.type_btn.text = "CHẾ ĐỘ: MƯỢN"
            self.root.ids.type_btn.background_color = get_color_from_hex('#FFD700') # Vàng

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
            # RÀNG BUỘC: Phải điền tên mới được ấn Bước 3
            name = self.root.ids.user_input.text.strip()
            if not name:
                self.root.ids.result_data.text = "⚠️ LỖI: BẠN CHƯA NHẬP TÊN!"
                self.root.ids.result_data.color = (1, 0, 0, 1)
                return
            self.scan_with_ocr()

    def start_camera_full(self):
        self.root.ids.cam_container.clear_widgets()
        self.cam = Camera(play=True, index=0, resolution=(640, 480))
        self.root.ids.cam_container.add_widget(self.cam)
        Clock.schedule_once(self.apply_rotation_full, 1.2)

    def apply_rotation_full(self, dt):
        try:
            with self.cam.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.cam.center)
            with self.cam.canvas.after:
                PopMatrix()
            self.cam.size = (self.root.ids.cam_container.height, self.root.ids.cam_container.width)
            self.cam.center = self.root.ids.cam_container.center
            self.root.ids.result_data.text = "Hệ thống sẵn sàng.\nVui lòng đưa nhãn vào khung hình."
            self.root.ids.main_btn.text = "BƯỚC 3: QUÉT NHÃN NGAY"
            self.root.ids.main_btn.background_color = (0.2, 0.6, 0.2, 1)
            self.step = 3
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi camera: {e}"

    def scan_with_ocr(self):
        self.root.ids.result_data.text = "⌛ Đang nhận diện chữ... Vui lòng đợi."
        self.root.ids.result_data.color = (0, 0, 0, 1)
        
        # Chụp ảnh tạm
        temp_path = os.path.join(self.user_data_dir, "ocr_scan.jpg")
        self.cam.export_to_png(temp_path)
        
        # Nháy màn hình báo hiệu
        self.root.ids.cam_container.opacity = 0.5
        Clock.schedule_once(lambda dt: self.process_ocr_request(temp_path), 0.2)

    def process_ocr_request(self, path):
        try:
            # Gửi yêu cầu đến OCR.space API
            with open(path, 'rb') as f:
                payload = {
                    'apikey': self.api_key,
                    'language': 'eng', # Nhãn thường là tiếng Anh/Số
                    'isOverlayRequired': False,
                    'scale': True,
                    'OCREngine': 2 # Engine 2 mạnh hơn cho chữ số
                }
                r = requests.post('https://api.ocr.space/parse/image', files={'image': f}, data=payload, timeout=15)
                
            self.root.ids.cam_container.opacity = 1
            result = r.json()
            
            if result.get('OCRExitCode') == 1:
                text = result['ParsedResults'][0]['ParsedText'].strip()
                if text:
                    # Lấy 2 dòng đầu hoặc 40 ký tự đầu để lưu
                    self.last_scan = text.replace('\n', ' | ')[:40]
                    self.root.ids.result_data.text = f"THÀNH CÔNG:\n{self.last_scan}"
                    self.root.ids.result_data.color = (0, 0.5, 0, 1)
                else:
                    self.root.ids.result_data.text = "⚠️ Không tìm thấy chữ trên nhãn."
            else:
                self.root.ids.result_data.text = f"Lỗi API: {result.get('ErrorMessage')}"
        except Exception as e:
            self.root.ids.cam_container.opacity = 1
            self.root.ids.result_data.text = "Lỗi kết nối OCR: Hãy kiểm tra Internet!"

    def export_data(self):
        name = self.root.ids.user_input.text.strip()
        if not name:
            self.root.ids.result_data.text = "⚠️ CẦN NHẬP TÊN TRƯỚC KHI LƯU!"
            return
        
        if platform == 'android':
            from android.storage import primary_external_storage_path
            dir_path = os.path.join(primary_external_storage_path(), "Documents")
        else:
            dir_path = os.path.expanduser("~")

        full_path = os.path.join(dir_path, "Log_ThietBi_OCR.csv")
        dt = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")

        try:
            exists = os.path.isfile(full_path)
            with open(full_path, 'a', encoding='utf-8') as f:
                if not exists:
                    f.write("Thoi Gian,Nguoi Thuc Hien,Che Do,Du Lieu OCR\n")
                f.write(f"{dt},{name},{self.mode},{self.last_scan}\n")
            self.root.ids.result_data.text = f"✅ ĐÃ LƯU: {dt}"
            self.root.ids.result_data.color = (0, 0, 1, 1)
        except Exception as e:
            self.root.ids.result_data.text = f"Lỗi file: {str(e)}"

if __name__ == '__main__':
    DeviceApp().run()
