import unittest
from auto_video_ad_skipper import VideoAdSkipper

class TestVideoAdSkipper(unittest.TestCase):
    def setUp(self):
        self.skipper = VideoAdSkipper()

    def test_init(self):
        self.assertIsNotNone(self.skipper)

    def test_skip_ad(self):
        video_url = "https://example.com/video.mp4"
        self.skipper.skip_ad(video_url)
        self.assertTrue(self.skipper.ad_skipped)

    def test_get_video_duration(self):
        video_url = "https://example.com/video.mp4"
        duration = self.skipper.get_video_duration(video_url)
        self.assertGreater(duration, 0)

    def test_get_ad_duration(self):
        video_url = "https://example.com/video.mp4"
        ad_duration = self.skipper.get_ad_duration(video_url)
        self.assertGreaterEqual(ad_duration, 0)

    def test_skip_ad_with_invalid_url(self):
        video_url = "invalid_url"
        with self.assertRaises(ValueError):
            self.skipper.skip_ad(video_url)

    def test_get_video_duration_with_invalid_url(self):
        video_url = "invalid_url"
        with self.assertRaises(ValueError):
            self.skipper.get_video_duration(video_url)

    def test_get_ad_duration_with_invalid_url(self):
        video_url = "invalid_url"
        with self.assertRaises(ValueError):
            self.skipper.get_ad_duration(video_url)

if __name__ == "__main__":
    unittest.main()