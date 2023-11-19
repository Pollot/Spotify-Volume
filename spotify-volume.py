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
exit_key = "f12"

# Settings
volume_step = 2   # The increment/decrement step size for volume adjustments
max_volume = 100  # Maximum playback volume
min_volume = 0    # Minimum playback volume
bar_length = 25   # Volume bar length
refresh_rate = 5  # Time in seconds to refresh playback data

# Dynamic variables (don't modify them!)
volume = 0          # Initial volume, it will change after playback has been started
block_keys = False  # Blocks keys, unless there is a song playing
restriction = False # If API restriction is active
muted = False       # If playback is muted

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

scope = "user-read-playback-state,user-modify-playback-state" # Permissions

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                               redirect_uri=redirect_uri, scope=scope))

def clear_terminal():
    os.system('cls' if os.name=='nt' else 'clear')

# Print in the same line
last_length = 0
def print_inline(string):
    global last_length
    current_length = len(string)
    print(f"\r{string}", end=" " * (last_length - current_length), flush=True)
    last_length = len(string)

# Volume bar
def print_volume(volume):
    filled_length = int(bar_length * volume / max_volume)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    print_inline(f"Volume: [{bar}] {volume}%")

def print_muted():
    print_inline("Playback is muted")

def exception_handling(exception):
    global block_keys
    global restriction

    if exception.http_status == 403:
        clear_terminal()
        print("API restriction violated, please wait a moment")
        block_keys = True
        restriction = True
    else:
        pass


def refresh_playback_data():
    current_song = None
    current_is_playing = False
    global block_keys
    global volume
    global muted
    global restriction

    while True:
        playback_data = sp.current_playback()

        if playback_data:
            new_song = playback_data["item"]["name"]
            new_is_playing = playback_data["is_playing"]

            if current_song != new_song or current_is_playing != new_is_playing or block_keys == True:
                current_song = new_song
                current_is_playing = new_is_playing

                if current_is_playing is False:
                    clear_terminal()
                    print("Playback paused")
                else:    
                    artists = ", ".join([artist["name"] for artist in playback_data["item"]["artists"]])
                    album = playback_data["item"]["album"]["name"]
                    clear_terminal()
                    print(f"Now playing: {current_song} by {artists}")
                    print(f"From: {album}")
                
                volume = int(playback_data["device"]["volume_percent"])
                # Ensure that volume is divisible by volume_step
                while volume % volume_step != 0:
                    if volume < max_volume - volume_step:
                        volume += 1
                    else:
                        volume -= 1
                try:
                    sp.volume(volume)
                    muted = False
                    restriction = False
                    print_volume(volume)
                except SpotifyException as exception:
                    exception_handling(exception)
                    sleep(25) # Increase refresh rate to avoid restriction
                
            if restriction is False:
                block_keys = False

        else:
            if block_keys is False:
                clear_terminal()
                print("Nothing is currently playing")
                block_keys = True
        
        sleep(refresh_rate)

# Start the thread for refreshing playback data
playback_thread = threading.Thread(target=refresh_playback_data)
playback_thread.daemon = True  # The thread will exit when the main program exits
playback_thread.start()


def volume_up(key):
    if muted or block_keys:
        return
    
    keyboard.block_key(volume_up_key)
    global volume

    try:
        if volume <= max_volume - volume_step:
            volume += volume_step
            sp.volume(volume)
            print_volume(volume)
    except SpotifyException as exception:
        exception_handling(exception)

    keyboard.unblock_key(volume_up_key)


def volume_down(key):
    if muted or block_keys:
        return

    keyboard.block_key(volume_down_key)
    global volume

    try:
        if volume >= min_volume + volume_step:
            volume -= volume_step
            sp.volume(volume)
            print_volume(volume)
    except SpotifyException as exception:
        exception_handling(exception)

    keyboard.unblock_key(volume_down_key)

def volume_mute(key):
    if block_keys:
        return
    
    keyboard.block_key(volume_mute_key)
    global muted

    try:
        if muted:
            sp.volume(volume)
            muted = False
            print_volume(volume)
        else:
            sp.volume(0)
            muted = True
            print_muted()
    except SpotifyException as exception:
        exception_handling(exception)
    
    keyboard.unblock_key(volume_mute_key)


keyboard.on_press_key(volume_up_key, volume_up)
keyboard.on_press_key(volume_down_key, volume_down)
keyboard.on_press_key(volume_mute_key, volume_mute)

keyboard.wait(exit_key)
print_inline("Exiting the program...")