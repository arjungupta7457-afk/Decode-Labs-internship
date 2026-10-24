"""
DecodeBot - Rule-Based AI Chatbot (Complete Improved Version)
DecodeLabs AI Internship | Project 1 | Batch 2026

Features:
- Rule-based intent detection with compiled regular expressions
- Safe, restricted AST calculator (no eval)
- Persistent user memory and preferences (JSON)
- Persistent to-do list (JSON)
- Python and DSA mini-quizzes
- Password generation and unit conversion
- Chat history, session statistics, and text logging
- Friendly terminal interface with optional typing effect

Requires Python 3.10+; standard library only.
"""

import ast
import datetime as dt
import difflib
import json
import operator
import os
import random
import re
import secrets
import string
import sys
import time
from pathlib import Path

# ----------------------------------------------------------
# Configuration
# ----------------------------------------------------------
BOT_NAME = "DecodeBot"
DATA_DIR = Path(__file__).resolve().parent / "decodebot_data"
MEMORY_FILE = DATA_DIR / "memory.json"
TODO_FILE = DATA_DIR / "todos.json"
LOG_FILE = DATA_DIR / "chat_log.txt"

TYPING_EFFECT = sys.stdout.isatty()
TYPING_SPEED = 0.008
MAX_TYPING_SECONDS = 1.0
HISTORY_LIMIT = 12
MAX_EXPR_LENGTH = 100
MAX_ABS_RESULT = 10**100
MAX_POWER_EXPONENT = 100
MAX_PASSWORD_LENGTH = 128

if os.name == "nt":
    os.system("")

class Color:
    BOT = "\033[96m"
    USER = "\033[93m"
    INFO = "\033[90m"
    BOLD = "\033[1m"
    ERROR = "\033[91m"
    RESET = "\033[0m"

# ----------------------------------------------------------
# Intent patterns: specific patterns should appear first
# ----------------------------------------------------------
INTENT_PATTERNS = {
    "calc": [
        r"^(?:calc|calculate|compute|solve|what is|what's)\s+(?P<expr>[\d\s.+\-*/()%^]+)\??$",
        r"^(?P<expr>[\d\s.()]+(?:\+|-|\*|/|%|\^)[\d\s.+\-*/()%^]+)$",
    ],
    "how_are_you": [r"\bhow are you\b", r"\bhow(?:'s| is) it going\b", r"\bhow do you do\b"],
    "get_name": [r"\bwhat(?:'s| is) my name\b", r"\bdo you (?:know|remember) my name\b"],
    "memory_show": [r"\bwhat do you remember\b", r"\bshow (?:my )?memory\b", r"\bmy saved memory\b"],
    "memory_clear": [r"^(?:forget everything|clear memory|forget my memory)$"],
    "todo_add": [r"^todo\s+add\s+(?P<task>.+)$", r"^add (?:a )?todo\s+(?P<task>.+)$"],
    "todo_list": [r"^(?:todo\s+list|show todos|list todos|my tasks|show tasks)$"],
    "todo_done": [r"^todo\s+done\s+(?P<number>\d+)$", r"^(?:complete|finish) task\s+(?P<number>\d+)$"],
    "todo_remove": [r"^todo\s+remove\s+(?P<number>\d+)$", r"^delete task\s+(?P<number>\d+)$"],
    "quiz_python": [r"^(?:quiz\s+python|python quiz)$"],
    "quiz_dsa": [r"^(?:quiz\s+dsa|dsa quiz)$"],
    "password": [r"^(?:password|generate password|make a password)(?:\s+(?P<length>\d+))?$"],
    "convert": [r"^convert\s+(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>km|miles?|mi|kg|lbs?|c|celsius|f|fahrenheit)\s+to\s+(?P<target>km|miles?|mi|kg|lbs?|c|celsius|f|fahrenheit)$"],
    "word_count": [r"^count words\s+(?P<text>.+)$"],
    "mood_good": [
        r"\b(?:i'?m|i am|feeling)\s+(?:fine|good|great|awesome|happy|well|ok|okay|not bad)\b",
        r"^(?:fine|good|great|awesome|ok|okay|not bad)\b(?!\s+(?:morning|afternoon|evening|night))",
    ],
    "mood_bad": [r"\b(?:i'?m|i am|feeling)\s+(?:sad|bad|tired|bored|stressed|upset|angry|not good)\b"],
    "set_name": [
        r"\bmy name is (?P<name>[a-z][a-z'-]{0,29}(?:\s+[a-z][a-z'-]{0,29})?)\b",
        r"\bcall me (?P<name>[a-z][a-z'-]{0,29})\b",
        r"^i am (?P<name>[a-z][a-z'-]{0,29})$",
        r"^i'?m (?P<name>[a-z][a-z'-]{0,29})$",
    ],
    "bot_name": [r"\b(?:your name|who are you)\b"],
    "creator": [r"\bwho (?:made|created|built|developed) you\b"],
    "time": [r"^(?:what time is it|tell me the time|time|current time)\??$"],
    "date": [r"^(?:what(?:'s| is) the date|what day is it|today|date|current date)\??$"],
    "joke": [r"\bjoke\b", r"\bmake me laugh\b", r"\bfunny\b"],
    "coin": [r"\bcoin\b", r"\b(?:flip|toss)\b"],
    "dice": [r"\bdice\b", r"\broll\b", r"\bdie\b"],
    "help": [r"^(?:help|commands?|what can you do)\??$"],
    "history": [r"^history$"],
    "stats": [r"^(?:stats|summary)$"],
    "thanks": [r"\b(?:thanks|thank you|thx)\b"],
    "farewell": [r"^(?:bye|goodbye|exit|quit|see you|good night)$"],
    "greeting": [
        r"^(?:hi|hello|hey|hola|namaste|yo)[!. ]*$",
        r"^good (?:morning|afternoon|evening)[!. ]*$",
    ],
}

