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

Question types supported: Short Answer, Numerical, True/False, Multichoice,
                Drag and Drop, Matching, Missing Words, Random Short Answer Match,
                Description, Cloze, Essay, and CodeRunner.

Question types not supported: Calculated and Simple calculated.

Description of classes:
- Quiz: Represents a Moodle quiz that contains questions, including the option of
                creating categories for the questions.
- QuestionType: Base class containing properties/methods common to all question types.
|-- NST: Contains properties/methods common for Numerical, Short Answer and True/False questions.
| |-- Numerical: Questions whose answers are numerical, each answer with an optional tolerance.
| |-- Short Answer: Question where the answer is a short string.
| |-- TrueFalse: True/False question.
|-- DMMR: Contains common attributes and information for Drag and Drop, Missing Words,
| |               Matching and Random Short Answer Match.
| |-- Drag and Drop: Question where the answers are in a dragbox so
| |                 that the user can drag it to the correct spot.
| |-- Missing Words: Question where the words are missing from a
| |                 sentence. The answers are in a drop down and the correct must be selected.
| |-- Matching: Question where the possible answers must be match with the
| |                 correct definition or expression.
| |-- Random Short Answer Match: Questions with the answers are selected from another category.
|-- Multichoice: Creates a multichoice question where more than one possible answer is displayed.
|-- Description: Question where the description entered is displayed.
|-- Essay: Creates an essay question where text may be inserted or different files may be attached.
|-- Cloze: Questions consist of a passage of text (in Moodle format) that has various answers
|                 embedded within it, including multiple choice, short answers and numerical answers.
|-- CodeRunner: Computer programming questions for languages and formats that Moodle plugin allows.

NOTE 1: Most of the information entered for the creation of the questions is validated,
        but not everything is validated.  User must make an effort to enter valid data.
NOTE 2: PyMoodleQ is under active development, and as such, may still have some bugs lurking.
        If you think you've found one, please send us the details so that we may try to
        re-create it and fix it as soon as possible.

Authors: Juan O. López Gerena (juano.lopez@upr.edu), Lian I. Meléndez Santana
"""

from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import html

#####################
### Question Type ###
#####################
@dataclass
class QuestionType:
    """Base class containing properties/methods common to all question types."""

    # Grade percentages that Moodle provides
    _grades: frozenset[int | float] = frozenset({100, 90, 83.33333, 80, 75, 70, 66.66667,
               60, 50, 40, 33.33333, 30, 25, 20, 16.66667, 14.28571, 12.5, 11.11111, 10,
               5, 0, -5, -10, -11.11111, -12.5, -14.28571, -16.66667, -20, -25, -30,
               -33.33333, -40, -50, -60, -66.66667, -70, -75, -80, -83.33333, -90, -100})

    # Penalty percentages for questions that allow multiple attempts
    _penalty: frozenset[int | float] = frozenset({100, 50, 33.33333, 25, 20, 10, 0})

    # Keep track of whether the answer(s) have been appended to the question
    _appended: bool = field(default=False, init=False)

    # A question may have multiple answers; we store them in a list in XML format.
    _answers: list[ET.Element] = field(init=False, default_factory=list)

    # A question may have multiple hints; we store them in a list in XML format.
    _hints: list[ET.Element] = field(init=False, default_factory=list)

    # XML template for question element
    _questionEl: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""
                    <question type="">
                        <name>
                            <text></text>
                        </name>
                        <questiontext format="html">
                            <text></text>
                        </questiontext>
                        <generalfeedback format="html">
                            <text></text>
                        </generalfeedback>
                        <defaultgrade>5</defaultgrade>
                        <penalty>0.3333333</penalty>
                        <hidden></hidden>
                        <idnumber></idnumber>
                    </question>"""))

    def _validate_fraction(self, fraction: float | int, nonNegative: bool = False):
        """
        Validate a value to make sure it is one of the allowed values
        and of type float or of type int.
        Optional parameter specifies whether negative values are prohibited.

        Args:
            fraction (int): Value to validate.
            nonNegative (bool): Whether value must be non-negative.

        Raises:
            TypeError: If fraction is not an int or a float.
            ValueError: If fraction is not one of the allowed values.
        """
        if not isinstance(fraction, (int, float)):
            raise TypeError("Fraction parameter must be either type int or type float.")
        elif nonNegative and fraction not in [x for x in self._grades if x >= 0]:
            raise ValueError("Fraction must be one of the allowed values.")
        elif fraction not in self._grades:
            raise ValueError("Fraction must be one of the allowed values.")

    def _validate_string(self, string: str, strDesc: str, nonEmpty: bool = True):
        """
        Validate a value to make sure it is a string.
        Optional parameter specified whether string cannot be empty.

        Args:
            string (str): Value to validate.
            strDesc (str): Description of string; to be used in exceptions.
            nonEmpty (bool): Whether string must be non-empty.

        Raises:
            TypeError: If the parameter is not a string.
            ValueError: If the parameter is not one of the allowed values.
        """
        if not isinstance(string, str):
            raise TypeError(strDesc + " must be a string.")
        elif nonEmpty and len(string.strip()) == 0:
            raise ValueError(strDesc + "must not be empty.")

    def _validate_question(self, title: str, question: str):
        """
        Validate the title and question text of a question.

        Args:
            title (str): Title of the question.
            question (str): The text of the question.

        Raises:
            TypeError: If the title or question is not a string.
            ValueError: If the title or question is empty.
        """
        self._validate_string(title, "Question title")
        self._validate_string(question, "Question")

    def set_grade(self, defaultgrade: float | int = 5, penalty: float = 0.0):
        """
        Sets the default grade and penalty for the question.

        Args:
            defaultgrade (float): The default grade for the question; defaults to 5.
            penalty (float, optional): Fraction deducted for incorrect answers or for trying to
                                       answer more than one time; defaults to 0.0.

        Raises:
            TypeError: If defaultgrade or penalty are not numeric.
            ValueError: If defaultgrade is negative or penalty isn't one of the allowed values.
        """
        self._validate_grade(defaultgrade, penalty)
        self._questionEl[3].text = str(defaultgrade)
        self._questionEl[4].text = str(round(penalty/100, 7))

    def set_hidden(self, hidden: int = 0):
        """
        Sets the hidden status of the question in the XML structure.

        Args:
            hidden (int, optional): Indicates if the question is hidden
                                    (0 = visible, 1 = hidden); defaults to 0.
        Raises:
            TypeError: If hidden is not an integer.
            ValueError: If hidden is not 0 or 1.
        """
        self._validate_hidden(hidden)
        self._questionEl[5].text = str(hidden)

    def _validate_grade(self, defaultgrade: float, penalty: float):
        """
        Validates the default grade and penalty.

        Args:
            defaultgrade (float): Maximum grade for the question.
            penalty (float): Penalty for incorrect answers.

        Raises:
            TypeError: If defaultgrade or penalty are not numeric.
            ValueError: If defaultgrade is negative or penalty isn't one of the allowed values.
        """
        if not isinstance(defaultgrade, (float, int)):
            raise TypeError("Default grade must be a numeric value.")
        elif defaultgrade < 1 or defaultgrade > 100:
            raise ValueError("Default grade must be between 1 and 100.")

        if not isinstance(penalty, (float, int)):
            raise TypeError("Penalty must be a numeric value.")
        elif penalty not in self._penalty:
            raise ValueError("Penalty must be one of the following values: " +
                             ','.join(map(str, self._penalty)))

    def _validate_hidden(self, hidden: int):
        """
        Validates the hidden attribute.

        Args:
            hidden (int): Whether the question is hidden (0 or 1).

        Raises:
            TypeError: If hidden is not an integer.
            ValueError: If hidden is not 0 or 1.
        """
        if not isinstance(hidden, int):
            raise TypeError("Hidden must be an integer.")
        elif hidden not in (0, 1):
            raise ValueError("Hidden must be 0 or 1.")

    def add_hint(self, hint: str):
        """
        Add a hint to be shown if the answer is not correct and the user has
        multiple tries.  This method may be called several times to add
        different hints, where each incorrect (or partially correct) answer
        will reveal the next hint.  According to the Moodle docs:
        "The number of tries the student gets is the number of hints in the
        question definition plus one, with a minimum of three."

        Args:
            hint(str): Hint displayed when answer is not correct.

        Raises:
            TypeError: If hint provided isn't a string.
        """

        self._validate_string(hint, "Hint")

        self._hints.append(ET.fromstring(f"""
        <hint format="html">
            <text>{hint}</text>
        </hint>"""))

    def _cdata_enclose(self, string: str) -> str:
        """
        Encloses the input string in a CDATA tag if it contains HTML (if it contains '<').

        Args:
            string (str): Input text to check for HTML tags.

        Returns:
            str: Text enclosed in CDATA if HTML is present; otherwise, unchanged text.
        """
        if "<" in string:
            return f"<![CDATA[{string}]]>"
        else:
            return string

    def _build_xml(self) -> str:
        """Returns a pretty-printed string version of the XML."""
        ET.indent(self._questionEl)
        return ET.tostring(self._questionEl, encoding='unicode')


