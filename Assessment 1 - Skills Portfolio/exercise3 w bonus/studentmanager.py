import os  # builds file paths relative to this script's folder instead of hardcoding paths
import tkinter as tk
from tkinter import messagebox, simpledialog

BG_COLOR = "#B8F2F4"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#0F172A"
BTN_COLOR = "#5EEAD4"
HIDE_BTN_COLOR = "#FCA5A5"

# points to resources/studentMarks.txt right next to this script
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "resources", "studentMarks.txt")

students = []  # stores each student as a dict so I can use named keys instead of index numbers


def load_students():
    students.clear()  # wipe old entries first so reloading doesn't duplicate records
    if not os.path.exists(file_path):
        messagebox.showwarning("Missing File", f"Could not find {file_path}.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # line 0 is the student count, so start from index 1 for actual student rows
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) != 6:
            continue
        try:
            students.append({
                "code": int(parts[0].strip()),
                "name": parts[1].strip(),
                "cw1": int(parts[2].strip()),
                "cw2": int(parts[3].strip()),
                "cw3": int(parts[4].strip()),
                "exam": int(parts[5].strip()),
            })
        except ValueError:
            continue  # skip broken or non-numeric rows instead of crashing startup

    refresh_count()


def save_students():
    # write the updated count on line 1, followed by each student row
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"{len(students)}\n")
        for s in students:
            f.write(f"{s['code']},{s['name']},{s['cw1']},{s['cw2']},{s['cw3']},{s['exam']}\n")
    refresh_count()


def refresh_count():
    count_label.config(text=f"Students: {len(students)}")


def cw_total(s):
    return s["cw1"] + s["cw2"] + s["cw3"]  # 3 coursework marks out of 20 each = 60 max


def total_marks(s):
    return cw_total(s) + s["exam"]  # 60 coursework + 100 exam = 160 total marks


def percentage(s):
    return (total_marks(s) / 160) * 100


def grade_for(pct):
    # standard grade boundaries out of 100%
    if pct >= 70:
        return "A"
    if pct >= 60:
        return "B"
    if pct >= 50:
        return "C"
    if pct >= 40:
        return "D"
    return "F"


def format_student(s):
    # keep every student card formatted the same way across views
    pct = percentage(s)
    return (
        f"Name: {s['name']}  |  ID: {s['code']}\n"
        f"Coursework: {cw_total(s)}/60  |  Exam: {s['exam']}/100\n"
        f"Total: {total_marks(s)}/160  |  {pct:.1f}%  |  Grade: {grade_for(pct)}\n"
        f"{'-' * 46}\n"
    )


def show_output(text):
    # clear old output before writing new text so views don't stack
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, text)


def show_privacy_screen():
    # hide student marks on startup and on demand so sensitive data isn't left exposed
    show_output(
        "RECORDS HIDDEN FOR PRIVACY\n"
        "----------------------------------------------\n"
        "Click an option above to view or manage records."
    )


def has_records():
    if students:
        return True
    show_output("No student records available.")
    return False


def find_student(query):
    # lowercase + strip so searching by name or ID works regardless of casing or spaces
    clean = query.strip().lower()
    for s in students:
        if str(s["code"]) == clean or s["name"].lower() == clean:
            return s
    return None


def duplicate_code(code, ignore_student=None):
    # ignore_student lets an existing student keep their own ID when updating other fields
    for s in students:
        if s is not ignore_student and s["code"] == code:
            return True
    return False


def valid_marks(cw1, cw2, cw3, exam):
    return (
        0 <= cw1 <= 20
        and 0 <= cw2 <= 20
        and 0 <= cw3 <= 20
        and 0 <= exam <= 100
    )


def ask_int(title, prompt):
    # return None if the user cancels or enters non-numeric text
    raw = simpledialog.askstring(title, prompt)
    if raw is None:
        return None
    try:
        return int(raw.strip())
    except ValueError:
        messagebox.showinfo("Invalid Input", "Please enter a whole number.")
        return None


def view_all():
    if not has_records():
        return

    body = "".join(format_student(s) for s in students)
    avg = sum(percentage(s) for s in students) / len(students)
    show_output(f"{body}\nStudents: {len(students)}  |  Class Average: {avg:.1f}%")


def view_one():
    if not has_records():
        return

    query = simpledialog.askstring("Individual Student", "Enter student name or ID:")
    if not query:
        return

    found = find_student(query)
    if found:
        show_output(format_student(found))
    else:
        messagebox.showinfo("Not Found", "No matching student found.")


