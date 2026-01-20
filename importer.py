import os
import json
import argparse
from database import add_question
from config import EXTRACTED_FOLDER

def import_questions_from_file(filepath):
    """Imports questions from a single JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data.get('questions', [])

            imported_count = 0
            for question_data in questions:
                question_data['source_filename'] = os.path.basename(filepath)
                if add_question(question_data):
                    imported_count += 1

            print(f"Imported {imported_count} new questions from {filepath}")

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filepath}")
    except Exception as e:
        print(f"An unexpected error occurred with file {filepath}: {e}")

def import_all_questions(folder):
    """Imports all questions from JSON files in a given folder."""
    if not os.path.isdir(folder):
        print(f"Error: Folder '{folder}' not found.")
        return

    for filename in os.listdir(folder):
        if filename.endswith('.json'):
            filepath = os.path.join(folder, filename)
            import_questions_from_file(filepath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import questions from JSON files into the database.')
    parser.add_argument('--folder', type=str, default=EXTRACTED_FOLDER,
                        help=f'The folder containing the JSON files (default: {EXTRACTED_FOLDER})')
    args = parser.parse_args()

    import_all_questions(args.folder)
