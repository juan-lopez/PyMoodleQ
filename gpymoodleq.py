#!/usr/bin/env python3
#
# Copyright 2026 Juan O. López Gerena
#
# This file is part of PyMoodleQ.
#
# PyMoodleQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyMoodleQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyMoodleQ. If not, see <https://www.gnu.org/licenses/>.

"""
PyMoodleQ is a module for creating and exporting questions for the Moodle LMS
in XML format.  Most standard question types are supported, and categories are
supported as well.  PyMoodleQ requires Python 3.9+, due some features of ElementTree.

This is a GUI for the PyMoodleQ module.  It is a work in progress; it hasn't been
thoroughly tested and doesn't yet support all of the functionality of PyMoodleQ.

Authors: Juan O. López Gerena (juano.lopez@upr.edu), Lian I. Meléndez Santana
"""

import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from pymoodleq import *

# Next button to be a little closer to the dropdown
root = tk.Tk()
root.title("PyMoodleQ")
root.geometry("600x600")

# As a future option, to be able to edit the information of a question
quiz = Quiz()

""" Remember that the questions are appended in the
 following format: ("typeOfQ", xmlQuestion) """
questionList = list()
answerList = list()
gui_entries = dict()

def validate_int(num):
    """Validates that input is a non-negative integer."""
    return num.isdigit() and int(num) >= 0

def validate_string(text):
    """Validates that input is a non-empty string."""
    return bool(text.strip())

def show_help(message):
    """Displays a help message in a popup."""
    messagebox.showinfo("Help", message)

def delete_items():
    """Delete all of the questions selected in the ListBox."""
    selectedQuestions = listBox.curselection()
    # Every time we delete an item, the indices shift, so delete in reverse order
    for selectedIndex in selectedQuestions[::-1]:
        listBox.delete(selectedIndex)

def update_button_state(button, list):
    if len(list) > 1:
        button.config(state=tk.NORMAL)
    else:
        button.config(state=tk.DISABLED)

def show_form():
    """Displays specific frame based on the user's dropdown selection.

    Hides main frame and displays a specific frame correspoding to the
    selected question type.
    """
    selection = dropdown_var.get()
    if selection == "True False":
        mainFrame.pack_forget()
        create_frame("True False", true_false, "tf")
    elif selection == "Numerical":
        mainFrame.pack_forget()
        create_frame("Numerical", numerical, "num")
    elif selection == "Short Answer":
        mainFrame.pack_forget()
        create_frame("Short Answer", shortAnswer, "shortA")
    elif selection == "Multichoice":
        mainFrame.pack_forget()
        create_frame("Multichoice", multichoice, "multi")
    elif selection == "Essay":
        mainFrame.pack_forget()
        create_frame("Essay", essay, "essay")
    elif selection == "Matching":
        mainFrame.pack_forget()
        create_frame("Matching", matching, "match")
    elif selection == "Cloze":
        mainFrame.pack_forget()
        create_frame("Cloze", cloze, "cloze")
    elif selection == "Random Match SA":
        mainFrame.pack_forget()
        create_frame("Random Match SA", randomMatchSA, "randomMSA")
    else:
        error_label.config(text="Please select an option!", fg="red")

