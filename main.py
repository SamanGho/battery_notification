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
