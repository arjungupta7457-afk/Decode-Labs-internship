"""
==========================================================
  DecodeBot - Rule-Based AI Chatbot  (improved version)
  DecodeLabs AI Internship | Project 1 | Batch 2026
  Author : <Your Name>
==========================================================
  Concepts used:
    - Control flow (if / elif / else)
    - Continuous loop (while)
    - Pattern matching (pre-compiled regex) for intent detection
    - State / memory (user name, history, "awaiting name")
    - Safe expression evaluation (AST)
    - File logging & exception handling
==========================================================
"""

import ast
import datetime
import difflib
import operator
import os
import random
import re
import string
import sys
import time

# ----------------------------------------------------------
# Configuration
# ----------------------------------------------------------
BOT_NAME = "DecodeBot"
LOG_FILE = "chat_log.txt"
TYPING_EFFECT = sys.stdout.isatty()   # auto-off when output is piped/redirected
TYPING_SPEED = 0.012                  # seconds per character
MAX_TYPING_SECONDS = 1.5              # long replies never take longer than this
HISTORY_LIMIT = 10                    # messages shown by the 'history' command
MAX_EXPR_LENGTH = 100                 # calculator input limit

if os.name == "nt":                   # enable ANSI colours on Windows terminals
    os.system("")


class Color:
    BOT = "\033[96m"       # cyan
    USER = "\033[93m"      # yellow
    INFO = "\033[90m"      # grey
    BOLD = "\033[1m"
    RESET = "\033[0m"


# ----------------------------------------------------------
# Knowledge Base: intent patterns (ORDER MATTERS -
# more specific intents are checked before general ones)
# ----------------------------------------------------------
INTENT_PATTERNS = {
    "calc": [
        r"^(?:calc|calculate|compute|solve|what is|what's)\s+(?P<expr>[\d\s.+\-*/()%^]+)\??$",
        r"^(?P<expr>[\d\s.()]+[+\-*/%^][\d\s.+\-*/()%^]+)$",
    ],
    "how_are_you": [r"how are you", r"how('?s| is) it going", r"how do you do"],
    "mood_good": [
        r"\b(i'?m|i am|feeling)\s+(fine|good|great|awesome|happy|well|ok|okay|not bad)\b",
        # "good morning / good night" must NOT be treated as a mood
        r"^(fine|good|great|awesome|ok|okay|not bad)\b(?!\s+(morning|afternoon|evening|night))",
    ],
    "mood_bad": [
        r"\b(i'?m|i am|feeling)\s+(sad|bad|tired|bored|stressed|upset|angry|not good)\b",
    ],
    "get_name": [r"what('?s| is) my name", r"do you (know|remember) my name"],
    "set_name": [
        r"\bmy name is (?P<name>[a-z]+)",
        r"\bcall me (?P<name>[a-z]+)",
        r"^i am (?P<name>[a-z]+)$",
        r"^i'?m (?P<name>[a-z]+)$",
    ],
    "bot_name": [r"your name", r"who are you"],
    "creator": [r"who (made|created|built|developed) you"],
    "time": [r"\btime\b"],
    "date": [r"\bdate\b", r"\bwhat day\b", r"\btoday\b"],
    "joke": [r"\bjoke\b", r"make me laugh", r"\bfunny\b"],
    "coin": [r"\bcoin\b", r"\b(flip|toss)\b"],
    "dice": [r"\bdice\b", r"\broll\b", r"\bdie\b"],
    "help": [r"\bhelp\b", r"what can you do", r"\bcommands?\b"],
    "history": [r"\bhistory\b"],
    "stats": [r"\bstats\b", r"\bsummary\b"],
    "thanks": [r"\b(thanks|thank you|thx)\b"],
    "farewell": [r"\b(bye|goodbye|exit|quit|see you|good night)\b"],
    "greeting": [r"\b(hi|hello|hey|hola|namaste|yo)\b",
                 r"\bgood (morning|afternoon|evening)\b"],
}

# Compile once at start-up instead of on every message.
COMPILED_PATTERNS = {
    intent: [re.compile(p) for p in patterns]
    for intent, patterns in INTENT_PATTERNS.items()
}

# Words that follow "I'm ..." but are clearly not names.
NOT_NAMES = {
    "hungry", "sleepy", "back", "here", "ready", "new", "busy", "sorry",
    "lost", "confused", "curious", "late", "early", "done", "leaving",
    "fine", "good", "great", "sad", "bad", "tired", "bored", "stressed",
}