def get_file_name(frame):
    """Saves the quiz to an XML file chosen by the user."""
    fileName = filedialog.asksaveasfilename(initialfile="Untitled.xml", defaultextension=".xml", filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")])
    if "error_fileName" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_fileName"] = error_label
    else:
        error_label = gui_entries["error_fileName"]

    error_label.config(text="")

    if questionList:
        # Add questions to quiz
        for question in questionList:
            if question[0] == "cat":
                quiz.add_category(question[1], question[2])
            else:
                quiz.add_question(question[1])

        # Export quiz
        if fileName:
            with open(fileName, "w") as file:
                file.write(str(quiz))
    else:
        error_label.config(text="Quiz must contain at least one question.")
        error_label.pack()

##############
# TRUE FALSE #
##############
def true_false(frame):
    """Creates a True False question with the user input
    and adds it to the question list."""

    if "error_label_trueFralse" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_label_trueFralse"] = error_label
    else:
        error_label = gui_entries["error_label_trueFralse"]

    error_label.config(text="")

    try:
        newQ = TrueFalse()
        newQ.set_question(gui_entries["question_title"].get(), gui_entries["question_text"].get())
        newQ.set_answer(gui_entries["tf_answer"].get == "True")
        newQ.set_grade(int(gui_entries["grade_entered"].get()))

        # Add question to mainFrame Box
        listBox.insert("end", f"tf {gui_entries["question_title"].get()}")
        questionList.append(("tf",newQ))

        # Hide tf_frame and show mainFrame again
        gui_entries["tf"].pack_forget()
        mainFrame.pack(pady=20)
    except Exception as e:
        error_label.config(text=e)
        error_label.pack()

####################
# TRUE FALSE FRAME #
####################
def tf_frame(frame):

    tf_label = tk.Label(frame, text="Select correct answer:", font=("Arial", 12))
    tf_label.pack(pady=(10, 2))

    tf_answer = tk.StringVar(value="True")
    trueRadio = tk.Radiobutton(frame, text="True", variable=tf_answer, value="True")
    falseRadio = tk.Radiobutton(frame, text="False", variable=tf_answer, value="False")

    trueRadio.pack(pady=5)
    falseRadio.pack(pady=5)

    gui_entries["tf_answer"] = tf_answer

#############
# NUMERICAL #
#############
def numerical(frame):
    """Creates a Numerical question with the user inputs and
    adds it to the question list.

    Question may contain multiple answers.
    """

    if "error_label_num" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_label_num"] = error_label
    else:
        error_label = gui_entries["error_label_num"]

    error_label.config(text="")
    try:
        newQ = Numerical()
        newQ.set_question(gui_entries["question_title"].get(), gui_entries["question_text"].get())
        newQ.set_grade(int(gui_entries["grade_entered"].get()))

        # Add answers to question
        for answer in answerList:
            newQ.add_answer(answer[0], answer[1], answer[2], answer[3])

        listBox.insert("end", f"num {gui_entries["question_title"].get()}")
        questionList.append(("num",newQ))


        # Hide frame3 and show mainFrame again
        gui_entries["num"].pack_forget()
        mainFrame.pack(pady=20)
    except Exception as e:
        error_label.config(text=e)
        error_label.pack()


###################
# NUMERICAL FRAME #
###################
def numerical_frame(question, frame, answerList):

    list_button_container = tk.Frame(frame)
    MAXITEMSTODISPLAY = 10
    #If no initial items to display, then omit the list variable argument
    answerBox = tk.Listbox(list_button_container, selectmode=tk.SINGLE,
                        height=MAXITEMSTODISPLAY)

    enter_answer = tk.Button(frame, text="Add answer", command=lambda: add_answer(question, answerBox, answerList))
    enter_answer.pack(pady=10)

    list_button_container.pack()  # Keeps them together
    answerBox.pack(side="left",padx=5, pady=10)

    # Up button
    up_button = tk.Button(list_button_container, text="Up", command=lambda: move_up(answerBox, answerList), width=5)
    up_button.pack(pady=5)

    # Down button
    down_button = tk.Button(list_button_container, text="Down", command=lambda: move_down(answerBox, answerList), width=5)
    down_button.pack(pady=5)

    # Delete button
    delete_button = tk.Button(list_button_container, text="Delete", command=lambda: delete_selected(answerBox, answerList), width=5)
    delete_button.pack(pady=5)

################
# SHORT ANSWER #
################
def shortAnswer(frame):
    """Creates a Short Answer question with the user inputs and
    adds it to the question list.

    Question may contain multiple answers.
    """
    if "error_label_shortA" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_label_shortA"] = error_label
    else:
        error_label = gui_entries["error_label_shortA"]

    error_label.config(text="")
    try:
        newQ = ShortAnswer()
        newQ.set_question(gui_entries["question_title"].get(), gui_entries["question_text"].get())
        newQ.set_grade(int(gui_entries["grade_entered"].get()))

        # Add answers to question
        for answer in answerList:
            newQ.add_answer(answer[0], answer[1], answer[2])


        listBox.insert("end", f"num {gui_entries["question_title"].get()}")
        questionList.append(("num", newQ))


        # Hide frame3 and show mainFrame again
        gui_entries["shortA"].pack_forget()
        mainFrame.pack(pady=20)
    except Exception as e:
        error_label.config(text=e)
        error_label.pack()

######################
# SHORT ANSWER FRAME #
######################
def shortA_frame(frame, answerList):
    """_summary_

    Args:
        frame (_type_): frame where all the things that are going to be displayed
                        for
        answerList (_type_): _description_
    """
    list_button_container = tk.Frame(frame)
    MAXITEMSTODISPLAY = 10
    #If no initial items to display, then omit the list variable argument
    answerBox = tk.Listbox(list_button_container, selectmode=tk.SINGLE,
                        height=MAXITEMSTODISPLAY)

    enter_answer = tk.Button(frame, text="Add answer", command=lambda: add_answer("shortA", answerBox, answerList))
    enter_answer.pack(pady=10)

    list_button_container.pack()  # Keeps them together

    answerBox.pack(side="left",padx=5, pady=10)

    # Up button
    up_button = tk.Button(list_button_container, text="Up", command=lambda: move_up(answerBox, answerList), width=5)
    up_button.pack(pady=5)

    # Down button
    down_button = tk.Button(list_button_container, text="Down", command=lambda: move_down(answerBox, answerList), width=5)
    down_button.pack(pady=5)

    # Delete button
    delete_button = tk.Button(list_button_container, text="Delete", command=lambda: delete_selected(answerBox, answerList), width=5)
    delete_button.pack(pady=5)

def multichoice(frame):

    if "error_label_multi" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_label_multi"] = error_label
    else:
        error_label = gui_entries["error_label_multi"]

    error_label.config(text="")
    try:
        newQ = Multichoice()
        newQ.set_question(gui_entries["question_title"].get(), gui_entries["question_text"].get())
        newQ.set_grade(int(gui_entries["grade_entered"].get()))

        if (gui_entries["dropdown_num"].get() == "None"):
            gui_entries["dropdown_num"] = None

        newQ.set_answer_attributes(bool(gui_entries["single_var"].get()), bool(gui_entries["shuffle_var"].get()), gui_entries["dropdown_num"].get())

        # Add answers to question
        for answer in answerList:
            newQ.add_answer(answer[0], answer[1], answer[2])

        listBox.insert("end", f"multi {gui_entries["question_title"].get()}")
        questionList.append(("multi", newQ))

        # Hide frame4 and show mainFrame again
        gui_entries["multi"].pack_forget()
        mainFrame.pack(pady=20)
    except Exception as e:
        error_label.config(text=e)
        error_label.pack()

def multichoiceFrame(frame):

    list_button_container = tk.Frame(frame)
    MAXITEMSTODISPLAY = 10
    #If no initial items to display, then omit the list variable argument
    answerBox = tk.Listbox(list_button_container, selectmode=tk.SINGLE,
                        height=MAXITEMSTODISPLAY)

    gui_entries["dropdown_num"] = tk.StringVar(value="Select a numbering format")
    dropdown = ttk.Combobox(frame, textvariable=gui_entries["dropdown_num"], values=["None", "1", "a", "A", "i", "I"], state="readonly")
    dropdown.pack(pady=10)

    gui_entries["single_var"] = tk.BooleanVar(value=False)
    single_answer = tk.Checkbutton(frame, text="Single correct answer", variable=gui_entries["single_var"])
    single_answer.pack(pady=10)

    gui_entries["shuffle_var"] = tk.BooleanVar(value=False)
    shuffle_answer = tk.Checkbutton(frame, text="Shuffle answers", variable=gui_entries["shuffle_var"])
    shuffle_answer.pack(pady=10)

    enter_answer = tk.Button(frame, text="Add answer", command=lambda: add_answer("multi", answerBox, answerList))
    enter_answer.pack(pady=10)

    list_button_container.pack()  # Keeps them together

    answerBox.pack(side="left",padx=5, pady=10)

    # Up button
    up_button = tk.Button(list_button_container, text="Up", command=lambda: move_up(answerBox, answerList), width=5)
    up_button.pack(pady=5)

    # Down button
    down_button = tk.Button(list_button_container, text="Down", command=lambda: move_down(answerBox, answerList), width=5)
    down_button.pack(pady=5)

    # Delete button
    delete_button = tk.Button(list_button_container, text="Delete", command=lambda: delete_selected(answerBox, answerList), width=5)
    delete_button.pack(pady=5)


def add_answer(question, answerBox, answerList):
    """ Displays a pop up to add an answer for questions that
    allows more than one answer.
    """
    try:
        popup = tk.Toplevel(root)
        popup.title("Enter answer")
        popup.geometry("400x400")

        # Fraction input
        tk.Label(popup, text="Enter fraction: ").pack(pady=5)
        fraction_frame = tk.Frame(popup)
        fraction_frame.pack(pady=5)
        fraction = tk.Entry(fraction_frame, width=30)
        fraction.pack(side="left")
        tk.Button(fraction_frame, text="?", command=lambda: show_help("Fraction should be a non-negative integer."), width=2).pack(side="left", padx=5)

        # Answer text input
        tk.Label(popup, text="Enter answer text: ").pack(pady=5)
        text_frame = tk.Frame(popup)
        text_frame.pack(pady=5)
        text = tk.Entry(text_frame, width=30)
        text.pack(side="left")
        tk.Button(text_frame, text="?", command=lambda: show_help("Answer text is a possible answer for the question."), width=2).pack(side="left", padx=5)

        # Feedback input
        tk.Label(popup, text="Enter feedback: ").pack(pady=5)
        feedback_frame = tk.Frame(popup)
        feedback_frame.pack(pady=5)
        feedback = tk.Entry(feedback_frame, width=30)
        feedback.pack(side="left")
        tk.Button(feedback_frame, text="?", command=lambda: show_help("Provide feedback related to the answer."), width=2).pack(side="left", padx=5)

        if question == "num":
            # Tolerance input
            tk.Label(popup, text="Enter tolerance: ").pack(pady=5)
            tolerance_frame = tk.Frame(popup)
            tolerance_frame.pack(pady=5)
            tolerance = tk.Entry(tolerance_frame, width=30)
            tolerance.pack(side="left")
            tk.Button(tolerance_frame, text="?", command=lambda: show_help("Provide tolerance related to the answer."), width=2).pack(side="left", padx=5)

        error_label = tk.Label(popup, text="", fg="red")
        def submit():
            try:
                a_fraction = fraction.get()
                a_text = text.get()
                a_feedback = feedback.get()
                error_label.config(text="")
                error_label.pack()

                if not validate_int(a_fraction):
                    error_label.config(text="Fraction must be a non-negative integer.")
                    return
                if not validate_string(a_text):
                    error_label.config(text="Answer text cannot be empty.")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Error in submitting answer: {e}")

            answerBox.insert("end", f"{a_text}")

            if question == "num":
                a_tolerance = tolerance.get()
                answerList.append((int(a_fraction), a_text, a_feedback, a_tolerance))
            else:
                answerList.append((int(a_fraction), a_text, a_feedback))
            popup.destroy()

            # === Able submit button for question ===
            if len(answerList) > 1 and question == "multi":
                gui_entries["submit_btn"].config(state=tk.NORMAL)

        tk.Button(popup, text="Submit", command=submit).pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"Error in add answer: {e}")

