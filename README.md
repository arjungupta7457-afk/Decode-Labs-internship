# DecodeBot — Rule-Based AI Chatbot

**DecodeLabs AI Internship | Project 1 | Batch 2026**

DecodeBot is a Python-based, rule-driven chatbot that interacts with users through a terminal interface. It uses regular expressions for intent detection, a restricted Abstract Syntax Tree (AST) calculator for safe mathematical operations, and JSON files to store user memory and to-do lists between sessions.

The project demonstrates fundamental concepts of Python programming, including object-oriented programming, file handling, exception handling, regular expressions, data structures, and persistent storage.

## Features

- **Rule-Based Conversations:** Responds to greetings, farewells, moods, questions about the bot, and common conversational messages.
- **Intent Detection:** Uses compiled regular expressions to recognize supported commands.
- **Safe Calculator:** Evaluates mathematical expressions using Python's AST module without using `eval()`.
- **Persistent User Memory:** Stores the user's name, preferences, and personal notes in a JSON file.
- **To-Do Manager:** Adds, lists, completes, and removes tasks with persistent JSON storage.
- **Python Quiz:** Tests basic Python knowledge with multiple-choice questions and explanations.
- **DSA Quiz:** Tests fundamental Data Structures and Algorithms concepts.
- **Password Generator:** Generates random passwords using a cryptographically secure random source.
- **Unit Converter:** Converts distance, weight, and temperature units.
- **Word Counter:** Counts words, characters, and characters excluding whitespace.
- **Chat History:** Displays recent messages from the current session.
- **Session Statistics:** Tracks messages, bot replies, session duration, tasks, and commands used.
- **Text Logging:** Saves chat messages and session events to a local text file.
- **Typing Effect:** Displays a typing animation in supported terminal environments.
- **Error Handling:** Handles common input errors and attempts to keep the chatbot running when a feature encounters an unexpected exception.

## Technologies Used

- **Programming Language:** Python 3.10+
- **Standard Library Modules:** `ast`, `datetime`, `difflib`, `json`, `operator`, `os`, `random`, `re`, `secrets`, `string`, `sys`, `time`, and `pathlib`
- **Data Storage:** JSON and TXT files
- **Interface:** Command-line / terminal interface

No third-party Python packages are required.

## Project Structure

After running the chatbot, the project directory will contain the following structure:

```text
DecodeBot/
│
├── DecodeBot.py
├── README.md
│
└── decodebot_data/
    ├── memory.json
    ├── todos.json
    └── chat_log.txt
```

**File descriptions:**

- `DecodeBot.py` — Main Python file containing the chatbot implementation.
- `README.md` — Project documentation and usage instructions.
- `memory.json` — Stores the user's name, preferences, and saved notes.
- `todos.json` — Stores to-do tasks and their completion status.
- `chat_log.txt` — Records chat messages and session events.

The `decodebot_data` directory and its data files are created automatically when needed.

## Requirements

- Python 3.10 or later
- A terminal or command-line interface
- A code editor such as Visual Studio Code (optional)

## Installation and Setup

### Step 1: Install Python

Download Python from the official website:

https://www.python.org/downloads/

During installation on Windows, enable **Add Python to PATH** if that option is available.

Verify the installation:

```bash
python --version
```

If the `python` command is unavailable on Windows, try:

```bash
py --version
```

### Step 2: Download or Clone the Project

If you have downloaded the project files, extract them into a folder named `DecodeBot`.

Alternatively, if the project is hosted on GitHub, clone it using:

```bash
git clone YOUR_REPOSITORY_URL
```

Replace `YOUR_REPOSITORY_URL` with the actual repository URL.

### Step 3: Open the Project Folder

Open the project folder in Visual Studio Code, or navigate to it using your terminal:

```bash
cd DecodeBot
```

Make sure `DecodeBot.py` is present in the current directory.

### Step 4: Run DecodeBot

On Windows:

```bash
python DecodeBot.py
```

Alternatively:

```bash
py DecodeBot.py
```

On macOS or Linux:

```bash
python3 DecodeBot.py
```

No `pip install` command or virtual environment is necessary for this standard-library-only version.

## How to Use DecodeBot

When launched, DecodeBot displays a welcome message and asks for your name if no name has previously been saved.

Type a supported command and press Enter. To see the available commands at any time, enter:

```text
help
```

To end the session, enter:

```text
bye
```

## Command Reference

### 1. Conversation

| Command | Description |
|---|---|
| `hi` | Responds to a greeting |
| `hello` | Greets the user |
| `good morning` | Responds to a morning greeting |
| `my name is Alex` | Saves the user's name |
| `what's my name?` | Retrieves the saved name |
| `how are you?` | Responds to a conversational question |
| `joke` | Tells a programming joke |
| `time` | Displays the current time |
| `date` | Displays the current date |
| `bye` | Ends the session |

### 2. Calculator

The calculator supports arithmetic operations such as addition, subtraction, multiplication, division, modulo, exponentiation, and parentheses.

