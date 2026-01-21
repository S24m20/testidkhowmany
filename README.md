# Ethiopian Educational Quiz System (v2)

This project is a complete, end-to-end system for classifying educational questions, storing them in a database, and delivering them as quizzes via a Telegram bot. It includes an AI-powered classifier tailored for the Ethiopian curriculum and a web-based interface for reviewing and editing the classifications.

**Note:** This version introduces a new user-facing flagging feature. These changes are fully backward-compatible. No changes to your database schema or setup are required.

## What's New in v2

- **User-Facing Question Flagging:** Users taking a quiz on Telegram can now flag questions they believe are incorrect or have issues.
- **Enhanced Review Interface:** The Streamlit review app now displays a `review_priority` column, making it easy for administrators to find and prioritize user-flagged questions.

## Key Features

- **AI-Powered Classification:** Uses sentence transformers to match questions to the Ethiopian curriculum (grades 9-12).
- **Flexible Data Import:** Imports questions from various JSON formats and intelligently infers the subject from filenames.
- **SQLite Database:** A portable, serverless database to store all questions, user data, and quiz sessions.
- **Streamlit Review Interface:** A user-friendly web app to review, edit, and analyze question classifications.
- **Telegram Quiz Bot:** A conversational bot that generates quizzes based on subject, grade, and unit, and tracks user progress.
- **Modular Architecture:** A clean, well-structured codebase with a clear separation of concerns.

## Project Structure

```
.
├── extracted/              # Folder for raw JSON question files
├── curriculum/             # Folder for curriculum definition files
├── bot.py                  # The Telegram quiz bot
├── classifier.py           # The core AI classification engine
├── classify.py             # Command-line tool to run the classifier
├── config.py               # Centralized configuration for the system
├── database.py             # Database schema and management functions
├── importer.py             # Script to import questions into the database
├── init.py                 # Script to initialize the database
├── review_app.py           # The Streamlit review interface
├── requirements.txt        # Python dependencies for the project
└── README.md               # This file
```

## Setup and Installation

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

- Python 3.8 or higher
- `pip` for installing packages

### 2. Install Dependencies

Clone the repository, navigate to the project's root directory, and run the following command to install the required Python libraries:

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

This project requires a Telegram Bot Token to run the quiz bot. You can get a token by talking to the [BotFather](https://t.me/botfather) on Telegram.

Once you have your token, set it as an environment variable.

- **On Linux/macOS:**
  ```bash
  export TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"
  ```

- **On Windows (Command Prompt):**
  ```bash
  set TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"
  ```

### 4. (Optional) Configure a Proxy

If you need to run the bot through a proxy, you can set the `TELEGRAM_PROXY_URL` environment variable. The bot supports both HTTP and SOCKS5 proxies.

- **On Linux/macOS:**
  ```bash
  export TELEGRAM_PROXY_URL="socks5h://user:pass@host:port"
  ```

- **On Windows (Command Prompt):**
  ```bash
  set TELEGRAM_PROXY_URL="socks5h://user:pass@host:port"
  ```

## Usage Workflow

Follow this workflow to get the system up and running with your own data.

### Step 1: Add Your Data

1.  **Curriculum Files:** Make sure your curriculum definition files (e.g., `biology.json`, `chemistry.json`) are in the `curriculum/` folder.
2.  **Question Files:** Place your JSON question files into the `extracted/` folder. The importer is flexible and can handle different formats and filenames (e.g., `biology.json`, `physics_chapter1.json`).

### Step 2: Process the Data

1.  **Initialize the Database:**
    This command will create the `quiz_database.db` file with the correct schema.
    ```bash
    python init.py
    ```

2.  **Import Questions:**
    This will load all questions from the `extracted/` folder into the database.
    ```bash
    python importer.py
    ```

3.  **Classify Questions:**
    Run the classifier for each subject you've imported. This will match the questions to the curriculum and save the results.
    ```bash
    python classify.py --subject biology
    python classify.py --subject chemistry
    # ... and so on for each subject
    ```

### Step 3: Run the Applications

You can run the Streamlit review app and the Telegram bot simultaneously.

1.  **Run the Review Interface:**
    This will start the web server for the review app.
    ```bash
    streamlit run review_app.py
    ```
    You can then access the interface in your browser at `http://localhost:8501`. In the main table, you can now see the `review_priority` column. Look for questions marked as `"High (User Flagged)"` to find the ones that users have flagged.

2.  **Run the Telegram Bot:**
    This will start the quiz bot.
    ```bash
    python bot.py
    ```
    Open your Telegram app, find your bot, and send the `/start` command to begin a quiz. After you answer a question, you will see a "Flag This Question" button.
