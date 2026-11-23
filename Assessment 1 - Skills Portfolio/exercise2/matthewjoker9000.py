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


def load_scene(filename):
    path = os.path.join(scenes_dir, filename)
    if os.path.exists(path):
        # resize every image to match the canvas so proportions stay tidy
        img = Image.open(path).resize((SCENE_W, SCENE_H), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    return None


def draw_scene(scene_key):
    photo = scene_images.get(scene_key)
    scene_canvas.delete("all")  # wipe old canvas items before drawing the new scene
    if photo:
        scene_canvas.create_image(0, 0, anchor="nw", image=photo)
        scene_canvas.image = photo  # extra reference on the canvas for safety
    # put the choice buttons back on top since delete("all") clears canvas windows too
    scene_canvas.create_window(125, 255, window=choice1_btn)
    scene_canvas.create_window(295, 255, window=choice2_btn)


def show_intro():
    global state
    state = "intro"
    draw_scene("intro")
    dialogue_label.config(text="Hi.. ! Im Matthew")
    punchline_label.config(text="")
    choice1_btn.config(text="hey there...")
    choice2_btn.config(text="oh wsp...")


def go_to_ask():
    global state
    state = "ask"
    draw_scene("ask")
    dialogue_label.config(text="Wanna hear a joke .... ?")
    punchline_label.config(text="")
    choice1_btn.config(text="ew..! no!")
    choice2_btn.config(text="yes matthew!")


def tell_next_joke():
    global current_joke, state
    if jokes:
        current_joke = random.choice(jokes)
    else:
        # fallback joke so the app still runs if randomJokes.txt is missing
        current_joke = ("Why did Matthew cross the road?", "To grab snacks from the other aisle!")

    state = "setup"
    draw_scene("setup")
    dialogue_label.config(text=current_joke[0])  # show the question first, save the punchline
    punchline_label.config(text="")  # clear the last punchline so it doesn't spoil the new one
    choice1_btn.config(text="umm.. why..")
    choice2_btn.config(text="i dont wana hear it.")