class DuplicateAnswerError(Exception):
    """Custom exception for duplicate answers in a question."""
    pass


class QuestionError(Exception):
    """Custom exception for generic question-related errors."""
    pass


###########
### NST ###
###########
@dataclass
class NST(QuestionType):
    """
    Superclass of Numerical/Short Answer/TrueFalse (NST) question types, subclass of `QuestionType`.
    """
    # _answerList stores all the valid or partially valid answers with their
    #           respectives grade fraction for validation purposes.
    _answerList: list[dict[str, str | int]] = field(init=False, default_factory=list)
    _xmlAnswerTemplate: str = field(default="""
                    <answer fraction="" format="html">
                        <text></text>
                        <feedback>
                            <text></text>
                        </feedback>
                    </answer>""", init=False)

    def add_answer(self, fraction: int, text: str | int | float, feedback: str = ""):
        """
        Adds an answer to the question with its fraction, text, and feedback.

        Args:
            fraction (int): Points assigned to this answer.
            text (str | int | float): The answer text to be displayed.
            feedback (str, optional): Feedback for the answer. Defaults to an empty string.

        Raises:
            TypeError: If any argument has an invalid type.
            ValueError: If `fraction` is not within the range 0-100.
            DuplicateAnswerError: If the answer text had already been added.
        """
        self._validate_answer(fraction, text, feedback)
        text = self._cdata_enclose(str(text))
        feedback = self._cdata_enclose(feedback)

        # Create answer element using the XML template
        answerElement = ET.fromstring(self._xmlAnswerTemplate)

        # Insert arguments into XML to fill their corresponding fields
        answerElement.attrib['fraction'] = str(fraction)
        answerElement[0].text = str(text)
        answerElement[1][0].text = feedback

        # Store the answer details in answerList and add it to answers
        self._answerList.append({"fraction": fraction, "text": text})
        self._answers.append(answerElement)

    def _validate_answer(self, fraction: int, text: str | int | float, feedback: str):
        """
        Validates the arguments for adding an answer.

        Args:
            fraction (int): Points assigned to the answer.
            text (str | int | float): The answer text to validate.
            feedback (str): The feedback text to validate.

        Raises:
            TypeError: If any argument has an invalid type.
            ValueError: If `fraction` is not within the range 0-100 or text is empty.
            DuplicateAnswerError: If the answer text had already been added.
        """
        self._validate_fraction(fraction)

        # Validate text
        if not isinstance(text, (str, int, float)) or len(str(text).strip()) == 0:
            raise TypeError("Text must be a non-empty string, integer, or float.")

        # Validate feedback
        if not isinstance(feedback, str):
            raise TypeError("Feedback must be of type string.")

        # Check for duplicate answers
        if any(text in d.values() for d in self._answerList):
            raise DuplicateAnswerError("This answer has already been entered.")

