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
