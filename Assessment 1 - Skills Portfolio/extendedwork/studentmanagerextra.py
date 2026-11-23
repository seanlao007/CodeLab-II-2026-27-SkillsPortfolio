import os  # builds a path from this script's location so it works no matter what folder I run it from
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


def format_student(s):
    # reuse the helper functions here so every screen shows the exact same layout
    cw_total = get_cw_total(s)
    pct = get_percentage(s)
    grade = get_grade(pct)
    return (
        f"Name: {s['name']}  |  Number: {s['code']}\n"
        f"Coursework Total: {cw_total}/60  |  Exam Mark: {s['exam']}/100\n"
        f"Overall Percentage: {pct:.1f}%  |  Grade: {grade}\n"
        f"{'-' * 45}\n"
    )


def show_text(message):
    # clear old text first so clicking a button gives a fresh view instead of stacking text
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, message)


def find_student(query):
    # lowercase + strip so typing a name in any case or matching the student number works
    query = query.strip().lower()
    for s in students:
        if str(s["code"]) == query or s["name"].lower() == query:
            return s
    return None


def view_all():
    if not students:
        show_text("No student records found.")
        return

    text = ""
    total_pct = 0
    for s in students:
        text += format_student(s)
        total_pct += get_percentage(s)

    avg_pct = total_pct / len(students)
    text += f"\nSUMMARY -> Total Students: {len(students)}  |  Average Percentage: {avg_pct:.1f}%"
    show_text(text)


def view_one():
    choice = simpledialog.askstring("View Student", "Enter student name or number:")
    if not choice:  # stop quietly if the user hits Cancel or closes the popup
        return

    found = find_student(choice)
    if found:
        show_text(format_student(found))
    else:
        messagebox.showinfo("Not Found", "No matching student found.")


def show_highest():
    if not students:
        show_text("No student records found.")
        return

    # compare students by total marks out of 160 to find the top scorer
    best = max(students, key=get_total_marks)
    show_text("HIGHEST TOTAL SCORE\n\n" + format_student(best))


def show_lowest():
    if not students:
        show_text("No student records found.")
        return

    # compare students by total marks out of 160 to find the lowest scorer
    lowest = min(students, key=get_total_marks)
    show_text("LOWEST TOTAL SCORE\n\n" + format_student(lowest))




# main tkinter window setup
root = tk.Tk()
root.title("Student Manager")
root.geometry("680x500")
root.configure(bg=BG_COLOR)

tk.Label(
    root,
    text="Student Manager",
    font=("Arial", 16, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
).pack(pady=(10, 6))

# top row of buttons for core features (1 to 4)
btn_row = tk.Frame(root, bg=BG_COLOR)
btn_row.pack(pady=(2, 4))
tk.Button(btn_row, text="1. View All Students", bg=BTN_COLOR, fg=TEXT_COLOR, width=18, command=view_all).pack(side="left", padx=3)
tk.Button(btn_row, text="2. Individual Student", bg=BTN_COLOR, fg=TEXT_COLOR, width=18, command=view_one).pack(side="left", padx=3)
tk.Button(btn_row, text="3. Highest Score", bg=BTN_COLOR, fg=TEXT_COLOR, width=18, command=show_highest).pack(side="left", padx=3)
tk.Button(btn_row, text="4. Lowest Score", bg=BTN_COLOR, fg=TEXT_COLOR, width=18, command=show_lowest).pack(side="left", padx=3)


# main display box for lists, searches, high/low scores, and action messages
output_box = tk.Text(root, width=74, height=18, font=("Consolas", 10), bg=CARD_COLOR, fg=TEXT_COLOR, padx=10, pady=10)
output_box.pack(padx=16, pady=(0, 12))

load_students()
view_all()  # load the text file and show everyone right away when the app opens
root.mainloop()  # keep the GUI running and listening for clicks