####################
### Short Answer ###
####################
@dataclass
class ShortAnswer(NST):
    """
    Represents a Short Answer question type, inheriting from `NST`.

    Attributes:
        Inherits all attributes from the `NST` base class.
    """
    __sensitive: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""<usecase>0</usecase>"""))

    def set_question(self, title: str, question: str):
        """
        Sets the type, title, and text for the short answer question.

        Args:
            title (str): Title of the question.
            question (str): Question text.

        Raises:
            TypeError: If the title or question is not a string.
            ValueError: If the title or question is empty.
        """
        self._validate_question(title, question)

        # Set attributes in the question XML structure
        self._questionEl.attrib['type'] = "shortanswer"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def case_sensitive(self, sensitive: bool = False):
        """Choose if the answer must be case sensitive.

        Args:
            sensitive (bool, optional): True if case sensitive, if not False.
        """
        if sensitive == True:
            self.__sensitive.text = str(1)
        elif sensitive == False:
            self.__sensitive.text = str(0)
        else:
            raise TypeError("Usecase sensitive must be 1 or 0.")


    def _validate_answer(self, fraction: int, text: str | int | float, feedback: str):
        """
        Validates the arguments for adding an answer.

        Args:
            fraction (int): Points assigned to the answer.
            text (str | int | float): The answer text to validate.
            feedback (str): The feedback text to validate.

        Raises:
            TypeError: If any argument has an invalid type.
            ValueError: If `fraction` is not within the range 0-100 or text is empty.
            DuplicateAnswerError: If the answer text had already been added.
        """
        self._validate_fraction(fraction, nonNegative=True)

        # Validate text
        if not isinstance(text, (str, int, float)) or len(str(text).strip()) == 0:
            raise TypeError("Text must be a non-empty string, integer, or float.")

        # Validate feedback
        if not isinstance(feedback, str):
            raise TypeError("Feedback must be of type string.")

        # Check for duplicate answers
        if any(text in d.values() for d in self._answerList):
            raise DuplicateAnswerError("This answer has already been entered.")

    def __str__(self):
        """
        Converts the short answer question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.

        Raises:
            QuestionError: If no answers have been appended to the question.
        """
        try:
            if not self._appended:
                self._appended = True
                self._questionEl.append(self.__sensitive)
                for answer in self._answers:
                    self._questionEl.append(answer)
                for hint in self._hints:
                    self._questionEl.append(hint)
        except:
            raise QuestionError("At least one answer must be entered.")

        return self._build_xml()


#####################
### True or False ###
#####################
@dataclass
class TrueFalse(NST):
    """
    Represents a True/False question type, inheriting from `NST`.

    Attributes:
        Inherits all attributes from the `NST` base class.
    """

    def set_question(self, title: str, question: str):
        """
        Sets the True/False question type, title, and text.

        Args:
            title (str): Title of the question.
            question (str): The question text.

        Raises:
            QuestionError: If validation of inputs fails.
        """
        # Validate and set attributes
        self._validate_question(title, question)
        self._questionEl.attrib['type'] = "truefalse"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def set_grade(self, defaultgrade: float | int):
        """
        Sets the default grade for the question. There is no penalty
        for a truefalse question.

        Args:
            defaultgrade (float): The maximum grade for the question.

        Raises:
            TypeError: If the grade is not numeric.
            ValueError: If the grade is negative.
        """
        self._validate_grade(defaultgrade, 100)
        self._questionEl[3].text = str(defaultgrade)
        self._questionEl[4].text = str(1)

    def set_answer(self, right_answer: bool, right_feedback: str = "", wrong_feedback: str = ""):
        """
        Sets the answers and feedback for the True/False question. Answer provided will be considered
        as the correct answer.

        Args:
            right_answer (bool): Indicates whether the correct answer is True or False.
            right_feedback (str, optional): Feedback for the correct answer. Defaults to an empty string.
            wrong_feedback (str, optional): Feedback for the incorrect answer. Defaults to an empty string.

        Raises:
            QuestionError: If input types are incorrect or validation fails.
        """
        # Add answers based on the correct response
        if right_answer:
            self.add_answer(100, "true", right_feedback)
            self.add_answer(0, "false", wrong_feedback)
        else:
            self.add_answer(0, "true", wrong_feedback)
            self.add_answer(100, "false", right_feedback)

    def __str__(self):
        """
        Converts the question object to a formatted XML string.

        Returns:
            str: The XML string representation of the question.

        Raises:
            QuestionError: If no answers have been appended.
        """
        try:
            if not self._appended:
                self._appended = True
                for answer in self._answers:
                    self._questionEl.append(answer)
        except:
            raise QuestionError("At least one answer must be entered.")

        return self._build_xml()

#################
### Numerical ###
#################
@dataclass
class Numerical(NST):
    """
    Represents a Numerical question type, inheriting from `NST`.
    """
    __units: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""<root>
            <unitgradingtype></unitgradingtype>
            <unitpenalty></unitpenalty>
            <showunits></showunits>
            <unitsleft></unitsleft>
        </root>"""))

    def set_question(self, title: str, question: str):
        """
        Sets the question type, title, and text for the numerical question.

        Args:
            title (str): Title of the question.
            question (str): Question text.

        Raises:
            QuestionError: If validation fails.
        """
        self._validate_question(title, question)
        self._questionEl.attrib['type'] = "numerical"
        self._questionEl[0][0].text = title
        self._questionEl[1][0].text = f"<![CDATA[{question}]]>"

    def add_answer(self, fraction: int, text: str | int | float, feedback: str = "", tolerance: int | float = 0):
        """
        Adds an answer to the question with its fraction, text, feedback and tolerance.

        Args:
            fraction (int): Points assigned to this answer.
            text (str | int | float): The answer text to be displayed.
            feedback (str, optional): Feedback for the answer. Defaults to an empty string.
            tolerance (int, optional): Difference accepted between right answer an answer provided.

        Raises:
            TypeError: If any argument has an invalid type.
            ValueError: If `fraction` is not within the range 0-100.
            DuplicateAnswerError: If the answer text had already been added.
        """
        self._validate_answer(fraction, text, feedback, tolerance)
        text = self._cdata_enclose(str(text))
        feedback = self._cdata_enclose(feedback)

        # Create answer element using the XML template
        answerElement = ET.fromstring(self._xmlAnswerTemplate)

        # Insert arguments into XML to fill their corresponding fields
        answerElement.attrib['fraction'] = str(fraction)
        answerElement[0].text = str(text)
        answerElement[1][0].text = feedback

        # b is an object that makes part of answerElement
        # Used because xmlAnswerTemplate doesn't have tolerance tag
        # but a Numerical answer provides it
        b = ET.SubElement(answerElement, "tolerance")
        b.text = str(tolerance)

        # Store the answer details in garage and add it to answers
        self._answerList.append({"fraction": fraction, "text": text})
        self._answers.append(answerElement)

    def _validate_answer(self, fraction: int, text: str | int | float, feedback: str, tolerance: int):
        """
        Validates the arguments for adding an answer.

        Args:
            fraction (int): Points assigned to the answer.
            text (str | int | float): The answer text to validate.
            feedback (str): The feedback text to validate.

        Raises:
            TypeError: If any argument has an invalid type.
            ValueError: If `fraction` is not within the range 0-100 or text is empty.
            DuplicateAnswerError: If the answer text had already been added.
        """
        self._validate_fraction(fraction, nonNegative=True)

        # Validate text
        if not isinstance(text, (str, int, float)) or len(str(text).strip()) == 0:
            raise TypeError("Text must be a non-empty string, integer, or float.")

        # Validate feedback
        if not isinstance(feedback, str):
            raise TypeError("Feedback must be of type string.")

        # Validate tolerance
        # if tolerance <= 0:
        #     raise TypeError("Tolerance parameter must be type float or int and greater than or equal to 0.")

        # Check for duplicate answers
        if any(text in d.values() for d in self._answerList):
            raise DuplicateAnswerError("This answer has already been entered.")


    def set_units(self, unitgrade: float, unitpenalty: float, showunits: int, unitsleft: int):
        """
        Sets unit-related attributes for the numerical question.

        Args:
            unitgrade (float): Grading weight for units.
            unitpenalty (float): Penalty for incorrect units.
            showunits (int): Whether units are displayed (1 for yes, 0 for no).
            unitsleft (int): Whether units are placed to the left of the value (1 for yes, 0 for no).

        Raises:
            TypeError: If arguments are not of the correct type.
        """
        if not isinstance(unitgrade, float) or not isinstance(unitpenalty, float):
            raise TypeError("Units parameters must be of type float")
        if not isinstance(showunits, int) or not isinstance(unitsleft, int):
            raise TypeError("Display units parameters must be of type int.")
        self.__units[0].text = str(unitgrade)
        self.__units[1].text = str(unitpenalty)
        self.__units[2].text = str(showunits)
        self.__units[3].text = str(unitsleft)

    def __str__(self):
        """
        Converts the numerical question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.

        Raises:
            QuestionError: If no answers have been added.
        """
        try:
            if not self._appended:
                self._appended = True
                for answer in self._answers:
                    self._questionEl.append(answer)
                for unit_element in self.__units:
                    self._questionEl.append(unit_element)
                for hint in self._hints:
                    self._questionEl.append(hint)
        except:
            raise QuestionError("At least one answer must be entered.")

        return self._build_xml()

