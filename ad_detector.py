import cv2
import numpy as np
from sklearn.metrics import mean_squared_error

class AdDetector:
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.ad_frames = []
        self.non_ad_frames = []

    def extract_features(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        return hist.flatten()

    def compare_frames(self, frame1, frame2):
        features1 = self.extract_features(frame1)
        features2 = self.extract_features(frame2)
        return mean_squared_error(features1, features2)

    def detect_ad(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count % 10 == 0:
                if not self.ad_frames:
                    self.ad_frames.append(frame)
                else:
                    similarity = self.compare_frames(frame, self.ad_frames[-1])
                    if similarity < self.threshold:
                        self.ad_frames.append(frame)
                    else:
                        self.non_ad_frames.append(frame)
        cap.release()
        return self.ad_frames, self.non_ad_frames

    def save_ad_frames(self, ad_frames, output_path):
        for i, frame in enumerate(ad_frames):
            cv2.imwrite(f"{output_path}/ad_frame_{i}.jpg", frame)

    def save_non_ad_frames(self, non_ad_frames, output_path):
        for i, frame in enumerate(non_ad_frames):
            cv2.imwrite(f"{output_path}/non_ad_frame_{i}.jpg", frame)

def main():
    detector = AdDetector()
    video_path = "input_video.mp4"
    ad_frames, non_ad_frames = detector.detect_ad(video_path)
    detector.save_ad_frames(ad_frames, "ad_frames")
    detector.save_non_ad_frames(non_ad_frames, "non_ad_frames")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")