COMPILED_PATTERNS = {
    intent: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for intent, patterns in INTENT_PATTERNS.items()
}

NOT_NAMES = {
    "hungry", "sleepy", "back", "here", "ready", "new", "busy", "sorry",
    "lost", "confused", "curious", "late", "early", "done", "leaving",
    "fine", "good", "great", "sad", "bad", "tired", "bored", "stressed",
    "okay", "ok", "angry", "happy", "well",
}

RESPONSES = {
    "greeting": [
        "Hello, {name}! How can I help you today?",
        "Hey {name}! Great to see you.",
        "Hi there, {name}! What's on your mind?",
    ],
    "farewell": [
        "Goodbye, {name}! Have a great day.",
        "See you soon, {name}! Keep learning.",
        "Bye {name}! It was nice chatting with you.",
    ],
    "how_are_you": [
        "I'm running smoothly! How about you?",
        "Doing great, thanks for asking. How are you feeling?",
    ],
    "mood_good": ["That's awesome to hear, {name}!", "Glad you're doing well, {name}!"],
    "mood_bad": [
        "Sorry to hear that, {name}. Want a joke to cheer you up? Type 'joke'.",
        "Tough days happen, {name}. Take a short break—you've got this!",
    ],
    "thanks": ["You're welcome, {name}!", "Anytime, {name}!", "Happy to help!"],
    "bot_name": [f"I'm {BOT_NAME}, a rule-based chatbot built with Python."],
    "creator": ["I was built as a Python rule-based chatbot project."],
    "joke": [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the AI break up with the robot? It felt no connection.",
        "There are 10 types of people: those who understand binary and those who don't.",
        "Why was the computer cold? It left its Windows open!",
        "A SQL query walks into a bar and asks two tables: 'Can I join you?'",
    ],
    "unknown": [
        "Hmm, I didn't understand that. Type 'help' to see what I can do.",
        "I'm not sure how to respond to that yet.",
        "That's beyond my rules for now. Try 'help'.",
    ],
}

HELP_TEXT = f"""
{BOT_NAME} commands
-------------------
Conversation:
  hi / hello / good morning
  my name is Alex
  what's my name?
  how are you? / tell me a joke
  time / date / bye

Calculator:
  calc 12 * (3 + 4)
  calc 2^5
  25 / 5
  3 x 4

Memory:
  remember favourite_language = Python
  remember I am learning machine learning
  what do you remember?
  clear memory

To-do list:
  todo add Complete DSA assignment
  todo list
  todo done 1
  todo remove 1

Learning:
  quiz python
  quiz dsa

Developer utilities:
  password [length]       (default length: 16)
  convert 10 km to miles
  convert 32 F to C
  count words Hello world

Session:
  history
  stats
  help
  bye
"""