############
### DMMR ###
############
@dataclass
class DMMR(QuestionType):
    """
    Represents a Drag and Drop/Matching/Missing Words/Random SA Match (DMMR) question type,
    inheriting from `QuestionType`.
    """
    _feedback: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""<root>
            <correctfeedback format="html">
                <text></text>
            </correctfeedback>
            <partiallycorrectfeedback format="html">
                <text></text>
            </partiallycorrectfeedback>
            <incorrectfeedback format="html">
                <text></text>
            </incorrectfeedback>
            <shownumcorrect></shownumcorrect>
        </root>"""))

    def set_feedback(self, correctFeed: str = "", partFeed: str = "", incoFeed: str = ""):
        """
        Sets the feedback messages for correct, partially correct, and incorrect responses.

        Args:
            correctFeed (str, optional): Feedback for a correct response. Defaults to an empty string.
            partFeed (str, optional): Feedback for a partially correct response. Defaults to an empty string.
            incoFeed (str, optional): Feedback for an incorrect response. Defaults to an empty string.

        Raises:
            TypeError: If correctFeed, partFeed, or incoFeed aren't of type string.
            ValueError: If correctFeed, partFeed, or incoFeed are empty.
        """
        self._validate_feedback(correctFeed, partFeed, incoFeed)
        self._feedback[0][0].text = correctFeed
        self._feedback[1][0].text = partFeed
        self._feedback[2][0].text = incoFeed

    def _validate_feedback(self, correctFeed: str, partFeed: str, incoFeed: str):
        """
        Validates the feedback inputs for the question.

        Args:
            correctFeed (str): Feedback for a correct response.
            partFeed (str): Feedback for a partially correct response.
            incoFeed (str): Feedback for an incorrect response.

        Raises:
            TypeError: If correctFeed, partFeed, or incoFeed aren't of type string.
            ValueError: If correctFeed, partFeed, or incoFeed are empty.
        """
        # Validate correct feedback
        if not isinstance(correctFeed, str):
            raise TypeError("Correct feedback must be a string.")
        elif len(correctFeed.strip()) == 0:
            raise ValueError("Correct feedback must not be empty.")

        # Validate partially correct feedback
        if not isinstance(partFeed, str):
            raise TypeError("Partially correct feedback must be a string.")
        elif len(partFeed.strip()) == 0:
            raise ValueError("Partially correct feedback must not be empty.")

        # Validate incorrect feedback
        if not isinstance(incoFeed, str):
            raise TypeError("Incorrect feedback must be a string.")
        elif len(incoFeed.strip()) == 0:
            raise ValueError("Incorrect feedback must not be empty.")

    def add_hint(self, hint: str, clearwrong: bool = False, shownumcorrect: bool = False):
        """ Add hint that will be provided for multiple tries. Hint entered is not
            validated that's correct.

            Args:
            hint (str): Text to be shown as hint. Not validated if it's correct.
            clearwrong (bool): True if wrong answers wil not appear with multiple tries.
            shownumcorrect (bool, optional): True if show number of correct responses.
        """

        if not isinstance(hint, str) or len(hint) == 0:
            raise TypeError("Hint must be type string and not empty.")

        hint = ET.fromstring(f"""
        <hint format="html">
        <text>{hint}</text>
        </hint>""")

        if clearwrong:
            ET.SubElement(hint, "clearwrong")
        if shownumcorrect:
            ET.SubElement(hint, "shownumcorrect")

        self._hints.append(ET.fromstring(f"""
        <hint format="html">
        <text>{hint}</text>
        </hint>"""))

###################
### Drag & Drop ###
###################
@dataclass
class DragAndDrop(DMMR):
    """
    Represents a Drag and Drop question type, inheriting from `DMMR`.

    Attributes:
        Inherits all attributes from the `DMMR` base class.
    """

    def set_question(self, title: str, question: str):
        """
        Sets question attributes like type, title and question text.

        Args:
            title (str): Title of question.
            question (str): Question text.
        """
        # Validate type of received arguments
        self._validate_question(title, question)

        # Store arguments in _questionEl (XML)
        self._questionEl.attrib['type'] = "ddwtos"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def add_answer(self, text: str, group: int):
        """
        Adds an answer with it's respective group into XMl.

        Args:
            text (str): Answer text.
            group (int): Group of answer where it belongs.
        """
        answer = ET.fromstring("""
        <dragbox>
        <text></text>
        <group></group>
        </dragbox>""")

        self._validate_answer(text, group)
        answer[0].text = text
        answer[1].text = str(group)
        self._answers.append(answer)

    def _validate_answer(self, text: str, group: int):
        """
        Validates if attributes recieved are valid.

        Args:
            text (str): Answer text to be validated. Content is not validated that is correct.
            group (int): Group to be validated. Number of group recieved is not validated that
                         maintains a specific order

        Raises:
            TypeError: If attributes aren't their corresponding type.
        """

        if not isinstance(text, str) or len(text.strip()) == 0:
            if isinstance(text, int) == False:
                raise TypeError("Text must be type string.")
        if not isinstance(group, int) or group < 1:
            raise TypeError("Group must be type int or greater than 0.")

    def __str__(self):
        """
        Converts the Drag and Drop question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.

        Raises:
            QuestionError: If no answers have been added.
        """

        # Appending feedback tags to main XML
        for tag in self._feedback:
            self._questionEl.append(tag)
        try:
            if not self._appended:
                self._appended = True
                for answer in self._answers:
                    self._questionEl.append(answer)
        except:
            raise QuestionError("At least one answer must be entered.")

        return self._build_xml()

################
### Matching ###
################
@dataclass
class Matching(DMMR):
    """
    Represents a Matching question type, inheriting from `DMMR`.
    """
    __subquestions: list[ET.Element] = field(init=False, default_factory=list)

    # TODO: Change name of function
    def add_subquestion(self, question: str, answer: str):
        """
        Adds attributes into the subquestion to be appended into the main question.

        Args:
            question (str): Question text.
            answer (str): Answer to question provided.
        """
        questionFormat = ET.fromstring("""
            <subquestion format="html">
            <text></text>
            <answer>
                <text></text>
            </answer>
            </subquestion>""")

        self.__validate_subquestion(question, answer)

        questionFormat[0].text = question
        questionFormat[1][0].text = str(answer)
        self.__subquestions.append(questionFormat)
        self._answers.append(answer)

    def set_question(self, title: str, question: str):
        """
        Sets type of question, title and question text in XML.

        Args:
            title (str): Title of the question.
            question (str): Question text.
        """
        # Validate type of received arguments
        self._validate_question(title, question)

        # Store arguments in _questionEl (XML)
        self._questionEl.attrib['type'] = "matching"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def __validate_subquestion(self, question: str, answer):
        """
        Validates if attributes are valid.

        Args:
            question (str): Question text.
            answer (_type_): Answer for question provided.

        Raises:
            TypeError: If `question` isn't type string.
            ValueError: If `answer` has been entered before.
        """
        if not isinstance(question, str):
            raise TypeError("Text must be type string.")
        if answer in self._answers:
            raise ValueError("Enter a different answer.")

    def __str__(self):
        """
        Converts the Matching question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.

        Raises:
            QuestionError: If no answers have been added.
        """
        for tag in self._feedback:
            self._questionEl.append(tag)
        try:
            if not self._appended:
                self._appended = True
                for question in self.__subquestions:
                    self._questionEl.append(question)
        except:
            raise QuestionError("At least one answer must be entered.")

        return self._build_xml()

#####################
### Missing Words ###
#####################
@dataclass
class MissingWords(DMMR):
    """
    Represents a Missing Words question type, inheriting from `DMMR`.
    """
    __shuffle: int = field(default=0, init=False)

    def set_question(self, title: str, question: str):
        """
        Sets type of question, title and question text into XML.

        Args:
            title (str): Title of question.
            question (str): Question text.
        """
        # Validate type of received arguments
        self._validate_question(title, question)

        # Store arguments in _questionEl (XML)
        self._questionEl.attrib['type'] = "gapselect"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def add_answer(self, text: str, group: int):
        """
        Adds an answer and to which group it belongs to.

        Args:
            text (str): Answer text.
            group (int): Group where the answer belongs to.
        """
        answer = ET.fromstring("""
            <selectoption>
            <text></text>
            <group></group>
            </selectoption>""")

        self._validate_answer(text, group)
        answer[0].text = text
        answer[1].text = str(group)
        self._answers.append(answer)

    def _validate_answer(self, text: str, group: int):
        """
        Validates attributes recieved for answer.

        Args:
            text (str): Answer text to be validated.
            group (int): Group where the answer text belongs to.

        Raises:
            TypeError: If attributes aren't type string or int.
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            if isinstance(text, int) == False:
                raise TypeError("Text must be type string.")
        if not isinstance(group, int) or group < 1:
            raise TypeError("Group must be type int or greater than 0.")

    def enable_shuffle(self, enable: int = 0):
        """
        Determines if answers will be shuffled.

        Args:
            enable (int, optional): 1 if enabliong suffle. Default 0.
        """
        if (enable == 1 or enable == 0):
            self.__shuffle = enable
        else:
            raise ValueError("Value for enable shuffle must be 1 or 0.")

    def __str__(self):
        """
        Converts the Missing Words question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.

        Raises:
            QuestionError: If no answers have been added.
        """
        b = ET.SubElement(self._questionEl, "shuffleanswers")
        b.text = str(self.__shuffle)

        for tag in self._feedback:
            self._questionEl.append(tag)
        try:
            if not self._appended:
                self._appended = True
                for answer in self._answers:
                    self._questionEl.append(answer)
        except:
            raise QuestionError("At least one answer must be entered.")

        return self._build_xml()

