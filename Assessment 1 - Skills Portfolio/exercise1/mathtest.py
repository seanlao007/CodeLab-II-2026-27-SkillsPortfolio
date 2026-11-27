import random
import tkinter as tk
from tkinter import messagebox

BG_COLOR = "#FFF0F6"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#2B2D42"
EASY_COLOR = "#D8F3DC"
MOD_COLOR = "#CAF0F8"
ADV_COLOR = "#FFE5B4"
SUBMIT_COLOR = "#BDE0FE"

UI_FONT = "Helvetica"
TITLE_FONT = "Times"
NUM_FONT = "Courier"

difficulty = "Easy"
question_num = 0
total_questions = 10
score = 0
attempt = 1
num1 = 0
num2 = 0
operation = "+"
correct_answer = 0
time_left = 15
timer_id = None  # save after() id so I can cancel or reset the timer cleanly


def get_random_number(min_val, max_val):
    # randint includes both ends so min and max values can show up
    return random.randint(min_val, max_val)


def pick_operation():
    return random.choice(["+", "-"])  # only plus or minus in this quiz


def get_max_time():
    # extra 5s per level: 15s easy, 20s moderate, 30s advanced
    if difficulty == "Easy":
        return 15
    if difficulty == "Moderate":
        return 20
    return 30


def stop_timer():
    global timer_id
    # cancel any active countdown so old timers don't stack or run double speed
    if timer_id is not None:
        root.after_cancel(timer_id)
        timer_id = None


def tick_timer():
    global time_left, timer_id, attempt

    timer_label.config(text=f"Time left: {time_left}s")

    if time_left <= 0:  # countdown hit zero
        timer_id = None
        if attempt == 1:
            # reset back to this difficulty's max timer for a second try at 5 points
            attempt = 2
            time_left = get_max_time()
            feedback_label.config(text=f"Time's up on try 1! Last chance ({time_left}s, 5 pts).", fg="#B45309")
            answer_entry.delete(0, tk.END)
            tick_timer()
        else:
            # out of time on the second try too, so move on
            messagebox.showinfo("Time's Up!", f"Out of time! Answer was {correct_answer}.")
            next_question()
        return

    time_left -= 1
    timer_id = root.after(1000, tick_timer)  # schedule next tick in 1s without blocking UI


def check_answer(user_ans):
    global score, attempt

    stop_timer()  # pause countdown while checking the answer

    if user_ans == correct_answer:
        if attempt == 1:
            score += 10  # full points on first try
            messagebox.showinfo("Nice!", "Right on the 1st try! +10 pts")
        else:
            score += 5  # half points on second try
            messagebox.showinfo("Clutch!", "Got it on the 2nd try! +5 pts")
        next_question()
    else:
        if attempt == 1:
            # wrong on first try, so restart this level's timer for one last shot at 5 points
            attempt = 2
            time_left = get_max_time()
            feedback_label.config(text="Nope, try again! (5 pts)", fg="#B45309")
            answer_entry.delete(0, tk.END)
            answer_entry.focus_set()
            tick_timer()
        else:
            messagebox.showinfo("Wrong", f"No luck! The answer was {correct_answer}.")
            next_question()


def show_problem(first_num, op, second_num):
    problem_label.config(text=f"{first_num} {op} {second_num} =")
    answer_entry.delete(0, tk.END)
    answer_entry.focus_set()  # focus input box so I can type right away


def next_question():
    global question_num, attempt, num1, num2, operation, correct_answer, time_left

    stop_timer()

    if question_num >= total_questions:  # finished all 10 questions
        show_results()
        return

    question_num += 1
    attempt = 1  # reset back to first attempt for the new question
    time_left = get_max_time()  # use max timer for current difficulty

    # pick number range based on chosen difficulty
    if difficulty == "Easy":
        low, high = 1, 9
    elif difficulty == "Moderate":
        low, high = 10, 99
    else:
        low, high = 1000, 9999

    num1 = get_random_number(low, high)
    num2 = get_random_number(low, high)
    operation = pick_operation()

    if operation == "+":
        correct_answer = num1 + num2
    else:
        # allow negative results when subtracting
        correct_answer = num1 - num2

    info_label.config(text=f"Q {question_num}/{total_questions}  |  Score: {score}")
    feedback_label.config(text="Type your answer and hit Enter or Submit.", fg=TEXT_COLOR)
    show_problem(num1, operation, num2)
    tick_timer()  # start timer for this question


