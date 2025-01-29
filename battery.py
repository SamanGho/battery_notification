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
from contextlib import contextmanager

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

    def cleanup_log(self):
        """Clean up log file every 3 days"""
        try:
            logger = logging.getLogger()
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.FileHandler) and handler.baseFilename == os.path.abspath(log_file_path):
                    logger.removeHandler(handler)
                    handler.close()

            with open(log_file_path, 'w'):
                pass

            new_handler = logging.FileHandler(log_file_path)
            new_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
            logger.addHandler(new_handler)

            logging.info("Log file cleaned up successfully.")
            return True
        except Exception as e:
            logging.error(f"Log cleanup failed: {e}")
            return False

    def _play_audio_thread(self):
        """Audio playback in a separate thread using pydub"""
        try:
            try:
                audio = AudioSegment.from_file(self.music_file_path)
            except CouldntDecodeError as e:
                logging.error(f"Unsupported audio format: {e}")
                return
            except Exception as e:
                logging.error(f"Error loading audio file: {e}")
                return

            samples = np.array(audio.get_array_of_samples())

            if audio.channels > 1:
                samples = samples.reshape((-1, audio.channels))
            else:
                samples = samples.reshape((-1, 1))

            samplerate = audio.frame_rate
            dtype = self._get_dtype(audio.sample_width)

            samples = samples.astype(dtype)

            if dtype == np.int16:
                samples = samples.astype(np.float32) / 32768.0
            elif dtype == np.int32:
                samples = samples.astype(np.float32) / 2147483648.0

            while not self.stop_playback.is_set():
                sd.play(samples, samplerate)
                sd.wait()

        except Exception as e:
            logging.error(f"Audio thread error: {e}")
    def _get_dtype(self, sample_width):
        """Get numpy dtype based on audio sample width"""
        return {
            1: np.int8,  # 8-bit
            2: np.int16,  # 16-bit
            3: np.int32,  # 24-bit (stored in 32-bit)
            4: np.int32  # 32-bit
        }.get(sample_width, np.float32)
    def send_notification(self, title, message):
        """Send cross-platform notifications"""
        try:
            if self.system == "Windows" and self.notifier:
                self.notifier.show_toast(title, message, duration=5)
            elif self.system == "Darwin" and self.notifier:
                self.notifier.notify(message, title=title)
            elif self.system == "Linux":
                if "notify2" in globals() and self.notifier:
                    notification = notify2.Notification(title, message)
                    notification.show()
                elif "Notify" in globals() and self.notifier:
                    notification = Notify.Notification.new(title, message)
                    notification.show()
            logging.info(f"Notification: {title} - {message}")
        except Exception as e:
            logging.error(f"Notification error: {e}")

    def play_music(self):
        """Play music with error handling and notifications"""
        try:
            if not os.path.exists(self.music_file_path):
                logging.error(f"Music file not found: {self.music_file_path}")
                return False

            self.stop_playback.clear()
            self.play_thread = threading.Thread(target=self._play_audio_thread, daemon=True)
            self.play_thread.start()

            self.song_playing = True
            self.send_notification("Music Started",
                                   f"Music started playing at {datetime.now().strftime('%H:%M:%S')}")
            logging.info(f"Playing music: {os.path.basename(self.music_file_path)}")
            return True
        except Exception as e:
            logging.error(f"Music playback error: {e}")
            return False


    def stop_music(self):
        """Stop music playback with error handling"""
        try:
            if self.song_playing:
                self.stop_playback.set()
                sd.stop()

                if self.play_thread and self.play_thread.is_alive():
                    self.play_thread.join(timeout=5)

                self.song_playing = False
                self.play_thread = None
                self.send_notification("Music Stopped",
                                       f"Music stopped at {datetime.now().strftime('%H:%M:%S')}")
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
        current_charging = battery.BatteryStatus == 2  # 2 means charging

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
        """Battery and music monitoring"""
        logging.info("Battery and Music Monitoring Started...")

        while True:
            try:
                if datetime.now() >= self.next_log_cleanup:
                    if self.cleanup_log():
                        self.next_log_cleanup = datetime.now() + timedelta(days=3)
                    else:
                        self.next_log_cleanup = datetime.now() + timedelta(hours=1)

                battery_info = self.get_battery_info()
                if battery_info:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    status = "Charging" if battery_info['charging'] else "Discharging"

                    logging.info(f"Battery: {battery_info['percentage']}% Status: {status}")

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




def get_music_file():
    """Get music file path with persistence"""
    config_file = os.path.join(SCRIPT_DIR, "music_config.txt")

    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            saved_path = f.read().strip()
        if os.path.exists(saved_path):
            return saved_path

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Music File",
        filetypes=[
            ("Audio Files", "*.mp3 *.wav *.ogg *.flac *.aac *.m4a"),
            ("MP3 Files", "*.mp3"),
            ("WAV Files", "*.wav"),
            ("All Files", "*.*")
        ]
    )
    root.destroy()

    if file_path:
        with open(config_file, "w") as f:
            f.write(file_path)
        return file_path
    else:
        logging.error("No music file selected. Exiting.")
        exit(1)



def main():
    music_path = get_music_file()
    notifier = BatteryMusicNotifier(music_path)
    notifier.monitor_battery_and_music()


if __name__ == "__main__":
    main()
