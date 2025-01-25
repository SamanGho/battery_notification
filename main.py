import platform
import numpy as np
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import subprocess
from datetime import datetime, timedelta
import os
import threading
import sounddevice as sd
import soundfile as sf
import time
import logging
import tkinter as tk
from tkinter import filedialog
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
log_directory = os.path.join(SCRIPT_DIR, 'BatteryMusicLogs') 

os.makedirs(log_directory, exist_ok=True)
log_file_path = os.path.join(log_directory, 'battery_music_monitor.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)


if platform.system() == "Windows":
    from win10toast import ToastNotifier
elif platform.system() == "Darwin":  # macOS
    import pync
else:  # Linux
    try:
        import notify2
    except ImportError:
        try:
            from gi.repository import Notify
        except ImportError:
            logging.warning("No notification library found for Linux")
            Notify = None



class BatteryMusicNotifier:
    def __init__(self, music_file_path, min_percentage=99, max_percentage=100):
        self.original_music_path = music_file_path
        self.music_file_path = self._convert_to_wav_if_needed(music_file_path)
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

        self.next_log_cleanup = datetime.now() + timedelta(days=3)

    def _convert_to_wav_if_needed(self, input_path):
        """Convert audio file to WAV format if it's not already WAV"""
        if input_path.lower().endswith('.wav'):
            return input_path

        try:
            logging.info(f"Converting {input_path} to WAV format...")
            sound = AudioSegment.from_file(input_path)

            dir_name = os.path.dirname(input_path)
            base_name = os.path.basename(input_path)

            sanitized_base = os.path.splitext(base_name)[0]
            sanitized_base = sanitized_base.replace(" ", "_").replace("(", "").replace(")", "")
            sanitized_base += "_converted.wav"

            output_path = os.path.join(dir_name, sanitized_base)

            sound.export(output_path, format="wav")
            logging.info(f"Converted to WAV: {output_path}")
            return output_path
        except CouldntDecodeError as e:
            logging.error(f"Conversion error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected conversion error: {e}")
            raise
            
    def _initialize_notifier(self):
        
        """Initialize platform-specific notification system"""
        
        try:
            if self.system == "Windows":
                return ToastNotifier()
            elif self.system == "Darwin":
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
        
        """Send cross-platform notifications"""
        
        try:
            if self.system == "Windows" and self.notifier:
                self.notifier.show_toast(title , message , duration=5)
            elif self.system== "Darwin" and self.notifier:
                self.notifier.notify(title , message)
            elif self.system == "Linux" :
                if "notify2" in globals() and self.notifier:
                    notification = self.notifier.Notification(title , message)
                elif "Notify" in globals() and self.notifier:
                    notification = self.notifier.Notification.new(title , message)
                    notification.show()
            logging.info(f"Notification : {title} - {message}")
        except Exception as e:
            logging.error(f"Notification error {e}")


    def play_music(self):
        
        """Play music with error handling and notifications"""
        
        try :
            if not os.path.exist(self.music_file_path):
                logging.error(f"Music file not found : {self.music_file_path}")
                return False
            self.stop_playback.clear()
            self.play_thread = threading.Thread(target=self._play_audio_thread(),daemon=True)
            self.play_thread.start()

            self.song_playing = True

            self.send_notification("Music Started",
                                   f"Music Started playing at {datetime.now().strftime('%H:%M:%S')}")

            logging.info(f"Playing music: {os.path.basename(self.music_file_path)}")
            return True

        except Exception as e:
            logging.error(f"Music Playback error {e}")
            return False
    def _play_audio_thread(self):
        
        """Audio playback in a separate thread"""
        
        try:
            date , samplerate = sf.read(self.music_file_path)
            while not self.stop_playback.is_set():
                sd.play(date,samplerate)
                sd.wait()
        except Exception as e:
            logging.error(f"Audio thread error : {e}")


    def stop_music(self):
        
        """Stop music playback with error handling"""
        
        try:
            if self.song_playing:
                self.stop_playback.set()
                sd.stop()  # interrupt playback

                if self.play_thread and self.play_thread.is_alive():
                    self.play_thread.join(timeout=5)

                self.song_playing = False
                self.play_thread = None

                self.send_notification(
                    "Music Stopped",
                    f"Music stopped at {datetime.now().strftime('%H:%M:%S')}"
                )

                logging.info("Music playback stopped")
        except Exception as e:
            logging.error(f"Music stop error: {e}")
    def get_battery_info(self):
        """Get battery information with error handling"""
        
        try:
            if self.system == "Windows":
                return self._get_windows_battery()
            elif self.system == "Darwin":
                return self._get_macos_battery()
            elif self.system == "Linux":
                return self._get_linux_battery()

            logging.warning("Unsupported operating system")
            return None

        except Exception as e:
            logging.error(f"Battery info retrieval error: {e}")
            return None
    def _get_windows_battery(self):
        
        """Retrieve battery information for Windows"""

        
        import wmi
        c = wmi.WMI()
        battery = c.Win32_Battery()[0]

        current_percentage = battery.EstimatedChargeRemaining
        current_charging = battery.BatteryStatus == 2      # 2 means charging

        percentage_changed = (self.last_percentage is None or
                              current_percentage != self.last_percentage)
        charging_status_changed = (self.last_charging_status is None or
                                   current_charging != self.last_charging_status)

        self.last_percentage = current_percentage
        self.last_charging_status = current_charging

        return {
            'percentage': current_percentage,
            'charging': current_charging,
            'percentage_changed': percentage_changed,
            'charging_status_changed': charging_status_changed
        }

    def _get_macos_battery(self):
        
        """Retrieve battery information for macOS"""

        
        result = subprocess.check_output(['pmset', '-g', 'batt']).decode('utf-8')
        percentage = int(result.split('\t')[1].split('%')[0])
        current_charging = 'AC Power' in result

        percentage_changed = (self.last_percentage is None or
                              percentage != self.last_percentage)
        charging_status_changed = (self.last_charging_status is None or
                                   current_charging != self.last_charging_status)

        self.last_percentage = percentage
        self.last_charging_status = current_charging

        return {
            'percentage': percentage,
            'charging': current_charging,
            'percentage_changed': percentage_changed,
            'charging_status_changed': charging_status_changed
        }
    def _get_linux_battery(self):
        """Retrieve battery information for Linux"""
        
        result = subprocess.check_output(['acpi', '-b']).decode('utf-8')
        percentage = int(result.split(': ')[1].split('%')[0])
        current_charging = 'Charging' in result

        percentage_changed = (self.last_percentage is None or
                              percentage != self.last_percentage)
        charging_status_changed = (self.last_charging_status is None or
                                   current_charging != self.last_charging_status)

        self.last_percentage = percentage
        self.last_charging_status = current_charging

        return {
            'percentage': percentage, 'charging': current_charging,
            'percentage_changed': percentage_changed,
            'charging_status_changed': charging_status_changed
        }
    def monitor_battery_and_music(self):
        """ battery and music monitoring"""

        
        logging.info("Battery and Music Monitoring Started...")

        while True:
            try:
                battery_info = self.get_battery_info()

                if battery_info:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    status = "Charging" if battery_info['charging'] else "Discharging"

                    logging.info(
                        f"Battery: {battery_info['percentage']}% "
                        f"Status: {status}"
                    )

                    target_met = (
                            battery_info['percentage'] >= self.MIN_PERCENTAGE and
                            battery_info['percentage'] <= self.MAX_PERCENTAGE
                    )

                    if battery_info['charging']:
                        if target_met:
                            self.was_charging_before_unplug = True
                            self.target_met_before_unplug = True
                            if not self.song_playing:
                                self.play_music()
                        else:
                            if self.song_playing:
                                self.stop_music()
                    else:
                        if self.was_charging_before_unplug and self.target_met_before_unplug:
                            if self.song_playing:
                                self.stop_music()

                            self.was_charging_before_unplug = False
                            self.target_met_before_unplug = False

                time.sleep(3)

            except KeyboardInterrupt:
                self.stop_music()
                logging.info("Monitoring stopped by user.")
                break
            except Exception as e:
                logging.error(f"An error occurred during monitoring: {e}")
                break

def main():
    # full path to music
    music_file_path = r"Path to music.wav"

    notifier = BatteryMusicNotifier(music_file_path)
    notifier.monitor_battery_and_music()


if __name__ == "__main__":
    main()