#################################
### Random Short Answer Match ###
#################################
@dataclass
class RandomSAMatch(DMMR):
    """
    Represents a Random Short Answer Match question type, inheriting from `DMMR`.
    """
    __subcategory: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""
            <root>
                <subcats></subcats>
            </root>"""))
    __num_questions: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""
            <root>
                <choose></choose>
            </root>"""))


    def set_question(self, title: str, question: str):
        """Receives type of question, title, question text and inserts it into XML.

        Args:
            title (str): title of question
            question (str): question text
        """
        # Validate type of received arguments
        self._validate_question(title, question)

        # Store arguments in _questionEl (XML)
        self._questionEl.attrib['type'] = "randomsamatch"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)


    def include_subcategories(self, subcategory: bool):
        """Allows for the question to be chosen from subcategories too.

        Args:
            subcategory (bool): If true, questions will be chosen from subcategories too.

        """
        if not isinstance(subcategory, bool):
            raise TypeError("Subcategory to be added must be of type bool.")
        if subcategory:
            self.__subcategory[0].text = "1"
        else:
            self.__subcategory[0].text = "0"


    def set_num_questions(self, questionAmount: int = 2):
        """
        Recieves and sets the amount of questions to be displayed. This number
        must be from 2 to 10.

        Args:
            questionAmount (int, optional): Amount of questions to be selected from
                            subcategory. Defaults to 2.
        """
        if not isinstance(questionAmount, int):
            raise TypeError("Number of questions must be type int.")
        if questionAmount < 2 or questionAmount > 10:
            raise ValueError("Numner of questions must be between 2 and 10.")
        self.__num_questions[0].text = str(questionAmount)

    def __str__(self):
        """
        Converts the Missing Words question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.
        """
        for tag in self._feedback:
            self._questionEl.append(tag)
        for tag in self.__subcategory:
            self._questionEl.append(tag)
        for tag in self.__num_questions:
            self._questionEl.append(tag)

        return self._build_xml()

