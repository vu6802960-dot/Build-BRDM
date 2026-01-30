from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from PIL import Image

class CameraHandler:
    def __init__(self, callback):
        self.callback = callback

    def open_camera(self):
        layout = BoxLayout(orientation='vertical')
        # Dùng resolution thấp (640x480) để Camera khởi động cực nhanh và ổn định
        self.camera = Camera(play=True, resolution=(640, 480))
        
        btn = Button(text="CAPTURE", size_hint_y=None, height=60)
        btn.bind(on_press=self.capture)
        
        layout.add_widget(self.camera)
        layout.add_widget(btn)
        
        self.popup = Popup(title="Scanner", content=layout, size_hint=(0.9, 0.9))
        self.popup.open()

    def capture(self, *args):
        if self.camera.texture:
            pix = self.camera.texture.pixels
            size = self.camera.texture.size
            img = Image.frombytes('RGBA', size, pix).convert('RGB')
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            from ocr_processor import OCRProcessor
            ocr = OCRProcessor()
            res = ocr.process_image(img)
            self.callback(res)
            self.popup.dismiss()
