from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from PIL import Image
import numpy as np

class CameraHandler:
    def __init__(self, callback):
        self.callback = callback
        self.camera = None
        self.popup = None

    def open_camera(self):
        # Tạo giao diện chụp ảnh tạm thời
        layout = BoxLayout(orientation='vertical')
        self.camera = Camera(play=True, resolution=(1280, 720))
        
        btn_layout = BoxLayout(size_hint_y=None, height=70, padding=10)
        capture_btn = Button(text="[b]CAPTURE[/b]", markup=True, background_color=(0.2, 0.6, 0.8, 1))
        capture_btn.bind(on_press=self.capture_image)
        
        cancel_btn = Button(text="CANCEL", background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())
        
        btn_layout.add_widget(capture_btn)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(self.camera)
        layout.add_widget(btn_layout)
        
        self.popup = Popup(title="Scan Device Label", content=layout, size_hint=(0.95, 0.9))
        self.popup.open()

    def capture_image(self, instance):
        if not self.camera or not self.camera.texture:
            return
            
        try:
            # Lấy dữ liệu pixel từ Camera Texture
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels
            
            # Chuyển đổi sang PIL Image
            image = Image.frombytes('RGBA', size, pixels)
            image = image.convert('RGB')
            # Kivy texture bị ngược trục Y nên cần lật lại
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            
            # Gọi OCR Processor (đã import trong main hoặc ocr_processor)
            from ocr_processor import OCRProcessor
            ocr = OCRProcessor()
            result = ocr.process_image(image)
            
            # Trả kết quả về cho App và đóng camera
            self.callback(result)
            self.popup.dismiss()
        except Exception as e:
            print(f"Error capturing: {e}")
            self.callback(None)