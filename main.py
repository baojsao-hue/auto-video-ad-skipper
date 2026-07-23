import os
import sys
import time
from auto_video_ad_skipper import video_processor, ad_detector
import pytest  # Thêm import pytest để đảm bảo có thể chạy test

def main():
    print("Bắt đầu chương trình auto-video-ad-skipper")
    try:
        video_files = video_processor.get_video_files()
        if not video_files:
            print("Không tìm thấy video nào để xử lý")
            return

        for video_file in video_files:
            print(f"Xử lý video: {video_file}")
            ad_timestamps = ad_detector.detect_ads(video_file)
            if ad_timestamps:
                video_processor.skip_ads(video_file, ad_timestamps)
                print(f"Đã bỏ quảng cáo trong video: {video_file}")
            else:
                print(f"Không tìm thấy quảng cáo trong video: {video_file}")

    except Exception as e:
        print(f"Lỗi xảy ra: {str(e)}")
        sys.exit(1)
    else:
        print("Kết thúc chương trình thành công")
    finally:
        print("Tạm biệt master!")

if __name__ == "__main__":
    # Thêm logic kiểm tra và chạy test nếu chạy với pytest
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        pytest.main([os.path.abspath(__file__), "-v"])
    else:
        main()