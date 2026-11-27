import os  # using os so the file path still works if I run from another folder
import tkinter as tk
from tkinter import messagebox, simpledialog

BG_COLOR = "#B8F2F4"
BAR_COLOR = "#E0FBFB"
BOX_COLOR = "#FFFFFF"
TEXT_COLOR = "#0F172A"
BTN_COLOR = "#5EEAD4"
TAB_IDLE = "#CCFBF1"
TAB_ACTIVE = "#2DD4BF"
HIDE_BTN_COLOR = "#FCA5A5"

# getting the path to resources/studentMarks.txt relative to this script
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "resources", "studentMarks.txt")

students = []  # keeping each student as a dict so I can use names like s["exam"]


def load_students():
    students.clear()  # wipe the list first so reloading doesn't stack duplicates
    if not os.path.exists(file_path):  # warn instead of crashing if file isn't there
        messagebox.showwarning("File Missing", f"Can't find {file_path}.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # line 0 is the total count, so I start at index 1 for actual student rows
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) != 6:  # make sure row has all 6 fields before parsing
            continue
        try:
            student = {
                "code": int(parts[0].strip()),
                "name": parts[1].strip(),
                "cw1": int(parts[2].strip()),
                "cw2": int(parts[3].strip()),
                "cw3": int(parts[4].strip()),
                "exam": int(parts[5].strip()),
            }
            students.append(student)
        except ValueError:
            continue  # skip bad lines instead of crashing when the app starts

    refresh_count()


def save_students():
    # put the student count on the first line, then write each student below it
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"{len(students)}\n")
        for s in students:
            f.write(f"{s['code']},{s['name']},{s['cw1']},{s['cw2']},{s['cw3']},{s['exam']}\n")
    refresh_count()  # keep the sidebar count synced after saving


def refresh_count():
    count_label.config(text=f"Total: {len(students)}")


def cw_total(s):
    return s["cw1"] + s["cw2"] + s["cw3"]  # three coursework pieces out of 20 = 60


def total_marks(s):
    return cw_total(s) + s["exam"]  # 60 coursework + 100 exam = 160 total marks


def percentage(s):
    return (total_marks(s) / 160) * 100  # turn total out of 160 into a percentage


def grade_for(pct):
    # checking from highest boundary down so it hits the right grade
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
    # keeping one format function so every view prints students the same way
    pct = percentage(s)
    return (
        f"Name: {s['name']}  |  ID: {s['code']}\n"
        f"Coursework: {cw_total(s)}/60  |  Exam: {s['exam']}/100\n"
        f"Total: {total_marks(s)}/160  |  {pct:.1f}%  |  Grade: {grade_for(pct)}\n"
        f"{'-' * 46}\n"
    )


def show_output(text):
    # clearing old output first so new results don't get stuck below old ones
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, text)


def hide_records():
    # hiding marks at startup and on Hide so data isn't just sitting on screen
    show_output("Marks hidden.\n\nPick a section on the left to view or edit records.")


def find_student(query):
    clean = query.strip().lower()  # lowercasing and trimming so search is forgiving
    for s in students:
        if str(s["code"]) == clean or s["name"].lower() == clean:
            return s
    return None  # return None if no match so caller can show a message


def duplicate_code(code, ignore_student=None):
    # ignoring the current student when updating so they can keep their own ID
    for s in students:
        if s is not ignore_student and s["code"] == code:
            return True
    return False


def open_tab(tab_name):
    # hiding all three bars first, then showing whichever tab I picked
    views_bar.pack_forget()
    records_bar.pack_forget()
    tools_bar.pack_forget()

    tab_views_btn.config(bg=TAB_IDLE)
    tab_records_btn.config(bg=TAB_IDLE)
    tab_tools_btn.config(bg=TAB_IDLE)

    # show matching action bar and highlight that tab button
    if tab_name == "views":
        views_bar.pack(fill="x", pady=(0, 8))
        tab_views_btn.config(bg=TAB_ACTIVE)
    elif tab_name == "records":
        records_bar.pack(fill="x", pady=(0, 8))
        tab_records_btn.config(bg=TAB_ACTIVE)
    elif tab_name == "tools":
        tools_bar.pack(fill="x", pady=(0, 8))
        tab_tools_btn.config(bg=TAB_ACTIVE)


