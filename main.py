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
                    