def submit_answer():
    text = answer_entry.get().strip()
    # strip a leading minus sign so negative numbers pass isdigit()
    if text.lstrip("-").isdigit():
        check_answer(int(text))
    else:
        feedback_label.config(text="Whole numbers only please!", fg="#B91C1C")


def show_results():
    stop_timer()

    # grade boundaries out of 100 max points
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "D"

    play_again = messagebox.askyesno(
        "Results",
        f"Score: {score} / 100\nGrade: {grade}\n\nPlay another round?"
    )

    if play_again:
        show_menu()  # go back to difficulty menu for another round
    else:
        root.destroy()


def start_quiz(chosen_level):
    global difficulty, score, question_num
    # reset round stats before starting
    difficulty = chosen_level
    score = 0
    question_num = 0

    # switch from menu frame to quiz frame in the same window
    menu_frame.pack_forget()
    quiz_frame.pack(pady=18, padx=22, fill="both", expand=True)
    next_question()


def show_menu():
    stop_timer()  # stop clock if going back to menu mid-round
    quiz_frame.pack_forget()
    menu_frame.pack(pady=20, padx=22, fill="both", expand=True)


# main window setup
root = tk.Tk()
root.title("Maths Quiz")
root.geometry("430x340")
root.configure(bg=BG_COLOR)

# menu screen for picking difficulty
menu_frame = tk.Frame(root, bg=CARD_COLOR, padx=16, pady=16)
tk.Label(menu_frame, text="MATHS QUIZ", font=(TITLE_FONT, 17, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR).pack(pady=(0, 4))
tk.Label(menu_frame, text="10 questions • Easy 15s / Mod 20s / Adv 30s • +10 / +5 pts", font=(UI_FONT, 9), bg=CARD_COLOR, fg="#64748B").pack(pady=(0, 12))

# lambda delays start_quiz until the button is actually clicked
tk.Button(menu_frame, text="1. Easy", font=(UI_FONT, 10, "bold"), bg=EASY_COLOR, fg=TEXT_COLOR, width=18, command=lambda: start_quiz("Easy")).pack(pady=4)
tk.Button(menu_frame, text="2. Moderate", font=(UI_FONT, 10, "bold"), bg=MOD_COLOR, fg=TEXT_COLOR, width=18, command=lambda: start_quiz("Moderate")).pack(pady=4)
tk.Button(menu_frame, text="3. Advanced", font=(UI_FONT, 10, "bold"), bg=ADV_COLOR, fg=TEXT_COLOR, width=18, command=lambda: start_quiz("Advanced")).pack(pady=4)

# quiz screen where questions, timer, and input live
quiz_frame = tk.Frame(root, bg=CARD_COLOR, padx=16, pady=16)

top_row = tk.Frame(quiz_frame, bg=CARD_COLOR)
top_row.pack(fill="x", pady=(0, 6))
info_label = tk.Label(top_row, text="", font=(UI_FONT, 10, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
info_label.pack(side="left")
timer_label = tk.Label(top_row, text="Time left: 15s", font=(NUM_FONT, 10, "bold"), bg=CARD_COLOR, fg="#DC2626")
timer_label.pack(side="right")

problem_label = tk.Label(quiz_frame, text="", font=(NUM_FONT, 20, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
problem_label.pack(pady=8)

answer_entry = tk.Entry(quiz_frame, font=(NUM_FONT, 12, "bold"), justify="center", width=12, bg="#F8FAFC", fg=TEXT_COLOR)
answer_entry.pack(pady=6)
answer_entry.bind("<Return>", lambda event: submit_answer())  # submit when pressing Enter

btn_row = tk.Frame(quiz_frame, bg=CARD_COLOR)
btn_row.pack(pady=8)
tk.Button(btn_row, text="Submit", font=(UI_FONT, 10, "bold"), bg=SUBMIT_COLOR, fg=TEXT_COLOR, width=12, command=submit_answer).pack(side="left", padx=4)
tk.Button(btn_row, text="Menu", font=(UI_FONT, 10), bg="#F1F5F9", fg=TEXT_COLOR, width=8, command=show_menu).pack(side="left", padx=4)

feedback_label = tk.Label(quiz_frame, text="", font=(UI_FONT, 9), bg=CARD_COLOR, fg=TEXT_COLOR)
feedback_label.pack(pady=(4, 0))

show_menu()  # start on the difficulty menu
root.mainloop()  # keep the app window open