def view_all():
    if not students:  # stop early if there are no records loaded
        show_output("No students in list yet.")
        return

    # loop through everyone to build the text and add up percentages for the average
    body = ""
    pct_sum = 0
    for s in students:
        body += format_student(s)
        pct_sum += percentage(s)

    avg = pct_sum / len(students)
    show_output(f"{body}\n{len(students)} students  |  Average: {avg:.1f}%")


def view_one():
    if not students:
        show_output("No students in list yet.")
        return

    query = simpledialog.askstring("Find Student", "Name or ID:")
    if not query:
        return  # user cancelled or left it blank

    found = find_student(query)
    if found:
        show_output(format_student(found))
    else:
        messagebox.showinfo("Not Found", "Couldn't find that student.")


def show_highest():
    if not students:
        show_output("No students in list yet.")
        return

    top = max(students, key=total_marks)  # compare by total marks out of 160
    show_output("Top Score\n\n" + format_student(top))


def show_lowest():
    if not students:
        show_output("No students in list yet.")
        return

    low = min(students, key=total_marks)  # compare by total marks out of 160
    show_output("Lowest Score\n\n" + format_student(low))


def sort_students():
    if not students:
        show_output("No students in list yet.")
        return

    direction = simpledialog.askstring("Sort", "Type 'asc' or 'desc':")
    if not direction:
        return  # stop if cancelled or empty

    direction = direction.strip().lower()
    # sorted() returns a new list so I don't mess up the loaded order in students
    if direction == "asc":
        ordered = sorted(students, key=percentage)
    elif direction == "desc":
        ordered = sorted(students, key=percentage, reverse=True)
    else:
        messagebox.showinfo("Check Input", "Type 'asc' or 'desc'.")
        return

    body = ""
    for s in ordered:
        body += format_student(s)
    show_output(f"Sorted ({direction})\n\n{body}")


def add_student():
    # catch non-numbers or cancelled popups before trying int()
    try:
        code = int(simpledialog.askstring("Add Student", "Student ID:"))
        name = simpledialog.askstring("Add Student", "Full name:")
        cw1 = int(simpledialog.askstring("Add Student", "Coursework 1 (0-20):"))
        cw2 = int(simpledialog.askstring("Add Student", "Coursework 2 (0-20):"))
        cw3 = int(simpledialog.askstring("Add Student", "Coursework 3 (0-20):"))
        exam = int(simpledialog.askstring("Add Student", "Exam mark (0-100):"))
    except (ValueError, TypeError):
        messagebox.showinfo("Check Input", "Enter whole numbers for ID and marks.")
        return

    if not name or not name.strip():  # bail out if name is blank
        return

    if duplicate_code(code):  # don't let two students share an ID
        messagebox.showinfo("ID Taken", f"ID {code} is already used.")
        return

    # keep coursework in 0-20 and exam in 0-100
    if not (0 <= cw1 <= 20 and 0 <= cw2 <= 20 and 0 <= cw3 <= 20 and 0 <= exam <= 100):
        messagebox.showinfo("Check Marks", "Coursework must be 0-20 and exam must be 0-100.")
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
    save_students()  # write straight to the file so changes aren't lost
    show_output("Saved new student:\n\n" + format_student(new_record))


def delete_student():
    if not students:
        show_output("No students in list yet.")
        return

    query = simpledialog.askstring("Delete Student", "Name or ID to remove:")
    if not query:
        return  # stop if cancelled or empty

    found = find_student(query)
    if not found:
        messagebox.showinfo("Not Found", "Couldn't find that student.")
        return

    # pop up a yes/no check first so I don't delete someone by mistake
    ok = messagebox.askyesno("Delete?", f"Remove {found['name']} ({found['code']})?")
    if not ok:
        return

    students.remove(found)
    save_students()  # update the file after removing the record
    show_output(f"Removed {found['name']} ({found['code']}).")


