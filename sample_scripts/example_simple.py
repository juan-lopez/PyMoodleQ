import pymoodleq

# First, we create the quiz that will contain the questions
theQuiz = pymoodleq.Quiz()

# We create a multiple-choice question with all of the choices we want
theQuestion = pymoodleq.Multichoice()
# Set the question title and the question text
theQuestion.set_question("What is python?", "What does the term 'python' refer to?")
theQuestion.set_grade(5, 50) # 5 points, 50% penalty for each attempt
theQuestion.add_answer(0, "A type of snake")
theQuestion.add_answer(0, "A horror film from 2000")
theQuestion.add_answer(0, "A high-level programming language")
theQuestion.add_answer(100, "All answers are correct") # 100% of the points
theQuestion.set_answer_attributes(single=True, shuffle=True, numbering="")
# Once we're done with the question, we add it to the quiz
theQuiz.add_question(theQuestion)

# Once we've added all of our questions, generate the XML file
theQuiz.write("example_simple.xml")