def essay(frame):
    if "error_label_essay" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_label_essay"] = error_label
    else:
        error_label = gui_entries["error_label_essay"]

    error_label.config(text="")
    try:
        newQ = Essay()
        newQ.set_question(gui_entries["question_title"].get(), gui_entries["question_text"].get())
        newQ.set_grade(int(gui_entries["grade_entered"].get()))

        # === Enabling attachments and required ===
        if gui_entries["dropdown_attch_enable"].get() == "Infinite":
            dropAttachEnable = -1
        elif gui_entries["dropdown_attch_enable"].get() == "None":
            dropAttachEnable = 0
        else:
            dropAttachEnable = int(gui_entries["dropdown_attch_enable"].get())

        if gui_entries["required_attch"].get() == "Required attachments":
            requiredAttach = 0
        else:
            requiredAttach = int(gui_entries["required_attch"].get())
        newQ.enable_attachments(dropAttachEnable, requiredAttach)

        # === Response attributes ===
        if gui_entries["response_required"].get() == "True":
            responseRequired = 1
        else:
            responseRequired = 0
        newQ.set_response_attributes(gui_entries["dropdown_response"].get(), responseRequired, 5)

        # === Attach files ===
        filesTypes = []
        for att_type, var in gui_entries["file_type_vars"].items():
            if var.get():
                filesTypes.append(att_type.lower().replace(" ", "_"))
        newQ.set_attachment_type(filesTypes)
        listBox.insert("end", f"essay {gui_entries["question_title"].get()}")
        questionList.append(("essay", newQ))
    except Exception as e:
        error_label.config(text=e)
        error_label.pack()