def update_student():
    if not students:
        show_output("No students in list yet.")
        return

    query = simpledialog.askstring("Update Student", "Name or ID to edit:")
    if not query:
        return  # stop if cancelled or empty

    found = find_student(query)
    if not found:
        messagebox.showinfo("Not Found", "Couldn't find that student.")
        return

    field = simpledialog.askstring(
        "Edit Field",
        "Which field? (name, code, cw1, cw2, cw3, exam)"
    )
    if not field:
        return

    field = field.strip().lower()
    # handle text name separately from numeric ID and marks
    if field == "name":
        new_name = simpledialog.askstring("Edit Name", "New name:")
        if not new_name or not new_name.strip():
            return
        found["name"] = new_name.strip()
    elif field in ("code", "cw1", "cw2", "cw3", "exam"):
        raw_num = simpledialog.askstring("Edit Value", f"New {field}:")
        if raw_num is None:  # user hit Cancel
            return
        try:
            new_num = int(raw_num.strip())
        except ValueError:
            messagebox.showinfo("Check Input", "Enter a whole number.")
            return

        # check rules for whichever field I'm changing
        if field == "code" and duplicate_code(new_num, ignore_student=found):
            messagebox.showinfo("ID Taken", f"ID {new_num} is already used.")
            return
        if field in ("cw1", "cw2", "cw3") and not (0 <= new_num <= 20):
            messagebox.showinfo("Check Mark", "Coursework must be between 0 and 20.")
            return
        if field == "exam" and not (0 <= new_num <= 100):
            messagebox.showinfo("Check Mark", "Exam mark must be between 0 and 100.")
            return
        found[field] = new_num
    else:
        messagebox.showinfo("Unknown Field", "Use name, code, cw1, cw2, cw3, or exam.")
        return

    save_students()  # save updated value back to studentMarks.txt
    show_output("Updated:\n\n" + format_student(found))


def grade_summary():
    if not students:
        show_output("No students in list yet.")
        return

    # tally each grade and count passes (40% or higher)
    grades = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    passes = 0
    for s in students:
        pct = percentage(s)
        grades[grade_for(pct)] += 1
        if pct >= 40:
            passes += 1

    pass_pct = (passes / len(students)) * 100
    summary = (
        "Grade Counts\n"
        f"{'-' * 46}\n"
        f"A (70%+): {grades['A']}   |   B (60-69%): {grades['B']}   |   C (50-59%): {grades['C']}\n"
        f"D (40-49%): {grades['D']}   |   F (<40%): {grades['F']}\n"
        f"{'-' * 46}\n"
        f"Pass (>=40%): {passes}/{len(students)} ({pass_pct:.1f}%)"
    )
    show_output(summary)


def filter_grade():
    if not students:
        show_output("No students in list yet.")
        return

    target = simpledialog.askstring("Filter Grade", "Grade (A, B, C, D, or F):")
    if not target:
        return  # stop if cancelled or empty

    target = target.strip().upper()
    if target not in ("A", "B", "C", "D", "F"):  # reject anything outside valid letter grades
        messagebox.showinfo("Check Grade", "Enter A, B, C, D, or F.")
        return

    # collect only students whose grade matches what was typed
    matches = []
    for s in students:
        if grade_for(percentage(s)) == target:
            matches.append(s)

    if not matches:
        show_output(f"No students with grade {target}.")
        return

    body = ""
    for s in matches:
        body += format_student(s)
    show_output(f"Grade {target} ({len(matches)}/{len(students)})\n\n{body}")