def show_highest():
    if not has_records():
        return
    top = max(students, key=total_marks)  # pick highest total marks out of 160
    show_output("HIGHEST SCORE\n\n" + format_student(top))


def show_lowest():
    if not has_records():
        return
    low = min(students, key=total_marks)  # pick lowest total marks out of 160
    show_output("LOWEST SCORE\n\n" + format_student(low))


def sort_students():
    if not has_records():
        return

    direction = simpledialog.askstring("Sort Records", "Sort order ('asc' or 'desc'):")
    if not direction:
        return

    direction = direction.strip().lower()
    # create a new sorted list so the main students list order isn't changed unexpectedly
    if direction == "asc":
        ordered = sorted(students, key=percentage)
    elif direction == "desc":
        ordered = sorted(students, key=percentage, reverse=True)
    else:
        messagebox.showinfo("Invalid Choice", "Please enter 'asc' or 'desc'.")
        return

    body = "".join(format_student(s) for s in ordered)
    show_output(f"SORTED BY PERCENTAGE ({direction.upper()})\n\n{body}")


def add_student():
    code = ask_int("Add Student", "Student ID:")
    if code is None:
        return
    if duplicate_code(code):  # prevent two students from sharing the same ID
        messagebox.showinfo("Duplicate ID", f"Student ID {code} is already in use.")
        return

    name = simpledialog.askstring("Add Student", "Student full name:")
    if not name or not name.strip():
        return

    cw1 = ask_int("Add Student", "Coursework 1 (0-20):")
    cw2 = ask_int("Add Student", "Coursework 2 (0-20):")
    cw3 = ask_int("Add Student", "Coursework 3 (0-20):")
    exam = ask_int("Add Student", "Exam mark (0-100):")
    if None in (cw1, cw2, cw3, exam):
        return

    if not valid_marks(cw1, cw2, cw3, exam):
        messagebox.showinfo("Invalid Marks", "Coursework must be 0-20 and exam must be 0-100.")
        return

    new_record = {
        "code": code,
        "name": name.strip(),
        "cw1": cw1,
        "cw2": cw2,
        "cw3": cw3,
        "exam": exam,
    }
    students.append(new_record)
    save_students()  # save straight to studentMarks.txt so new data persists
    show_output("Student added and saved:\n\n" + format_student(new_record))


def delete_student():
    if not has_records():
        return

    query = simpledialog.askstring("Delete Student", "Enter student name or ID to delete:")
    if not query:
        return

    found = find_student(query)
    if not found:
        messagebox.showinfo("Not Found", "No matching student found.")
        return

    # ask before deleting so a mistyped ID or accidental click doesn't wipe a record
    ok = messagebox.askyesno(
        "Confirm Delete",
        f"Delete {found['name']} (ID: {found['code']})?"
    )
    if not ok:
        return

    students.remove(found)
    save_students()
    show_output(f"Removed {found['name']} ({found['code']}) and updated studentMarks.txt.")


def update_student():
    if not has_records():
        return

    query = simpledialog.askstring("Update Student", "Enter student name or ID to update:")
    if not query:
        return

    found = find_student(query)
    if not found:
        messagebox.showinfo("Not Found", "No matching student found.")
        return

    field = simpledialog.askstring(
        "Update Field",
        "Field to update (name, code, cw1, cw2, cw3, exam):"
    )
    if not field:
        return

    field = field.strip().lower()
    if field == "name":
        new_name = simpledialog.askstring("Update Name", "Enter new name:")
        if not new_name or not new_name.strip():
            return
        found["name"] = new_name.strip()
    elif field in ("code", "cw1", "cw2", "cw3", "exam"):
        new_num = ask_int("Update Value", f"New value for {field}:")
        if new_num is None:
            return
        if field == "code" and duplicate_code(new_num, ignore_student=found):
            messagebox.showinfo("Duplicate ID", f"Student ID {new_num} is already in use.")
            return
        if field in ("cw1", "cw2", "cw3") and not (0 <= new_num <= 20):
            messagebox.showinfo("Invalid Mark", "Coursework must be between 0 and 20.")
            return
        if field == "exam" and not (0 <= new_num <= 100):
            messagebox.showinfo("Invalid Mark", "Exam mark must be between 0 and 100.")
            return
        found[field] = new_num
    else:
        messagebox.showinfo("Invalid Field", "Use name, code, cw1, cw2, cw3, or exam.")
        return

    save_students()
    show_output("Student updated and saved:\n\n" + format_student(found))


