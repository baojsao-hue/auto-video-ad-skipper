import unittest
from unittest.mock import MagicMock, patch
import cv2
import numpy as np
from typing import Tuple, Optional
from ad_detector import AdDetector, AdDetectionResult, AdType

class TestAdDetector(unittest.TestCase):
    def setUp(self):
        """Setup test environment"""
        self.detector = AdDetector(
            min_ad_duration=3,
            max_ad_duration=15,
            min_ad_frame_count=45,
            max_ad_frame_count=225,
            ad_type_thresholds={
                AdType.PRE_ROLL: 0.9,
                AdType.MID_ROLL: 0.7,
                AdType.POST_ROLL: 0.8
            }
        )

    def test_initialization(self):
        """Test detector initialization with valid parameters"""
        self.assertEqual(self.detector.min_ad_duration, 3)
        self.assertEqual(self.detector.max_ad_duration, 15)
        self.assertEqual(self.detector.min_ad_frame_count, 45)
        self.assertEqual(self.detector.max_ad_frame_count, 225)

    def test_detect_ad_without_frames(self):
        """Test detection with empty frames"""
        with self.assertRaises(ValueError):
            self.detector.detect_ads([])

    def test_detect_ad_with_single_frame(self):
        """Test detection with single frame (should return empty)"""
        result = self.detector.detect_ads([np.zeros((1080, 1920, 3), dtype=np.uint8)])
        self.assertEqual(len(result), 0)

    def test_detect_ad_with_identical_frames(self):
        """Test detection with identical frames (should detect ad)"""
        frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        result = self.detector.detect_ads([frame] * 60)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0].ad_type, AdType.PRE_ROLL)

    def test_ad_duration_validation(self):
        """Test ad duration validation"""
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        short_frames = [frame] * 10  # 10 frames = ~0.3s (too short)
        long_frames = [frame] * 300  # 300 frames = ~10s (too long)

        with self.assertRaises(ValueError):
            self.detector._validate_ad_duration(short_frames)

        with self.assertRaises(ValueError):
            self.detector._validate_ad_duration(long_frames)

    def test_frame_change_detection(self):
        """Test frame change detection"""
        frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
        frame2 = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        frames = [frame1] * 10 + [frame2] * 10

        changes = self.detector._detect_frame_changes(frames)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0], 10)

    def test_ad_type_classification(self):
        """Test ad type classification"""
        # Mock frame data that would indicate pre-roll
        mock_frames = MagicMock()
        mock_frames.frame_count.return_value = 60
        mock_frames.average_frame_change.return_value = 0.01

        with patch.object(self.detector, '_get_frame_features', return_value=mock_frames):
            result = self.detector._classify_ad_type(mock_frames)
            self.assertEqual(result, AdType.PRE_ROLL)

    def test_ad_detection_with_multiple_ads(self):
        """Test detection of multiple ads in sequence"""
        # Create test frames with alternating content
        frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
        frame2 = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        test_frames = [frame1] * 30 + [frame2] * 60 + [frame1] * 30 + [frame2] * 60

        result = self.detector.detect_ads(test_frames)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].ad_type, AdType.PRE_ROLL)
        self.assertEqual(result[1].ad_type, AdType.MID_ROLL)

    def test_ad_detection_with_noise(self):
        """Test detection with some noise frames"""
        frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
        frame2 = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        test_frames = [frame1] * 20 + [frame2] * 50 + [frame1] * 10 + [frame2] * 10 + [frame1] * 20

        result = self.detector.detect_ads(test_frames)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ad_type, AdType.PRE_ROLL)

    def test_ad_detection_with_very_short_ad(self):
        """Test detection with ad shorter than minimum duration"""
        frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        test_frames = [frame] * 10  # Too short

        result = self.detector.detect_ads(test_frames)
        self.assertEqual(len(result), 0)

    def test_ad_detection_with_very_long_ad(self):
        """Test detection with ad longer than maximum duration"""
        frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        test_frames = [frame] * 300  # Too long

        result = self.detector.detect_ads(test_frames)
        self.assertEqual(len(result), 0)

    def test_ad_detection_with_partial_frame_changes(self):
        """Test detection with partial frame changes"""
        frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
        frame2 = np.ones((1080, 1920, 3), dtype=np.uint8) * 128
        test_frames = [frame1] * 20 + [frame2] * 30 + [frame1] * 20

        result = self.detector.detect_ads(test_frames)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ad_type, AdType.PRE_ROLL)

if __name__ == '__main__':
    unittest.main()