def essayFrame(frame):
    file_types = [
        "Archive", "Audio", "HTML Audio", "Web Audio", "Document",
        "HTML Track", "Image", "Optimized Image", "Web Image",
        "Presentation", "Spreadsheet", "Media Source", "Video",
        "HTML Video", "Web Video", "Web File"
    ]
    gui_entries["file_type_vars"] = {}
    for ftype in file_types:
        gui_entries["file_type_vars"][ftype] = tk.BooleanVar(value=False)  # Initialize all to False
    gui_entries["dropdown_attch_enable"] = tk.StringVar(value="Enable attachments")
    dropdown_enable = ttk.Combobox(frame, textvariable=gui_entries["dropdown_attch_enable"], values=["None", 1, 2, 3, "Infinite"], state="readonly")
    dropdown_enable.pack(pady=10)

    gui_entries["required_attch"] = tk.StringVar(value="Required attachments")
    required_attach = ttk.Combobox(frame, textvariable=gui_entries["required_attch"], values=[1,2,3] , state="disabled")
    required_attach.pack(pady=10)

    gui_entries["attach_btn"] = tk.StringVar(value="Attach File")
    attach_btn = tk.Button(frame, textvariable=gui_entries["attach_btn"], state="disabled", command=lambda: files(frame))
    attach_btn.pack(pady=10)

    gui_entries["dropdown_response"] = tk.StringVar(value="Response template")
    dropdown_response = ttk.Combobox(frame, textvariable=gui_entries["dropdown_response"], values=["editorfilepicker", "noinline", "editor", "plain", "monospaced"], state="readonly")
    dropdown_response.pack(pady=10)

    response_required = tk.Label(frame, text="Text response is required:", font=("Arial", 12))
    response_required.pack(pady=(10, 2))

    gui_entries["response_required"] = tk.StringVar(value="True")
    trueRadio = tk.Radiobutton(frame, text="True", variable=gui_entries["response_required"], value="True")
    falseRadio = tk.Radiobutton(frame, text="False", variable=gui_entries["response_required"], value="False")
    trueRadio.pack(pady=5)
    falseRadio.pack(pady=5)

    def files_button(event):
        file_type = gui_entries["dropdown_attch_enable"].get()
        if file_type != "None":
            required_attach.config(state="readonly")
            attach_btn.config(state="normal")
        else:
            required_attach.config(state="disabled")
            attach_btn.config(state="disabled")
    dropdown_enable.bind("<<ComboboxSelected>>", files_button)


