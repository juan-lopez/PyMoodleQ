import pymoodleq

def test_mc(myQuiz):
    """Testing Multichoice."""
    counter = 1
    # Use different attribute values for shuffle and numbering
    singleMC = [False, True]
    singleText = ["Multiple", "Single"]
    shuffleMC = [False, True]
    shuffleText = ["", "Shuffled"]
    lstNumbering = ["", "1", "a", "A", "i", "I"]
    for i in range(1, 3):
        for j in range(1, 4):
            rightAnswer = i * j
            question = pymoodleq.Multichoice()
            question.set_question(f"Multichoice Q {counter} {singleText[i-1]} {shuffleText[(j-1)%2]} {lstNumbering[counter-1]}".rstrip(),
                                  f"<strong>What</strong> is {i} &times; {j}?")
            question.set_grade(5, 100) # 100% penalty
            question.add_answer(100, rightAnswer, "Correct!")
            question.add_answer(0, str(rightAnswer - 2), "Two more")
            question.add_answer(0, str(rightAnswer - 1), "One more")
            question.add_answer(0, str(rightAnswer + 2), "Two less")
            question.add_answer(0, str(rightAnswer + 1), "One less")
            question.set_answer_attributes(single=singleMC[i-1], shuffle=shuffleMC[(j-1)%2], numbering=lstNumbering[counter-1])
            myQuiz.add_question(question)
            counter += 1

theQuiz = pymoodleq.Quiz()

test_mc(theQuiz)      # Multichoice

theQuiz.write("ex_multichoice2.xml")