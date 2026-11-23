import random
import tkinter as tk
from tkinter import messagebox

BG_COLOR = "#E8F6FF"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#16324F"
EASY_COLOR = "#C7F2A4"
MOD_COLOR = "#AEE6FF"
ADV_COLOR = "#FFE599"
SUBMIT_COLOR = "#9BE7FF"

# keeps track of where we are in the round, the score, and the current sum
difficulty = "Easy"
question_num = 0
total_questions = 10  # 10 questions per round
score = 0
attempt = 1
num1 = 0
num2 = 0
operation = "+"
correct_answer = 0


def randomInt(min_val, max_val):
    # randint includes both ends, so randomInt(1, 9) actually allows 1 and 9
    return random.randint(min_val, max_val)


def decideOperation():
    # picks + or - at random for each question
    return random.choice(["+", "-"])


def isCorrect(user_ans):
    global score, attempt

    if user_ans == correct_answer:
        if attempt == 1:
            score += 10  # full marks on the first try
            messagebox.showinfo("Correct!", "Nice job! Right on the 1st try (+10 points).")
        else:
            score += 5  # half marks if they get it on the second try
            messagebox.showinfo("Correct!", "Good save! Right on the 2nd try (+5 points).")
        next_question()
    else:
        if attempt == 1:
            # give them one more shot on this same question before moving on
            attempt = 2
            feedback_label.config(text="Not quite! Try one more time (5 points).", fg="#B45309")
            answer_entry.delete(0, tk.END)
        else:
            # already missed twice, so show the right answer and move to the next one
            messagebox.showinfo("Wrong", f"Out of tries! The answer was {correct_answer}.")
            next_question()


def displayProblem(first_num, op, second_num):
    problem_label.config(text=f"{first_num} {op} {second_num} =")
    answer_entry.delete(0, tk.END)  # clear the input box so the old answer isn't left behind


def next_question():
    global question_num, attempt, num1, num2, operation, correct_answer

    # once 10 questions have been asked, wrap up and show the final score/grade
    if question_num >= total_questions:
        displayResults()
        return

    question_num += 1
    attempt = 1  # reset back to attempt 1 for the new question

    # set number ranges based on the difficulty button the user clicked
    if difficulty == "Easy":
        low, high = 1, 9
    elif difficulty == "Moderate":
        low, high = 10, 99
    else:
        low, high = 1000, 9999

    num1 = randomInt(low, high)
    num2 = randomInt(low, high)
    operation = decideOperation()

    if operation == "+":
        correct_answer = num1 + num2
    else:
        # subtraction can give negative answers, especially in Moderate and Advanced
        correct_answer = num1 - num2

    info_label.config(text=f"Question {question_num} of {total_questions}   |   Score: {score}")
    feedback_label.config(text="Type your answer and click Submit.", fg=TEXT_COLOR)
    displayProblem(num1, operation, num2)
def submit_answer():
    text = answer_entry.get().strip()
    # lstrip("-") lets negative numbers like -15 pass isdigit() without int() crashing
    if text.lstrip("-").isdigit():
        isCorrect(int(text))
    else:
        feedback_label.config(text="Please enter a whole number.", fg="#B91C1C")


def displayResults():
    # work out the grade from the score out of 100
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
        "Quiz Results",
        f"Final Score: {score} / 100\nGrade: {grade}\n\nWould you like to play again?"
    )

    if play_again:
        displayMenu()
    else:
        root.destroy()


def start_quiz(chosen_level):
    global difficulty, score, question_num
    difficulty = chosen_level
    score = 0
    question_num = 0

    # switch from the menu frame to the quiz frame in the same window
    menu_frame.pack_forget()
    quiz_frame.pack(pady=18, padx=24, fill="both")
    next_question()


def displayMenu():
    quiz_frame.pack_forget()
    menu_frame.pack(pady=20, padx=24, fill="both")

