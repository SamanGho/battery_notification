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
   git clone https://github.com/yourusername/battery-music-monitor.git
   cd battery-music-monitor
## Usage
- Edit the script:
- Replace Path to music.wav in main() with your audio file's absolute path


## Install dependencies:


All Platforms:
   ```bash
  pip install sounddevice soundfile
 ```
## Windows
```bash
  pip install wmi win10toast # Windows
 ```
## MacOS
```bash
  pip install pync 

```
## Linux
``` bash

sudo apt-get install acpi portaudio19-dev libasound2-dev  # Debian/Ubuntu
pip install notify2
