import pymoodleq
import random
import re

# Constants
AMOUNTOFQUESTIONS = 10
HIGHESTEXPONENT = 2 # Keep this > 1
MINCOEFFICIENT = -9
MAXCOEFFICIENT = 9

def generate_polynomial():
    coefficient = get_coefficient(plusSign = False, nonZero = True) # Leading coefficient
    polynomial = f"{coefficient}x^{HIGHESTEXPONENT}" # Assumed that HIGHESTEXPONENT > 1
    for term in range(HIGHESTEXPONENT-1, 1, -1):
        coefficient = get_coefficient(nonZero = True)
        polynomial += f"{coefficient}x^{term}"
    # We do linear and constant term "manually"
    coefficient = get_coefficient(nonZero = True)
    polynomial += f"{coefficient}x"
    coefficient = get_coefficient(nonZero = True, lastTerm = True)
    polynomial += coefficient
    return polynomial


def get_coefficient(plusSign = True, nonZero = False, lastTerm = False):
    """Generate a random coefficient and return the corresponding string.

    Args:
        plusSign (bool): Whether to include the '+' in case the coefficient is positive.
        nonZero (bool): Whether to accept 0 or generate a non-zero value.
        lastTerm (bool): Whether this is the last term, then cannot be '+' or '-'

    Returns:
        A string representation of the coefficient to be used in the polynomial.
        If the number is -1, only - is returned.
        If the number is 1, either '+' or an empty string is returned (depends on plusSign).
        If the number is 0, +0 is returned.
    """
    while True:
        number = random.randint(MINCOEFFICIENT, MAXCOEFFICIENT)
        if number < -1:
            return str(number)
        elif number == -1:
            return "-" if not lastTerm else "-1"
        elif number == 0:
            if not nonZero:
                return "+0"
        elif number == 1:
            if lastTerm:
                return "+1"
            else:
                return "+" if plusSign else ""
        else: # number > 1
            return f"+{number}" if plusSign else str(number)

def derive_polynomial(poly_str):
    # Remove spaces and replace minus with +- to easily split by +
    poly_str = poly_str.replace(" ", "").replace("-", "+-")
    terms = [t for t in poly_str.split("+") if t]

    derived_terms = []

    # Pattern to match: (coefficient)x^(exponent)
    # Groups: 1: coefficient, 2: x, 3: exponent
    pattern = re.compile(r'([+-]?\d*)?(x)?(?:\^(\d+))?')

    for term in terms:
        match = pattern.fullmatch(term)
        if not match: continue

        coeff_str, has_x, exp_str = match.groups()

        # Handle coefficient defaults
        if coeff_str in (None, "", "+"): coeff = 1
        elif coeff_str == "-": coeff = -1
        else: coeff = int(coeff_str)

        # Handle exponent defaults
        if not has_x:  # Constant term (e.g., "5")
            continue   # Derivative is 0

        exp = int(exp_str) if exp_str else 1

        # Power Rule: d/dx [ax^n] = (a*n)x^(n-1)
        new_coeff = coeff * exp
        new_exp = exp - 1

        if new_exp == 0:
            derived_terms.append(f"{new_coeff}")
        elif new_exp == 1:
            derived_terms.append(f"{new_coeff}x")
        else:
            derived_terms.append(f"{new_coeff}x^{new_exp}")

    # Clean up the output string (joining and fixing "+-")
    result = "+".join(derived_terms).replace("+-", "-")
    return result if result else "0"

# Example Usage:
# print(derive_polynomial("3x^3 + 4x^2 - 5x + 10")) # Output: 9x^2+8x-5

theQuiz = pymoodleq.Quiz()
theQuiz.add_category("Derivatives")

for i in range(AMOUNTOFQUESTIONS):
    polynomial = generate_polynomial()
    derivative = derive_polynomial(polynomial)
    question = pymoodleq.ShortAnswer()
    question.set_question(f"Derivative of {polynomial}",
                          f"Find the derivative of \\( {polynomial} \\).")
    question.set_grade(5)
    question.add_answer(100, derivative, "Correct!")
    theQuiz.add_question(question)

theQuiz.write("ex_sa_derivatives.xml")