RESPONSES = {
    "greeting": ["Hello, {name}! How can I help you today?",
                 "Hey {name}! Great to see you.",
                 "Hi there, {name}! What's on your mind?"],
    "farewell": ["Goodbye, {name}! Have a great day.",
                 "See you soon, {name}! Keep learning.",
                 "Bye {name}! It was nice chatting with you."],
    "how_are_you": ["I'm running at 100% efficiency! How about you?",
                    "Doing great, thanks for asking! How are you feeling?"],
    "mood_good": ["That's awesome to hear, {name}!",
                  "Glad you're doing well, {name}!"],
    "mood_bad": ["Sorry to hear that, {name}. Want a joke to cheer you up? Type 'joke'.",
                 "Tough days happen, {name}. Take a short break - you've got this!"],
    "thanks": ["You're welcome, {name}!", "Anytime, {name}!", "Happy to help!"],
    "bot_name": [f"I'm {BOT_NAME}, a rule-based chatbot built with Python."],
    "creator": ["I was built by an AI intern at DecodeLabs as Project 1!"],
    "joke": ["Why do programmers prefer dark mode? Because light attracts bugs!",
             "Why did the AI break up with the robot? It felt no connection.",
             "There are 10 types of people: those who understand binary and those who don't.",
             "Why was the computer cold? It left its Windows open!",
             "A SQL query walks into a bar and asks two tables: 'Can I join you?'"],
    "unknown": ["Hmm, I didn't understand that. Type 'help' to see what I can do.",
                "I'm not sure how to respond to that yet.",
                "That's beyond my rules for now! Try 'help'."],
}

HELP_TEXT = """Here's what I can do:
  - Greet me             -> hi / hello / good morning
  - Tell me your name    -> my name is Alex
  - Ask your name        -> what's my name?
  - Time & date          -> what time is it? / what's the date?
  - Calculator           -> calc 12 * (3 + 4)  or  25 / 5  or  3 x 4
  - Jokes                -> tell me a joke
  - Games                -> flip a coin / roll a dice
  - Chat history         -> history
  - Session stats        -> stats
  - Exit                 -> bye / exit / quit"""

KEYWORDS = ["hello", "bye", "exit", "time", "date", "joke", "help",
            "history", "stats", "calc", "name", "thanks", "coin", "dice"]


# ----------------------------------------------------------
# Safe calculator (no eval!)
# ----------------------------------------------------------
OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def safe_eval(expression):
    """Evaluate a maths expression safely using Python's AST."""
    if len(expression) > MAX_EXPR_LENGTH:
        raise ValueError("Expression too long")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        # type() check (not isinstance) so True/False are rejected
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left, right = _eval(node.left), _eval(node.right)
            if isinstance(node.op, ast.Pow) and (abs(right) > 100 or abs(left) > 1e6):
                raise ValueError("Exponent too large")
            return OPERATORS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported expression")

    return _eval(ast.parse(expression, mode="eval"))


def normalise(raw):
    """Lower-case, tidy quotes and accept friendly maths symbols."""
    text = raw.lower().strip().replace("\u2019", "'")
    text = text.replace("\u00d7", "*").replace("\u00f7", "/")
    text = re.sub(r"(?<=\d)\s*x\s*(?=\d)", "*", text)     # 3 x 4 -> 3*4
    return text


def time_of_day_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


