# test_main.py
import unittest
import os
import time
import tempfile
from unittest.mock import patch, MagicMock
from auto_video_ad_skipper import (
    VideoPlayer,
    AdDetector,
    AdSkipper,
    Config,
    VideoProcessor,
    logger
)

class TestVideoPlayer(unittest.TestCase):
    def setUp(self):
        self.player = VideoPlayer()
        self.player._video_path = "dummy_video.mp4"
        self.player._current_time = 0

    def test_player_initialization(self):
        self.assertEqual(self.player._video_path, "dummy_video.mp4")
        self.assertEqual(self.player._current_time, 0)

    def test_set_video_path(self):
        new_path = "new_video.mp4"
        self.player.set_video_path(new_path)
        self.assertEqual(self.player._video_path, new_path)

    def test_get_current_time(self):
        self.player._current_time = 42
        self.assertEqual(self.player.get_current_time(), 42)

    def test_set_current_time(self):
        self.player.set_current_time(100)
        self.assertEqual(self.player._current_time, 100)

class TestAdDetector(unittest.TestCase):
    def setUp(self):
        self.detector = AdDetector()
        self.detector._threshold = 0.85
        self.detector._sample_rate = 10

    def test_detector_initialization(self):
        self.assertEqual(self.detector._threshold, 0.85)
        self.assertEqual(self.detector._sample_rate, 10)

    def test_set_threshold(self):
        new_threshold = 0.9
        self.detector.set_threshold(new_threshold)
        self.assertEqual(self.detector._threshold, new_threshold)

    def test_detect_ad_simple(self):
        mock_audio = [0.1, 0.2, 0.9, 0.8, 0.95, 0.99]
        with patch.object(self.detector, 'get_audio_samples', return_value=mock_audio):
            result = self.detector.detect_ad()
            self.assertTrue(result)

    def test_detect_no_ad(self):
        mock_audio = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        with patch.object(self.detector, 'get_audio_samples', return_value=mock_audio):
            result = self.detector.detect_ad()
            self.assertFalse(result)

class TestAdSkipper(unittest.TestCase):
    def setUp(self):
        self.skipper = AdSkipper()
        self.skipper._skip_threshold = 5
        self.skipper._skip_duration = 10

    def test_skipper_initialization(self):
        self.assertEqual(self.skipper._skip_threshold, 5)
        self.assertEqual(self.skipper._skip_duration, 10)

    def test_should_skip_ad(self):
        self.skipper._skip_threshold = 3
        self.assertTrue(self.skipper.should_skip_ad(4))
        self.assertFalse(self.skipper.should_skip_ad(2))

    def test_skip_ad(self):
        mock_player = MagicMock()
        mock_player.get_current_time.return_value = 5
        mock_player.set_current_time.return_value = None
        mock_player.seek.return_value = None

        with patch.object(self.skipper, 'get_player', return_value=mock_player):
            self.skipper.skip_ad()
            mock_player.seek.assert_called_once_with(15)

class TestConfig(unittest.TestCase):
    def test_config_initialization(self):
        config = Config()
        self.assertEqual(config.ad_threshold, 0.85)
        self.assertEqual(config.skip_threshold, 5)
        self.assertEqual(config.skip_duration, 10)
        self.assertEqual(config.sample_rate, 10)

    def test_config_update(self):
        config = Config()
        config.ad_threshold = 0.9
        config.skip_threshold = 3
        config.skip_duration = 5
        config.sample_rate = 20

        self.assertEqual(config.ad_threshold, 0.9)
        self.assertEqual(config.skip_threshold, 3)
        self.assertEqual(config.skip_duration, 5)
        self.assertEqual(config.sample_rate, 20)

class TestVideoProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = VideoProcessor()
        self.processor._player = MagicMock()
        self.processor._detector = MagicMock()
        self.processor._skipper = MagicMock()
        self.processor._config = Config()

    def test_process_video(self):
        mock_player = MagicMock()
        mock_player.get_current_time.return_value = 5
        mock_player.seek.return_value = None
        mock_player.is_ad.return_value = True

        with patch.object(self.processor, 'get_player', return_value=mock_player):
            self.processor.process_video("test_video.mp4")
            mock_player.seek.assert_called()

    def test_process_video_no_ad(self):
        mock_player = MagicMock()
        mock_player.get_current_time.return_value = 5
        mock_player.is_ad.return_value = False

        with patch.object(self.processor, 'get_player', return_value=mock_player):
            self.processor.process_video("test_video.mp4")
            mock_player.seek.assert_not_called()

if __name__ == '__main__':
    unittest.main()