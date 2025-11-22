# app/services/ocr_preprocessor.py
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
import pyiqa
import os

class OCRPreprocessor:
    def __init__(self, image_path, policies, device=None):
        self.image_path = image_path
        self.policies = policies
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.image = cv2.imread(image_path)
        self.processed_image = self.image.copy()
        self.quality_score = None

        if self.policies.get("quality_check", {}).get("enabled", False):
            self.niqe_metric = pyiqa.create_metric('niqe', device=self.device)
        else:
            self.niqe_metric = None

    def check_quality(self):
        if not self.niqe_metric:
            return
        image_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
        image_tensor = torch.from_numpy(image_rgb).float() / 255.0
        image_tensor = image_tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)
        with torch.no_grad():
            self.quality_score = self.niqe_metric(image_tensor).item()
        print(f"Quality Score (NIQE): {self.quality_score:.4f}")
        threshold = self.policies["quality_check"].get("threshold", 5.0)
        if self.quality_score > threshold:
            print("Image quality low → enabling denoise")
            self.policies["denoise"] = True
        else:
            self.policies["denoise"] = False

    def grayscale(self):
        if self.policies.get("grayscale", False):
            self.processed_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)

    def denoise(self):
        if self.policies.get("denoise", False):
            if len(self.processed_image.shape) == 2:
                self.processed_image = cv2.fastNlMeansDenoising(self.processed_image)
            else:
                self.processed_image = cv2.fastNlMeansDenoisingColored(self.processed_image, None, 10, 10, 7, 21)

    def enhance_contrast(self):
        if self.policies.get("contrast_enhance", False):
            if len(self.processed_image.shape) == 2:
                self.processed_image = cv2.equalizeHist(self.processed_image)
            else:
                ycrcb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2YCrCb)
                ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
                self.processed_image = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    def resize(self):
        if "resize" in self.policies:
            target_dpi = self.policies["resize"].get("dpi", None)
            if target_dpi:
                scale_factor = target_dpi / 72
                new_width = int(self.processed_image.shape[1] * scale_factor)
                new_height = int(self.processed_image.shape[0] * scale_factor)
                self.processed_image = cv2.resize(
                    self.processed_image, (new_width, new_height), interpolation=cv2.INTER_CUBIC
                )

    def save(self, output_path=None):
        output_path = output_path or "processed_" + os.path.basename(self.image_path)
        cv2.imwrite(output_path, self.processed_image)
        return output_path
   

    def run_pipeline(self):
        if self.policies.get("quality_check", {}).get("enabled", False):
            self.check_quality()
        self.grayscale()
        self.denoise()
        self.enhance_contrast()
        self.resize()
        output_path = self.save()
        return output_path
