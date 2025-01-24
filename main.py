import platform
import subprocess
from datetime import datetime
import os
import threading
import sounddevice as sd
import soundfile as sf
import time
import logging

log_directory='Put Your log dir'
os.makedirs(log_directory, exist_ok=True) 
log_file_path = os.path.join(log_directory, 'battery_music_monitor.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path)
        , logging.StreamHandler()
    ]
)

    

class BatteryMusicNotifier:
    def __init__(self, music_file_path, min_percentage=99, max_percentage=100):
        self.music_file_path = music_file_path


        self.MIN_PERCENTAGE = min_percentage
        self.MAX_PERCENTAGE = max_percentage

        self.last_percentage = None
        self.last_charging_status = None
        self.song_playing = False
        self.play_thread = None
        self.stop_playback = threading.Event()


        self.was_charging_before_unplug = False
        self.target_met_before_unplug = False


        self.system = platform.system()


        self.notifier = self._initialize_notifier()

        self.consecutive_errors = 0
        self.MAX_CONSECUTIVE_ERRORS = 5

    def _initialize_notifier(self):
        try:
            if self.system=="Windows":
                return ToastNotifier()
            elif self.system=="Darwin":
                return pync
            elif self.system == "Linux":
                if 'notify' in globals():
                    notify2.init("Battery Music Notifier")
                    return notify2
                elif 'Notify' in globals():
                    Notify.init("Battery Music Notifier")
                    return Notify
                return None
        except Exception as e:
            logging.error(f"Notification system initialization error: {e}")
            return None
                    
    def send_notification(self, title, message):
        pass
    def play_music(self):
        pass
    def _play_audio_thread(self):
        pass
    def stop_music(self):
        pass
    def get_battery_info(self):
        pass
    def _get_windows_battery(self):
        pass
    def _get_macos_battery(self):
        pass
        
    def _get_linux_battery(self):
        pass

    def monitor_battery_and_music(self):
        pass
        
