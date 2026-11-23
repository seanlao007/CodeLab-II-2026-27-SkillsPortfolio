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


def save_students():
    # overwrite the file with the updated count and current list of students
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"{len(students)}\n")  # keep line 1 matching how many students are stored
        for s in students:
            f.write(f"{s['code']},{s['name']},{s['cw1']},{s['cw2']},{s['cw3']},{s['exam']}\n")


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


def sort_records():
    if not students:
        show_text("No student records found.")
        return

    order = simpledialog.askstring("Sort Records", "Type 'asc' or 'desc':")
    if not order:
        return

    order = order.strip().lower()
    # make a new sorted copy so we don't scramble the original students list order
    if order == "asc":
        sorted_list = sorted(students, key=get_percentage)
    elif order == "desc":
        sorted_list = sorted(students, key=get_percentage, reverse=True)
    else:
        messagebox.showinfo("Invalid Choice", "Please type 'asc' or 'desc'.")
        return

    text = f"SORTED RECORDS ({order.upper()})\n\n"
    total_pct = 0
    for s in sorted_list:
        text += format_student(s)
        total_pct += get_percentage(s)

    avg_pct = total_pct / len(sorted_list)
    text += f"\nSUMMARY -> Total Students: {len(sorted_list)}  |  Average Percentage: {avg_pct:.1f}%"
    show_text(text)


def add_student():
    # catch ValueError if they type letters for numbers, and TypeError if they hit Cancel
    try:
        code = int(simpledialog.askstring("Add Student", "Student code:"))
        name = simpledialog.askstring("Add Student", "Student full name:")
        cw1 = int(simpledialog.askstring("Add Student", "Coursework 1 (out of 20):"))
        cw2 = int(simpledialog.askstring("Add Student", "Coursework 2 (out of 20):"))
        cw3 = int(simpledialog.askstring("Add Student", "Coursework 3 (out of 20):"))
        exam = int(simpledialog.askstring("Add Student", "Exam mark (out of 100):"))
    except (ValueError, TypeError):
        messagebox.showinfo("Invalid Input", "Please enter valid numbers and don't leave blanks.")
        return

    if not name or not name.strip():
        return

    # keep coursework marks in 0..20 and exam marks in 0..100
    if not (0 <= cw1 <= 20 and 0 <= cw2 <= 20 and 0 <= cw3 <= 20 and 0 <= exam <= 100):
        messagebox.showinfo("Invalid Marks", "Coursework marks must be 0-20 and exam mark must be 0-100.")
        return

    new_student = {
        "code": code,
        "name": name.strip(),
        "cw1": cw1,
        "cw2": cw2,
        "cw3": cw3,
        "exam": exam,
    }
    students.append(new_student)
    save_students()  # write the new record straight to the text file
    show_text("Added new student and saved to studentMarks.txt:\n\n" + format_student(new_student))


def delete_student():
    choice = simpledialog.askstring("Delete Student", "Enter student name or number to delete:")
    if not choice:
        return

    found = find_student(choice)
    if not found:
        messagebox.showinfo("Not Found", "No matching student found.")
        return

    students.remove(found)
    save_students()  # update the text file so the deleted student stays gone
    show_text(f"Deleted record for {found['name']} ({found['code']}) and saved to studentMarks.txt.")


def update_student():
    choice = simpledialog.askstring("Update Student", "Enter student name or number to update:")
    if not choice:
        return

    found = find_student(choice)
    if not found:
        messagebox.showinfo("Not Found", "No matching student found.")
        return

    field = simpledialog.askstring(
        "Update Field",
        "Which item do you want to update?\nType: name, code, cw1, cw2, cw3, or exam"
    )
    if not field:
        return

    # match the typed field name to a dict key so only that one value gets changed
    field = field.strip().lower()
    if field == "name":
        new_name = simpledialog.askstring("New Name", "Enter new student name:")
        if new_name and new_name.strip():
            found["name"] = new_name.strip()
        else:
            return
    elif field in ["code", "cw1", "cw2", "cw3", "exam"]:
        try:
            new_val = int(simpledialog.askstring("New Value", f"Enter new value for {field}:"))
        except (ValueError, TypeError):
            messagebox.showinfo("Invalid Input", "Please enter a whole number.")
            return

        # check valid mark limits before saving changes
        if field in ["cw1", "cw2", "cw3"] and not (0 <= new_val <= 20):
            messagebox.showinfo("Invalid Marks", "Coursework marks must be between 0 and 20.")
            return
        if field == "exam" and not (0 <= new_val <= 100):
            messagebox.showinfo("Invalid Marks", "Exam mark must be between 0 and 100.")
            return

        found[field] = new_val
    else:
        messagebox.showinfo("Invalid Field", "Choose name, code, cw1, cw2, cw3, or exam.")
        return

    save_students()  # save the edited value back to studentMarks.txt
    show_text("Updated student record and saved to studentMarks.txt:\n\n" + format_student(found))


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

# second row of buttons for extra features (5 to 8)
ext_row = tk.Frame(root, bg=BG_COLOR)
ext_row.pack(pady=(2, 10))
tk.Button(ext_row, text="5. Sort Records", bg=BTN_COLOR, fg=TEXT_COLOR, width=18, command=sort_records).pack(side="left", padx=3)
tk.Button(ext_row, text="6. Add Student", bg=BTN_COLOR, fg=TEXT_COLOR, width=18, command=add_student).pack(side="left", padx=3)
tk.Button(ext_row, text="7. Delete Student", bg=BTN_COLOR, fg=TEXT_COLOR, width=18, command=delete_student).pack(side="left", padx=3)
tk.Button(ext_row, text="8. Update Student", bg=BTN_COLOR, fg=TEXT_COLOR, width=18, command=update_student).pack(side="left", padx=3)

# main display box for lists, searches, high/low scores, and action messages
output_box = tk.Text(root, width=74, height=18, font=("Consolas", 10), bg=CARD_COLOR, fg=TEXT_COLOR, padx=10, pady=10)
output_box.pack(padx=16, pady=(0, 12))

load_students()
view_all()  # load the text file and show everyone right away when the app opens
root.mainloop()  # keep the GUI running and listening for clicks