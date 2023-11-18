import os
import threading
from time import sleep
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import keyboard

# Keybinds
volume_up_key = "f13"
volume_down_key = "f14"
volume_mute_key = "f15"
exit = "f12"

# Variables
volume_step = 2 # The increment/decrement step size for volume adjustments
max_volume = 100 # Maximum playback volume
min_volume = 0 # Minimum playback volume
playback_refresh = 10 # Time in seconds to refresh playback data (for displaying current song)

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

scope = "user-read-playback-state,user-modify-playback-state" # Permissions

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                               redirect_uri=redirect_uri, scope=scope))

playback_data = sp.current_playback()

if playback_data:
    volume = int(playback_data["device"]["volume_percent"]) # Initial player volume
    current_song = playback_data["item"]["name"]
    print(f"Now playing: {current_song}")
else:
    volume = 50
    current_song = None
    print("Nothing is currently playing")

while volume % volume_step != 0:
    volume += 1

try:
    sp.volume(volume)
    print(f"Current volume: {volume}%")
except SpotifyException as exception:
    print("Couldn't set the initial volume")

if volume == 0:
    muted = True
else:
    muted = False

def display_current_song():
    global playback_data
    global current_song
    while True:
        playback_data = sp.current_playback()
        if playback_data:
            new_song = playback_data["item"]["name"]
            if new_song != current_song:
                current_song = new_song
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"Now playing: {current_song}")
        sleep(playback_refresh)

# Start the thread for continuous song display
song_thread = threading.Thread(target=display_current_song)
song_thread.daemon = True  # The thread will exit when the main program exits
song_thread.start()


def volume_up(key):
    if muted:
        print("Playback is muted")
        return
    keyboard.block_key(volume_up_key)
    global volume
    try:
        if volume <= max_volume - volume_step:
            volume += volume_step
            sp.volume(volume)
            print(f"Volume increased to {volume}%")
        else:
            print(f"Volume is already at {volume}%")
    except SpotifyException as exception:
        pass
    keyboard.unblock_key(volume_up_key)

def volume_down(key):
    if muted:
        print("Playback is muted")
        return
    keyboard.block_key(volume_down_key)
    global volume
    try:
        if volume >= min_volume + volume_step:
            volume -= volume_step
            sp.volume(volume)
            print(f"Volume decreased to {volume}%")
        else:
            print(f"Volume is already at {volume}%")
    except SpotifyException as exception:
        pass
    keyboard.unblock_key(volume_down_key)

def volume_mute(key):
    keyboard.block_key(volume_mute_key)
    global muted
    try:
        if muted:
            sp.volume(volume)
            muted = False
            print("Playback unmuted")
        else:
            sp.volume(0)
            muted = True
            print("Playback muted")
    except SpotifyException as exception:
        pass
    keyboard.unblock_key(volume_mute_key)


keyboard.on_press_key(volume_up_key, volume_up)
keyboard.on_press_key(volume_down_key, volume_down)
keyboard.on_press_key(volume_mute_key, volume_mute)

keyboard.wait(exit)
print("Exiting the program...")