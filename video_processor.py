import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import os

class VideoProcessor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_clip = VideoFileClip(video_path)

    def extract_frames(self):
        try:
            frames = []
            for frame in self.video_clip.iter_frames():
                frames.append(frame)
            return frames
        except Exception as e:
            print(f"Error extracting frames: {e}")
            return []

    def detect_advertisement(self, frames):
        try:
            ad_frames = []
            for frame in frames:
                # Sử dụng kỹ thuật xử lý ảnh để phát hiện quảng cáo
                # Ví dụ: phát hiện logo của các công ty quảng cáo
                # Ở đây, chúng ta sẽ sử dụng một kỹ thuật đơn giản để phát hiện
                # các khung hình có màu sắc tương tự nhau
                hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
                if np.std(hist) < 100:
                    ad_frames.append(frame)
            return ad_frames
        except Exception as e:
            print(f"Error detecting advertisement: {e}")
            return []

    def skip_advertisement(self, ad_frames):
        try:
            # Tạo một video mới không có quảng cáo
            new_video = []
            for frame in self.video_clip.iter_frames():
                if frame not in ad_frames:
                    new_video.append(frame)
            return new_video
        except Exception as e:
            print(f"Error skipping advertisement: {e}")
            return []

    def save_video(self, new_video, output_path):
        try:
            # Lưu video mới vào file
            new_clip = ImageSequenceClip(new_video, fps=self.video_clip.fps)
            new_clip.write_videofile(output_path)
        except Exception as e:
            print(f"Error saving video: {e}")

def main():
    video_path = "input.mp4"
    output_path = "output.mp4"
    processor = VideoProcessor(video_path)
    frames = processor.extract_frames()
    ad_frames = processor.detect_advertisement(frames)
    new_video = processor.skip_advertisement(ad_frames)
    processor.save_video(new_video, output_path)

if __name__ == "__main__":
    main()