def view_raw_file():
    # reading the raw file directly just to check what's saved on disk
    if not os.path.exists(file_path):
        messagebox.showwarning("File Missing", f"Can't find {file_path}.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()

    show_output(f"studentMarks.txt\n{'-' * 46}\n{raw}")


root = tk.Tk()
root.title("Student Manager")
root.geometry("860x560")
root.minsize(720, 460)  # keeping a min size so the top buttons don't get squished off-screen
root.configure(bg=BG_COLOR)

# left sidebar holds the title, total count, section tabs, and Hide button
side_nav = tk.Frame(root, bg=BAR_COLOR, width=165)
side_nav.pack(side="left", fill="y", padx=(12, 6), pady=12)
side_nav.pack_propagate(False)  # stop frame shrinking to fit labels/buttons

tk.Label(
    side_nav,
    text="Student Manager",
    font=("Arial", 13, "bold"),
    bg=BAR_COLOR,
    fg=TEXT_COLOR,
).pack(anchor="w", padx=10, pady=(12, 2))

count_label = tk.Label(
    side_nav,
    text="Total: 0",
    font=("Arial", 9, "bold"),
    bg=BAR_COLOR,
    fg=TEXT_COLOR,
)
count_label.pack(anchor="w", padx=10, pady=(0, 12))

tab_views_btn = tk.Button(
    side_nav,
    text="Views",
    font=("Arial", 9, "bold"),
    bg=TAB_ACTIVE,
    fg=TEXT_COLOR,
    anchor="w",
    padx=10,
    pady=5,
    command=lambda: open_tab("views"),
)
tab_views_btn.pack(fill="x", padx=10, pady=3)

tab_records_btn = tk.Button(
    side_nav,
    text="Records",
    font=("Arial", 9, "bold"),
    bg=TAB_IDLE,
    fg=TEXT_COLOR,
    anchor="w",
    padx=10,
    pady=5,
    command=lambda: open_tab("records"),
)
tab_records_btn.pack(fill="x", padx=10, pady=3)

tab_tools_btn = tk.Button(
    side_nav,
    text="Grades & File",
    font=("Arial", 9, "bold"),
    bg=TAB_IDLE,
    fg=TEXT_COLOR,
    anchor="w",
    padx=10,
    pady=5,
    command=lambda: open_tab("tools"),
)
tab_tools_btn.pack(fill="x", padx=10, pady=3)

tk.Button(
    side_nav,
    text="Hide",
    font=("Arial", 9, "bold"),
    bg=HIDE_BTN_COLOR,
    fg=TEXT_COLOR,
    padx=10,
    pady=4,
    command=hide_records,
).pack(side="bottom", fill="x", padx=10, pady=(4, 12))

# right panel stays pinned at the top for buttons, with the text box taking the rest of the space
main_area = tk.Frame(root, bg=BG_COLOR)
main_area.pack(side="right", fill="both", expand=True, padx=(6, 12), pady=12)

views_bar = tk.Frame(main_area, bg=BAR_COLOR, padx=8, pady=8)
tk.Button(views_bar, text="1. View All", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=11, pady=4, command=view_all).pack(side="left", padx=2)
tk.Button(views_bar, text="2. Individual", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=11, pady=4, command=view_one).pack(side="left", padx=2)
tk.Button(views_bar, text="3. Highest", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=11, pady=4, command=show_highest).pack(side="left", padx=2)
tk.Button(views_bar, text="4. Lowest", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=11, pady=4, command=show_lowest).pack(side="left", padx=2)
tk.Button(views_bar, text="5. Sort", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=11, pady=4, command=sort_students).pack(side="left", padx=2)

records_bar = tk.Frame(main_area, bg=BAR_COLOR, padx=8, pady=8)
tk.Button(records_bar, text="6. Add", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=14, pady=4, command=add_student).pack(side="left", padx=4)
tk.Button(records_bar, text="7. Delete", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=14, pady=4, command=delete_student).pack(side="left", padx=4)
tk.Button(records_bar, text="8. Update", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=14, pady=4, command=update_student).pack(side="left", padx=4)

tools_bar = tk.Frame(main_area, bg=BAR_COLOR, padx=8, pady=8)
tk.Button(tools_bar, text="9. Grades", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=14, pady=4, command=grade_summary).pack(side="left", padx=4)
tk.Button(tools_bar, text="10. Filter Grade", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=14, pady=4, command=filter_grade).pack(side="left", padx=4)
tk.Button(tools_bar, text="11. Raw File", font=("Arial", 9, "bold"), bg=BTN_COLOR, fg=TEXT_COLOR, width=14, pady=4, command=view_raw_file).pack(side="left", padx=4)

views_bar.pack(fill="x", pady=(0, 8))  # start on Views tab so buttons are ready right away

# Consolas keeps the '|' dividers lined up cleanly
text_frame = tk.Frame(main_area, bg=BOX_COLOR)
text_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side="right", fill="y")

output_box = tk.Text(
    text_frame,
    font=("Consolas", 10),
    bg=BOX_COLOR,
    fg=TEXT_COLOR,
    padx=10,
    pady=10,
    yscrollcommand=scrollbar.set,
)
output_box.pack(side="left", fill="both", expand=True)
scrollbar.config(command=output_box.yview)

load_students()  # load records into memory on startup
hide_records()  # keep marks hidden until a view/edit button is clicked
root.mainloop()