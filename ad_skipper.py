import cv2
import numpy as np
import os

class AdSkipper:
    def __init__(self, video_path, ad_duration=30):
        self.video_path = video_path
        self.ad_duration = ad_duration
        self.video_capture = cv2.VideoCapture(video_path)
        self.frame_width = int(self.video_capture.get(3))
        self.frame_height = int(self.video_capture.get(4))
        self.fps = self.video_capture.get(5)

    def detect_ad(self):
        frame_count = 0
        ad_frames = []
        while self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if not ret:
                break
            frame_count += 1
            if self.is_ad_frame(frame):
                ad_frames.append(frame_count)
        self.video_capture.release()
        return ad_frames

    def is_ad_frame(self, frame):
        # Sử dụng thuật toán phân tích hình ảnh để phát hiện quảng cáo
        # Ví dụ: kiểm tra màu sắc, độ tương phản, v.v.
        # Ở đây, chúng ta sẽ sử dụng một thuật toán đơn giản để kiểm tra màu sắc
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        if cv2.countNonZero(mask) > self.frame_width * self.frame_height * 0.1:
            return True
        return False

    def skip_ad(self, ad_frames):
        # Tạo một video mới không có quảng cáo
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output.mp4', fourcc, self.fps, (self.frame_width, self.frame_height))
        self.video_capture = cv2.VideoCapture(self.video_path)
        frame_count = 0
        while self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if not ret:
                break
            frame_count += 1
            if frame_count not in ad_frames:
                out.write(frame)
        self.video_capture.release()
        out.release()

    def run(self):
        ad_frames = self.detect_ad()
        self.skip_ad(ad_frames)

if __name__ == '__main__':
    video_path = 'input.mp4'
    ad_skipper = AdSkipper(video_path)
    ad_skipper.run()