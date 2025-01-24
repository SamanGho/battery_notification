# Battery Music Monitor

Play a music file when your battery is charged within a specified range (e.g., 99-100%).

## Features
- Plays music when battery reaches target percentage while charging.
- Stops music when unplugged or outside the target range.
- Cross-platform notifications (Windows, macOS, Linux).

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