KEYWORDS = [
    "hello", "bye", "exit", "time", "date", "joke", "help", "history",
    "stats", "calc", "name", "thanks", "coin", "dice", "todo", "quiz",
    "password", "convert", "memory",
]

# ----------------------------------------------------------
# Safe calculator (no eval)
# ----------------------------------------------------------
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval(expression):
    """Evaluate a restricted mathematical expression using Python's AST."""
    expression = expression.strip()
    if not expression or len(expression) > MAX_EXPR_LENGTH:
        raise ValueError("Expression is empty or too long.")

    tree = ast.parse(expression, mode="eval")
    node_count = sum(1 for _ in ast.walk(tree))
    if node_count > 80:
        raise ValueError("Expression is too complex.")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > MAX_ABS_RESULT:
                raise ValueError("Number is too large.")
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow):
                if abs(right) > MAX_POWER_EXPONENT or abs(left) > 10**6:
                    raise ValueError("Exponent or base is too large.")
                if left == 0 and right < 0:
                    raise ZeroDivisionError
            result = OPERATORS[type(node.op)](left, right)

            if isinstance(result, complex) or not isinstance(result, (int, float)):
                raise ValueError("Unsupported result.")
            if abs(result) > MAX_ABS_RESULT:
                raise ValueError("Result is too large.")
            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            result = OPERATORS[type(node.op)](evaluate(node.operand))
            if abs(result) > MAX_ABS_RESULT:
                raise ValueError("Result is too large.")
            return result

        raise ValueError("Unsupported expression.")

    return evaluate(tree)

def normalise(raw):
    """Normalize common punctuation and math symbols."""
    text = raw.lower().strip().replace("\u2019", "'")
    text = text.replace("×", "*").replace("÷", "/")
    # Convert standalone x between numeric operands: 3 x 4 -> 3*4.
    text = re.sub(r"(?<=\d)\s*x\s*(?=[+-]?\d|\()", "*", text)
    return text

def time_of_day_greeting():
    hour = dt.datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"

# ----------------------------------------------------------
# Persistent JSON helpers
# ----------------------------------------------------------
def read_json(path, default):
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except (json.JSONDecodeError, OSError):
        print(f"{Color.INFO}Warning: Could not read {path.name}; using defaults.{Color.RESET}")
        return default

