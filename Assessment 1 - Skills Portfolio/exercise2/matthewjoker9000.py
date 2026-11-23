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


def reveal_punchline():
    global state, current_joke
    if not current_joke:  # fallback if reveal_punchline is ever reached without a joke set
        current_joke = ("Why did Matthew cross the road?", "To grab snacks from the other aisle!")
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
    # same two buttons stay on screen, so check state to decide what choice 1 does
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
    # same idea for choice 2 depending on where the user is in the flow
    if state == "intro":
        go_to_ask()
    elif state == "ask":
        tell_next_joke()
    elif state == "setup":
        show_sad_scene()
    elif state == "punchline":
        show_sad_scene()
    elif state == "sad":
        root.destroy()


# --- Main Tkinter Window ---
root = tk.Tk()
root.title("Matthew Jokester 9000")
root.geometry("570x490")
root.resizable(False, False)  # keep window size fixed so button coordinates stay aligned
root.configure(bg="#E6F7F2")

# load scene images once at startup rather than reading from disk on every click
for key in ["intro", "ask", "setup", "punchline", "sad"]:  # only load scenes actively used by the flow
    scene_images[key] = load_scene(f"{key}.png")

scene_canvas = tk.Canvas(root, width=SCENE_W, height=SCENE_H, highlightthickness=2, highlightbackground="#66C2A5")
scene_canvas.pack(pady=(12, 8))

# two choice buttons whose text updates to fit each scene
choice1_btn = tk.Button(scene_canvas, font=("Trebuchet MS", 9, "bold"), bg="#FFFFFF", width=20, command=handle_choice_1)
choice2_btn = tk.Button(scene_canvas, font=("Trebuchet MS", 9, "bold"), bg="#FFFFFF", width=20, command=handle_choice_2)

# dialogue panel underneath the scene for Matthew's lines and punchlines
dialogue_frame = tk.Frame(root, bg="#FFFFFF", highlightbackground="#66C2A5", highlightthickness=2, padx=14, pady=10)
dialogue_frame.pack(padx=15, fill="x")

name_label = tk.Label(dialogue_frame, text="Matthew", font=("Trebuchet MS", 9, "bold"), bg="#45B7D1", fg="#FFFFFF", padx=8, pady=1)
name_label.pack(anchor="w", pady=(0, 4))

dialogue_label = tk.Label(dialogue_frame, font=("Trebuchet MS", 11, "bold"), bg="#FFFFFF", fg="#1E2D2F", wraplength=500, justify="left", anchor="w")
dialogue_label.pack(fill="x")

punchline_label = tk.Label(dialogue_frame, font=("Trebuchet MS", 11, "italic"), bg="#FFFFFF", fg="#2B7A78", wraplength=500, justify="left", anchor="w")
punchline_label.pack(fill="x", pady=(4, 0))

tk.Button(root, text="Quit", font=("Trebuchet MS", 9, "bold"), bg="#FFE5E5", fg="#7A1C1C", padx=14, command=root.destroy).pack(pady=(8, 10))

show_intro()  # open on Matthew's intro scene
root.mainloop()  # start Tkinter's event loop so the GUI stays responsive