# 🔋🎵 Battery Music Monitor

A cross-platform tool that plays music when your device battery reaches a specified charge level (e.g., 99-100%), ideal for protecting battery health during charging.

## Features ✨
- ▶️ Play music when battery reaches target level while charging
- ⏹️ Automatically stop music when unplugged
- 🔔 Cross-platform desktop notifications
- 🖥️ Supports Windows, macOS, and Linux
- ⚙️ Configurable battery percentage thresholds
- 📝 Detailed logging system

## Requirements
- Python 3.x
- OS-specific tools (see below)

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/SamanGho/battery_notification.git
   cd battery_notification
## Usage
- Edit the script:
- Replace Path to music.wav in main() with your audio file's absolute path


## Install dependencies:


## Windows
```bash
  pip install wmi win10toast sounddevice soundfile # Windows
 ```
## MacOS
```bash
  pip install pync sounddevice soundfile

```
## Linux
``` bash

sudo apt-get install acpi portaudio19-dev libasound2-dev  # Debian/Ubuntu
pip install notify2 sounddevice soundfile

```

## Code Usage 🚀
Configure Music File
``` bash
music_file_path = r"/full/path/to/your/music.wav"  # Use absolute path
```
Run the Monitor
```bash
python battery_monitor.py
```
Adjust Battery Thresholds (Optional)
```
#Modify in the initialization:

#python
#Copy
# BatteryMusicNotifier(music_file, min%, max%)
notifier = BatteryMusicNotifier(music_file_path, 99, 100)
```
Configuration ⚙️
Supported Audio Formats
WAV, FLAC, OGG (via soundfile backend)

MP3 support requires additional libraries

Log File Location
