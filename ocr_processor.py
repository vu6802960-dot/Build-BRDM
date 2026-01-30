from jnius import autoclass
from kivy.utils import platform
import re

class OCRProcessor:
    def __init__(self):
        self.client = None
        if platform == 'android':
            try:
                TextRecognition = autoclass('com.google.mlkit.vision.text.TextRecognition')
                TextRecognizerOptions = autoclass('com.google.mlkit.vision.text.latin.TextRecognizerOptions')
                self.client = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
                self.InputImage = autoclass('com.google.mlkit.vision.common.InputImage')
            except Exception as e:
                print(f"ML Kit Init Error: {e}")

    def process_image(self, pil_image):
        if platform != 'android':
            return {'model': 'PC-Test', 'imei': '123456789012345', 'smsn': 'ABC12345'}

        try:
            # Chuyển PIL Image sang định dạng mà ML Kit hiểu (Bitmap)
            # Để đơn giản và tránh lỗi bộ nhớ, ta lưu tạm file
            temp_path = "last_scan.jpg"
            pil_image.save(temp_path)
            
            File = autoclass('java.io.File')
            Uri = autoclass('android.net.Uri')
            file_obj = File(temp_path)
            uri = Uri.fromFile(file_obj)
            
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            input_image = self.InputImage.fromFilePath(context, uri)
            
            # Gọi nhận diện
            task = self.client.process(input_image)
            
            # Đợi kết quả (Sử dụng vòng lặp an toàn thay vì block app)
            import time
            start_time = time.time()
            while not task.isComplete():
                if time.time() - start_time > 5: break # Timeout 5s
                time.sleep(0.1)
                
            if task.isSuccessful():
                result_text = task.getResult().getText()
                return self.parse_text(result_text)
            return None
        except Exception as e:
            print(f"OCR Error: {e}")
            return None

    def parse_text(self, text):
        imei = re.search(r'\d{15}', text)
        model = re.search(r'SM-[A-Z0-9]+', text)
        return {
            'model': model.group() if model else 'Unknown',
            'imei': imei.group() if imei else '',
            'smsn': 'N/A'
        }
