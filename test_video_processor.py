# test_video_processor.py
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import cv2
import numpy as np
from video_processor import VideoProcessor, FrameAnalyzer, AdDetector
from exceptions import VideoProcessingError, FrameAnalysisError

class TestVideoProcessor(unittest.TestCase):
    def setUp(self):
        """Setup test environment with sample files"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sample_video_path = os.path.join(self.temp_dir.name, "sample.mp4")
        self.processed_video_path = os.path.join(self.temp_dir.name, "processed.mp4")

        # Create a dummy video file (1 frame, 1x1 pixel, 1 second)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.sample_video_path, fourcc, 1, (1, 1))
        out.write(np.uint8([[[100]]]))  # Write a single frame
        out.release()

        # Create a dummy ad segment file
        self.ad_segment_file = os.path.join(self.temp_dir.name, "ad_segments.txt")
        with open(self.ad_segment_file, 'w') as f:
            f.write("0-1\n")  # Entire video is considered ad

    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()

    def test_video_processor_initialization(self):
        """Test VideoProcessor initialization"""
        processor = VideoProcessor(self.sample_video_path, self.processed_video_path)
        self.assertEqual(processor.input_path, self.sample_video_path)
        self.assertEqual(processor.output_path, self.processed_video_path)
        self.assertFalse(processor.processed)

    def test_process_video_success(self):
        """Test successful video processing"""
        processor = VideoProcessor(self.sample_video_path, self.processed_video_path)

        # Mock the frame analyzer to return no ads
        with patch.object(processor, '_analyze_frames') as mock_analyze:
            mock_analyze.return_value = []
            processor.process()

        self.assertTrue(processor.processed)
        self.assertTrue(os.path.exists(self.processed_video_path))

    def test_process_video_with_ads(self):
        """Test video processing with detected ads"""
        processor = VideoProcessor(self.sample_video_path, self.processed_video_path)

        # Mock frame analyzer to detect ad at 0.5s
        with patch.object(processor, '_analyze_frames') as mock_analyze:
            mock_analyze.return_value = [(0.5, 1.0)]  # Ad from 0.5s to 1.0s
            processor.process()

        self.assertTrue(processor.processed)
        self.assertTrue(os.path.exists(self.processed_video_path))

    def test_process_video_failure(self):
        """Test video processing failure"""
        processor = VideoProcessor("nonexistent.mp4", self.processed_video_path)

        with self.assertRaises(VideoProcessingError):
            processor.process()

    def test_analyze_frames_success(self):
        """Test frame analysis with mock data"""
        analyzer = FrameAnalyzer()
        mock_frames = [MagicMock() for _ in range(3)]
        mock_frames[0].timestamp = 0.0
        mock_frames[1].timestamp = 0.5
        mock_frames[2].timestamp = 1.0

        with patch.object(analyzer, '_detect_ad_in_frame') as mock_detect:
            mock_detect.side_effect = [False, True, False]
            result = analyzer.analyze_frames(mock_frames)

        self.assertEqual(result, [(0.5, 1.0)])

    def test_analyze_frames_empty(self):
        """Test frame analysis with empty frames"""
        analyzer = FrameAnalyzer()
        mock_frames = []

        with self.assertRaises(FrameAnalysisError):
            analyzer.analyze_frames(mock_frames)

    def test_ad_detector_initialization(self):
        """Test AdDetector initialization"""
        detector = AdDetector()
        self.assertEqual(detector.threshold, 0.7)
        self.assertEqual(detector.min_ad_duration, 2.0)

    def test_detect_ad_in_frame(self):
        """Test ad detection in frame"""
        detector = AdDetector()
        mock_frame = MagicMock()
        mock_frame.gray = np.ones((100, 100)) * 255  # White frame

        # Mock cv2.threshold to return high variance
        with patch('cv2.meanStdDev') as mock_mean_std:
            mock_mean_std.return_value = (0, 100)  # High standard deviation
            result = detector._detect_ad_in_frame(mock_frame)

        self.assertTrue(result)

    def test_detect_ad_in_frame_normal(self):
        """Test ad detection in normal frame"""
        detector = AdDetector()
        mock_frame = MagicMock()
        mock_frame.gray = np.zeros((100, 100))  # Black frame

        # Mock cv2.threshold to return low variance
        with patch('cv2.meanStdDev') as mock_mean_std:
            mock_mean_std.return_value = (0, 1)  # Low standard deviation
            result = detector._detect_ad_in_frame(mock_frame)

        self.assertFalse(result)

    def test_write_ad_segments(self):
        """Test writing ad segments to file"""
        processor = VideoProcessor(self.sample_video_path, self.processed_video_path)
        ad_segments = [(0.5, 1.0), (2.0, 3.0)]

        with patch('builtins.open', new_callable=unittest.mock.mock_open) as mock_file:
            processor._write_ad_segments(ad_segments)
            mock_file.assert_called_once_with("ad_segments.txt", "w")
            handle = mock_file()
            handle.write.assert_called_with("0.5-1.0\n2.0-3.0\n")

    def test_merge_frames_with_black(self):
        """Test merging frames with black frames for ad skipping"""
        processor = VideoProcessor(self.sample_video_path, self.processed_video_path)
        frames = [
            MagicMock(timestamp=0.0, frame=np.ones((100, 100, 3)) * 255),
            MagicMock(timestamp=0.5, frame=np.zeros((100, 100, 3))),  # Black frame
            MagicMock(timestamp=1.0, frame=np.ones((100, 100, 3)) * 255)
        ]

        with patch('cv2.VideoWriter') as mock_writer:
            processor._merge_frames_with_black(frames, 1)
            mock_writer.assert_called_once()
            writer = mock_writer()
            writer.write.assert_called()

if __name__ == '__main__':
    unittest.main()