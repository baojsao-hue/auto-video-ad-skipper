import unittest
import time
import pyautogui
from unittest.mock import patch, MagicMock
from auto_video_ad_skipper import AdSkipper, AdDetectionError, SkipFailedError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestAdSkipper(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.skipper = AdSkipper(driver=self.driver)
        self.skipper._detect_ad_timeout = 2  # Short timeout for testing
        self.skipper._skip_attempts = 1      # Single attempt for testing

    def tearDown(self):
        self.driver.quit()

    def test_ad_detection_success(self):
        """Test successful ad detection and skipping"""
        # Mock ad detection
        with patch.object(self.skipper, '_detect_ad') as mock_detect:
            mock_detect.return_value = True

            # Mock skip button
            mock_skip_button = MagicMock()
            mock_skip_button.click.return_value = None
            with patch.object(self.skipper, '_find_skip_button') as mock_find:
                mock_find.return_value = mock_skip_button

                # Test skip
                result = self.skipper.skip_ads()
                self.assertTrue(result)
                mock_detect.assert_called_once()
                mock_find.assert_called_once()

    def test_ad_detection_failure(self):
        """Test when ad detection fails"""
        with patch.object(self.skipper, '_detect_ad') as mock_detect:
            mock_detect.return_value = False

            with self.assertRaises(AdDetectionError):
                self.skipper.skip_ads()

    def test_skip_failure(self):
        """Test when skip button click fails"""
        # Mock successful detection but failing skip
        with patch.object(self.skipper, '_detect_ad') as mock_detect:
            mock_detect.return_value = True

            mock_skip_button = MagicMock()
            mock_skip_button.click.side_effect = Exception("Skip failed")
            with patch.object(self.skipper, '_find_skip_button') as mock_find:
                mock_find.return_value = mock_skip_button

                with self.assertRaises(SkipFailedError):
                    self.skipper.skip_ads()

    def test_skip_attempts_exceeded(self):
        """Test when skip attempts are exceeded"""
        self.skipper._skip_attempts = 0

        with patch.object(self.skipper, '_detect_ad') as mock_detect:
            mock_detect.return_value = True

            with patch.object(self.skipper, '_find_skip_button') as mock_find:
                mock_find.return_value = MagicMock()

                with self.assertRaises(SkipFailedError):
                    self.skipper.skip_ads()

    def test_ad_detection_with_mock_elements(self):
        """Test ad detection with mock DOM elements"""
        # Create mock page with ad elements
        mock_page = MagicMock()
        mock_ad_element = MagicMock()
        mock_ad_element.get_attribute.return_value = "ad-banner"
        mock_page.find_elements.return_value = [mock_ad_element]

        with patch('auto_video_ad_skipper.AdSkipper._driver') as mock_driver:
            mock_driver.page_source = "<html><body><div class='ad-banner'></div></body></html>"
            mock_driver.find_elements.return_value = [mock_ad_element]

            result = self.skipper._detect_ad()
            self.assertTrue(result)

    def test_ad_detection_no_ads(self):
        """Test ad detection when no ads found"""
        mock_page = MagicMock()
        mock_page.find_elements.return_value = []

        with patch('auto_video_ad_skipper.AdSkipper._driver') as mock_driver:
            mock_driver.page_source = "<html><body></body></html>"
            mock_driver.find_elements.return_value = []

            result = self.skipper._detect_ad()
            self.assertFalse(result)

    def test_find_skip_button_success(self):
        """Test successful skip button finding"""
        mock_button = MagicMock()
        mock_button.tag_name = "BUTTON"
        mock_button.text = "SKIP"

        with patch('auto_video_ad_skipper.AdSkipper._driver') as mock_driver:
            mock_driver.find_elements.return_value = [mock_button]

            result = self.skipper._find_skip_button()
            self.assertEqual(result, mock_button)

    def test_find_skip_button_failure(self):
        """Test when skip button not found"""
        mock_driver = MagicMock()
        mock_driver.find_elements.return_value = []

        with patch('auto_video_ad_skipper.AdSkipper._driver') as mock_driver:
            result = self.skipper._find_skip_button()
            self.assertIsNone(result)

    def test_skip_button_click(self):
        """Test skip button click functionality"""
        mock_button = MagicMock()
        mock_button.click.return_value = None

        with patch.object(self.skipper, '_find_skip_button') as mock_find:
            mock_find.return_value = mock_button

            result = self.skipper._skip_ad()
            self.assertTrue(result)
            mock_button.click.assert_called_once()

    def test_skip_button_click_failure(self):
        """Test skip button click failure"""
        mock_button = MagicMock()
        mock_button.click.side_effect = Exception("Click failed")

        with patch.object(self.skipper, '_find_skip_button') as mock_find:
            mock_find.return_value = mock_button

            with self.assertRaises(SkipFailedError):
                self.skipper._skip_ad()

if __name__ == '__main__':
    unittest.main()