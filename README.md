# Ethiopian Educational Quiz System

This project is a complete, end-to-end system for classifying educational questions, storing them in a database, and delivering them as quizzes via a Telegram bot. It includes an AI-powered classifier tailored for the Ethiopian curriculum and a web-based interface for reviewing and editing the classifications.

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
    You can then access the interface in your browser at `http://localhost:8501`.

2.  **Run the Telegram Bot:**
    This will start the quiz bot.
    ```bash
    python bot.py
    ```
    Open your Telegram app, find your bot, and send the `/start` command to begin a quiz.

## Component Details

- **`importer.py`**: A script that reads JSON files from the `extracted/` folder, handles different formats, infers subjects from filenames, and loads the questions into the database. It uses a hash to prevent duplicate questions.
- **`classifier.py`**: The core of the AI system. It uses a pre-trained sentence transformer model to calculate the semantic similarity between a question and the curriculum objectives. It combines this with keyword matching to produce a final confidence score.
- **`review_app.py`**: A web-based dashboard built with Streamlit. It provides visual analytics on the classification results and allows an administrator to review low-confidence questions, manually correct their classification, and save the changes to the database.
- **`bot.py`**: A conversational Telegram bot that guides users through the process of selecting a subject, grade, and unit to generate a quiz. It uses Telegram's native quiz polls for a smooth user experience and tracks user scores over time.
