import os
import sys
import configparser
from pathlib import Path

channels = []

# Get the streamers that you follow
def getfollows():
    """Cheacking if follows.txt exists and if it does returns a list with all the streamer names."""
    HOME = str(Path.home())
    try:
        with open(HOME+'/.config/twitchlivechecker/follows.txt', 'r') as follows:
            for line in follows:
                channels.append(line)
            # print(channels)
        return channels
    except FileNotFoundError:
        print("You seem to not follow any streamer.")
        print("Add your favorite streamers in ~/.config/twitchlivechecker/follows.txt")
        sys.exit()
