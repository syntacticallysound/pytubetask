# Standard library imports
import csv
import json
import os
import threading
from datetime import datetime
from tkinter import Tk, filedialog, simpledialog

# Third-party imports
import keyboard
import pytubefix
from PIL import Image, ImageDraw
from plyer import notification
from pystray import MenuItem as item
import pystray


# Configuration file path
config_file = os.path.expanduser("~/.youtube_downloader_config.json")

# Global variables
download_location = os.path.expanduser("~")
shortcut_key = 'ctrl+shift+y'
history_file = os.path.join(download_location, "download_history.csv")

# Load settings from configuration file
def load_settings():
    global download_location, shortcut_key
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            settings = json.load(file)
            download_location = settings.get('download_location', os.path.expanduser("~"))
            shortcut_key = settings.get('shortcut_key', 'ctrl+shift+y')
    update_history_file_location()

# Save settings to configuration file
def save_settings():
    settings = {
        'download_location': download_location,
        'shortcut_key': shortcut_key
    }
    with open(config_file, 'w') as file:
        json.dump(settings, file)

# Ensure the history file exists
def update_history_file_location():
    global history_file
    history_file = os.path.join(download_location, "download_history.csv")
    if not os.path.exists(history_file):
        with open(history_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "URL", "Date", "Time"])

# Notify helper function
def notify(title, message, icon_path='ytico.ico'):
    notification.notify(
        title=title,
        message=message,
        app_name='YouTube Downloader',
        app_icon= None,
        timeout=2
    )

# Function to download YouTube video or playlist
def download_video():
    global download_location, history_file
    clipboard_content = Tk().clipboard_get()

    if 'youtube.com' in clipboard_content or 'youtu.be' in clipboard_content:
        try:
            notify("YouTube Downloader", "Download started...")
            if "playlist" in clipboard_content or "list=" in clipboard_content:
                playlist = pytubefix.Playlist(clipboard_content)
                for video in playlist.videos:
                    stream = video.streams.get_highest_resolution()
                    stream.download(download_location)

                    now = datetime.now()
                    with open(history_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([stream.title, video.watch_url, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])

                    notify("YouTube Downloader", f"Download completed: {stream.title}")
                    print(f"Download completed: {stream.title}")
            else:
                yt = pytubefix.YouTube(clipboard_content)
                stream = yt.streams.get_highest_resolution()
                stream.download(download_location)

                now = datetime.now()
                with open(history_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([stream.title, clipboard_content, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])

                notify("YouTube Downloader", f"Download completed: {stream.title}")
                print(f"Download completed: {stream.title}")
        except Exception as e:
            notify("YouTube Downloader", f"Error: {e}")
            print(f"Error downloading video: {e}")
    else:
        notify("YouTube Downloader", "No valid YouTube URL found in clipboard.")
        print("No valid YouTube URL found in clipboard.")

# Function to set download location
def set_download_location():
    global download_location
    root = Tk()
    root.withdraw()
    download_location = filedialog.askdirectory(initialdir=download_location)
    root.destroy()

    update_history_file_location()
    save_settings()
    notify("YouTube Downloader", f"New download location: {download_location}")

# Function to set shortcut key
def set_shortcut_key():
    global shortcut_key
    root = Tk()
    root.withdraw()
    new_shortcut = simpledialog.askstring("Shortcut Key", "Enter new shortcut key combination:", initialvalue=shortcut_key)
    root.destroy()

    if new_shortcut:
        keyboard.remove_hotkey(shortcut_key)
        shortcut_key = new_shortcut
        keyboard.add_hotkey(shortcut_key, download_video)
        save_settings()
        notify("YouTube Downloader", f"New shortcut key: {shortcut_key}")

# Create icon image for the taskbar menu
def create_image():
    width, height = 64, 64
    icon = Image.new('RGB', (width, height), color=(255, 255, 255))  # White background
    draw = ImageDraw.Draw(icon)

    # Draw red rectangle (YouTube's background color)
    margin = 0
    draw.rectangle([margin, margin, width - margin, height - margin], fill=(255, 0, 0))

    # Draw white play button (triangle)
    play_button = [
        (margin + 10, margin + 8),                # Left point
        (width - margin - 10, height // 2),       # Right center
        (margin + 10, height - margin - 8)        # Bottom point
    ]
    draw.polygon(play_button, fill=(255, 255, 255))

    return icon

# Menu for the taskbar icon
menu = (
    item('Set Download Location', set_download_location),
    item('Set Shortcut Key', set_shortcut_key),
    item('Quit', lambda: icon.stop())
)

# Load settings on startup
load_settings()

# Create the icon
icon = pystray.Icon("YouTube Downloader")
icon.icon = create_image()
icon.menu = menu

# Register the keyboard shortcut
keyboard.add_hotkey(shortcut_key, download_video)

# Run the icon
icon.run()
