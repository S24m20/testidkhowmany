import os

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'quiz_database.db')

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

# Streamlit configuration
STREAMLIT_SERVER_PORT = 8501

# Classification configuration
DEFAULT_CLASSIFICATION_LIMIT = 1000
LOW_CONFIDENCE_THRESHOLD = 0.6
REVIEW_PRIORITY_THRESHOLD = 0.8

# File paths
EXTRACTED_FOLDER = 'extracted'
CURRICULUM_FOLDER = 'curriculum'
