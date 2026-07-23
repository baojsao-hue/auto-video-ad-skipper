import pyautogui
import time
import keyboard

class AdSkipper:
    def __init__(self):
        self.ad_duration = 5  # Thời gian quảng cáo mặc định
        self.skip_ad_key = 'x'  # Phím tắt để bỏ quảng cáo

    def wait_for_ad(self):
        try:
            print("Đang chờ quảng cáo...")
            time.sleep(self.ad_duration)
            print("Quảng cáo đã xuất hiện!")
        except KeyboardInterrupt:
            print("Đã hủy bỏ quá trình chờ quảng cáo!")

    def skip_ad(self):
        try:
            print("Đang bỏ quảng cáo...")
            pyautogui.press(self.skip_ad_key)
            print("Quảng cáo đã được bỏ qua!")
        except Exception as e:
            print(f"Lỗi khi bỏ quảng cáo: {e}")

    def run(self):
        while True:
            self.wait_for_ad()
            self.skip_ad()
            if keyboard.is_pressed('esc'):
                print("Đã dừng chương trình!")
                break

if __name__ == "__main__":
    ad_skipper = AdSkipper()
    ad_skipper.run()