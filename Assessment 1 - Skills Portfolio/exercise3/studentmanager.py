import os  # builds a reliable file path regardless of which folder I launch Python from
import tkinter as tk
from tkinter import messagebox, simpledialog

BG_COLOR = "#17E0E7"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1E293B"
BTN_COLOR = "#0CFFB6"

# points to resources/studentMarks.txt sitting right next to this script
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "resources", "studentMarks.txt")

students = []  # stores each student as a dict so I can use field names instead of list indexes


def load_students():
    students.clear()  # wipe the list first so reloading never duplicates rows
    if not os.path.exists(file_path):
        messagebox.showwarning("File Not Found", f"Could not find {file_path}.")  # warn if the data file is missing
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # line 0 is the student count, so start from index 1 for actual student records
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) == 6:
            student = {
                "code": int(parts[0].strip()),
                "name": parts[1].strip(),
                "cw1": int(parts[2].strip()),
                "cw2": int(parts[3].strip()),
                "cw3": int(parts[4].strip()),
                "exam": int(parts[5].strip()),
            }
            students.append(student)


def get_cw_total(s):
    return s["cw1"] + s["cw2"] + s["cw3"]  # 3 coursework marks out of 20 each -> 60 max


def get_total_marks(s):
    return get_cw_total(s) + s["exam"]  # 60 coursework + 100 exam -> 160 total marks


def get_percentage(s):
    return (get_total_marks(s) / 160) * 100  # overall percentage out of 160 marks


def get_grade(pct):
    # grade boundaries from the assignment brief
    if pct >= 70:
        return "A"
    elif pct >= 60:
        return "B"
    elif pct >= 50:
        return "C"
    elif pct >= 40:
        return "D"
    else:
        return "F"