def write_json(path, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    temporary.replace(path)

# ----------------------------------------------------------
# Quiz bank
# ----------------------------------------------------------
QUIZZES = {
    "python": [
        {
            "question": "Which keyword defines a function in Python?",
            "options": ["func", "def", "function", "define"],
            "answer": 1,
            "explanation": "Python functions are declared with the def keyword.",
        },
        {
            "question": "Which data type stores key-value pairs?",
            "options": ["list", "tuple", "dictionary", "set"],
            "answer": 2,
            "explanation": "A dictionary maps keys to values.",
        },
        {
            "question": "What does len('code') return?",
            "options": ["3", "4", "5", "Error"],
            "answer": 1,
            "explanation": "The string 'code' contains four characters.",
        },
        {
            "question": "Which symbol starts a single-line comment in Python?",
            "options": ["//", "#", "/*", "--"],
            "answer": 1,
            "explanation": "A hash symbol (#) starts a Python comment.",
        },
        {
            "question": "What is the result of 3 ** 2 in Python?",
            "options": ["6", "9", "8", "5"],
            "answer": 1,
            "explanation": "The ** operator raises a number to a power: 3 squared is 9.",
        },
    ],
    "dsa": [
        {
            "question": "Which data structure follows LIFO?",
            "options": ["Queue", "Stack", "Graph", "Linked list"],
            "answer": 1,
            "explanation": "A stack follows Last In, First Out.",
        },
        {
            "question": "What is the usual time complexity of binary search on a sorted array?",
            "options": ["O(n)", "O(log n)", "O(n²)", "O(1) always"],
            "answer": 1,
            "explanation": "Binary search halves the remaining search range each step.",
        },
        {
            "question": "Which traversal visits a node, then its left and right subtrees?",
            "options": ["Inorder", "Preorder", "Postorder", "Level order"],
            "answer": 1,
            "explanation": "Preorder traversal follows Root, Left, Right.",
        },
        {
            "question": "Which structure is commonly used for BFS?",
            "options": ["Stack", "Queue", "Heap only", "Hash function"],
            "answer": 1,
            "explanation": "BFS uses a queue to process nodes level by level.",
        },
        {
            "question": "In a singly linked list, each node normally stores data and what link?",
            "options": ["Next pointer", "Parent pointer", "Two child pointers", "No link"],
            "answer": 0,
            "explanation": "A singly linked-list node points to the next node.",
        },
    ],
}

# ----------------------------------------------------------
# Chatbot class
# ----------------------------------------------------------
class DecodeBot:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.memory = read_json(MEMORY_FILE, {"user_name": None, "facts": {}})
        if not isinstance(self.memory, dict):
            self.memory = {"user_name": None, "facts": {}}
        self.memory.setdefault("user_name", None)
        self.memory.setdefault("facts", {})
        self.todos = read_json(TODO_FILE, [])
        if not isinstance(self.todos, list):
            self.todos = []

        self.history = []
        self.start_time = dt.datetime.now()
        self.user_messages = 0
        self.bot_messages = 0
        self.unknown_streak = 0
        self.awaiting_name = False
        self.log_ok = True
        self.running = True
        self.commands_used = {}

    @property
    def user_name(self):
        name = self.memory.get("user_name")
        return name if isinstance(name, str) else None

    def save_memory(self):
        try:
            write_json(MEMORY_FILE, self.memory)
        except OSError as err:
            self.say_info(f"Memory could not be saved: {err}")

    def save_todos(self):
        try:
            write_json(TODO_FILE, self.todos)
        except OSError as err:
            self.say_info(f"Tasks could not be saved: {err}")

    def log(self, speaker, message):
        if not self.log_ok:
            return
        stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # One physical log line per message makes logs easier to inspect.
        safe_message = str(message).replace("\r", "\\r").replace("\n", "\\n")
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(f"[{stamp}] {speaker}: {safe_message}\n")
        except OSError as err:
            self.log_ok = False
            self.say_info(f"Logging disabled: {err}")

    def record(self, speaker, message):
        self.history.append((speaker, str(message)))
        self.log(speaker, message)

    def say_info(self, message):
        print(f"{Color.INFO}{message}{Color.RESET}")

    def bot_say(self, message):
        print(f"{Color.BOT}{Color.BOLD}{BOT_NAME}:{Color.RESET} {Color.BOT}", end="")
        if TYPING_EFFECT and message:
            delay = min(TYPING_SPEED, MAX_TYPING_SECONDS / max(1, len(message)))
            for char in message:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
            print(Color.RESET)
        else:
            print(message + Color.RESET)
        self.bot_messages += 1
        self.record(BOT_NAME, message)

    def pick(self, key):
        return random.choice(RESPONSES[key]).format(name=self.user_name or "friend")

    def detect_intent(self, text):
        for intent, patterns in COMPILED_PATTERNS.items():
            for pattern in patterns:
                match = pattern.search(text)
                if not match:
                    continue
                if intent == "set_name":
                    candidate = match.groupdict().get("name", "").strip()
                    if candidate.lower() in NOT_NAMES or any(part.lower() in NOT_NAMES for part in candidate.split()):
                        continue
                return intent, match
        # Treat plain arithmetic as calculator input.
        if re.fullmatch(r"[\d\s.+\-*/()%^]+", text) and re.search(r"[+\-*/%^]", text):
            return "calc", re.match(r"(?P<expr>.+)", text)
        return "unknown", None

    def respond(self, intent, match, text):
        if intent == "greeting":
            return self.pick("greeting")
        if intent == "farewell":
            self.running = False
            return self.pick("farewell")
        if intent == "how_are_you":
            return self.pick("how_are_you")
        if intent == "mood_good":
            return self.pick("mood_good")
        if intent == "mood_bad":
            return self.pick("mood_bad")
        if intent == "set_name":
            return self.set_user_name(match.group("name"))
        if intent == "get_name":
            return f"Of course! Your name is {self.user_name}." if self.user_name else "You haven't told me your name yet. Try: my name is Alex"
        if intent == "memory_show":
            return self.show_memory()
        if intent == "memory_clear":
            self.memory = {"user_name": None, "facts": {}}
            self.save_memory()
            return "Saved personal memory has been cleared."
        if intent == "todo_add":
            return self.todo_add(match.group("task"))
        if intent == "todo_list":
            return self.todo_list()
        if intent == "todo_done":
            return self.todo_done(int(match.group("number")))
        if intent == "todo_remove":
            return self.todo_remove(int(match.group("number")))
        if intent == "quiz_python":
            return self.run_quiz("python")
        if intent == "quiz_dsa":
            return self.run_quiz("dsa")
        if intent == "password":
            return self.generate_password(match.groupdict().get("length"))
        if intent == "convert":
            return self.convert_units(float(match.group("value")), match.group("unit"), match.group("target"))
        if intent == "word_count":
            return self.count_words(match.group("text"))
        if intent == "bot_name":
            return self.pick("bot_name")
        if intent == "creator":
            return self.pick("creator")
        if intent == "time":
            return f"The current time is {dt.datetime.now().strftime('%I:%M %p')}."
        if intent == "date":
            return f"Today is {dt.datetime.now().strftime('%A, %d %B %Y')}."
        if intent == "calc":
            return self.calculate(match.groupdict().get("expr") or text)
        if intent == "joke":
            return self.pick("joke")
        if intent == "coin":
            return f"I flipped a coin: it's {random.choice(['Heads', 'Tails'])}!"
        if intent == "dice":
            return f"I rolled a die: you got {random.randint(1, 6)}!"
        if intent == "help":
            return HELP_TEXT
        if intent == "history":
            return self.show_history()
        if intent == "stats":
            return self.show_stats()
        if intent == "thanks":
            return self.pick("thanks")
        if text.startswith("remember "):
            return self.remember_fact(text[len("remember "):])
        return self.fallback(text)

    def set_user_name(self, name):
        cleaned = " ".join(part.capitalize() for part in name.strip().split())
        if not cleaned or len(cleaned) > 61 or any(part.lower() in NOT_NAMES for part in cleaned.split()):
            return "I didn't catch a name there. Try: my name is Alex"
        self.memory["user_name"] = cleaned
        self.save_memory()
        self.awaiting_name = False
        return f"Nice to meet you, {cleaned}! I'll remember your name."

    def remember_fact(self, raw_fact):
        fact = raw_fact.strip()
        if not fact:
            return "Tell me what to remember, for example: remember favourite_language = Python"
        if "=" in fact:
            key, value = fact.split("=", 1)
            key, value = key.strip(), value.strip()
            if not key or not value:
                return "Use this format: remember key = value"
            if len(key) > 60 or len(value) > 250:
                return "Please keep the memory key under 60 characters and value under 250."
            self.memory["facts"][key] = value
            self.save_memory()
            return f"I saved this: {key} = {value}"
        if len(fact) > 250:
            return "That memory is too long. Please keep it under 250 characters."
        timestamp = dt.datetime.now().strftime("%Y-%m-%d")
        self.memory["facts"][f"note_{timestamp}_{len(self.memory['facts']) + 1}"] = fact
        self.save_memory()
        return "I'll save that note in your local memory."

    def show_memory(self):
        lines = []
        if self.user_name:
            lines.append(f"Name: {self.user_name}")
        facts = self.memory.get("facts", {})
        if isinstance(facts, dict):
            lines.extend(f"{key}: {value}" for key, value in facts.items())
        if not lines:
            return "I don't have any saved personal details yet. Try: remember favourite_language = Python"
        return "Saved memory:\n" + "\n".join(f"  - {line}" for line in lines)

    def calculate(self, expr):
        expr = expr.strip().rstrip("?").replace("^", "**")
        try:
            result = safe_eval(expr)
        except ZeroDivisionError:
            return "Oops! Division by zero is not allowed."
        except (ValueError, SyntaxError, TypeError, OverflowError, RecursionError):
            return "I couldn't calculate that safely. Try: calc 12 * (3 + 4)"
        if isinstance(result, float):
            result = int(result) if result.is_integer() else round(result, 6)
        display_expr = expr.replace("**", "^")
        return f"{display_expr} = {result}"

    def todo_add(self, task):
        task = task.strip()
        if not task:
            return "Please provide a task. Example: todo add Complete DSA assignment"
        if len(task) > 200:
            return "Please keep a task under 200 characters."
        self.todos.append({"task": task, "done": False, "created": dt.datetime.now().isoformat(timespec="seconds")})
        self.save_todos()
        return f"Added task #{len(self.todos)}: {task}"

    def todo_list(self):
        if not self.todos:
            return "Your to-do list is empty. Add one with: todo add Complete DSA"
        lines = ["Your tasks:"]
        for index, item in enumerate(self.todos, start=1):
            status = "x" if item.get("done") else " "
            lines.append(f"  {index}. [{status}] {item.get('task', '(unnamed task)')}")
        return "\n".join(lines)

    def todo_done(self, number):
        if number < 1 or number > len(self.todos):
            return f"Task number must be between 1 and {len(self.todos)}."
        self.todos[number - 1]["done"] = True
        self.save_todos()
        return f"Marked task #{number} as complete."

    def todo_remove(self, number):
        if number < 1 or number > len(self.todos):
            return f"Task number must be between 1 and {len(self.todos)}."
        removed = self.todos.pop(number - 1)
        self.save_todos()
        return f"Removed task #{number}: {removed.get('task', '(unnamed task)')}"

    def run_quiz(self, topic):
        questions = QUIZZES[topic]
        score = 0
        lines = [f"{topic.upper()} QUIZ — {len(questions)} questions"]
        for number, question in enumerate(questions, start=1):
            lines.append(f"\n{number}. {question['question']}")
            for option_index, option in enumerate(question["options"]):
                lines.append(f"   {chr(65 + option_index)}. {option}")
            while True:
                try:
                    answer = input(f"{Color.USER}Your answer (A-D, or Q to stop): {Color.RESET}").strip().upper()
                except (EOFError, KeyboardInterrupt):
                    return f"Quiz stopped. Score so far: {score}/{number - 1}."
                if answer == "Q":
                    return f"Quiz stopped. Score so far: {score}/{number - 1}."
                if answer in ("A", "B", "C", "D"):
                    break
                print("Please enter A, B, C, D, or Q.")
            selected = ord(answer) - ord("A")
            if selected == question["answer"]:
                score += 1
                lines.append("   Result: Correct!")
            else:
                correct = question["options"][question["answer"]]
                lines.append(f"   Result: Not quite. Correct answer: {correct}")
            lines.append(f"   Explanation: {question['explanation']}")
        lines.append(f"\nFinal score: {score}/{len(questions)}")
        return "\n".join(lines)

    def generate_password(self, requested_length):
        try:
            length = int(requested_length) if requested_length else 16
        except ValueError:
            return "Password length must be a whole number."
        if length < 8 or length > MAX_PASSWORD_LENGTH:
            return f"Choose a password length from 8 to {MAX_PASSWORD_LENGTH}."
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        # Guarantee at least one character from each of the main character groups.
        chars = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice("!@#$%^&*()-_=+"),
        ]
        chars.extend(secrets.choice(alphabet) for _ in range(length - len(chars)))
        secrets.SystemRandom().shuffle(chars)
        return f"Generated password ({length} characters): {''.join(chars)}\nKeep it private and store it in a trusted password manager."

    def convert_units(self, value, source, target):
        def category(unit):
            if unit in ("km", "mile", "miles", "mi"):
                return "distance"
            if unit in ("kg", "lb", "lbs"):
                return "weight"
            if unit in ("c", "celsius", "f", "fahrenheit"):
                return "temperature"
            return None

        source = source.lower()
        target = target.lower()
        aliases = {"mile": "miles", "mi": "miles", "lb": "lbs", "kg": "kg",
                   "c": "celsius", "f": "fahrenheit"}
        source = aliases.get(source, source)
        target = aliases.get(target, target)
        if category(source) != category(target):
            return "Those units cannot be converted to each other. Try km to miles, kg to lbs, or C to F."
        if source == target:
            result = value
        elif source == "km" and target == "miles":
            result = value * 0.621371
        elif source == "miles" and target == "km":
            result = value / 0.621371
        elif source == "kg" and target == "lbs":
            result = value * 2.2046226218
        elif source == "lbs" and target == "kg":
            result = value / 2.2046226218
        elif source == "celsius" and target == "fahrenheit":
            result = value * 9 / 5 + 32
        elif source == "fahrenheit" and target == "celsius":
            result = (value - 32) * 5 / 9
        else:
            return "I can't convert that pair yet."
        return f"{value:g} {source} = {result:.4f} {target}".rstrip("0").rstrip(".")

    def count_words(self, text):
        words = re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)
        return f"Words: {len(words)} | Characters: {len(text)} | Characters without spaces: {len(''.join(text.split()))}"

    def show_history(self):
        past = self.history[-HISTORY_LIMIT:]
        if not past:
            return "No chat history yet."
        lines = [f"  {speaker}: {message.splitlines()[0][:180]}" for speaker, message in past]
        return "Last messages:\n" + "\n".join(lines)

    def show_stats(self):
        duration = dt.datetime.now() - self.start_time
        minutes, seconds = divmod(int(duration.total_seconds()), 60)
        command_summary = ", ".join(f"{key}={value}" for key, value in sorted(self.commands_used.items()))
        return (
            "Session stats:\n"
            f"  User             : {self.user_name or 'Unknown'}\n"
            f"  User messages    : {self.user_messages}\n"
            f"  Bot replies      : {self.bot_messages}\n"
            f"  Duration         : {minutes}m {seconds}s\n"
            f"  Tasks saved      : {len(self.todos)}\n"
            f"  Commands used    : {command_summary or 'None yet'}"
        )

    def fallback(self, text):
        self.unknown_streak += 1
        for word in text.translate(str.maketrans("", "", string.punctuation)).split():
            suggestion = difflib.get_close_matches(word, KEYWORDS, n=1, cutoff=0.75)
            if suggestion:
                return f"I didn't get that. Did you mean '{suggestion[0]}'?"
        if self.unknown_streak >= 3:
            return "I'm still learning. Type 'help' to see commands I understand."
        return self.pick("unknown")

    def banner(self):
        print(Color.BOLD + "=" * 58)
        print(f"   {BOT_NAME} - Rule-Based AI Chatbot | DecodeLabs")
        print("=" * 58 + Color.RESET)
        print(f"{Color.INFO}Type 'help' for commands, 'bye' to exit.{Color.RESET}\n")
        self.log("SYSTEM", "---- Session started ----")

    def run(self):
        self.banner()
        if not self.user_name:
            self.bot_say(f"{time_of_day_greeting()}! I'm {BOT_NAME}. What's your name?")
            self.awaiting_name = True
        else:
            self.bot_say(f"{time_of_day_greeting()}! Welcome back, {self.user_name}.")

        while self.running:
            try:
                label = self.user_name or "You"
                raw = input(f"{Color.USER}{Color.BOLD}{label}:{Color.RESET} ")
            except (KeyboardInterrupt, EOFError):
                print()
                self.bot_say("Session interrupted. Goodbye!")
                break

            text = normalise(raw)
            if not text:
                self.bot_say("You didn't type anything. Say something!")
                continue

            self.user_messages += 1
            self.record("User", raw)
            intent, match = self.detect_intent(text)

            if self.awaiting_name:
                if intent == "unknown" and re.fullmatch(r"[a-zA-Z][a-zA-Z'-]{0,29}(?:\s+[a-zA-Z][a-zA-Z'-]{0,29})?", text):
                    reply = self.set_user_name(text)
                    self.awaiting_name = False
                    self.bot_say(reply)
                    continue
                if intent == "set_name":
                    self.awaiting_name = False
                elif intent not in ("greeting", "how_are_you"):
                    self.awaiting_name = False

            if intent != "unknown":
                self.unknown_streak = 0
                self.commands_used[intent] = self.commands_used.get(intent, 0) + 1

            try:
                reply = self.respond(intent, match, text)
            except Exception as err:
                # Keep the interactive session alive if a feature encounters an unexpected error.
                self.log("ERROR", f"{type(err).__name__}: {err}")
                reply = "Something went wrong while processing that command. Please try again."
            self.bot_say(reply)

        print(f"\n{Color.INFO}{self.show_stats()}")
        print(f"Data folder: {DATA_DIR}")
        print(f"Chat log: {LOG_FILE}{Color.RESET}")
        self.log("SYSTEM", "---- Session ended ----")

if __name__ == "__main__":
    try:
        DecodeBot().run()
    except OSError as error:
        print(f"Could not start DecodeBot: {error}")
