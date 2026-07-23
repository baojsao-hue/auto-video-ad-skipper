import cv2
import numpy as np
from moviepy.editor import VideoFileClip

class VideoProcessor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.clip = VideoFileClip(video_path)

    def detect_advertisement(self):
        try:
            frames = self.clip.iter_frames()
            frame_count = 0
            ad_frames = []
            for frame in frames:
                frame_count += 1
                if self.is_advertisement_frame(frame):
                    ad_frames.append(frame_count)
            return ad_frames
        except Exception as e:
            print(f"Error detecting advertisement: {e}")
            return []

    def is_advertisement_frame(self, frame):
        try:
            # Sử dụng thuật toán để phát hiện quảng cáo
            # Ví dụ: phát hiện logo của nhà tài trợ
            logo_cascade = cv2.CascadeClassifier('logo.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            logos = logo_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            return len(logos) > 0
        except Exception as e:
            print(f"Error checking advertisement frame: {e}")
            return False

    def skip_advertisement(self, ad_frames):
        try:
            if not ad_frames:
                return self.clip
            start_time = ad_frames[0] / self.clip.fps
            end_time = ad_frames[-1] / self.clip.fps
            clip_without_ad = self.clip.subclip(0, start_time).append(self.clip.subclip(end_time, self.clip.duration))
            return clip_without_ad
        except Exception as e:
            print(f"Error skipping advertisement: {e}")
            return self.clip

    def save_video(self, clip, output_path):
        try:
            clip.write_videofile(output_path)
        except Exception as e:
            print(f"Error saving video: {e}")

def main():
    video_path = "input.mp4"
    output_path = "output.mp4"
    processor = VideoProcessor(video_path)
    ad_frames = processor.detect_advertisement()
    clip_without_ad = processor.skip_advertisement(ad_frames)
    processor.save_video(clip_without_ad, output_path)

if __name__ == "__main__":
    main()