###################
### Multichoice ###
###################
@dataclass
class Multichoice(DMMR, NST):
    """Represents a Multichoice question type, inheriting from `NST` and `DMMR`."""
    __answer_attributes: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""<root>
            <single></single>
            <shuffleanswers></shuffleanswers>
            <answernumbering></answernumbering>
            <showstandardinstruction></showstandardinstruction>
        </root>"""))
    __numbering_formats: dict[str] = field(init=False, default_factory=lambda: {"none": "none", "a": "abc", "A": "ABCD", "1": "123", "i": "iii", "I": "IIII"})

    def set_question(self, title: str, question: str):
        """Sets type of question, title and question text into XML.

        Args:
            title (str): Title of question.
            question (str): Question text.
        """
        # Validate type of received arguments
        self._validate_question(title, question)

        # Store arguments in _questionEl (XML)
        self._questionEl.attrib['type'] = "multichoice"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def set_answer_attributes(self, single: bool, shuffle: bool, numbering: str = "", standard: int = 0):
        """Sets specific answer attributes into XML such as single, shuffle, numbering and standard.

        Args:
            single (bool): Whether a single answer can be chosen.  If false, multiple answers may be chosen.
            shuffle (bool): Answers provided will be shuffled or will be displayed the same way that has been entered.
            numbering (str, optional): Type of numbering for answers (abc, 123). Defaults to "".
            standard (int, optional): Whether to show the standard instructions for MC questions. Defaults to 0.
        """
        self._validate_answer_attributes(single, shuffle, numbering, standard)

        if numbering == "" or numbering is None:
            numbering = "none"

        self.__answer_attributes[0].text = str(single).lower()
        self.__answer_attributes[1].text = str(shuffle).lower()
        self.__answer_attributes[2].text = self.__numbering_formats[numbering]
        self.__answer_attributes[3].text = str(standard)

    def _validate_answer_attributes(self, single: bool, shuffle: bool, numbering: str, standard: int):
        """Validates that answer attributes are correct for input.

        Raises:
            TypeError: If arguments aren't type int, bool or str.
            ValueError: If argument isn't the value expected.
        """

        # Validate single
        if not isinstance(single, bool):
            raise TypeError("Single must be of type bool.")

        # Validate shuffle
        if not isinstance(shuffle, bool):
            raise TypeError("Shuffle must be of type bool.")

        # Validate numbering
        if not isinstance(numbering, str):
            if numbering != None:
                formats = list(self.__numbering_formats.keys())
                raise TypeError(f"Numbering must be one of the following: "+ ','.join(formats))
        elif numbering not in self.__numbering_formats.keys():
            if numbering != "":
                raise ValueError("Numbering must be valid.")

        # Validate standard
        if not isinstance(standard, int):
            raise TypeError("Standard must be of type int.")
        elif standard != 0 and standard != 1:
            raise ValueError("Standard must be 1 or 0.")

    def add_numbering(self, new_numbering_format):
        """Adds a new numbering format available.

        Args:
            new_numbering_format (str): Numbering format to be added.
        """

        num_format = new_numbering_format[0]
        self.__numbering_formats[num_format] = new_numbering_format

    def remove_numbering(self, numbering_format):
        """Removes an existing numbering format.

        Args:
            numbering_format (str): Numbering format to be deleted.

        """
        if isinstance(numbering_format, str):
            formats = list(self.__numbering_formats.keys())
            raise TypeError(f"Numbering must be one of the following: "+ ','.join(formats))
        self.__numbering_formats.pop(numbering_format)

    def __validate_options(self):
        """Validates if question has at least two answers.

        Raises:
            ValueError: If there are less than 2 answers.
        """
        if len(self._answerList) < 2:
            raise ValueError("There must be more than one answer.")

    def __validate_sum(self):
        """Validates that the sum of fractions equals to 100.

        Raises:
            ValueError: If the sum is less or more than 100.
        """
        sum = 0
        for answer in self._answers:
            sum += int(answer.attrib["fraction"])
        if sum != 100:
            raise ValueError("The fractions sum doesn't match up to 100.")

    def __str__(self):
        """
        Converts the Multichoice question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.
        """
        for tag in self.__answer_attributes:
            self._questionEl.append(tag)
        for feedback in self._feedback:
            self._questionEl.append(feedback)
        self.__validate_sum()
        self.__validate_options()
        for answer in self._answers:
            self._questionEl.append(answer)

        return self._build_xml()

###################
### Description ###
###################
@dataclass
class Description(QuestionType):
    """
    Represents a Description question type, inheriting from `NST`.

    """

    def set_question(self, title: str, question: str):
        """
        Sets the question's type, title, and text into the XML structure.

        Args:
            title (str): Title of the question.
            question (str): The text of the question.

        Raises:
            TypeError: If the title or question text is not a string.
            ValueError: If the title or question text is empty.
        """

        type = "description"
        self._validate_question(title, question)
        self._questionEl.attrib['type'] = type
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def __str__(self):
        """
        Converts the numerical question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.

        Raises:
            QuestionError: If no answers have been added.
        """

        return self._build_xml()

#############
### Cloze ###
#############
@dataclass
class Cloze(QuestionType):
    """
    Represents a Cloze question type, inheriting from `QuestionType`.

    Attributes:
        tolerance (ET.Element): XML element for storing tolerance settings.
        units (ET.Element): XML element for storing unit-related settings.
    """

    def set_question(self, title: str, question: str):
        """
        Sets the question's type, title, and text into the XML structure.

        Args:
            title (str): Title of the question.
            question (str): The text of the question.

        Raises:
            TypeError: If the title or question text is not a string.
            ValueError: If the title or question text is empty.
        """

        self._validate_question(title, question)
        self._questionEl.attrib['type'] = "cloze"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def set_penalty(self, penalty: float = 0.00):
        """Sets the penalty for the question.

        Args:
            penalty (float, optional): Fraction deducted for incorrect answers. Defaults to 0.00.
        """
        self.__validate_penalty(penalty)
        self._questionEl[4].text = str(round(penalty/100, 7))

    def set_grade(self, defaultgrade: float, penalty: float = 0.00):
        """
        Sets the default grade and penalty for the question.

        Args:
            defaultgrade (float): The maximum grade for the question.
            penalty (float, optional): Fraction deducted for incorrect answers. Defaults to 0.00.

        Raises:
            TypeError: If the grades are not numeric.
            ValueError: If the grades are negative.
        """
        self.set_penalty(penalty)

    def __validate_penalty(self, penalty: float):
        """
        Validates the penalty.

        Args:
            penalty (float): Penalty for incorrect answers.

        Raises:
            TypeError: If grades are not numeric.
            ValueError: If grades are negative.
        """

        if not isinstance(penalty, (float, int)):
            raise TypeError("Penalty must be a numeric value.")
        elif penalty < 0:
            raise ValueError("Penalty must be greater than or equal to 0.")

    def __str__(self):
        """
        Converts the numerical question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.

        Raises:
            QuestionError: If no answers have been added.
        """
        self._questionEl.remove(self._questionEl.find("./defaultgrade"))

        return self._build_xml()

#############
### Essay ###
#############
@dataclass
class Essay(QuestionType):
    """
    Represents an Essay question type, inheriting from `QUestionType`.
    """
    __essay: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""<root>
            <responseformat></responseformat>
            <responserequired></responserequired>
            <responsefieldlines></responsefieldlines>
            <minwordlimit></minwordlimit>
            <maxwordlimit></maxwordlimit>
            <attachments></attachments>
            <attachmentsrequired></attachmentsrequired>
            <maxbytes>0</maxbytes>
            <filetypeslist></filetypeslist>
            <graderinfo format="html">
            <text></text>
            </graderinfo>
            <responsetemplate format="html">
            <text></text>
            </responsetemplate>
        </root>"""))
    #TODO __attachments: list = field(init=False, default_factory=lambda: ["0", "1", "2", "3", "optional"])
    __responseType: frozenset[str] = frozenset({"editorfilepicker", "noinline", "editor", "plain", "monospaced"})
    __responselines: frozenset[int] = frozenset({2, 3, 5, 10, 15, 20, 25, 30, 35, 40})
    __min_words: int = 1
    __max_words: int = 999999
    # Filetypes
    __extensions: frozenset[str] = frozenset({'.mht', '.bmp', '.m3u8', '.dv', '.scss', '.hqx', '.mp3', '.mpe', '.htm', '.sxw', '.galleryitem', '.pptx', '.rhb', '.rmvb', '.tsv', '.stw', '.xfdf', '.stc', '.asc', '.bdoc', '.ppsm', '.dotm', '.vtt', '.jpg', '.eps', '.gtar', '.applescript', '.htc', '.hpp', '.jcw', '.xltx', '.ai', '.f4v', '.odi', '.odg', '.ps', '.gslides', '.sxi', '.pdf', '.gif', '.ppam', '.avi', '.js', '.pptm', '.css', 'audio', '.wma', 'html_video', '.rtf', '.odc', '.swfl', '.au', '.gz', '.jcl', '.dmg', '.cdoc', '.std', '.otf', '.sxm', '.latex', '.ppt', '.gallerycollection', '.notebook', '.xlsx', '.aac', '.jar', '.woff', '.asf', '.rar', '.flv', '.gsheet', '.rv', '.webm', '.ods', '.rm', '.tiff', '.odf', '.fmp4', 'media_source', '.sqt', '.m4a', '.pub', 'web_file', '.mw', '.otg', '.gzip', '.tar', '.gdoc', 'presentation', '.pps', '.xlsm', '.pct', '.texi', 'video', '.otp', '.ics', '.ttf', '.eot', '.svgz', '.oga', '.sxg', '.xhtml', '.mpeg', '.mhtml', 'web_image', '.html', '.texinfo', '.mpd', '.ram', '.jpeg', '.potm', '.imscc', '.c', '.xbk', '.swf', '.java', '.sit', '.ddoc', '.jmt', '.jqz', '.m3u', '.oth', 'document', '.ott', '.ppsx', '.wav', 'html_audio', '.jpe', '.xdp', '.potx', '.mp4', '.yml', '.doc', 'spreadsheet', '.svg', '.odp', '.ist', '.docm', '.jcb', '.yaml', '.xls', '.dir', '.qt', '.odb', '.smil', '.dcr', '.mdb', '.sh', '.tex', 'image', 'archive', '.aif', '.ra', '.ogv', '.wmv', '.asm', 'optimised_image', '.mpr', 'web_video', '.xsl', '.odm', '.m', '.epub', '.dxr', '.mws', '.gdraw', '.pic', '.dif', '.ogg', '.mbz', '.odt', '.aiff', '.gallery', '.cs', '.woff2', '.h', '.xfd', '.ts', '.m4v', '.sxd', '.dotx', '.jmx', 'web_audio', '.tif', '.sxc', '.docx', '.php', '.ico', '.xltm', '.nbk', '.isf', '.flac', '.smi', '.fdf', '.xml', '.png', '.swa', '.movie', '.json', '.xlsb', '.3gp', '.jnlp', '.psd', '.pict', '.ots', '.accdb', '.sti', '.txt', '.rtx', '.csv', '.cpp', '.mov', '.tgz', '.aifc', '.7z', 'html_track', '.h5p', '.zip', '.mpg', '.xlam', '.cct'})

    def set_question(self, title: str, question: str):
        """
        Sets the question's type, title, and text into the XML format.

        Args:
            title (str): Title of the question to be created.
            question (str): Text of the question.
        """

        self._validate_question(title, question)
        self._questionEl.attrib['type'] = "essay"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def set_response_attributes(self, responseFormat: str, responseRequired: int, responseLines: int = 5):
        """
        Sets specific response attributes into XML format.

        Args:
            responseFormat (str): Define what kind of response format will be displayed.
            responseRequired (int): If a response is required or not.
            responseLines (int): How many lines will be given to write the answer.
        """
        self.__validate_response_attributes(responseFormat, responseRequired, responseLines)
        self.__essay[0].text = responseFormat
        self.__essay[1].text = str(responseRequired)
        self.__essay[2].text = str(responseLines)


    def __validate_response_attributes(self, responseFormat: str, responseRequired: int, responseLines: int):
        """Validates that response attributes are correct for input.

        Args:
            responseFormat (str): Define what kind of response format will be displayed.
            responseRequired (int): If a response is required or not.
            responseLines (int): How many lines will be given to write the answer.

        Raises:
            TypeError: If attributes aren't type str or int.
            ValueError: If an attribute value isn't what is expected.
        """
        # Validate responseFormat
        if not isinstance(responseFormat, str):
            raise TypeError("Response format must be type string.")
        elif responseFormat not in self.__responseType:
            raise ValueError("Response format must be one of the following: "+ ','.join(self.__responseType))

        # Validate responseRequired
        if not isinstance(responseRequired, int):
            raise TypeError("Response required must be type int.")
        elif responseRequired != 1 and responseRequired != 0:
            raise ValueError("Response required must be 1 (true) or 0 (false).")

        # Validate responseLines
        if not isinstance(responseLines, int):
            raise TypeError("Response field lines must be type int.")
        elif responseLines not in self.__responselines:
            raise ValueError("Response field lines must be type int.")

    def word_limits(self, min: int = 1, max: int = 999999):
        """Sets word limits for answer to be provided.

        Args:
            min (int, optional): Minimum of words required of answer. Defaults to 1.
            max (int, optional): Maximum of words allowed of answer. Defaults to 999999.
        """
        self.__validate_word_limits(min, max)
        self.__essay[3] = str(min)
        self.__essay[4] = str(max)

    def __validate_word_limits(self, min: int, max: int):
        """Validates that words limits are correct.

        Args:
            min (int, optional): Minimum of words required of answer. Defaults to 1.
            max (int, optional): Maximum of words allowed of answer. Defaults to 999999.

        Raises:
            ValueError: If values aren't within the range of 1 to 999999.
        """

        if min < self.__min_words:
            raise ValueError("Minimum words must be a positive integer greater than 0.")
        if max > self.__max_words:
            raise ValueError("Maximum words must be a positive integer lower than 999999.")

    def set_response_template(self, template: str):
        """Sets response template into XML and it's a layout of the answer
            that must be provided. Response template isn't validated.

        Args:
            template (str): Initial text for the answer.

        Raises:
            TypeError: If template isn't type str.
        """
        if isinstance(template, str):
            self.__essay[10][0].text = template
        else:
            raise TypeError("Template response must by type string.")

    def set_grader_info(self, info: str):
        """Sets grader info into XML format. Text isn't validated.

        Args:
            info (str): Text to be inserted into XML.

        Raises:
            TypeError: If text isn't type str.
        """
        if isinstance(info, str):
            self.__essay[11][0].text = info
        else:
            raise TypeError("Info grader must by type string.")

    def enable_attachments(self, attach: int = 0, required: int = 0):
        """Sets if attachments are allowed and if allowed, how many are required.

        Args:
            attach (int, optional): How many attachments are permited. Value ranges from 1 to 3 or -1 if more that 3.
            Defaults to 0.
            required (int, optional): How many files are required. Defaults to 0.

        Raises:
            ValueError: If attachments required aren't within limit -1 to 3.
        """
        amount = [0, 1, 2, 3, -1]
        if attach in amount:
            self.__essay[5].text = str(attach)
            self.__essay[6].text = str(required)
        else:
            raise ValueError("Number of attachments required must be 0, 1, 2, 3 or -1.")

    def set_attachment_type(self, archive: str):
        """Set attachments types or extensions in XML.

        Args:
            archive (str): Extensions or groups must be separated by comas.
                           If it's a list must be a list of strings.

        Raises:
            ValueError: If extension or type of attachments isn't valid.
        """
        if isinstance(archive, str):
            # Check if it's separated by comas
            extension = archive.split(',')
        else: # setting is a list
            extension = archive

        extension = set(extension)

        if not extension.issubset(self.__extensions):
            raise ValueError("Extension must be valid." + ','.join(self.__extensions))

        self.__essay[8].text = ','.join(extension)

    def set_max_bytes(self, amount: int, type: str):
        """Sets max bytes for attachments to be accepted.

        Args:
            amount (int): Size of bytes.
            type (str): Type of byte (MB or KB).

        Raises:
            ValueError: If attributes values aren't accepted.
        """
        result = 0
        if type == "MB" or type == "mb":
            m = [50, 20, 10, 5, 2, 1]
            if amount not in m:
                raise ValueError("Amount of bytes must be one of the following: "+ ','.join(map(str, m)))
            result = amount * pow(2, 20)
        elif type == "KB" or type == "kb":
            k = [500, 100, 50, 10]
            if amount not in k:
                raise ValueError("Amount of bytes must be one of the following: "+ ','.join(map(str, k)))
            result = amount * pow(2, 10)

        self.__essay[7].text = str(result)


    def __str__(self):
        """
        Converts the essay question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.
        """

        for i in self.__essay:
            self._questionEl.append(i)
        return self._build_xml()

