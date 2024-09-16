# quiz app                                                                                                                                                                                                                                                                                                                      (regrettably the original comment here has had to be removed)

import tkinter as tk
import os
import sys
import json

class App:
    def __init__(self) -> None:
        #fun
        self.question_button_width = 17
        self.question_button_height = 10
        self.question_button_wraplength = 300

        self.default_font = ("Inter", 20)
        self.decoder = QuestionDecoder()
        self.questions = self.decoder.get_questions()
        self.score = 0
        self.max_score = len(self.questions)
        self.current_question_index = 0
        
        # bit misleading name; the guess_stack is a stack that contains whether the user got the questions right or wrong
        # so if the user got the 1st righht 2nd wrong and the 3rd also wrong it would look like this:
        # [True, False, False]
        self.guess_stack = []
        self.root = tk.Tk() # make the window
        self.root.title("Quiz") # set the title
        self.root.geometry("1920x1080") # set the size
        
        # This is my poor attempt at centering a div in python...
        # This is where I got the idea from: https://www.geeksforgeeks.org/horizontally-center-a-widget-using-tkinter/
        # And also this is the reason some frames are in the 1st column and some in the 0th
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        
        # Pre game
        self.pre_game_frame = tk.Frame(self.root) # frames make your life a bit easier
        self.welcome_label = tk.Label(self.pre_game_frame, font=self.default_font, text="Welcome to the quiz!")
        self.start_button = tk.Button(self.pre_game_frame, font=self.default_font, text="Start", command=self.start)
        
        self.welcome_label.grid(row=0, column=0)
        self.start_button.grid(row=1, column=0)
        self.pre_game_frame.grid(row=0, column=1)
        
        # The game loop
        self.quiz_frame = tk.Frame(self.root)
        self.question_title_label = tk.Label(self.quiz_frame, font=self.default_font, text="")
        self.question_answer_options_frame = tk.Frame(self.quiz_frame)
        self.next_question_button = tk.Button(self.quiz_frame, font=self.default_font, text="Skip", command=self.next)
        self.previous_question_button = tk.Button(self.quiz_frame, font=self.default_font, text="Previous", command=self.previous)
        self.progress_frame = tk.Frame(self.quiz_frame)
        self.score_display_label = tk.Label(self.progress_frame, font=self.default_font, text=f"Score: {self.score}/{self.max_score}")
        self.question_num_display_label = tk.Label(self.progress_frame, font=self.default_font, text=f"Question {self.current_question_index + 1}/{self.max_score}")
        
        self.question_title_label.grid(row=0, column=1)
        self.question_answer_options_frame.grid(row=1, column=1)
        self.previous_question_button.grid(row=0, column=0)
        self.next_question_button.grid(row=0, column=2)
        self.progress_frame.grid(row=2, column=1)
        self.question_num_display_label.grid(row=0, column=0)
        self.score_display_label.grid(row=1, column=0)
        # notice that we're not grid-ing the frame yet, we'll do that in self.start()
        
        # Post game
        self.post_game_frame = tk.Frame(self.root)
        self.game_over_label = tk.Label(self.post_game_frame, font=self.default_font, text="Game Over!")
        self.score_label = tk.Label(self.post_game_frame, font=self.default_font, text="")
        self.play_again_label = tk.Label(self.post_game_frame, font=self.default_font, text="Play again?")
        self.answer_frame = tk.Frame(self.post_game_frame)
        self.play_again_button = tk.Button(self.answer_frame, font=self.default_font, text="Yes", command=self.start)
        self.quit_button = tk.Button(self.answer_frame, font=self.default_font, text="No", command=self.root.quit)
        
        self.game_over_label.grid(row=0, column=0)
        self.score_label.grid(row=1, column=0)
        self.play_again_label.grid(row=2, column=0)
        self.answer_frame.grid(row=3, column=0) 
        self.play_again_button.grid(row=0, column=0, padx=10)
        self.quit_button.grid(row=0, column=1, padx=10)
        
        self.root.mainloop()
    
    def start(self):
        # if we're replaying the game we need to hide the post game frame and reset the stats
        self.post_game_frame.grid_forget() 
        self.score = 0
        self.current_question_index = 0
        
        self.pre_game_frame.grid_forget() # grid_forget() is used to hide the frame; destroy() would delete it altogether with all the grid() information that the widgets inside it had
        self.quiz_frame.grid(row=0, column=0)
        self.display_question()
        
    def display_question(self):
        current_question = self.questions[self.current_question_index]
        question_title = current_question.question
        question_answer_options = current_question.answer_options
        
        self.question_title_label.config(text=question_title)
        self.question_num_display_label.config(text=f"Question {self.current_question_index + 1}/{self.max_score}")
        self.score_display_label.config(text=f"Score: {self.score}/{self.max_score}")
        
        # delete any previous answer options
        self.question_answer_options_frame.destroy()
        self.question_answer_options_frame = tk.Frame(self.quiz_frame) 
        self.question_answer_options_frame.grid(row=1, column=1)
        
        # unnecessary logic to make the answer options appear in 'columns' amount of  columns
        columns = 4 # It's going to be hard coded like this idc
        
        """
        Here, I use a ternary operator, which is like an if statement but in one line
        it's like this:
        value = a if condition else b
        
        I need this if statement because if the length of the answer options is not divisible by the number of columns, I need to add one more row
        """
        rows = (len(question_answer_options) // columns)
        rows += 1 if len(question_answer_options) % columns != 0 else 0 
        
        col = 0
        row = 0
        for answer_option in question_answer_options:
            # 9090
            button = tk.Button(self.question_answer_options_frame, justify="left", wraplength=self.question_button_wraplength, font=self.default_font, width=self.question_button_width, height=self.question_button_height, padx=5, pady=5, text=answer_option, command=lambda answer=answer_option, current_question=current_question: self.click_answer(answer, current_question)) # you'll just have to memorise that when using a tk.Button this is how you call a function that requires variables otherwise if you don't do the variable=variable between the lambda and the ':' when you click any button it will use the variable of the last iteration because of reasons
            button.grid(row=row, column=col, padx=10, pady=10) # if you use padx and pady when grid-ing a widget it's like giving it a margin, if you give it when you CREATE a widget it's actual padding
            col += 1
            if col == columns:
                col = 0
                row += 1
    
    def click_answer(self, answer: str, current_question: "Question"):
        if current_question.check_answer(answer):
            self.score += 1
            self.guess_stack.append(True)
        else:
            self.guess_stack.append(False)
        
        self.next()
        
    def next(self):
        if self.current_question_index == self.max_score - 1:
            self.quiz_frame.grid_forget()
            self.post_game_frame.grid(row=0, column=1)
            self.score_label.config(text=f"Your score is {self.score}/{self.max_score}")
            return
        else:
            self.current_question_index += 1
            self.display_question()
            
    def previous(self):
        if self.current_question_index == 0:
            return
        else:
            self.current_question_index -= 1
            last_question_guess = self.guess_stack.pop() # gets the previous guess and removes it from the stack #TODO doesn't work if they didn't have a previous guess (also add possible toggle to option since it lets you guess?)
            if last_question_guess: # if the user guessed correctly on the previous question, we need to subtract the score
                self.score -= 1
            self.display_question()
            
class QuestionDecoder:
    def __init__(self) -> None:
        self.questions = []
        
    def load_json(self) -> dict:
        with open("questions.json", "r") as f:
            return json.load(f)
    
    def get_questions(self) -> list["Question"]: # This is type hinting that it returns a list of Question objects (wth is this)
        questions_json = self.load_json()
        
        for count, question in enumerate(questions_json.values()):
            self.questions.append(Question(question["question"], question["answer"], question["answer_options"], count))
            if question["answer"] not in question["answer_options"]:
                print("Warning: The answer is not in the answer options in question", count)
        
        return self.questions
    
class Question:
    def __init__(self, question: str, answer: str, answer_options: list, question_num: int) -> None:
        self.question = question
        self.answer = answer
        self.answer_options:list[str] = answer_options # you can type hint a variable so later autocorrect can help you and stuff (oh that's great)
        self.question_num = question_num
    
    def check_answer(self, answer: str) -> bool:
        return answer == self.answer

if __name__ == "__main__":
    # Set the working directory to the directory of the script
    # This is needed if we don't want to input the path every single time
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Add the script directory to the system path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    app = App()