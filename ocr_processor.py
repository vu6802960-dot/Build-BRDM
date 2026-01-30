import cv2
import numpy as np
import re
from PIL import Image
import pytesseract

class OCRProcessor:
    def __init__(self):
        self.config = r'--oem 3 --psm 6'

    def preprocess(self, pil_img):
        # Chuyển sang OpenCV BGR
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        # Xám & Khử nhiễu
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3,3), 0)
        # Ngưỡng thích nghi (Tốt cho tem nhãn phản quang)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return Image.fromarray(thresh)

    def process_image(self, image):
        processed = self.preprocess(image)
        # Phóng to để tăng độ chính xác
        w, h = processed.size
        processed = processed.resize((w*2, h*2), Image.LANCZOS)
        text = pytesseract.image_to_string(processed, config=self.config)
        
        return {
            'model': (re.search(r'SM-[A-Z0-9]+', text) or re.search(r'', '')).group() if 'SM-' in text else 'Unknown',
            'imei': (re.search(r'\b\d{15}\b', text) or re.search(r'', '')).group() if re.search(r'\b\d{15}\b', text) else '',
            'smsn': (re.search(r'\b[A-Z0-9]{8}\b', text) or re.search(r'', '')).group() if re.search(r'\b[A-Z0-9]{8}\b', text) else 'N/A'
        }