import sqlite3
import json
import hashlib
from datetime import datetime
from config import DB_PATH

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the database with the required schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        question_hash TEXT UNIQUE,
        question_text TEXT,
        options JSON,
        correct_answer TEXT,
        explanation TEXT,
        subject TEXT,
        grade TEXT,
        unit TEXT,
        subunit TEXT,
        curriculum_id TEXT,
        classification_confidence REAL,
        confidence_level TEXT,
        classification_method TEXT,
        bloom_level TEXT,
        difficulty TEXT,
        ethiopian_context_score REAL,
        needs_review BOOLEAN,
        review_priority TEXT,
        source_filename TEXT,
        added_at TIMESTAMP
    )
    ''')

    # Create quiz_sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_sessions (
        session_id TEXT PRIMARY KEY,
        user_id INTEGER,
        subject TEXT,
        grade TEXT,
        unit TEXT,
        questions TEXT,
        score INTEGER,
        completed BOOLEAN,
        started_at TIMESTAMP
    )
    ''')

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        language_code TEXT,
        quiz_count INTEGER DEFAULT 0,
        total_score INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def add_question(question_data):
    """Adds a new question to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    question_text = question_data.get('question_text', '')
    question_hash = hashlib.md5(question_text.encode()).hexdigest()

    try:
        cursor.execute('''
        INSERT INTO questions (
            question_hash, question_text, options, correct_answer, explanation,
            subject, difficulty, bloom_level, source_filename, needs_review, added_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            question_hash,
            question_text,
            json.dumps(question_data.get('options', [])),
            question_data.get('correct_answer'),
            question_data.get('explanation'),
            question_data.get('subject'),
            question_data.get('difficulty'),
            question_data.get('bloom_level'),
            question_data.get('source_filename'),
            True,  # Initially, all questions need review
            datetime.now()
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # This question already exists in the database
        return None
    finally:
        conn.close()

def get_unclassified_questions(subject, limit):
    """Retrieves unclassified questions for a given subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM questions
    WHERE subject = ? AND classification_confidence IS NULL
    LIMIT ?
    ''', (subject, limit))
    questions = cursor.fetchall()
    conn.close()
    return questions

def update_question_classification(question_id, classification_result):
    """Updates a question with its classification result."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE questions
    SET
        grade = ?,
        unit = ?,
        subunit = ?,
        curriculum_id = ?,
        classification_confidence = ?,
        confidence_level = ?,
        classification_method = ?,
        ethiopian_context_score = ?,
        needs_review = ?,
        review_priority = ?
    WHERE id = ?
    ''', (
        classification_result.get('grade'),
        classification_result.get('unit'),
        classification_result.get('subunit'),
        classification_result.get('curriculum_id'),
        classification_result.get('confidence'),
        classification_result.get('confidence_level'),
        classification_result.get('method'),
        classification_result.get('ethiopian_context_score'),
        classification_result.get('needs_review'),
        classification_result.get('review_priority'),
        question_id
    ))
    conn.commit()
    conn.close()

def get_questions_for_review(filters=None):
    """Retrieves questions for the review interface, with optional filters."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM questions"
    conditions = []
    params = []

    if filters:
        if filters.get('subject'):
            conditions.append("subject = ?")
            params.append(filters['subject'])
        if filters.get('confidence_level'):
            conditions.append("confidence_level = ?")
            params.append(filters['confidence_level'])
        if filters.get('needs_review'):
            conditions.append("needs_review = ?")
            params.append(1)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    questions = cursor.fetchall()
    conn.close()
    return questions

def update_question_manual(question_id, new_data):
    """Manually updates a question's details from the review interface."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE questions
    SET
        grade = ?,
        unit = ?,
        subunit = ?,
        needs_review = ?,
        classification_method = 'manual_review'
    WHERE id = ?
    ''', (
        new_data.get('grade'),
        new_data.get('unit'),
        new_data.get('subunit'),
        False,  # Set needs_review to False after manual update
        question_id
    ))
    conn.commit()
    conn.close()

def get_distinct_subjects():
    """Gets a list of distinct subjects from the questions table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT subject FROM questions WHERE subject IS NOT NULL")
    subjects = [row['subject'] for row in cursor.fetchall()]
    conn.close()
    return subjects

def get_or_create_user(user_data):
    """Gets or creates a user in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    telegram_id = user_data.id
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute('''
        INSERT INTO users (telegram_id, username, first_name, last_name, language_code)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            telegram_id,
            user_data.username,
            user_data.first_name,
            user_data.last_name,
            user_data.language_code
        ))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()

    conn.close()
    return user

def get_quiz_questions(subject, grade, unit, limit=5):
    """Retrieves questions for a quiz."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM questions
    WHERE subject = ? AND grade = ? AND unit = ? AND needs_review = 0
    ORDER BY RANDOM()
    LIMIT ?
    ''', (subject, grade, unit, limit))
    questions = cursor.fetchall()
    conn.close()
    return questions

def get_available_grades_for_subject(subject):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT grade FROM questions WHERE subject = ? AND grade IS NOT NULL", (subject,))
    grades = [row['grade'] for row in cursor.fetchall()]
    conn.close()
    return grades

def get_available_units_for_grade(subject, grade):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT unit FROM questions WHERE subject = ? AND grade = ? AND unit IS NOT NULL", (subject, grade))
    units = [row['unit'] for row in cursor.fetchall()]
    conn.close()
    return units

def update_user_stats(telegram_id, score, num_questions):
    """Updates a user's quiz count and total score."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE users
    SET
        quiz_count = quiz_count + 1,
        total_score = total_score + ?
    WHERE telegram_id = ?
    ''', (score, telegram_id))
    conn.commit()
    conn.close()

def get_classification_stats():
    """Retrieves classification statistics for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Stats by subject
    cursor.execute("SELECT subject, COUNT(*) as count FROM questions GROUP BY subject")
    by_subject = cursor.fetchall()

    # Stats by confidence level
    cursor.execute("SELECT confidence_level, COUNT(*) as count FROM questions GROUP BY confidence_level")
    by_confidence = cursor.fetchall()

    # Stats by review status
    cursor.execute("SELECT needs_review, COUNT(*) as count FROM questions GROUP BY needs_review")
    by_review = cursor.fetchall()

    conn.close()
    return {
        "by_subject": {row['subject']: row['count'] for row in by_subject if row['subject']},
        "by_confidence": {row['confidence_level']: row['count'] for row in by_confidence if row['confidence_level']},
        "by_review": {('Needs Review' if row['needs_review'] else 'Reviewed'): row['count'] for row in by_review}
    }

def flag_question(question_id):
    """Flags a question for review from the Telegram bot."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE questions
    SET
        needs_review = ?,
        review_priority = ?
    WHERE id = ?
    ''', (True, "High (User Flagged)", question_id))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