# TODO: Fix submit button so that it doesnt allow to submit the question if there
# aren't at least three question in list
def matchingFrame(frame):

    list_button_container = tk.Frame(frame)
    MAXITEMSTODISPLAY = 10
    #If no initial items to display, then omit the list variable argument
    answerBox = tk.Listbox(list_button_container, selectmode=tk.SINGLE,
                        height=MAXITEMSTODISPLAY)

    enter_answer = tk.Button(frame, text="Add answer", command=lambda: add_match_answer("match", answerBox, answerList))
    enter_answer.pack(pady=10)

    list_button_container.pack()  # Keeps them together

    answerBox.pack(side="left",padx=5, pady=10)

    # Up button
    up_button = tk.Button(list_button_container, text="Up", command=lambda: move_up(answerBox, answerList), width=5)
    up_button.pack(pady=5)

    # Down button
    down_button = tk.Button(list_button_container, text="Down", command=lambda: move_down(answerBox, answerList), width=5)
    down_button.pack(pady=5)

    # Delete button
    delete_button = tk.Button(list_button_container, text="Delete", command=lambda: delete_selected(answerBox, answerList), width=5)
    delete_button.pack(pady=5)

# Manages user input and creates question object
# A Matching question is basically a question that contains
# more questions with its respective answers and it must be paired
def matching(frame):

    if "error_label_match" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_label_match"] = error_label
    else:
        error_label = gui_entries["error_label_match"]

    try:
        newQ = Matching()
        newQ.set_question(gui_entries["question_title"].get(), gui_entries["question_text"].get())
        newQ.set_grade(int(gui_entries["grade_entered"].get()))

        # This question has subquestions and answer
        for subQ in answerList:
            newQ.add_subquestion(subQ[0], subQ[1])

        # Appeding question to list and listBox
        listBox.insert("end", f"match {gui_entries["question_title"].get()}")
        questionList.append(("match", newQ))

        go_mainFrame(frame)
    except Exception as e:
        error_label.config(text=e)
        error_label.pack()

