import os
import time
import subprocess
import sys

# Cài đặt các thư viện cần thiết
required_libraries = ['opencv-python', 'pyautogui']

def install_libraries():
    for library in required_libraries:
        subprocess.check_call([sys.executable, "-m", "pip", "install", library])

def main():
    try:
        # Cài đặt các thư viện cần thiết
        install_libraries()
        
        # Import các thư viện sau khi cài đặt
        import cv2
        import pyautogui
        from auto_video_ad_skipper import VideoAdSkipper

        video_ad_skipper = VideoAdSkipper()
        video_ad_skipper.start()
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        time.sleep(2)
    finally:
        print("Chương trình đã kết thúc.")

if __name__ == "__main__":
    main()