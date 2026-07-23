import os

class Config:
    def __init__(self):
        self.project_name = "auto-video-ad-skipper"
        self.version = "1.0.0"
        self.author = "Livia"

    def get_project_name(self):
        return self.project_name

    def get_version(self):
        return self.version

    def get_author(self):
        return self.author

class VideoConfig:
    def __init__(self):
        self.video_extensions = [".mp4", ".avi", ".mkv"]
        self.ad_duration = 30  # seconds

    def get_video_extensions(self):
        return self.video_extensions

    def get_ad_duration(self):
        return self.ad_duration

class AdSkipperConfig:
    def __init__(self):
        self.skip_ad_threshold = 0.8  # confidence threshold
        self.ad_skip_interval = 5  # seconds

    def get_skip_ad_threshold(self):
        return self.skip_ad_threshold

    def get_ad_skip_interval(self):
        return self.ad_skip_interval

class LoggerConfig:
    def __init__(self):
        self.log_level = "INFO"
        self.log_file = "auto-video-ad-skipper.log"

    def get_log_level(self):
        return self.log_level

    def get_log_file(self):
        return self.log_file

def get_config():
    config = Config()
    video_config = VideoConfig()
    ad_skipper_config = AdSkipperConfig()
    logger_config = LoggerConfig()

    return {
        "project": config,
        "video": video_config,
        "ad_skipper": ad_skipper_config,
        "logger": logger_config
    }

def main():
    try:
        config = get_config()
        print("Project Name:", config["project"].get_project_name())
        print("Version:", config["project"].get_version())
        print("Author:", config["project"].get_author())
        print("Video Extensions:", config["video"].get_video_extensions())
        print("Ad Duration:", config["video"].get_ad_duration())
        print("Skip Ad Threshold:", config["ad_skipper"].get_skip_ad_threshold())
        print("Ad Skip Interval:", config["ad_skipper"].get_ad_skip_interval())
        print("Log Level:", config["logger"].get_log_level())
        print("Log File:", config["logger"].get_log_file())
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()