# Battery Music Monitor

A cross-platform utility that plays music when your device's battery reaches a specified charge level and manages automatic startup.
for  laptops that when they charge fully it does not alarm you to unplug it .
 script  is running in bg ( background) play the music that you want until you unplug.
 
## Features

- 🎵 Play music when battery reaches target percentage (default: 99-100%)
- 🔔 Desktop notifications for playback status
- 🔄 Automatic startup configuration (Windows, macOS, Linux)
- 📝 Logging system for monitoring events
- 🎧 Supports multiple audio formats (MP3, WAV, OGG, FLAC, AAC, M4A)
- 🔋 Real-time battery status monitoring

## Requirements

- Python 3.6+
- Install ffmpeg for  converting audio file
- Required Python packages:
  ```bash
  python -m pip install pydub numpy sounddevice python-dotenv tkinter soundfile
  ```
- OS-specific dependencies:

  **Windows:**
  ```bash
  pip install win10toast
  ```

  **macOS:**
  ```bash
  pip install pync
  ```

  **Linux:**
  ```bash
  sudo apt-get install libnotify-dev python3-gi
  pip install notify2
  ```

## Installation

Clone the repository:
```bash
git clone https://github.com/SamanGho/battery_notification.git
cd battery_notification
```

Prepare your music file:
- Supported formats: MP3, WAV, OGG, FLAC, AAC, M4A
- Place your audio file in the project directory or keep it in your preferred location

## Usage

### First-Time Setup
Run the main script:
```bash
python battery.py
```
- A file dialog will appear to select your music file
- The script will automatically convert non-WAV files to WAV format

Configure automatic startup:
```bash
python startup_manager.py
```
This will:
- Create startup entries for your OS
- Start the monitoring service immediately
- Ensure the service runs on system startup

### Manual Control
To run without automatic startup:
```bash
python battery.py
```

To stop the service:
- Use `Ctrl+C` in the terminal if running manually
- Task Manager/System Monitor for background processes

## Configuration

### Battery Thresholds
Modify the initialization in `battery.py`:
```python
# Change these values as needed
notifier = BatteryMusicNotifier(music_path, min_percentage=95, max_percentage=100)
```

### Music File
Change the music file at any time by deleting `music_config.txt` and restarting.
The file dialog will reappear on the next launch.

### Logs
Logs are stored in `BatteryMusicLogs/battery_music_monitor.log` with entries like:
```
2023-12-31 23:59:59 - INFO: Battery: 99% Status: Charging
2023-12-31 23:59:59 - INFO: Playing music: alarm_converted.wav
```

## Notes

- 🚨 **First Run:** File dialog may take 10-15 seconds to appear
- 🔊 **Audio Conversion:** Original files are never modified - look for `*_converted.wav`
- 🔋 **Charging Detection:** Music stops when unplugged after reaching target charge
- ⚡ **Performance:** Uses <2% CPU on modern hardware

## Platform Support

| Feature             | Windows | macOS | Linux |
|---------------------|---------|-------|-------|
| Notifications      | ✅       | ✅     | ✅     |
| Background Operation | ✅       | ✅     | ✅     |
| Auto-Start        | ✅       | ✅     | ✅     |
| Battery Detection | ✅       | ✅     | ✅     |

## Troubleshooting

### Common Issues & Fixes

#### Music Doesn't Play
- Ensure your music file is accessible and in a supported format.
- Check logs in `BatteryMusicLogs/battery_music_monitor.log` for errors.

#### No Notifications on Linux
- Ensure `notify2` or `python-gobject` is installed properly.
- Try running with `sudo` if necessary.

#### Auto-Start Not Working
- Ensure `startup_manager.py` was run successfully.
- Manually add the script to system startup if needed.

