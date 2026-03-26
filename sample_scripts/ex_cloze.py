import pymoodleq

def mm_text(a, b, d, answer):
    if a == b ** d:
        case = "1"
    elif a < b ** d:
        case = "2"
    else:
        case = "3"
    return f"""<p>
        a = {{1:SHORTANSWER:={a}}}<br>
        b = {{1:SHORTANSWER:={b}}}<br>
        d = {{1:SHORTANSWER:={d}}}<br>
        Master Method Case {{2:MULTICHOICE:""" + "1~2~3".replace(case, "="+case) + f"""}}<br>
        <var>T</var>(<var>n</var>) = &Omicron;({{2:SHORTANSWER:={answer}}})
    </p>"""

quiz = pymoodleq.Quiz()
quiz.add_category("Master Method")
syntaxStr="""
<p>
    How to enter the running time:<br>
    &Omicron;(<var>n</var><sup>2</sup>) = &Omicron;(<kbd>n^2</kbd>)<br>
    &Omicron;(<var>n</var><sup>log<sub>3</sub>5</sup>) = &Omicron;(<kbd>n^log_3(5)</kbd>)<br>
    &Omicron;(<var>n</var><sup>2</sup>log n) = &Omicron;(<kbd>n^2*log(n)</kbd>)
</p>"""

q = pymoodleq.Cloze()
q.set_question("Master Method Practice Case 1", mm_text(2, 2, 1, "n*log(n)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Practice Case 2", mm_text(6, 3, 2, r"n^2~%0%n^log_3(6)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Practice Case 3", mm_text(5, 3, 1, "n^log_3(5)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 1 #1", mm_text(9, 3, 2, "n^2*log(n)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 1 #2", mm_text(8, 2, 3, "n^2*log(n)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 1 #3", mm_text(4, 2, 2, "n^2*log(n)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 2 #1", mm_text(3, 4, 1, r"n~%0%n^log_3(4)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 2 #2", mm_text(2, 2, 2, r"n^2~%0%n^log_2(2)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 2 #3", mm_text(4, 2, 3, r"n^3~%0%n^log_2(4)") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 3 #1", mm_text(4, 2, 1, r"n^2~%50%n^log_2(4)#Expression can be simplified") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 3 #2", mm_text(9, 3, 1, r"n^2~%50%n^log_3(9)#Expression can be simplified") + syntaxStr)
quiz.add_question(q)

q = pymoodleq.Cloze()
q.set_question("Master Method Case 3 #3", mm_text(4, 3, 1, "n^log_3(4)") + syntaxStr)
quiz.add_question(q)

quiz.write("ex_cloze.xml")