Examples:

```text
calc 12 * (3 + 4)
calc 2^5
25 / 5
3 x 4
```

Example output:

```text
DecodeBot: 12 * (3 + 4) = 84
```

The calculator uses a restricted AST evaluator instead of Python's `eval()` function. This limits the expressions that can be executed.

### 3. User Memory

Examples:

```text
remember favourite_language = Python
remember learning machine learning
what do you remember?
what's my name?
clear memory
```

Memory is stored locally in `decodebot_data/memory.json` and can be reused in future sessions.

**Note:** The `clear memory` command clears the saved name and personal facts managed by DecodeBot. It does not delete the chat log or saved to-do list.

### 4. To-Do Manager

Examples:

```text
todo add Complete DSA assignment
todo add Practice Python
todo list
todo done 1
todo remove 2
```

Tasks are saved in `decodebot_data/todos.json` so they remain available after restarting the chatbot.

Task numbers correspond to their current positions in the list.

### 5. Python and DSA Quizzes

Start a quiz using:

```text
quiz python
```

Or:

```text
quiz dsa
```

Each quiz contains five multiple-choice questions. DecodeBot checks answers, provides explanations, and calculates the final score.

Enter `A`, `B`, `C`, or `D` to answer a question. Enter `Q` to stop the quiz early.

### 6. Password Generator

Generate a default 16-character password:

```text
password
```

Generate a password with a specific length:

```text
password 24
```

The supported password length is 8–128 characters. The generator guarantees at least one lowercase letter, one uppercase letter, one digit, and one supported special character.

Keep generated passwords private and store them securely.

### 7. Unit Converter

Supported conversions include distance, weight, and temperature.

Examples:

```text
convert 10 km to miles
convert 5 miles to km
convert 10 kg to lbs
convert 32 F to C
convert 25 C to F
```

### 8. Word Counter

Example:

```text
count words Hello world, welcome to DecodeBot!
```

The response includes the word count, total character count, and character count excluding whitespace.

### 9. Session Management

| Command | Description |
|---|---|
| `history` | Shows recent messages from the current session |
| `stats` | Displays session statistics |
| `help` | Displays the command guide |
| `bye` | Ends the conversation |

Chat history shown by the `history` command is limited to recent messages in the current session. The text log is maintained separately in `chat_log.txt`.

## Data Storage and Privacy

DecodeBot stores its data locally in the `decodebot_data` directory.

- `memory.json` contains saved user details and notes.
- `todos.json` contains saved tasks.
- `chat_log.txt` contains logged conversation messages and session events.

These files are not encrypted by the application. Avoid saving passwords, API keys, or other sensitive information in chatbot memory. If you share the project publicly, do not commit personal memory files or chat logs to your repository.

## Error Handling and Security

DecodeBot includes several protective measures:

- Restricted AST-based mathematical evaluation rather than unrestricted `eval()`.
- Limits on expression length, complexity, exponent size, and numeric results.
- Password generation using Python's `secrets` module.
- Input length checks for memory entries and tasks.
- JSON file handling with basic recovery from missing or invalid files.
- Exception handling intended to prevent unexpected feature errors from immediately terminating the conversation.

These protections reduce certain risks but do not constitute a complete security audit. The application is a local educational project, not a hardened production chatbot.

## Current Limitations

- The chatbot follows predefined rules and patterns; it does not understand every natural-language message.
- It does not use a large language model or external AI API.
- It supports a limited set of commands and quiz questions.
- It uses a terminal interface rather than a graphical website.
- User memory and task storage are local JSON files without encryption.
- Chat history displayed in the session is not automatically restored from the log when the application restarts.

## Future Improvements

Potential enhancements include:

- Integration with an AI language model API for more flexible conversations.
- A browser-based interface using Flask.
- Persistent, searchable conversation history.
- Better natural-language understanding and intent classification.
- More Python, DSA, and AI/ML quizzes.
- Editing, searching, and prioritizing tasks.
- Configurable user preferences and improved memory management.
- Automated tests and more robust input validation.
- Optional database storage using SQLite.

These are proposed improvements, not features included in the current rule-based implementation.

## Learning Outcomes

This project provides practical experience with:

- Python functions and object-oriented programming.
- Classes, objects, and methods.
- Regular expressions and pattern matching.
- Abstract Syntax Trees and restricted expression evaluation.
- JSON file handling and persistent storage.
- Exception handling and input validation.
- Lists, dictionaries, and other data structures.
- Randomness and secure password generation.
- Command-line interfaces and basic application design.

## Author and Project Information

**Project:** DecodeBot — Rule-Based AI Chatbot  
**Program:** DecodeLabs AI Internship  
**Project Number:** Project 1  
**Batch:** 2026  
**Language:** Python 3.10+  
**License:** Not specified

---

*DecodeBot is an educational project designed to demonstrate Python programming and chatbot fundamentals. AI API integration and a web-based interface are planned extensions rather than current capabilities.*
