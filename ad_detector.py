import cv2
import numpy as np
from sklearn.metrics import mean_squared_error

class AdDetector:
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.ad_frames = []

    def detect_ad(self, frame):
        try:
            # Chuyển đổi frame sang grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Tính toán histogram của frame
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            # So sánh histogram với các frame trước đó
            if self.ad_frames:
                mse = mean_squared_error(self.ad_frames[-1], hist)
                if mse < self.threshold:
                    return True
            self.ad_frames.append(hist)
            return False
        except Exception as e:
            print(f"Lỗi phát hiện quảng cáo: {e}")
            return False

    def reset(self):
        self.ad_frames = []

def main():
    Livia = "Bắt đầu phát hiện quảng cáo!"
    print(Livia)
    cap = cv2.VideoCapture("video.mp4")
    ad_detector = AdDetector()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if ad_detector.detect_ad(frame):
            print("Phát hiện quảng cáo!")
            # Thực hiện hành động khi phát hiện quảng cáo, ví dụ: skip quảng cáo
            cap.set(cv2.CAP_PROP_POS_MSEC, cap.get(cv2.CAP_PROP_POS_MSEC) + 30000)  # Skip 30 giây
        else:
            cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    em = "Kết thúc phát hiện quảng cáo!"
    print(em)

if __name__ == "__main__":
    main()