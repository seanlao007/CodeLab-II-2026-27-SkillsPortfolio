import os  # using os so file paths still work if I run from another folder
import random
import tkinter as tk
from PIL import Image, ImageTk

# getting paths relative to this script so resources are found reliably
main_directory = os.path.dirname(os.path.abspath(__file__))
jokes_path = os.path.join(main_directory, "resources", "randomJokes.txt")
scenes_dir = os.path.join(main_directory, "resources", "scenes")

# split each line on the first ? so setup and punchline stay separate
jokes = []
if os.path.exists(jokes_path):  # only read file if it's actually there
    with open(jokes_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if "?" in line:  # maxsplit=1 leaves any extra ? inside the punchline
                setup, punchline = line.split("?", 1)
                jokes.append((setup.strip() + "?", punchline.strip()))

current_joke = None  # keep current joke so punchline matches the setup shown
state = "intro"  # track which scene I'm on so button clicks do the right thing
scene_images = {}  # keep image refs here so Python doesn't garbage-collect them

SCENE_W = 540
SCENE_H = 290


def load_scene(filename):
    path = os.path.join(scenes_dir, filename)
    if os.path.exists(path):
        # resize image to fit the canvas box
        img = Image.open(path).resize((SCENE_W, SCENE_H), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    return None  # fall back cleanly if an image file is missing


def draw_scene(scene_key):
    photo = scene_images.get(scene_key)
    scene_canvas.delete("all")  # wipe old items before drawing the next scene
    if photo:
        scene_canvas.create_image(0, 0, anchor="nw", image=photo)
        scene_canvas.image = photo  # hold a reference on the canvas too
    # delete("all") removes canvas windows too, so re-add the choice buttons
    scene_canvas.create_window(125, 255, window=choice1_btn)
    scene_canvas.create_window(295, 255, window=choice2_btn)


def show_intro():
    global state
    state = "intro"
    draw_scene("intro")
    dialogue_label.config(text="Hi.. ! Im Alexa")
    punchline_label.config(text="")  # clear punchline area on non-punchline scenes
    choice1_btn.config(text="hey there...")
    choice2_btn.config(text="oh wsp...")


def go_to_ask():
    global state
    state = "ask"
    draw_scene("ask")
    dialogue_label.config(text="Wanna hear a joke .... ?")
    punchline_label.config(text="")
    choice1_btn.config(text="ew..! no!")
    choice2_btn.config(text="yes alexa!")


def tell_next_joke():
    global current_joke, state
    if jokes:
        current_joke = random.choice(jokes)  # pick a random joke from the file
    else:
        # backup joke so the app still works if the text file is empty/missing
        current_joke = ("Why did Alexa cross the road?", "To grab snacks from the other aisle!")

    state = "setup"
    draw_scene("setup")
    dialogue_label.config(text=current_joke[0])
    punchline_label.config(text="")  # wipe old punchline before showing a new joke
    choice1_btn.config(text="idk... tell me")
    choice2_btn.config(text="i dont wana hear it.")


def reveal_punchline():
    global state, current_joke
    if not current_joke:  # safety fallback if punchline is triggered directly
        current_joke = ("Why did Alexa cross the road?", "To grab snacks from the other aisle!")
    state = "punchline"
    draw_scene("punchline")
    punchline_label.config(text=current_joke[1])
    choice1_btn.config(text="wow... another one !")
    choice2_btn.config(text="that was so bad.")


def show_sad_scene():
    global state
    state = "sad"
    draw_scene("sad")
    dialogue_label.config(text="wahhh..!!! wahh!!!........... iM So SaD!!! :((")
    punchline_label.config(text="")
    choice1_btn.config(text="okay try again")
    choice2_btn.config(text="Quit")


def handle_choice_1():
    # change what button 1 does depending on which scene we're in
    if state == "intro":
        go_to_ask()
    elif state == "ask":
        show_sad_scene()
    elif state == "setup":
        reveal_punchline()
    elif state == "punchline":
        tell_next_joke()
    elif state == "sad":
        go_to_ask()


def handle_choice_2():
    # change what button 2 does depending on which scene we're in
    if state == "intro":
        go_to_ask()
    elif state == "ask":
        tell_next_joke()
    elif state == "setup":
        show_sad_scene()
    elif state == "punchline":
        show_sad_scene()
    elif state == "sad":
        root.destroy()  # close the app window


# main window setup
root = tk.Tk()
root.title("Alexa Jokester 9000")
root.geometry("570x490")
root.resizable(False, False)  # lock size so button coordinates on canvas stay put
root.configure(bg="#E6F7F2")

# load all scene PNGs once at startup instead of reloading every click
for key in ["intro", "ask", "setup", "punchline", "sad"]:
    scene_images[key] = load_scene(f"{key}.png")

scene_canvas = tk.Canvas(root, width=SCENE_W, height=SCENE_H, highlightthickness=2, highlightbackground="#66C2A5")
scene_canvas.pack(pady=(12, 8))

# reuse two buttons on the canvas and swap their text per scene
choice1_btn = tk.Button(scene_canvas, font=("Trebuchet MS", 9, "bold"), bg="#FFFFFF", width=20, command=handle_choice_1)
choice2_btn = tk.Button(scene_canvas, font=("Trebuchet MS", 9, "bold"), bg="#FFFFFF", width=20, command=handle_choice_2)

# dialogue box below the scene for Alexa's setup and punchline
dialogue_frame = tk.Frame(root, bg="#FFFFFF", highlightbackground="#66C2A5", highlightthickness=2, padx=14, pady=10)
dialogue_frame.pack(padx=15, fill="x")

name_label = tk.Label(dialogue_frame, text="Alexa", font=("Trebuchet MS", 9, "bold"), bg="#45B7D1", fg="#FFFFFF", padx=8, pady=1)
name_label.pack(anchor="w", pady=(0, 4))

dialogue_label = tk.Label(dialogue_frame, font=("Trebuchet MS", 11, "bold"), bg="#FFFFFF", fg="#1E2D2F", wraplength=500, justify="left", anchor="w")
dialogue_label.pack(fill="x")

punchline_label = tk.Label(dialogue_frame, font=("Trebuchet MS", 11, "italic"), bg="#FFFFFF", fg="#2B7A78", wraplength=500, justify="left", anchor="w")
punchline_label.pack(fill="x", pady=(4, 0))

tk.Button(root, text="Quit", font=("Trebuchet MS", 9, "bold"), bg="#FFE5E5", fg="#7A1C1C", padx=14, command=root.destroy).pack(pady=(8, 10))

show_intro()  # open on the intro scene
root.mainloop()  # start the Tkinter event loop