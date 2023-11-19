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

# Variables
volume_step = 2   # The increment/decrement step size for volume adjustments
max_volume = 100  # Maximum playback volume
min_volume = 0    # Minimum playback volume
refresh_rate = 10 # Time in seconds to refresh playback data

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

scope = "user-read-playback-state,user-modify-playback-state" # Permissions

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                               redirect_uri=redirect_uri, scope=scope))

def clear_terminal():
    os.system('cls' if os.name=='nt' else 'clear')

playback_data = sp.current_playback()

if playback_data:
    current_song = playback_data["item"]["name"]
    clear_terminal()
    print(f"Now playing: {current_song}")

    volume = int(playback_data["device"]["volume_percent"]) # Playback volume
    # Ensure that volume is divisible by volume_step
    while volume % volume_step != 0:
        if volume < max_volume - volume_step:
            volume += 1
        else:
            volume -= 1
    sp.volume(volume)
    print(f"Playback volume: {volume}%")
else:
    volume = 20 # Initial volume if playback volume is not available
    current_song = None
    print("Nothing is currently playing")

block_keys = False

def refresh_playback_data():
    global playback_data
    global current_song
    global block_keys

    while True:
        playback_data = sp.current_playback()

        if playback_data:
            new_song = playback_data["item"]["name"]
            if current_song != new_song or block_keys == True:
                current_song = new_song
                clear_terminal()
                print(f"Now playing: {current_song}")
                
                volume = playback_data["device"]["volume_percent"]    
                print(f"Playback volume: {volume}%")
            
            block_keys = False
        else:
            if block_keys == False:
                clear_terminal()
                print("Nothing is currently playing")
                block_keys = True
        
        sleep(refresh_rate)

# Start the thread for refreshing playback data
song_thread = threading.Thread(target=refresh_playback_data)
song_thread.daemon = True  # The thread will exit when the main program exits
song_thread.start()


muted = False

def volume_up(key):
    if muted:
        print("Playback is muted")
        return
    
    if block_keys:
        print("Can't change volume becaue nothing is currently playing")
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
    
    if block_keys:
        print("Can't change volume becaue nothing is currently playing")
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
    if block_keys:
        print("Can't change volume becaue nothing is currently playing")
        return
    
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

keyboard.wait(exit_key)
print("Exiting the program...")