def add_match_answer(question, answerBox, answerList):
    """ Displays a pop up to add an answer for questions that
    allows more than one answer.
    """
    try:
        popup = tk.Toplevel(root)
        popup.title("Enter answer")
        popup.geometry("400x400")

        # Fraction input
        tk.Label(popup, text="Enter question: ").pack(pady=5)
        question_frame = tk.Frame(popup)
        question_frame.pack(pady=5)
        question = tk.Entry(question_frame, width=30)
        question.pack(side="left")

        # Answer text input
        tk.Label(popup, text="Enter answer: ").pack(pady=5)
        answer_frame = tk.Frame(popup)
        answer_frame.pack(pady=5)
        answer = tk.Entry(answer_frame, width=30)
        answer.pack(side="left")
        error_label = tk.Label(popup, text="", fg="red")
        def submit():
            try:
                a_question = question.get()
                a_answer = answer.get()
                error_label.config(text="")
                error_label.pack()
            except Exception as e:
                messagebox.showerror("Error", f"Error in submitting answer: {e}")

            answerBox.insert("end", f"{a_answer}")
            answerList.append((a_question, a_answer))
            popup.destroy()

            # === Able submit button for question ===
            if len(answerList) > 3:
                gui_entries["submit_btn"].config(state=tk.NORMAL)


        tk.Button(popup, text="Submit", command=submit).pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"Error in add answer: {e}")

def files(frame):
    """Display file type options using checkboxes in a new frame."""
    newFrame = tk.Frame(frame)
    newFrame.pack(pady=10)

    popup = tk.Toplevel(frame)
    popup.title("Select Allowed File Types")
    label = tk.Label(popup, text="Select allowed file types:", font=("Arial", 12))
    label.pack(pady=10)

    checkbox_frame = tk.Frame(popup)
    checkbox_frame.pack(pady=10)

    for ftype in gui_entries["file_type_vars"]:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(checkbox_frame, text=ftype, variable=var)
        gui_entries["file_type_vars"][ftype] = var  # Store the variable in the dictionary
        checkbox.pack(anchor="w")


    submit_btn = tk.Button(popup, text="Submit", command=popup.destroy)
    submit_btn.pack(pady=10)
    close_btn = tk.Button(popup, text="Close", command=popup.destroy)
    close_btn.pack(pady=10)

def cloze(frame):
    if "error_label_cloze" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_label_cloze"] = error_label
    else:
        error_label = gui_entries["error_label_cloze"]

    try:
        newQ = Cloze()
        newQ.set_question(gui_entries["question_title"].get(), gui_entries["question_text"].get("1.0", "end-1c"))
        newQ.set_grade(int(gui_entries["grade_entered"].get()))

        # Appeding question to list and listBox
        listBox.insert("end", f"cloze {gui_entries["question_title"].get()}")
        questionList.append(("cloze", newQ))

        go_mainFrame(frame)
    except Exception as e:
        error_label.config(text=e)
        error_label.pack()

def randomMatchSAFrame(frame):
    # Number of questions (2 to 10)
    dropdown_var = tk.StringVar(value="Amount of questions")
    gui_entries["rmsa_question"] = ttk.Combobox(frame, textvariable=dropdown_var, values=[2, 3, 4, 5, 6, 7, 8, 9, 10], state="readonly")
    gui_entries["rmsa_question"].pack(pady=10)
    # gui_entries["rmsa_question"].pack(pady=5)


def randomMatchSA(frame):
    if "error_label_randomMatchSA" not in gui_entries:
        error_label = tk.Label(frame, text=" ", fg="red")
        gui_entries["error_label_randomMatchSA"] = error_label
    else:
        error_label = gui_entries["error_label_randomMatchSA"]

    try:
        newQ = RandomSAMatch()
        newQ.set_question(gui_entries["question_title"].get(), gui_entries["question_text"].get())
        newQ.set_grade(int(gui_entries["grade_entered"].get()))
        print(int(gui_entries['rmsa_question'].get()))
        newQ.set_num_questions(int(gui_entries['rmsa_question'].get()))

        # Appeding question to list and listBox
        listBox.insert("end", f"randomMSA {gui_entries["question_title"].get()}")
        questionList.append(("randomMSA", newQ))

        go_mainFrame(frame)
    except Exception as e:
        error_label.config(text=e)
        error_label.pack()
