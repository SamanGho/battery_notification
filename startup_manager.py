import platform
import os
import sys
import shutil
import subprocess


def create_startup_entries():
    os_type = platform.system()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, 'battery.py')
    python_exec = sys.executable

    try:
        if os_type == "Windows":
            pythonw_path = python_exec.replace("python.exe", "pythonw.exe")
            if not os.path.exists(pythonw_path):
                pythonw_path = python_exec  # Fallback to python.exe

            startup_dir = os.path.join(
                os.getenv("APPDATA"),
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs",
                "Startup"
            )
            bat_path = os.path.join(startup_dir, "run_battery_music.bat")
            with open(bat_path, "w") as f:
                f.write(f'@echo off\nstart "" "{pythonw_path}" "{main_script}"\nexit /b\n')

            # Start the script immediately
            subprocess.Popen(
                [pythonw_path, main_script],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        elif os_type == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_path = os.path.join(autostart_dir, "battery_music.desktop")

            desktop_entry = f"""[Desktop Entry]
Type=Application
Exec=sh -c "{sys.executable} {main_script} >/dev/null 2>&1 &"
Hidden=false
X-GNOME-Autostart-enabled=true
Name=Battery Music Monitor
Comment=Start battery monitoring music service"""

            with open(desktop_path, "w") as f:
                f.write(desktop_entry)
            os.chmod(desktop_path, 0o755)

            # Start the script immediately
            subprocess.Popen(
                [sys.executable, main_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

        elif os_type == "Darwin":
            launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
            os.makedirs(launch_agents_dir, exist_ok=True)
            plist_path = os.path.join(launch_agents_dir, "com.user.batterymusic.plist")

            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.batterymusic</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{main_script}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/dev/null</string>
    <key>StandardErrorPath</key>
    <string>/dev/null</string>
    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>"""

            with open(plist_path, "w") as f:
                f.write(plist_content)
            os.chmod(plist_path, 0o644)

            ret = os.system(f"launchctl load -w {plist_path}")
            if ret != 0:
                raise Exception(f"launchctl load failed with exit code {ret}")

        else:
            print("Unsupported operating system")
            return False

        return True

    except Exception as e:
        print(f"Error creating startup entries: {str(e)}")
        return False


if __name__ == "__main__":
    if create_startup_entries():
        print("Successfully created background startup entries and started the script.")
    else:
        print("Failed to create startup entries")