# ----------------------------------------------------------
# Chatbot class
# ----------------------------------------------------------
class DecodeBot:
    def __init__(self):
        self.user_name = None
        self.history = []                 # list of (speaker, message)
        self.start_time = datetime.datetime.now()
        self.user_messages = 0
        self.unknown_streak = 0
        self.awaiting_name = False        # True right after we ask for a name
        self.log_ok = True                # flips to False if the log can't be written
        self.running = True

    # ---------- Utility ----------
    def log(self, speaker, message):
        if not self.log_ok:
            return
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{stamp}] {speaker}: {message}\n")
        except OSError as err:
            self.log_ok = False
            print(f"{Color.INFO}(Logging disabled: {err}){Color.RESET}")

    def record(self, speaker, message):
        self.history.append((speaker, message))
        self.log(speaker, message)

    def bot_say(self, message):
        print(f"{Color.BOT}{Color.BOLD}{BOT_NAME}:{Color.RESET} {Color.BOT}", end="")
        if TYPING_EFFECT and message:
            # Cap total time so long replies (like 'help') don't crawl.
            delay = min(TYPING_SPEED, MAX_TYPING_SECONDS / len(message))
            for ch in message:
                sys.stdout.write(ch)
                sys.stdout.flush()
                time.sleep(delay)
            print(Color.RESET)
        else:
            print(message + Color.RESET)
        self.record(BOT_NAME, message)

    def pick(self, key):
        """Pick a random reply and personalise it."""
        return random.choice(RESPONSES[key]).format(name=self.user_name or "friend")

    # ---------- Step 1: Understand ----------
    def detect_intent(self, text):
        for intent, patterns in COMPILED_PATTERNS.items():
            for pattern in patterns:
                match = pattern.search(text)
                if not match:
                    continue
                # "I'm hungry" is not a name - keep looking.
                if intent == "set_name" and match.group("name") in NOT_NAMES:
                    continue
                return intent, match
        return "unknown", None

    # ---------- Step 2: Decide (if-else engine) ----------
    def respond(self, intent, match, text):
        if intent == "greeting":
            return self.pick("greeting")

        elif intent == "farewell":
            self.running = False
            return self.pick("farewell")

        elif intent == "how_are_you":
            return self.pick("how_are_you")

        elif intent == "mood_good":
            return self.pick("mood_good")

        elif intent == "mood_bad":
            return self.pick("mood_bad")

        elif intent == "set_name":
            return self.set_user_name(match.group("name"))

        elif intent == "get_name":
            if self.user_name:
                return f"Of course! Your name is {self.user_name}."
            return "You haven't told me yet. Try: 'My name is ...'"

        elif intent == "bot_name":
            return self.pick("bot_name")

        elif intent == "creator":
            return self.pick("creator")

        elif intent == "time":
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."

        elif intent == "date":
            return f"Today is {datetime.datetime.now().strftime('%A, %d %B %Y')}."

        elif intent == "calc":
            return self.calculate(match.group("expr"))

        elif intent == "joke":
            return self.pick("joke")

        elif intent == "coin":
            return f"I flipped a coin: it's {random.choice(['Heads', 'Tails'])}!"

        elif intent == "dice":
            return f"I rolled a dice: you got {random.randint(1, 6)}!"

        elif intent == "help":
            return HELP_TEXT

        elif intent == "history":
            return self.show_history()

        elif intent == "stats":
            return self.show_stats()

        elif intent == "thanks":
            return self.pick("thanks")

        else:
            return self.fallback(text)

    # ---------- Feature handlers ----------
    def set_user_name(self, name):
        self.user_name = name.capitalize()
        return f"Nice to meet you, {self.user_name}! I'll remember your name."

    def calculate(self, expr):
        expr = expr.replace("^", "**").strip()
        try:
            result = safe_eval(expr)
        except ZeroDivisionError:
            return "Oops! Division by zero is not allowed."
        except (ValueError, SyntaxError, TypeError, OverflowError, RecursionError):
            return "I couldn't calculate that. Try: calc 12 * (3 + 4)"
        if isinstance(result, float):
            result = int(result) if result.is_integer() else round(result, 4)
        return f"{expr.replace('**', '^')} = {result}"

    def show_history(self):
        past = self.history[-HISTORY_LIMIT:]
        if not past:
            return "No chat history yet."
        lines = [f"  {speaker}: {msg.splitlines()[0]}" for speaker, msg in past]
        return "Last messages:\n" + "\n".join(lines)

    def show_stats(self):
        duration = datetime.datetime.now() - self.start_time
        minutes, seconds = divmod(int(duration.total_seconds()), 60)
        return (f"Session stats:\n"
                f"  User      : {self.user_name or 'Unknown'}\n"
                f"  Messages  : {self.user_messages}\n"
                f"  Duration  : {minutes}m {seconds}s")

    def fallback(self, text):
        self.unknown_streak += 1
        # Strip punctuation so "helo!" still suggests "hello".
        for word in text.translate(str.maketrans("", "", string.punctuation)).split():
            suggestion = difflib.get_close_matches(word, KEYWORDS, n=1, cutoff=0.75)
            if suggestion:
                return f"I didn't get that. Did you mean '{suggestion[0]}'?"
        if self.unknown_streak >= 3:
            return "I'm still learning! Type 'help' to see everything I understand."
        return self.pick("unknown")

    def try_bare_name(self, text):
        """Accept 'Alex' or 'Priya Sharma' as an answer to 'What's your name?'."""
        words = text.split()
        if 1 <= len(words) <= 2 and all(w.isalpha() and len(w) <= 20 for w in words):
            if words[0] not in NOT_NAMES:
                self.user_name = " ".join(w.capitalize() for w in words)
                return f"Nice to meet you, {self.user_name}! I'll remember your name."
        return None

    # ---------- Main loop ----------
    def banner(self):
        print(Color.BOLD + "=" * 55)
        print(f"   {BOT_NAME} - Rule-Based AI Chatbot | DecodeLabs")
        print("=" * 55 + Color.RESET)
        print(f"{Color.INFO}Type 'help' for commands, 'bye' to exit.{Color.RESET}\n")
        self.log("SYSTEM", "---- Session started ----")

    def run(self):
        self.banner()
        self.bot_say(f"{time_of_day_greeting()}! I'm {BOT_NAME}. What's your name?")
        self.awaiting_name = True

        while self.running:                       # continuous loop
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

            # Right after we ask for a name, a plain "Alex" counts as the answer.
            if self.awaiting_name:
                if intent == "unknown":
                    reply = self.try_bare_name(text)
                    if reply:
                        self.awaiting_name = False
                        self.bot_say(reply)
                        continue
                elif intent not in ("greeting", "how_are_you"):
                    self.awaiting_name = False    # user moved on to something else
                if intent == "set_name":
                    self.awaiting_name = False

            if intent != "unknown":
                self.unknown_streak = 0

            self.bot_say(self.respond(intent, match, text))

        print(f"\n{Color.INFO}{self.show_stats()}")
        print(f"Chat saved to '{LOG_FILE}'.{Color.RESET}")
        self.log("SYSTEM", "---- Session ended ----\n")


# ----------------------------------------------------------
if __name__ == "__main__":
    DecodeBot().run()