# Cloze -> crear un text box que sea bastante grandecito y que se pueda hacer scroll
# Random Match SA -> Add question text box, how many questions (2-10), and a check box
            # to check if they want to ad subcategories
# CodeRunner -> stays pending for future work

def go_mainFrame(frame):
    frame.pack_forget()
    mainFrame.pack(pady=20)

# Function for creating Question Frames
def create_frame(QType, funct, frame):
    """Creates a new frame for selected question type."""
    newFrame = tk.Frame(root)
    newFrame.pack(pady=10)
    # Store currentframe with question key as list key
    gui_entries[frame] = newFrame

    # Empty answer list just in case it was
    # previously for another question
    answerList.clear()

    # === Create buttons ===
    label = tk.Label(newFrame, text=f"Create {QType} Question", font=("Arial", 14, "bold"))
    # Simulating labels
    question_title = tk.StringVar(value="Question title")
    question_text = tk.StringVar(value="Question")
    grade = tk.StringVar(value="Grade")
    # Entries
    gui_entries["question_title"] = tk.Entry(newFrame, textvariable=question_title, width=30)
    if frame == "cloze":
        text_frame = tk.Frame(newFrame)
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget = tk.Text(text_frame, height=10, width=30, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        # text_frame.pack()
        # text_widget.get(0)
        gui_entries["question_text"]  = text_widget
    else:
        gui_entries["question_text"] = tk.Entry(newFrame, textvariable=question_text, width=30)
    gui_entries["grade_entered"] = tk.Entry(newFrame, textvariable=grade, width=30)
    gui_entries["cancel_btn"] = tk.Button(newFrame, text="Cancel", command=lambda: go_mainFrame(newFrame))
    gui_entries["submit_btn"] = tk.Button(newFrame, text="Submit", command=lambda: funct(newFrame))

    # === Disable submit button ===
    if frame == "multi":
        gui_entries["submit_btn"].config(state=tk.DISABLED)

    # === Display buttons ===
    label.pack(pady=10)
    gui_entries["question_title"].pack(pady=5)
    if frame == "cloze":
        text_frame.pack(pady=5)
    else:
        gui_entries["question_text"].pack(pady=5)

    if frame == "tf":
        tf_frame(newFrame)
    elif frame == "num":
        numerical_frame(frame, newFrame, answerList)
    elif frame == "shortA":
        shortA_frame(newFrame, answerList)
    elif frame == "multi":
        multichoiceFrame(newFrame)
    elif frame == "essay":
        essayFrame(newFrame)
    elif frame == "match":
        matchingFrame(newFrame)
    elif frame == "randomMSA":
        randomMatchSAFrame(newFrame)
    elif frame != 'cloze':
        answer = tk.StringVar(value="Correct answer")
        gui_entries["answer"] = tk.Entry(newFrame, textvariable=answer, width=30)
        gui_entries["answer"].pack(pady=5)

    # === Display buttons ===
    gui_entries["grade_entered"].pack(pady=5)
    gui_entries["cancel_btn"].pack(side="left", padx=10, pady=10)
    gui_entries["submit_btn"].pack(side="right", padx=10, pady=10)

def category(frame):
    listBox.insert("end", f"cat {gui_entries["category_title"].get()}")
    questionList.append(("cat", gui_entries["category_title"].get(),
                        gui_entries["category_description"].get()))
    frame.pack_forget()
    mainFrame.pack(pady=20)

def newCatFrame(frame):
    frame.pack_forget()
    newFrame = tk.Frame(root)
    newFrame.pack(pady=10)

    # === Create buttons and labels ===
    gui_entries["newCat"] = newFrame
    label = tk.Label(newFrame, text=f"Create New Category", font=("Arial", 14, "bold"))
    gui_entries["cat_cancel_btn"] = tk.Button(newFrame, text="Cancel", command=lambda: go_mainFrame(newFrame))
    gui_entries["cat_submit_btn"] = tk.Button(newFrame, text="Submit", command=lambda: category(newFrame))
    # Simulating labels
    category_title = tk.StringVar(value="Category Title")
    category_description = tk.StringVar(value="Category Description")

    # Entries
    gui_entries["category_title"] = tk.Entry(newFrame, textvariable=category_title, width=30)
    gui_entries["category_description"] = tk.Entry(newFrame, textvariable=category_description, width=30)

    # === Display ===
    label.pack(pady=10)
    gui_entries["category_title"].pack(pady=5)
    gui_entries["category_description"].pack(pady=5)
    gui_entries["cat_cancel_btn"].pack(side="left", padx=10, pady=10)
    gui_entries["cat_submit_btn"].pack(side="right", padx=10, pady=10)


# ========================================
# MAIN FRAME (Dropdown Page) LANDING PAGE
# ========================================
mainFrame = tk.Frame(root)
mainFrame.pack(pady=20)

label1 = tk.Label(mainFrame, text=" PyMoodleQ", font=("Arial", 14, "bold"))
label1.pack(pady=10)

dropdown_var = tk.StringVar(value="Select an option")
dropdown = ttk.Combobox(mainFrame, textvariable=dropdown_var, values=["Numerical", "Short Answer",
                                                                      "True False", "Multichoice", "Essay",
                                                                      "Matching", "Cloze", "Random Match SA"],
                        state="readonly")
dropdown.pack(pady=10)

error_label = tk.Label(mainFrame, text="", fg="red")
error_label.pack()

next_btn = tk.Button(mainFrame, text="Create", command=show_form)
next_btn.pack(pady=5)

MAXITEMSTODISPLAY = 10



# Create a frame to hold the buttons
buttonFrame = tk.Frame(mainFrame)
buttonFrame.pack(side="right", padx=10)

# Function to move selected question up
def move_up(listBox, list):
    """Moves the selected question on position up in the listBox and list."""
    selected = listBox.curselection()
    if selected and selected[0] > 0:  # Ensure not already at the top
        index = selected[0]
        item = listBox.get(index)
        listBox.delete(index)
        listBox.insert(index - 1, item)
        listBox.selection_set(index - 1)
        # question list
        list[index], list[index - 1] = list[index - 1], list[index]

# Function to move selected question down
def move_down(listBox, list):
    """Moves the selected question one position down in the listBox and list."""
    selected = listBox.curselection()
    if selected and selected[0] < listBox.size() - 1:  # Ensure not at the bottom
        index = selected[0]
        item = listBox.get(index)
        listBox.delete(index)
        listBox.insert(index + 1, item)
        listBox.selection_set(index + 1)
        # question list
        list[index], list[index - 1] = list[index - 1], list[index]


# Function to delete the selected question
def delete_selected(listBox, list):
    """Deletes the selected question from listBox and list."""
    selected = listBox.curselection()
    if selected:
        listBox.delete(selected[0])
        list.pop(selected[0])

# Create a container frame to hold the listBox and buttonFrame
list_button_container = tk.Frame(mainFrame)
list_button_container.pack()  # Keeps them together

# Listbox inside the container
listBox = tk.Listbox(list_button_container, selectmode=tk.SINGLE, height=MAXITEMSTODISPLAY)
listBox.pack(side="left", pady=10)

# Create a frame to hold the buttons (inside the container)
buttonFrame = tk.Frame(list_button_container)
buttonFrame.pack(side="right", padx=10)

# Up button
up_button = tk.Button(buttonFrame, text="Up", command=lambda: move_up(listBox, questionList), width=5)
up_button.pack(pady=5)

# Down button
down_button = tk.Button(buttonFrame, text="Down", command=lambda: move_down(listBox, questionList), width=5)
down_button.pack(pady=5)

# Delete button
delete_button = tk.Button(buttonFrame, text="Delete", command=lambda: delete_selected(listBox, questionList), width=5)
delete_button.pack(pady=5)

# Export XML button BELOW the container frame
xml_btn = tk.Button(mainFrame, text="Export XML", command=lambda: get_file_name(mainFrame))
xml_btn.pack(pady=10)  # Placed below listBox & buttons

# Export XML button BELOW the container frame
xml_btn = tk.Button(mainFrame, text="Add Category", command=lambda: newCatFrame(mainFrame))
xml_btn.pack(pady=10)  # Placed below listBox & buttons

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the Tkinter loop
root.mainloop()
