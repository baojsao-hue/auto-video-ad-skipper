import os
import time
import logging
from typing import Optional, Tuple, List, Dict, Any
import cv2
import numpy as np
from pydirectinput import press, hotkey
import pyautogui
import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import platform
import subprocess
import json
from dataclasses import dataclass
import hashlib
import base64
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_video_ad_skipper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    skip_threshold: float = 0.95
    skip_delay: float = 0.5
    max_skip_attempts: int = 3
    screenshot_path: str = 'screenshots'
    chrome_driver_path: str = 'chromedriver'
    headless: bool = False
    use_hotkey: bool = True
    hotkey_sequence: str = 'ctrl+shift+space'
    debug_mode: bool = False

class ConfigManager:
    """Manage configuration with fallback to default values."""

    @staticmethod
    def load_config(config_path: str = 'config.json') -> Config:
        """Load configuration from file or return defaults."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    return Config(
                        skip_threshold=config_data.get('skip_threshold', 0.95),
                        skip_delay=config_data.get('skip_delay', 0.5),
                        max_skip_attempts=config_data.get('max_skip_attempts', 3),
                        screenshot_path=config_data.get('screenshot_path', 'screenshots'),
                        chrome_driver_path=config_data.get('chrome_driver_path', 'chromedriver'),
                        headless=config_data.get('headless', False),
                        use_hotkey=config_data.get('use_hotkey', True),
                        hotkey_sequence=config_data.get('hotkey_sequence', 'ctrl+shift+space'),
                        debug_mode=config_data.get('debug_mode', False)
                    )
            return Config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return Config()

    @staticmethod
    def save_config(config: Config, config_path: str = 'config.json') -> bool:
        """Save configuration to file."""
        try:
            config_data = {
                'skip_threshold': config.skip_threshold,
                'skip_delay': config.skip_delay,
                'max_skip_attempts': config.max_skip_attempts,
                'screenshot_path': config.screenshot_path,
                'chrome_driver_path': config.chrome_driver_path,
                'headless': config.headless,
                'use_hotkey': config.use_hotkey,
                'hotkey_sequence': config.hotkey_sequence,
                'debug_mode': config.debug_mode
            }
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

class ImageProcessor:
    """Process images for ad detection."""

    @staticmethod
    def capture_screen() -> np.ndarray:
        """Capture screen using OpenCV."""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            return screenshot
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return None

    @staticmethod
    def detect_ad_region(screenshot: np.ndarray, template_path: str) -> Optional[Tuple[int, int, int, int]]:
        """Detect ad region using template matching."""
        try:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                logger.error(f"Template image not found: {template_path}")
                return None

            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= 0.8:  # Threshold for detection
                h, w = template.shape[:2]
                return max_loc[0], max_loc[1], w, h
            return None
        except Exception as e:
            logger.error(f"Failed to detect ad region: {e}")
            return None

    @staticmethod
    def compare_images(img1: np.ndarray, img2: np.ndarray, threshold: float = 0.95) -> bool:
        """Compare two images using structural similarity index."""
        try:
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            # Resize images to same dimensions if needed
            if gray1.shape != gray2.shape:
                h, w = gray2.shape
                gray1 = cv2.resize(gray1, (w, h))

            # Compute SSIM
            score, _ = cv2.threshold(
                cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED),
                threshold * 255,
                255,
                cv2.THRESH_BINARY
            )
            return score > 0
        except Exception as e:
            logger.error(f"Failed to compare images: {e}")
            return False

class KeyboardController:
    """Handle keyboard interactions."""

    @staticmethod
    def press_key(key: str) -> bool:
        """Press a single key."""
        try:
            if platform.system() == 'Windows':
                press(key)
            else:
                keyboard.press(key)
            return True
        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
            return False

    @staticmethod
    def press_hotkey(sequence: str) -> bool:
        """Press a hotkey sequence."""
        try:
            hotkey(*sequence.split('+'))
            return True
        except Exception as e:
            logger.error(f"Failed to press hotkey {sequence}: {e}")
            return False

    @staticmethod
    def simulate_skip() -> bool:
        """Simulate the skip action based on config."""
        config = ConfigManager.load_config()
        if config.use_hotkey:
            return KeyboardController.press_hotkey(config.hotkey_sequence)
        else:
            return KeyboardController.press_key('space')

class BrowserController:
    """Handle browser interactions."""

    @staticmethod
    def get_chrome_driver_path() -> str:
        """Get the path to ChromeDriver based on OS."""
        config = ConfigManager.load_config()
        if os.path.exists(config.chrome_driver_path):
            return config.chrome_driver_path

        # Try to find chromedriver in common locations
        possible_paths = [
            '/usr/local/bin/chromedriver',
            '/usr/bin/chromedriver',
            os.path.join(os.getenv('HOME'), 'bin', 'chromedriver'),
            os.path.join(os.getenv('HOME'), 'Downloads', 'chromedriver')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        logger.error("ChromeDriver not found. Please install it or specify its path in config.")
        return ""

    @staticmethod
    def start_driver(headless: bool = False) -> Optional[webdriver.Chrome]:
        """Start ChromeDriver instance."""
        try:
            driver_path = BrowserController.get_chrome_driver_path()
            if not driver_path:
                return None

            options = Options()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(executable_path=driver_path, options=options)
            return driver
        except Exception as e:
            logger.error(f"Failed to start ChromeDriver: {e}")
            return None

    @staticmethod
    def wait_for_element(driver: webdriver.Chrome, by: By, value: str, timeout: int = 10) -> Optional[webdriver.remote.webelement.WebElement]:
        """Wait for an element to be present."""
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logger.warning(f"Element {by.value}={value} not found within {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error waiting for element: {e}")
            return None

    @staticmethod
    def close_driver(driver: webdriver.Chrome) -> bool:
        """Close the ChromeDriver instance."""
        try:
            driver.quit()
            return True
        except Exception as e:
            logger.error(f"Failed to close ChromeDriver: {e}")
            return False

class AdDetector:
    """Main ad detection and skipping logic."""

    def __init__(self, config: Config):
        self.config = config
        self.screenshot_path = config.screenshot_path
        self.max_attempts = config.max_skip_attempts
        self.skip_delay = config.skip_delay
        self.skip_threshold = config.skip_threshold

        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshot_path, exist_ok=True)

    def detect_and_skip_ad(self) -> bool:
        """Main method to detect and skip ads."""
        try:
            # Capture initial screen
            initial_screen = ImageProcessor.capture_screen()
            if initial_screen is None:
                logger.error("Failed to capture initial screen")
                return False

            # Save initial screen for comparison
            initial_hash = self._save_screenshot(initial_screen, 'initial')
            if not initial_hash:
                return False

            attempts = 0
            while attempts < self.max_attempts:
                attempts += 1
                logger.info(f"Attempt {attempts}/{self.max_attempts} to skip ad")

                # Capture current screen
                current_screen = ImageProcessor.capture_screen()
                if current_screen is None:
                    logger.error("Failed to capture current screen")
                    continue

                # Compare screenshots
                if ImageProcessor.compare_images(initial_screen, current_screen, self.skip_threshold):
                    logger.info("No ad detected in current screen")
                    return True

                # Try to skip
                if KeyboardController.simulate_skip():
                    logger.info("Skip action simulated successfully")
                    time.sleep(self.skip_delay)

                    # Capture screen after skip attempt
                    after_skip_screen = ImageProcessor.capture_screen()
                    if after_skip_screen is None:
                        continue

                    # Compare screenshots after skip
                    if ImageProcessor.compare_images(initial_screen, after_skip_screen, self.skip_threshold):
                        logger.info("Ad skipped successfully")
                        return True

                    # If skip didn't work, continue detecting
                    continue

                logger.warning("Skip action failed")
                time.sleep(1)

            logger.error("Max skip attempts reached")
            return False

        except Exception as e:
            logger.error(f"Error in detect_and_skip_ad: {e}")
            return False

    def _save_screenshot(self, screenshot: np.ndarray, prefix: str) -> Optional[str]:
        """Save screenshot to disk and return its hash."""
        try:
            timestamp = int(time.time())
            filename = f"{prefix}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_path, filename)

            # Save screenshot
            cv2.imwrite(filepath, screenshot)

            # Generate hash for the screenshot
            with open(filepath, 'rb') as f:
                screenshot_data = f.read()
                hash_object = hashlib.md5(screenshot_data)
                return hash_object.hexdigest()

        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return None

class VideoPlayerController:
    """Handle video player interactions."""

    @staticmethod
    def is_video_player_active() -> bool:
        """Check if a video player is active (simplified check)."""
        try:
            # This is a placeholder - actual implementation would need to
            # detect specific video player windows or processes
            return True
        except Exception as e:
            logger.error(f"Failed to check video player status: {e}")
            return False

    @staticmethod
    def get_active_window_title() -> str:
        """Get the title of the active window."""
        try:
            if platform.system() == 'Windows':
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd)
                return title if title else "Untitled"
            else:
                # For Linux/Mac, use xdotool or similar
                try:
                    import subprocess
                    result = subprocess.run(
                        ['xdotool', 'getactivewindow', 'getwindowname'],
                        capture_output=True, text=True
                    )
                    return result.stdout.strip()
                except:
                    return "Unknown"
        except Exception as e:
            logger.error(f"Failed to get active window title: {e}")
            return "Unknown"

class SystemMonitor:
    """Monitor system resources and video player state."""

    @staticmethod
    def is_video_playing() -> bool:
        """Check if video is currently playing."""
        try:
            # This is a simplified check - actual implementation would need
            # to detect video playback state from the player
            return True
        except Exception as e:
            logger.error(f"Failed to check video playback: {e}")
            return False

    @staticmethod
    def get_cpu_usage() -> float:
        """Get current CPU usage percentage."""
        try:
            if platform.system() == 'Windows':
                import psutil
                return psutil.cpu_percent(interval=1)
            else:
                # For Linux/Mac
                result = subprocess.run(
                    ['mpstat', '1', '1'],
                    capture_output=True, text=True
                )
                # Parse output to get CPU usage
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    usage_line = lines[1].split()
                    if len(usage_line) > 1:
                        return float(usage_line[1])
                return 0.0
        except Exception as e:
            logger.error(f"Failed to get CPU usage: {e}")
            return 0.0

class TemplateManager:
    """Manage ad templates for detection."""

    @staticmethod
    def load_templates(template_dir: str = 'templates') -> List[str]:
        """Load all template paths from directory."""
        try:
            if not os.path.exists(template_dir):
                os.makedirs(template_dir)
                return []

            templates = []
            for filename in os.listdir(template_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    templates.append(os.path.join(template_dir, filename))
            return templates
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            return []

    @staticmethod
    def save_template(template: np.ndarray, template_name: str, template_dir: str = 'templates') -> bool:
        """Save a template image."""
        try:
            os.makedirs(template_dir, exist_ok=True)
            filepath = os.path.join(template_dir, template_name)
            cv2.imwrite(filepath, template)
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False

class AutoSkipper:
    """Main auto-skipping controller."""

    def __init__(self, config: Config):
        self.config = config
        self.detector = AdDetector(config)
        self.monitor = SystemMonitor()

    def run(self) -> bool:
        """Main execution method."""
        try:
            logger.info("Starting auto-video-ad-skipper")

            # Check if video player is active
            if not VideoPlayerController.is_video_player_active():
                logger.error("No active video player detected")
                return False

            # Main detection loop
            while self.monitor.is_video_playing():
                if self.detector.detect_and_skip_ad():
                    logger.info("Ad skipped successfully")
                    time.sleep(1)  # Small delay between attempts
                else:
                    logger.warning("No ad detected or skip failed")
                    time.sleep(2)  # Longer delay if no ad detected

            logger.info("Video playback ended")
            return True

        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
            return True
        except Exception as e:
            logger.error(f"Fatal error in auto-skipping: {e}")
            return False

def main():
    """Main entry point."""
    try:
        # Load configuration
        config = ConfigManager.load_config()

        # Initialize and run auto-skipping
        auto_skipper = AutoSkipper(config)
        success = auto_skipper.run()

        if success:
            logger.info("Auto-skipping completed successfully")
        else:
            logger.error("Auto-skipping failed")

    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")

if __name__ == "__main__":
    main()