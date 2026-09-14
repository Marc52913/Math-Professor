import random
import re
from fractions import Fraction

import streamlit as st

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Math Professor",
    page_icon="∑",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CURRICULUM
# ============================================================

CURRICULUM = {
    "Foundations": [
        "Counting",
        "Addition",
        "Subtraction",
        "Multiplication",
        "Division",
        "Order of Operations",
        "Fractions",
        "Decimals",
        "Percentages",
        "Ratios and Proportions",
        "Negative Numbers",
        "Factors and Multiples",
    ],
    "Pre-Algebra": [
        "Variables",
        "Algebraic Expressions",
        "Exponents",
        "Square Roots",
        "Simplifying Expressions",
        "Linear Equations",
        "Inequalities",
        "Word Problems",
    ],
    "Algebra": [
        "Polynomials",
        "Factoring",
        "Special Products",
        "Quadratic Equations",
        "Systems of Equations",
        "Rational Expressions",
        "Radicals",
        "Functions",
        "Exponential Functions",
        "Logarithms",
        "Sequences and Series",
    ],
    "Geometry": [
        "Angles",
        "Triangles",
        "Congruence",
        "Similarity",
        "Pythagorean Theorem",
        "Circles",
        "Coordinate Geometry",
        "Area and Volume",
        "Geometric Proofs",
    ],
    "Trigonometry": [
        "Sine",
        "Cosine",
        "Tangent",
        "Unit Circle",
        "Trigonometric Identities",
        "Trigonometric Equations",
        "Inverse Trigonometric Functions",
        "Law of Sines",
        "Law of Cosines",
    ],
    "Precalculus": [
        "Advanced Functions",
        "Polynomial Functions",
        "Rational Functions",
        "Exponential and Logarithmic Functions",
        "Parametric Equations",
        "Polar Coordinates",
        "Sequences and Series",
        "Limits",
    ],
    "Calculus": [
        "Limits",
        "Continuity",
        "Derivatives",
        "Applications of Derivatives",
        "Integrals",
        "Fundamental Theorem of Calculus",
        "Applications of Integration",
        "Differential Equations",
        "Multivariable Calculus",
        "Partial Derivatives",
        "Multiple Integrals",
        "Vector Calculus",
    ],
    "University Mathematics": [
        "Linear Algebra",
        "Matrices",
        "Vector Spaces",
        "Eigenvalues and Eigenvectors",
        "Differential Equations",
        "Probability",
        "Statistics",
        "Discrete Mathematics",
        "Number Theory",
        "Mathematical Logic",
        "Combinatorics",
        "Graph Theory",
        "Numerical Methods",
    ],
    "Advanced Mathematics": [
        "Real Analysis",
        "Complex Analysis",
        "Abstract Algebra",
        "Group Theory",
        "Ring Theory",
        "Measure Theory",
        "Topology",
        "Functional Analysis",
        "Partial Differential Equations",
        "Optimization",
        "Mathematical Modeling",
    ],
}

LEVEL_ORDER = list(CURRICULUM.keys())


