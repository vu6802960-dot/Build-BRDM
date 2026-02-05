from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Rotate, PushMatrix, PopMatrix

# Giao diện đầy đủ các thành phần nghiệp vụ
KV = r'''
ScreenManager:
    LoadingScreen:
    MainScreen:

<LoadingScreen>:
    name: 'loading'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        MDLabel:
            text: "DEVICE MANAGER PRO\nĐang khởi tạo hệ thống..."
            halign: "center"
            theme_text_color: "Primary"
            font_style: "Button"

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "12dp"
        spacing: "10dp"

        # 1. CAMERA VÙNG HIỂN THỊ (Sẽ xoay dọc -90 độ)
        MDCard:
            size_hint_y: 0.35
            md_bg_color: 0, 0, 0, 1
            radius: [15,]
            RelativeLayout:
                id: cam_container
                MDLabel:
                    text: "Camera Screen"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 0.3

        # 2. FORM NHẬP LIỆU & QUẢN LÝ
        MDCard:
            orientation: 'vertical'
            padding: "15dp"
            spacing: "10dp"
            radius: [15,]
            elevation: 1
            size_hint_y: 0.55

            MDTextField:
                id: borrower_name
                hint_text: "Tên người mượn / trả"
                mode: "rectangle"
                icon_left: "account"

            # Ô chọn Mượn/Trả (Dạng Toggle Button chuyên nghiệp)
            MDBoxLayout:
                size_hint_y: None
                height: "50dp"
                spacing: "10dp"
                MDLabel:
                    text: "Loại hình:"
                    bold: True
                    size_hint_x: 0.4
                MDRectangleFlatIconButton:
                    id: type_btn
                    text: "MƯỢN"
                    icon: "export"
                    size_hint_x: 0.6
                    on_release: root.toggle_type()

            MDLabel:
                text: "DỮ LIỆU ĐÃ QUÉT:"
                font_style: "Caption"
                bold: True

            # 3. VÙNG HIỂN THỊ DỮ LIỆU QUÉT ĐƯỢC
            ScrollView:
                MDLabel:
                    id: scan_result
                    text: "Chưa có dữ liệu scan..."
                    size_hint_y: None
                    height: self.texture_size[1]
                    theme_text_color: "Secondary"

        # 4. HÀNG NÚT BẤM ĐIỀU KHIỂN
        MDBoxLayout:
            size_hint_y: None
            height: "55dp"
            spacing: "10dp"

            MDFillRoundFlatButton:
                id: scan_btn
                text: "BẬT CAMERA QUÉT"
                size_hint_x: 0.7
                on_release: root.activate_camera()
            
            MDFillRoundFlatIconButton:
                text: "EXPORT"
                icon: "file-export"
                size_hint_x: 0.3
                md_bg_color: 0.5, 0.5, 0.5, 1
                on_release: root.export_data()
'''

class LoadingScreen(Screen):
    pass

class MainScreen(Screen):
    def toggle_type(self):
        if self.ids.type_btn.text == "MƯỢN":
            self.ids.type_btn.text = "TRẢ"
            self.ids.type_btn.icon = "import"
        else:
            self.ids.type_btn.text = "MƯỢN"
            self.ids.type_btn.icon = "export"

    def activate_camera(self):
        # Xin quyền trước khi mở
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA])
        
        self.ids.scan_result.text = "Đang khởi động Camera..."
        self.ids.scan_btn.disabled = True
        Clock.schedule_once(self.deferred_camera_load, 1.5)

    def deferred_camera_load(self, dt):
        from kivy.uix.camera import Camera
        try:
            self.camera_obj = Camera(play=True, resolution=(-1, -1))
            
            # FIX: XOAY CAMERA DỌC CHO SAMSUNG
            with self.camera_obj.canvas.before:
                PushMatrix()
                Rotate(angle=-90, origin=self.camera_obj.center)
            with self.camera_obj.canvas.after:
                PopMatrix()
                
            self.ids.cam_container.clear_widgets()
            self.ids.cam_container.add_widget(self.camera_obj)
            self.ids.scan_result.text = "Hệ thống sẵn sàng quét dữ liệu."
            self.ids.scan_btn.text = "QUÉT (SCAN)"
            self.ids.scan_btn.disabled = False
        except Exception as e:
            self.ids.scan_result.text = f"Lỗi camera: {str(e)}"

    def export_data(self):
        # Logic xuất CSV đơn giản
        user = self.ids.borrower_name.text
        if not user:
            self.ids.scan_result.text = "LỖI: Vui lòng nhập tên!"
            return
        self.ids.scan_result.text = f"Đã xuất file thành công cho: {user}"

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def on_start(self):
        # Giữ màn hình Loading 2 giây để Samsung ổn định RAM
        Clock.schedule_once(self.switch_to_main, 2)

    def switch_to_main(self, dt):
        self.root.current = 'main'

if __name__ == '__main__':
    MainApp().run()
