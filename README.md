# Spotify Volume
A simple python script to control Spotify volume using keyboard shortcuts.

# Installation
1. Install python from [official website](https://www.python.org/downloads/) or by using winget in your terminal or command prompt:
```
winget install python
```

2. Install dependencies by running the following command in your terminal or command prompt:
```
pip install spotipy keyboard python-dotenv
```

3. Download this repository as ZIP and extract it or clone it using git

# Set up
1. Log into [Spotify for Developers](https://developer.spotify.com/).

2. Create a new app:
    - Choose any desired app name and description
    - Set the redirect URI to anything you prefer, such as ```https://open.spotify.com/``` or ```http://localhost/```
    - Select Web API
    - Accept the [Developer Terms of Service](https://developer.spotify.com/terms) and [Design Guidelines](https://developer.spotify.com/documentation/design)

3. Open your application details and enter them into ```.env-example``` file

4. Rename ```.env-example``` file to ```.env```

# Usage
1. Edit the ```spotify-volume.py``` file. Change the key bindings to your desired keyboard shortcuts by modifying these lines of code:
```python
volume_up_key = "f13"
volume_down_key = "f14"
volume_mute_key = "f15"
exit = "f12"
```

2. Run the Python script by opening the ```spotify-volume.bat``` file or through the shell with ```python [path]/spotify-volume.py```. Running the script directly won't work because it needs to create a cache file for your Spotify token.