def grade_summary():
    if not has_records():
        return

    grades = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    passes = 0
    for s in students:
        pct = percentage(s)
        grades[grade_for(pct)] += 1
        if pct >= 40:
            passes += 1

    pass_pct = (passes / len(students)) * 100
    summary = (
        "GRADE BREAKDOWN\n"
        f"{'-' * 46}\n"
        f"A (70%+): {grades['A']}   |   B (60-69%): {grades['B']}   |   C (50-59%): {grades['C']}\n"
        f"D (40-49%): {grades['D']}   |   F (<40%): {grades['F']}\n"
        f"{'-' * 46}\n"
        f"Passed (>=40%): {passes}/{len(students)} ({pass_pct:.1f}%)"
    )
    show_output(summary)


def filter_grade():
    if not has_records():
        return

    target = simpledialog.askstring("Filter by Grade", "Enter grade (A, B, C, D, or F):")
    if not target:
        return

    target = target.strip().upper()
    if target not in ("A", "B", "C", "D", "F"):
        messagebox.showinfo("Invalid Grade", "Please enter A, B, C, D, or F.")
        return

    matches = [s for s in students if grade_for(percentage(s)) == target]
    if not matches:
        show_output(f"No students have Grade {target}.")
        return

    body = "".join(format_student(s) for s in matches)
    show_output(f"GRADE {target} STUDENTS ({len(matches)}/{len(students)})\n\n{body}")


def view_raw_file():
    # show the raw text file contents directly without modifying loaded records
    if not os.path.exists(file_path):
        messagebox.showwarning("Missing File", f"Could not find {file_path}.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()

    show_output(f"RAW FILE: studentMarks.txt\n{'-' * 46}\n{raw}")


# main window setup
root = tk.Tk()
root.title("Student Manager")
root.geometry("820x560")
root.configure(bg=BG_COLOR)

top_bar = tk.Frame(root, bg=BG_COLOR)
top_bar.pack(fill="x", padx=14, pady=(12, 6))

tk.Label(
    top_bar,
    text="Student Manager",
    font=("Arial", 16, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR,
).pack(side="left")

tk.Button(
    top_bar,
    text="Hide Records",
    font=("Arial", 9, "bold"),
    bg=HIDE_BTN_COLOR,
    fg=TEXT_COLOR,
    padx=10,
    pady=3,
    command=show_privacy_screen,
).pack(side="right")

count_label = tk.Label(
    top_bar,
    text="Students: 0",
    font=("Arial", 10, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    padx=10,
)
count_label.pack(side="right")

row1 = tk.Frame(root, bg=BG_COLOR)
row1.pack(pady=3)

row2 = tk.Frame(root, bg=BG_COLOR)
row2.pack(pady=(3, 8))

buttons_row1 = [
    ("1. View All", view_all),
    ("2. Individual", view_one),
    ("3. Highest", show_highest),
    ("4. Lowest", show_lowest),
    ("5. Sort", sort_students),
]

buttons_row2 = [
    ("6. Add", add_student),
    ("7. Delete", delete_student),
    ("8. Update", update_student),
    ("9. Grades", grade_summary),
    ("10. Filter Grade", filter_grade),
    ("11. Raw File", view_raw_file),
]

for label, cmd in buttons_row1:
    tk.Button(
        row1,
        text=label,
        font=("Arial", 9, "bold"),
        bg=BTN_COLOR,
        fg=TEXT_COLOR,
        width=14,
        pady=4,
        command=cmd,
    ).pack(side="left", padx=3)

for label, cmd in buttons_row2:
    tk.Button(
        row2,
        text=label,
        font=("Arial", 9, "bold"),
        bg=BTN_COLOR,
        fg=TEXT_COLOR,
        width=12,
        pady=4,
        command=cmd,
    ).pack(side="left", padx=2)

# monospace Consolas keeps '|' dividers and columns lined up cleanly in the output area
text_frame = tk.Frame(root, bg=CARD_COLOR)
text_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side="right", fill="y")

output_box = tk.Text(
    text_frame,
    font=("Consolas", 10),
    bg=CARD_COLOR,
    fg=TEXT_COLOR,
    padx=10,
    pady=10,
    yscrollcommand=scrollbar.set,
)
output_box.pack(side="left", fill="both", expand=True)
scrollbar.config(command=output_box.yview)

load_students()
show_privacy_screen()  # load records into memory but keep them hidden until a button is clicked
root.mainloop()