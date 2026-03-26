import pymoodleq

theQuiz = pymoodleq.Quiz()

counter = 1
# Generate multiplication exercises
for i in range(1, 3): # 1 <= i < 3
    for j in range(1, 4): # 1 <= j < 4
        rightAnswer = i * j
        question = pymoodleq.Multichoice()
        # Variables will be substituted in question title and question text
        question.set_question(f"Multichoice Q {counter}".rstrip(),
                                f"<strong>What</strong> is {i} &times; {j}?")
        question.set_grade(5, 100) # 100% penalty
        question.add_answer(100, rightAnswer, "Correct!")
        question.add_answer(0, str(rightAnswer - 2), "Two more")
        question.add_answer(0, str(rightAnswer - 1), "One more")
        question.add_answer(0, str(rightAnswer + 2), "Two less")
        question.add_answer(0, str(rightAnswer + 1), "One less")
        question.set_answer_attributes(single=True, shuffle=True)
        theQuiz.add_question(question)
        counter += 1

theQuiz.write("ex_multichoice.xml")