import os
import pytube
import keyboard
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from tkinter import Tk, filedialog, simpledialog
from plyer import notification
import csv
from datetime import datetime
import json

# Configuration file path
config_file = os.path.expanduser("~/.youtube_downloader_config.json")

# Load settings from configuration file
def load_settings():
    global download_location, shortcut_key
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            settings = json.load(file)
            download_location = settings.get('download_location', os.path.expanduser("~"))
            shortcut_key = settings.get('shortcut_key', 'ctrl+shift+y')
    else:
        download_location = os.path.expanduser("~")
        shortcut_key = 'ctrl+shift+y'
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
        with open(history_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "URL", "Date", "Time"])

# Function to download YouTube video
def download_video():
    global download_location, history_file
    clipboard_content = Tk().clipboard_get()
    if 'youtube.com' in clipboard_content:
        try:
            notification.notify(
                title='YouTube Downloader',
                message='Download started...',
                timeout=2
            )
            yt = pytube.YouTube(clipboard_content)
            stream = yt.streams.get_highest_resolution()
            stream.download(download_location)
            
            # Log the download
            now = datetime.now()
            with open(history_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([stream.title, clipboard_content, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])
            
            notification.notify(
                title='YouTube Downloader',
                message=f'Download completed: {stream.title}',
                timeout=2
            )
            print(f'Download completed: {stream.title}')
        except Exception as e:
            notification.notify(
                title='YouTube Downloader',
                message=f'Error: {e}',
                timeout=2
            )
            print(f'Error downloading video: {e}')
    else:
        notification.notify(
            title='YouTube Downloader',
            message='No valid YouTube URL found in clipboard.',
            timeout=2
        )
        print('No valid YouTube URL found in clipboard.')

# Function to set new download location
def set_download_location():
    global download_location, history_file
    root = Tk()
    root.withdraw()
    download_location = filedialog.askdirectory(initialdir=download_location)
    root.destroy()
    
    # Update history file location
    update_history_file_location()
    save_settings()
    
    notification.notify(
        title='YouTube Downloader',
        message=f'New download location: {download_location}',
        timeout=2
    )
    print(f'New download location: {download_location}')

# Function to set new shortcut key
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
        notification.notify(
            title='YouTube Downloader',
            message=f'New shortcut key: {shortcut_key}',
            timeout=2
        )
        print(f'New shortcut key: {shortcut_key}')

# Get the directory path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to your custom icon image (assuming it's in the same directory as the script)
custom_icon_path = os.path.join(script_dir, "ytico.png")
# Function to create the icon image
def create_image():
    try:
        icon_image = Image.open(custom_icon_path)
        return icon_image
    except Exception as e:
        print(f"Error loading custom icon: {e}")
        # If loading the custom icon fails, fallback to default icon
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=(0, 0, 0))
        dc.rectangle((0, height // 2, width // 2, height), fill=(0, 0, 0))
        return image

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