##################
### CodeRunner ###
##################
@dataclass
class CodeRunner(QuestionType):
    """Represents a CodeRunner question type, inheriting from `QuestionType`. """
    # NOTE: This class needs more thorough testing!
    coderunner_types: set = field(init=False, default_factory=lambda: {"c_function", "c_program", "cpp_function", "cpp_program", "directed_graph",
                    "java_method", "java_program", "multilanguage", "nodejs", "octave_function"
                    "pascal_function", "pascal_program", "php", "python2", "python3", "python3_w_input",
                    "sql", "undirected_graph"})
    test_cases : list = field(init=False, default_factory=lambda: [])
    template: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""<root>
                    <coderunnertype></coderunnertype>
                    <prototypetype>0</prototypetype>
                    <allornothing>1</allornothing>
                    <penaltyregime>10, 20, ...</penaltyregime>
                    <precheck>0</precheck>
                    <hidecheck>0</hidecheck>
                    <showsource>0</showsource>
                    <answerboxlines>18</answerboxlines>
                    <answerboxcolumns>100</answerboxcolumns>
                    <answerpreload></answerpreload>
                    <globalextra></globalextra>
                    <useace></useace>
                    <resultcolumns></resultcolumns>
                    <template></template>
                    <iscombinatortemplate></iscombinatortemplate>
                    <allowmultiplestdins></allowmultiplestdins>
                    <answer></answer>
                    <validateonsave>1</validateonsave>
                    <testsplitterre></testsplitterre>
                    <language></language>
                    <acelang></acelang>
                    <sandbox></sandbox>
                    <grader></grader>
                    <cputimelimitsecs></cputimelimitsecs>
                    <memlimitmb></memlimitmb>
                    <sandboxparams></sandboxparams>
                    <templateparams></templateparams>
                    <hoisttemplateparams>1</hoisttemplateparams>
                    <extractcodefromjson>1</extractcodefromjson>
                    <templateparamslang>None</templateparamslang>
                    <templateparamsevalpertry>0</templateparamsevalpertry>
                    <templateparamsevald>{}</templateparamsevald>
                    <twigall>0</twigall>
                    <uiplugin></uiplugin>
                    <uiparameters></uiparameters>
                    <attachments>0</attachments>
                    <attachmentsrequired>0</attachmentsrequired>
                    <maxfilesize>10240</maxfilesize>
                    <filenamesregex></filenamesregex>
                    <filenamesexplain></filenamesexplain>
                    <displayfeedback>1</displayfeedback>
                    <giveupallowed>0</giveupallowed>
                    <prototypeextra></prototypeextra>
                    </root>"""))

    def set_question(self, title: str, question: str):
        """
        Sets the type, title, and text for coderunner question.

        Args:
            title (str): Title of the question.
            question (str): Question text.

        Raises:
            QuestionError: If validation of input parameters fails.
        """
        self._validate_question(title, question)

        # Set attributes in the question XML structure
        self._questionEl.attrib['type'] = "coderunner"
        self._questionEl[0][0].text = self._cdata_enclose(title)
        self._questionEl[1][0].text = self._cdata_enclose(question)

    def set_coderunner_type(self, type: str):
        """
        Sets the coderunner type of question and inserts it into XML.

        Args:
            type (str): Type of coderunner question. (c_function, c_program, cpp_function,
                        cpp_program, directed_graph, java_method, java_program, multilanguage,
                        nodejs, octave_function, pascal_function, pascal_program, php, python2,
                        python3, python3_w_input, sql, undirected_graph)

        Raises:
            TypeError: Argument received isn't type string.
            ValueError: Argument received isn't valid.
        """
        if not isinstance(type, str):
            raise TypeError("Coderunner type of question must be type string.")
        elif type not in self.coderunner_types:
            raise ValueError("Coderunner must one of the following: " + ", ".join(self.coderunner_types))
        self.template[0].text = type

    def set_all_or_nothing(self, attribute: bool = False):
        """
        Set if partial points are given if not all test cases are
        passed.

        Args:
            attribute (bool, optional): True if partial points are going to be given. Default to False.
        """
        if attribute == True:
            self.template[2].text = "1"
        else:
            self.template[2].text = "0"

    def set_answer_preload(self, preload: str):
        """
        Sets preload argument into XML. This text isn't validated to be correct.

        Args:
            preload (str): Text to be displayed to start an answer.

        Raises:
            TypeError: Argument received isn't type string.
            ValueError: Argument received is an empty string.
        """
        self._validate_string(preload, "Answer preload")
        self.template[9].text = self._cdata_enclose(preload)

    def set_template(self, template: str):
        """
        Sets template argument into XML. This text isn't validate to be correct.

        Args:
            template (str): Text that will be displayed as a starting answer.

        Raises:
            TypeError: Argument received isn't type string.
            ValueError: Argument received is an empty string.
        """
        self._validate_string(template, "Template params")
        self.template[13].text = self._cdata_enclose(template)

    def set_answer(self, answer: str):
        """
        Sets answer text into XML This text isn't validated to be correct.

        Args:
            answer (str): Text that represents a possible answer or the correct answer.

        Raises:
            TypeError: Argument received isn't type string.
            ValueError: Argument received is an empty string.
        """
        self._validate_string(answer, "Answer")
        self.template[16].text = self._cdata_enclose(answer)

    def add_test_case(self, useasexample: bool, display: str, expected: str, testcode: str = "", stdin: str = "", extra: str = ""):
        """
        Adds into the XML a new case that serves as testing for the answer submitted.
        Values aren't validated to match the test case or the code.

        Args:
            useasexample (bool): Determines if test case will be used as an example for code submitted.
            display (str): Determines what kind of display will the test case have. Types of display valid:
                            'SHOW', 'HIDE', 'HIDE_IF_FAIL', 'HIDE_IF_SUCCEED'.
            expected (str): Expected result.
            testcode (str): Code for the test. Default to empty string.
            stdin (str): Input for the test. Default to empty string.
            extra (str): Useful text used by the template. Default to empty string.
        Raises:
            TypeError: Arguments received aren't type string.
            ValueError: Arguments values aren't valid.
        """
        test_case = ET.fromstring("""<testcase testtype="0" useasexample="" hiderestiffail="" mark="1.0000000" >
                        <testcode>
                                    <text></text>
                        </testcode>
                        <stdin>
                                    <text></text>
                        </stdin>
                        <expected>
                                    <text></text>
                        </expected>
                        <extra>
                                    <text></text>
                        </extra>
                        <display>
                                    <text></text>
                        </display>
                        </testcase>""")


        # If testcase will be used as an example
        test_case.attrib['useasexample'] = str(int(useasexample)) # True/False => "1"/"0"

        # Type of display for testcase
        if display == "SHOW" or display == "HIDE" or \
        display == "HIDE_IF_FAIL" or display == "HIDE_IF_SUCCEED":
            test_case[4][0].text = display
        else:
            raise ValueError("Display must be one of the following: SHOW, HIDE, HIDE_IF_FAIL or HIDE_IF_SUCEED")

        # Expected answer for testcase
        self._validate_string(expected, "Expected output")
        test_case[2][0].text = self._cdata_enclose(expected)

        if isinstance(testcode, str) and testcode != "":
            test_case[0][0].text = self._cdata_enclose(testcode)

        if isinstance(stdin, str) and stdin != "":
            test_case[1][0].text = self._cdata_enclose(stdin)

        if isinstance(extra, str) and extra != "":
            test_case[3][0].text = self._cdata_enclose(extra)

        self.test_cases.append(test_case)

    def __str__(self):
        """
        Converts the coderunner question's XML structure to a formatted string.

        Returns:
            str: The formatted XML string representation of the question.
        """
        if self.template[0].text == None:
            raise ValueError("Coderunner type is missing. Must be one of the following: " + ", ".join(self.coderunner_types))

        if len(self.test_cases) == 0:
            raise ValueError("Must have at least one test case.")
        else:
            cases = ET.fromstring("<testcases></testcases>")
            for i in self.test_cases:
                cases.append(i)

        for i in self.template:
            self._questionEl.append(i)
        self._questionEl.append(cases)
        return self._build_xml()


############
### Quiz ###
############
@dataclass
class Quiz:
    """Represents a quiz that must contain questions, and may also contain categories."""
    __quiz: ET.Element = field(init=False, default_factory=lambda: ET.fromstring("""<quiz></quiz>"""))
    __questionList: list[QuestionType] = field(init=False, default_factory=list)
    __questionsAppended: bool = field(default=False, init=False)

    def add_category(self, text: str, info: str = "", idNumber: int = -1):
        """
        Adds a category-type question that may be used by Moodle to categorize questions.

        Args:
            text (string): Name of the category.
            info (string): Category information.
            idNumber (int): If used, the ID number must be unique within each category.
                            It provides another way of identifying a question, which is
                            sometimes useful, but can usually be left blank.
        """
        category = ET.fromstring("""
                        <question type="category">
                            <category>
                            <text></text>
                            </category>
                            <info format="html">
                            <text></text>
                            </info>
                            <idnumber></idnumber>
                        </question>""")
        # Validate and insert text into XML
        if isinstance(text, str) and len(text) > 0:
            self.categoryName = text
            category[0][0].text = self._cdata_enclose(text)
        else:
            raise ValueError("Category name must be a non-empty string.")

        # Validate and insert category info into XML
        if (isinstance(info, str)):
            if (info != ""):
                category[1][0].text = self._cdata_enclose(info)
        else:
            raise TypeError("Category info text must be of type string.")

        # Validate and insert id number into XML
        if(isinstance(idNumber, int)):
            if idNumber != -1 and idNumber >= 0:
                category[2].text = str(idNumber),
        else:
            raise TypeError("Id number must be of type int.")

        # Appended new category to XML
        self.__quiz.append(category)

    def add_question(self, question: QuestionType):
        """
        Add a question in XML Format to the category.

        Args:
            question (QuestionType): Question to be added to the category.

        Raises:
            ValueError: If the input is not type `QuestionType`.
            RepeatedQuestion: If the question is already in the category.
        """
        if isinstance(question, QuestionType):
            if question not in self.__questionList:
                self.__questionList.append(question)
                self.__quiz.append(ET.fromstring(str(question)))
            else:
                raise RepeatedQuestion("This question is already in the list.")
        else:
            raise ValueError("Question must be of type QuestionType.")

    def _cdata_enclose(self, string: str) -> str:
        """
        Encloses the input string in a CDATA tag if it contains HTML.

        Args:
            string (str): Input text to check for HTML tags.

        Returns:
            str: Text enclosed in CDATA if HTML is present; otherwise, unchanged text.
        """
        if "<" in string:
            return f"<![CDATA[{string}]]>"
        else:
            return string

    def __is_valid(self) -> bool:
        """
        Validate if the category contains at least one question.

        Returns:
            bool: True if the category has at least one question and questions hasn't been added before.

        Raises:
            ValueError: If the category does not contain any question.
        """
        if len(self.__questionList) > 0 and not self.__questionsAppended:
            return True
        else:
            raise ValueError("There must be at least one question in the list, and questions must not be already appended.")

    def __str__(self) -> str:
        """
        Generate the XML representation of the category.

        Returns:
            str: The XML representation of the category.

        Raises:
            ValueError: If the category is invalid for not having any question.
        """
        if self.__is_valid():

            ET.indent(self.__quiz)
            quizAsStr = html.unescape(ET.tostring(self.__quiz, encoding='unicode', xml_declaration=True,
                                         short_empty_elements=False))
            # Add a comment in the XML to indicate it was generated by PyMoodleQ.
            comment = "\n<!-- XML generated by PyMoodleQ."
            comment +="\n     https://github.com/juan-lopez/PyMoodleQ -->"
            posAfterXMLDecl = quizAsStr.find("?>") + 2
            quizAsStr = quizAsStr[:posAfterXMLDecl] + comment + quizAsStr[posAfterXMLDecl:]
            return quizAsStr

    def write(self, fileName: str):
        """
        Write the category with its questions to an XML file.

        Args:
            fileName (str): The name of the XML file. Defaults to the category name with a `.xml` extension.

        Raises:
            ValueError: If the category is invalid for not having any question.
                        If a non-blank file name is not provided.
        """
        if fileName is None or fileName.strip() == "":
            raise ValueError("You must supply a file name to write the file to.")
        if not fileName.endswith(".xml"):
            fileName += ".xml"

        if self.__is_valid():
            with open(fileName, "w", encoding="utf-8") as file:
                s = self.__str__()
                file.write(s)

class RepeatedQuestion(Exception):
    """Custom exception for handling repeated questions in a category."""
    pass