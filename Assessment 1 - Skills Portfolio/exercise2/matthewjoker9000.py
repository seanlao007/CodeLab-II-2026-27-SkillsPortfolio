import os  # builds paths from the script's location so it doesn't break on another PC
import random
import tkinter as tk
from PIL import Image, ImageTk  # Pillow handles opening and resizing the scene PNGs for Tkinter

# locate the jokes file and scene images relative to where this script lives
main_directory = os.path.dirname(os.path.abspath(__file__))
jokes_path = os.path.join(main_directory, "resources", "randomJokes.txt")
scenes_dir = os.path.join(main_directory, "resources", "scenes")

# load jokes into (setup, punchline) pairs so setup and punchline stay separate
jokes = []
if os.path.exists(jokes_path):
    with open(jokes_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            # split only at the first ? in case the punchline has one too
            if "?" in line:
                setup, punchline = line.split("?", 1)
                jokes.append((setup.strip() + "?", punchline.strip()))

current_joke = None  # holds the active joke so reveal_punchline() knows what to show
state = "intro"  # keeps track of the current scene so the choice buttons react right
scene_images = {}  # stores PhotoImages so Python's garbage collector doesn't blank them out

SCENE_W = 540
SCENE_H = 290