LESSONS = {
    "Addition": (
        "Addition combines quantities. "
        "For example, 7 + 5 means start at 7 and increase by 5."
    ),
    "Subtraction": (
        "Subtraction finds the difference between quantities. "
        "It can also be viewed as adding the opposite."
    ),
    "Multiplication": (
        "Multiplication is repeated addition. "
        "For example, 4 × 3 means four groups of three."
    ),
    "Division": (
        "Division separates a quantity into equal groups. "
        "If 20 ÷ 5 = 4, then 20 contains four groups of 5."
    ),
    "Order of Operations": (
        "Use parentheses first, then exponents, then multiplication or division, "
        "and finally addition or subtraction. Operations at the same level are "
        "performed from left to right."
    ),
    "Fractions": (
        "A fraction a/b represents a divided by b, where b cannot be zero. "
        "The numerator counts parts and the denominator tells how many equal parts make a whole."
    ),
    "Decimals": (
        "Decimals represent parts of a whole using place value. "
        "Tenths, hundredths, and thousandths correspond to powers of ten."
    ),
    "Percentages": (
        "A percentage is a ratio out of 100. "
        "For example, 25% = 25/100 = 1/4."
    ),
    "Ratios and Proportions": (
        "A ratio compares quantities. A proportion states that two ratios are equal."
    ),
    "Negative Numbers": (
        "Negative numbers lie below zero on the number line. "
        "Adding a negative is equivalent to subtracting its positive magnitude."
    ),
    "Variables": (
        "A variable is a symbol representing a quantity. "
        "In 3x + 2, x is the variable and 3 is its coefficient."
    ),
    "Algebraic Expressions": (
        "An algebraic expression consists of variables, coefficients, and constants. "
        "Variables represent numbers, coefficients multiply variables, and constants "
        "are terms without variables. Expressions may be monomials, binomials, or "
        "trinomials. You can evaluate expressions by substitution and the order of "
        "operations, expand them using the Distributive Property, and simplify them "
        "by combining like terms."
    ),
    "Special Products": (
        "Special products are rules that provide faster ways to multiply algebraic "
        "expressions. Important forms include the product of two binomials using FOIL, "
        "the square of a binomial, the product of a sum and difference, the cube of "
        "a binomial, and the product of a binomial and a trinomial."
    ),
    "Exponents": (
        "An exponent tells how many times a base is used as a factor. "
        "For example, 2^4 = 2 × 2 × 2 × 2 = 16."
    ),
    "Square Roots": (
        "The square root of a nonnegative number is the nonnegative value whose square equals that number."
    ),
    "Linear Equations": (
        "A linear equation has variables to the first power. "
        "The goal is to isolate the variable while preserving equality."
    ),
    "Inequalities": (
        "Inequalities compare quantities. When multiplying or dividing both sides by a negative number, reverse the inequality sign."
    ),
    "Polynomials": (
        "A polynomial is a sum of terms involving nonnegative integer powers of variables."
    ),
    "Factoring": (
        "Factoring rewrites an expression as a product of simpler expressions."
    ),
    "Quadratic Equations": (
        "A quadratic equation has the form ax² + bx + c = 0 with a ≠ 0. "
        "Common methods include factoring, completing the square, and the quadratic formula."
    ),
    "Functions": (
        "A function assigns exactly one output to each input in its domain."
    ),
    "Limits": (
        "A limit describes the value a function approaches as the input approaches a particular value."
    ),
    "Derivatives": (
        "A derivative measures instantaneous rate of change. "
        "Geometrically, it is the slope of the tangent line."
    ),
    "Integrals": (
        "An integral can represent accumulated change or signed area. "
        "An indefinite integral represents a family of antiderivatives."
    ),
    "Probability": (
        "Probability measures how likely an event is. "
        "For equally likely outcomes, P(E) = favorable outcomes / total outcomes."
    ),
    "Linear Algebra": (
        "Linear algebra studies vectors, matrices, linear transformations, and systems of linear equations."
    ),
}


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "selected_level": "Foundations",
    "selected_topic": "Addition",
    "difficulty": 1,
    "score": 0,
    "attempts": 0,
    "correct": 0,
    "streak": 0,
    "best_streak": 0,
    "current_problem": None,
    "feedback": None,
    "show_solution": False,
    "chat_messages": [],
    "last_ai_request": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPERS
# ============================================================

def all_topics():
    return [topic for topics in CURRICULUM.values() for topic in topics]


def difficulty_label(level):
    return {
        1: "Beginner",
        2: "Basic",
        3: "Intermediate",
        4: "Advanced",
        5: "Challenge",
    }.get(level, "Intermediate")


def update_difficulty():
    streak = st.session_state.streak
    if streak >= 8:
        st.session_state.difficulty = min(5, st.session_state.difficulty + 1)
    elif streak == 0:
        st.session_state.difficulty = max(1, st.session_state.difficulty - 1)


def normalize_answer(value):
    text = str(value).strip().lower()
    text = text.replace("×", "*").replace("÷", "/").replace("−", "-")
    text = text.replace(",", "")
    text = re.sub(r"\s+", "", text)
    return text


def numeric_equal(user_answer, correct_answer):
    try:
        a = float(Fraction(str(user_answer)))
        b = float(Fraction(str(correct_answer)))
        return abs(a - b) < 1e-9
    except Exception:
        return normalize_answer(user_answer) == normalize_answer(correct_answer)


def answer_matches(user_answer, expected):
    if user_answer is None:
        return False

    user = normalize_answer(user_answer)

    if isinstance(expected, (list, tuple, set)):
        return any(answer_matches(user, item) for item in expected)

    expected_text = normalize_answer(expected)

    if user == expected_text:
        return True

    return numeric_equal(user, expected_text)


def make_problem(question, answer, solution, hint, topic):
    return {
        "question": question,
        "answer": answer,
        "solution": solution,
        "hint": hint,
        "topic": topic,
    }


# ============================================================
# PROBLEM GENERATORS
# ============================================================

def generate_problem(topic, difficulty):
    d = max(1, min(5, difficulty))

    if topic == "Addition":
        a = random.randint(1, 20 * d)
        b = random.randint(1, 20 * d)
        return make_problem(
            f"{a} + {b} = ?",
            a + b,
            f"{a} + {b} = {a + b}",
            "Combine the two quantities.",
            topic,
        )

    if topic == "Subtraction":
        a = random.randint(10, 30 * d)
        b = random.randint(1, a)
        return make_problem(
            f"{a} − {b} = ?",
            a - b,
            f"{a} − {b} = {a - b}",
            "Subtract the second number from the first.",
            topic,
        )

    if topic == "Multiplication":
        a = random.randint(2, 12 * d)
        b = random.randint(2, 12 * d)
        return make_problem(
            f"{a} × {b} = ?",
            a * b,
            f"{a} × {b} = {a * b}",
            f"Think of {a} groups of {b}.",
            topic,
        )

    if topic == "Division":
        b = random.randint(2, 10 * d)
        q = random.randint(2, 12 * d)
        a = b * q
        return make_problem(
            f"{a} ÷ {b} = ?",
            q,
            f"{a} ÷ {b} = {q}",
            "Ask how many groups of the divisor fit into the dividend.",
            topic,
        )

    if topic == "Order of Operations":
        a = random.randint(2, 8 * d)
        b = random.randint(2, 6)
        c = random.randint(1, 10)
        answer = a + b * c
        return make_problem(
            f"{a} + {b} × {c} = ?",
            answer,
            f"Multiply first: {b} × {c} = {b*c}. Then {a} + {b*c} = {answer}.",
            "Multiplication comes before addition.",
            topic,
        )

    if topic == "Percentages":
        percent = random.choice([10, 20, 25, 30, 40, 50])
        number = random.randint(2, 20) * 10
        answer = number * percent / 100
        return make_problem(
            f"What is {percent}% of {number}?",
            answer,
            f"{percent}% = {percent}/100, so ({percent}/100) × {number} = {answer:g}.",
            "Convert the percentage to a decimal or fraction.",
            topic,
        )

    if topic == "Fractions":
        denominator = random.randint(2, 9)
        n1 = random.randint(1, denominator - 1)
        n2 = random.randint(1, denominator - 1)
        result = Fraction(n1 + n2, denominator)
        return make_problem(
            f"{n1}/{denominator} + {n2}/{denominator} = ?",
            str(result),
            f"Keep the denominator {denominator}: "
            f"({n1} + {n2})/{denominator} = {n1+n2}/{denominator} = {result}.",
            "The denominators already match, so add the numerators.",
            topic,
        )

    if topic == "Variables":
        x = random.randint(1, 10)
        a = random.randint(2, 8)
        b = random.randint(1, 10)
        answer = a * x + b
        return make_problem(
            f"If x = {x}, evaluate {a}x + {b}.",
            answer,
            f"Substitute x = {x}: {a}({x}) + {b} = {answer}.",
            "Replace x with its given value.",
            topic,
        )

    if topic == "Algebraic Expressions":
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        return make_problem(
            f"Simplify: {a}x + {b}x",
            f"{a+b}x",
            f"Combine like terms: ({a} + {b})x = {a+b}x.",
            "Look for terms with the same variable and exponent.",
            topic,
        )

    if topic == "Special Products":
        a = random.randint(2, 8); b = random.randint(2, 9)
        kind = random.choice(["square", "difference", "foildemo"])
        if kind == "square":
            return make_problem(f"Expand: ({a}x + {b})²", f"{a*a}x² + {2*a*b}x + {b*b}", f"Use (A + B)² = A² + 2AB + B².", "Square the first term, double the product, then square the second term.", topic)
        if kind == "difference":
            return make_problem(f"Expand: ({a}x + {b})({a}x − {b})", f"{a*a}x² − {b*b}", f"Use (A + B)(A − B) = A² − B².", "Use the difference of squares identity.", topic)
        c = random.randint(1, 7); e = random.randint(1, 7)
        return make_problem(f"Expand: ({a}x + {c})({b}x + {e})", f"{a*b}x² + {a*e + b*c}x + {c*e}", "Use FOIL: First, Outer, Inner, Last, then combine like terms.", "Multiply First, Outer, Inner, and Last.", topic)

    if topic == "Exponents":
        base = random.randint(2, 5)
        exponent = random.randint(2, 4 + d // 2)
        answer = base ** exponent
        return make_problem(
            f"{base}^{exponent} = ?",
            answer,
            f"{base}^{exponent} means multiplying {base} by itself {exponent} times: {answer}.",
            "The exponent counts the factors of the base.",
            topic,
        )

    if topic == "Linear Equations":
        x = random.randint(-10, 10)
        a = random.randint(2, 9)
        b = random.randint(-12, 12)
        c = a * x + b
        sign = "+" if b >= 0 else "−"
        shown_b = abs(b)
        question = f"Solve: {a}x {sign} {shown_b} = {c}"
        solution = (
            f"Subtract {b} from both sides: {a}x = {c-b}. "
            f"Divide by {a}: x = {x}."
        )
        return make_problem(question, x, solution, "Undo addition or subtraction first, then multiplication or division.", topic)

    if topic == "Factoring":
        p = random.randint(1, 9)
        q = random.randint(1, 9)
        b = p + q
        c = p * q
        return make_problem(
            f"Factor: x² + {b}x + {c}",
            f"(x+{p})(x+{q})",
            f"Find two numbers whose product is {c} and sum is {b}: {p} and {q}. "
            f"Therefore x² + {b}x + {c} = (x + {p})(x + {q}).",
            f"Find two numbers that multiply to {c} and add to {b}.",
            topic,
        )

    if topic == "Quadratic Equations":
        p = random.randint(1, 6)
        q = random.randint(1, 6)
        b = p + q
        c = p * q
        return make_problem(
            f"Solve: x² + {b}x + {c} = 0",
            f"x=-{p}, x=-{q}",
            f"Factor: (x + {p})(x + {q}) = 0. "
            f"Set each factor to zero: x = −{p} or x = −{q}.",
            "Try factoring the quadratic first.",
            topic,
        )

    if topic == "Functions":
        x = random.randint(-5, 5)
        a = random.randint(2, 6)
        b = random.randint(-5, 5)
        value = a * x + b
        sign = "+" if b >= 0 else "−"
        return make_problem(
            f"If f(x) = {a}x {sign} {abs(b)}, find f({x}).",
            value,
            f"Substitute x = {x}: f({x}) = {a}({x}) + ({b}) = {value}.",
            "Substitute the input into the function rule.",
            topic,
        )

    if topic == "Limits":
        a = random.randint(-5, 5)
        b = random.randint(1, 9)
        answer = a + b
        return make_problem(
            f"Find lim(x→{a}) [x + {b}].",
            answer,
            f"This function is continuous, so substitute x = {a}: {a} + {b} = {answer}.",
            "For a polynomial or linear function, direct substitution works.",
            topic,
        )

    if topic == "Derivatives":
        n = random.randint(2, 5)
        coefficient = random.randint(2, 7)
        answer = f"{coefficient*n}x^{n-1}"
        return make_problem(
            f"Find d/dx ({coefficient}x^{n}).",
            answer,
            f"Use the power rule d/dx[x^n] = nx^(n−1). "
            f"Therefore d/dx[{coefficient}x^{n}] = {coefficient*n}x^{n-1}.",
            "Use the power rule.",
            topic,
        )

    if topic == "Integrals":
        n = random.randint(1, 4)
        coefficient = random.randint(2, 6)
        power = n + 1
        answer = f"{coefficient}/{power}x^{power}+C"
        return make_problem(
            f"Integrate: ∫ {coefficient}x^{n} dx",
            answer,
            f"Increase the exponent by 1 and divide by the new exponent: "
            f"({coefficient}/{power})x^{power} + C.",
            "Use the power rule for integration.",
            topic,
        )

    if topic == "Probability":
        total = random.randint(5, 20)
        favorable = random.randint(1, total - 1)
        result = Fraction(favorable, total)
        return make_problem(
            f"An experiment has {total} equally likely outcomes. "
            f"{favorable} are favorable. What is P(E)?",
            str(result),
            f"P(E) = favorable outcomes / total outcomes = {favorable}/{total} = {result}.",
            "Use P(E) = favorable outcomes ÷ total outcomes.",
            topic,
        )

    if topic == "Linear Algebra":
        a = random.randint(1, 6)
        b = random.randint(1, 6)
        return make_problem(
            f"Compute the determinant of [[{a}, 0], [0, {b}]].",
            a * b,
            f"For a diagonal 2×2 matrix, det = {a}×{b} = {a*b}.",
            "For [[a,0],[0,b]], the determinant is ab.",
            topic,
        )

    # Generic prompt for topics without a local generator.
    return make_problem(
        f"Use the AI Professor to study: {topic}.",
        "",
        "Open the Professor tab and ask for a lesson, example, or problem on this topic.",
        "Ask the AI Professor to teach the topic from first principles.",
        topic,
    )


# ============================================================
# OPENAI
# ============================================================

def get_api_key():
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        return ""


def get_ai_client():
    if not OPENAI_AVAILABLE:
        return None

    key = get_api_key()
    if not key:
        return None

    try:
        return OpenAI(api_key=key)
    except Exception:
        return None


def build_system_prompt():
    level = st.session_state.selected_level
    topic = st.session_state.selected_topic
    difficulty = difficulty_label(st.session_state.difficulty)

    return f"""
You are an expert mathematics professor and patient tutor.

Current learner context:
- Curriculum level: {level}
- Current topic: {topic}
- Difficulty: {difficulty}
- Current streak: {st.session_state.streak}

Teaching rules:
1. Teach from first principles when the learner is confused.
2. Never assume a step is obvious if it is important to understanding.
3. Use correct mathematical notation and explain symbols.
4. Give a concise explanation first, then a worked example when useful.
5. When checking a student's work, identify the exact step where the reasoning becomes invalid.
6. Do not simply give an answer when the learner is clearly trying to learn. Guide them with a hint first unless they explicitly request the full solution.
7. If the learner asks for a full solution, show the algebra or reasoning step by step.
8. Adjust the depth to the learner's level.
9. For advanced mathematics, state definitions before using theorems or formulas.
10. Challenge incorrect assumptions instead of agreeing with them.
11. Distinguish exact answers from approximations.
12. For calculations, show enough work to make the method reproducible.
13. Keep responses organized with headings, equations, and short steps.
14. Do not claim that an answer is correct unless the reasoning supports it.
15. If a problem is ambiguous, state the ambiguity and make a reasonable assumption.
16. When creating practice problems, do not reveal the answer immediately unless requested.
17. Encourage understanding, not memorization.

You can teach anything from basic arithmetic through calculus, linear algebra,
probability, discrete mathematics, analysis, abstract algebra, topology, and other
university-level mathematics.
"""


def ask_ai(user_message):
    client = get_ai_client()

    if client is None:
        return (
            "The AI Professor is not connected yet.\n\n"
            "Make sure the `openai` package is installed and that "
            "`OPENAI_API_KEY` is stored in `.streamlit/secrets.toml`."
        )

    try:
        recent = st.session_state.chat_messages[-10:]
        conversation = []

        for message in recent:
            conversation.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

        conversation.append({"role": "user", "content": user_message})

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=build_system_prompt(),
            input=conversation,
        )

        text = getattr(response, "output_text", None)
        if text:
            return text

        return "I received a response, but it did not contain readable text."

    except Exception as exc:
        return (
            "The AI request failed.\n\n"
            f"Error: `{exc}`\n\n"
            "Check your API key, internet connection, package installation, "
            "and selected model."
        )


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    /* Main application */
    .stApp {
        background: #071a12;
        color: #e8f5ee;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 85% 5%, rgba(22, 101, 52, 0.22), transparent 28%),
            linear-gradient(135deg, #071a12 0%, #0a2117 52%, #071810 100%);
    }

    [data-testid="stHeader"] {
        background: rgba(7, 26, 18, 0.82);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #05140d;
        border-right: 1px solid #174d32;
    }

    [data-testid="stSidebar"] * {
        color: #e8f5ee;
    }

    /* Titles */
    .main-title {
        color: #f0fff6;
        font-size: 2.55rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        color: #9bc7ad;
        margin-bottom: 1.35rem;
    }

    /* Cards */
    .stat-card {
        padding: 1rem;
        min-height: 92px;
        border-radius: 16px;
        border: 1px solid #1b5e3a;
        background: linear-gradient(145deg, #0d2b1d, #0a2117);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
        text-align: center;
    }

    .stat-number {
        color: #c9f7d9;
        font-size: 1.75rem;
        font-weight: 800;
    }

    .stat-label {
        color: #82b997;
        font-size: 0.82rem;
    }

    .problem-box {
        padding: 1.35rem;
        border-radius: 16px;
        border: 1px solid #247447;
        background: linear-gradient(145deg, #103823, #0b281a);
        margin: 0.7rem 0 1.1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    }

    /* Inputs */
    .stTextInput input,
    .stTextArea textarea {
        background: #0a2117 !important;
        color: #effff5 !important;
        border: 1px solid #24633f !important;
        border-radius: 10px !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #45a86d !important;
        box-shadow: 0 0 0 1px #45a86d !important;
    }

    /* Select boxes and sliders */
    [data-baseweb="select"] > div {
        background: #0a2117 !important;
        border-color: #24633f !important;
        color: #effff5 !important;
    }

    /* Buttons */
    .stButton > button {
        background: #126b3a;
        color: #f2fff7;
        border: 1px solid #23814b;
        border-radius: 10px;
        font-weight: 650;
        transition: all 0.18s ease;
    }

    .stButton > button:hover {
        background: #18884a;
        border-color: #4bbd76;
        color: white;
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: #159447;
        border-color: #37b968;
        color: white;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #081d13;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #174d32;
    }

    .stTabs [data-baseweb="tab"] {
        color: #8fbea2;
        border-radius: 8px;
    }

    .stTabs [aria-selected="true"] {
        color: #eafff1 !important;
        background: #124e2e;
    }

    /* Chat */
    [data-testid="stChatMessage"] {
        border: 1px solid #174d32;
        background: rgba(10, 33, 23, 0.72);
        border-radius: 14px;
        margin-bottom: 0.7rem;
    }

    [data-testid="stChatInput"] {
        background: #0a2117;
        border: 1px solid #24633f;
    }

    [data-testid="stChatInput"] textarea {
        color: #effff5 !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid #24633f;
    }

    /* Dividers and general muted text */
    hr {
        border-color: #174d32 !important;
    }

    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: #82b997 !important;
    }

    /* Code blocks */
    [data-testid="stCodeBlock"] {
        background: #04110b !important;
        border: 1px solid #174d32;
    }

    /* Links */
    a {
        color: #69d98f !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("∑ AI Math Professor")
    st.caption("From arithmetic to advanced mathematics")

    level = st.selectbox(
        "Curriculum level",
        LEVEL_ORDER,
        index=LEVEL_ORDER.index(st.session_state.selected_level),
    )

    if level != st.session_state.selected_level:
        st.session_state.selected_level = level
        st.session_state.selected_topic = CURRICULUM[level][0]
        st.session_state.current_problem = None
        st.session_state.feedback = None

    topic = st.selectbox(
        "Topic",
        CURRICULUM[level],
        index=CURRICULUM[level].index(st.session_state.selected_topic),
    )

    if topic != st.session_state.selected_topic:
        st.session_state.selected_topic = topic
        st.session_state.current_problem = None
        st.session_state.feedback = None

    st.divider()

    st.session_state.difficulty = st.slider(
        "Difficulty",
        min_value=1,
        max_value=5,
        value=st.session_state.difficulty,
        format="%d",
    )

    st.caption(f"Current: **{difficulty_label(st.session_state.difficulty)}**")

    st.divider()

    if st.button("Reset progress", use_container_width=True):
        for key in ["score", "attempts", "correct", "streak", "best_streak"]:
            st.session_state[key] = DEFAULTS[key]
        st.session_state.current_problem = None
        st.session_state.feedback = None
        st.session_state.show_solution = False
        st.rerun()

    if st.button("Clear chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown('<div class="main-title">AI Math Professor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Learn mathematics from basic arithmetic to university-level theory.</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f'<div class="stat-card"><div class="stat-number">{st.session_state.score}</div>'
        '<div class="stat-label">Score</div></div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f'<div class="stat-card"><div class="stat-number">{st.session_state.correct}</div>'
        '<div class="stat-label">Correct</div></div>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f'<div class="stat-card"><div class="stat-number">{st.session_state.streak}</div>'
        '<div class="stat-label">Streak</div></div>',
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f'<div class="stat-card"><div class="stat-number">{st.session_state.best_streak}</div>'
        '<div class="stat-label">Best streak</div></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN TABS
# ============================================================

tab_professor, tab_lesson, tab_practice, tab_tools = st.tabs(
    ["Professor", "Lesson", "Practice", "Math Tools"]
)


# ============================================================
# PROFESSOR TAB
# ============================================================

with tab_professor:
    st.subheader("Ask the Professor")

    api_connected = get_ai_client() is not None

    if api_connected:
        st.success("AI Professor connected.")
    else:
        st.info(
            "AI mode is not connected. Practice and built-in lessons still work. "
            "Add OPENAI_API_KEY to `.streamlit/secrets.toml` to enable the chatbot."
        )

    if not st.session_state.chat_messages:
        st.markdown(
            f"""
            **Current lesson:** {st.session_state.selected_topic}

            Try:
            - `Teach me this topic from the beginning.`
            - `Give me a practice problem.`
            - `Explain this like I am a beginner.`
            - `Check my solution: ...`
            - `Why does this formula work?`
            """
        )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        f"Ask about {st.session_state.selected_topic}..."
    )

    if prompt:
        st.session_state.chat_messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Professor is thinking..."):
                answer = ask_ai(prompt)
            st.markdown(answer)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": answer}
        )

    st.divider()

    quick1, quick2, quick3 = st.columns(3)

    with quick1:
        if st.button("Teach this topic", use_container_width=True):
            request = (
                f"Teach me {st.session_state.selected_topic} from first principles. "
                "Start with the definition, then give one simple example and one "
                "slightly harder example."
            )
            st.session_state.chat_messages.append({"role": "user", "content": request})
            answer = ask_ai(request)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()

    with quick2:
        if st.button("Give me a challenge", use_container_width=True):
            request = (
                f"Give me one {difficulty_label(st.session_state.difficulty)} "
                f"practice problem on {st.session_state.selected_topic}. "
                "Do not reveal the answer unless I ask."
            )
            st.session_state.chat_messages.append({"role": "user", "content": request})
            answer = ask_ai(request)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()

    with quick3:
        if st.button("Explain a common mistake", use_container_width=True):
            request = (
                f"What is a common mistake students make when learning "
                f"{st.session_state.selected_topic}? Explain how to avoid it."
            )
            st.session_state.chat_messages.append({"role": "user", "content": request})
            answer = ask_ai(request)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()


# ============================================================
# LESSON TAB
# ============================================================

with tab_lesson:
    st.subheader(st.session_state.selected_topic)

    explanation = LESSONS.get(
        st.session_state.selected_topic,
        f"{st.session_state.selected_topic} is part of the {st.session_state.selected_level} curriculum.",
    )

    st.write(explanation)

    st.markdown("### Learning approach")
    st.markdown(
        """
        1. Understand the definition.
        2. Study a worked example.
        3. Try a problem yourself.
        4. Check the reasoning.
        5. Increase difficulty only after the method is understood.
        """
    )

    if st.button("Ask AI for a full lesson"):
        request = (
            f"Teach a complete lesson on {st.session_state.selected_topic}. "
            "Use this structure: definition, intuition, notation, worked example, "
            "common mistakes, then two practice problems without answers."
        )
        if not api_connected:
            st.warning("Connect the AI API in secrets.toml first.")
        else:
            answer = ask_ai(request)
            st.markdown(answer)


# ============================================================
# PRACTICE TAB
# ============================================================

with tab_practice:
    st.subheader("Practice")

    if st.button("Generate new problem", type="primary"):
        st.session_state.current_problem = generate_problem(
            st.session_state.selected_topic,
            st.session_state.difficulty,
        )
        st.session_state.feedback = None
        st.session_state.show_solution = False

    problem = st.session_state.current_problem

    if problem is None:
        st.info("Generate a problem to begin.")
    else:
        st.markdown(
            f'<div class="problem-box"><strong>{problem["topic"]}</strong><br><br>'
            f'<span style="font-size:1.35rem">{problem["question"]}</span></div>',
            unsafe_allow_html=True,
        )

        user_answer = st.text_input(
            "Your answer",
            key="practice_answer",
            placeholder="Enter your answer...",
        )

        b1, b2, b3 = st.columns(3)

        with b1:
            if st.button("Check answer", use_container_width=True):
                if not user_answer.strip():
                    st.warning("Enter an answer first.")
                else:
                    st.session_state.attempts += 1

                    if answer_matches(user_answer, problem["answer"]):
                        st.session_state.correct += 1
                        st.session_state.score += 10 * st.session_state.difficulty
                        st.session_state.streak += 1
                        st.session_state.best_streak = max(
                            st.session_state.best_streak,
                            st.session_state.streak,
                        )
                        update_difficulty()
                        st.session_state.feedback = ("correct", "Correct. Your answer matches.")
                    else:
                        st.session_state.streak = 0
                        update_difficulty()
                        st.session_state.feedback = (
                            "incorrect",
                            "Not quite. Check your reasoning and try again.",
                        )

        with b2:
            if st.button("Show hint", use_container_width=True):
                st.session_state.feedback = ("hint", problem["hint"])

        with b3:
            if st.button("Show solution", use_container_width=True):
                st.session_state.show_solution = True

        if st.session_state.feedback:
            kind, message = st.session_state.feedback

            if kind == "correct":
                st.success(message)
            elif kind == "hint":
                st.info(f"Hint: {message}")
            else:
                st.error(message)

        if st.session_state.show_solution:
            st.markdown("### Solution")
            st.write(problem["solution"])
            st.caption(f"Expected answer: {problem['answer']}")

        st.caption(
            f"Difficulty: {difficulty_label(st.session_state.difficulty)} • "
            f"Accuracy: "
            f"{(st.session_state.correct / st.session_state.attempts * 100):.0f}%"
            if st.session_state.attempts
            else f"Difficulty: {difficulty_label(st.session_state.difficulty)}"
        )


# ============================================================
# MATH TOOLS TAB
# ============================================================

with tab_tools:
    st.subheader("Math Toolbox")

    if not SYMPY_AVAILABLE:
        st.warning("SymPy is not installed. Run: python -m pip install sympy")
    else:
        tool = st.selectbox(
            "Choose a tool",
            [
                "Simplify",
                "Factor",
                "Expand",
                "Solve",
                "Differentiate",
                "Integrate",
            ],
        )

        expression = st.text_input(
            "Expression",
            placeholder="Examples: x^2 + 2*x + 1, x^2 - 5*x + 6",
        )

        variable = st.text_input("Variable", value="x")

        if st.button("Calculate", type="primary"):
            try:
                expr = sp.sympify(expression.replace("^", "**"))
                symbol = sp.Symbol(variable)

                if tool == "Simplify":
                    result = sp.simplify(expr)
                elif tool == "Factor":
                    result = sp.factor(expr)
                elif tool == "Expand":
                    result = sp.expand(expr)
                elif tool == "Solve":
                    result = sp.solve(expr, symbol)
                elif tool == "Differentiate":
                    result = sp.diff(expr, symbol)
                else:
                    result = sp.integrate(expr, symbol)

                st.latex(sp.latex(result))
                st.code(str(result))

            except Exception as exc:
                st.error(f"Could not process the expression: {exc}")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(
    "AI Math Professor • Built for learning, practice, and mathematical reasoning"
)
