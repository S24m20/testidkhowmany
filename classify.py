import argparse
from database import get_unclassified_questions, update_question_classification
from classifier import Classifier
from config import DEFAULT_CLASSIFICATION_LIMIT

def classify_questions(subject, limit):
    """
    Orchestrates the classification process for a given subject.
    """
    print(f"Starting classification for subject: {subject} (limit: {limit})")

    # 1. Initialize the classifier
    try:
        classifier = Classifier(subject)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # 2. Get unclassified questions from the database
    questions = get_unclassified_questions(subject, limit)
    if not questions:
        print(f"No unclassified questions found for subject: {subject}")
        return

    print(f"Found {len(questions)} unclassified questions to process.")

    # 3. Classify each question and update the database
    for i, question in enumerate(questions):
        question_dict = dict(question)
        print(f"Processing question {i+1}/{len(questions)} (ID: {question_dict['id']})...")

        result = classifier.classify_question(question_dict)
        update_question_classification(question_dict['id'], result)

    print(f"\nClassification complete for {len(questions)} questions.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Classify questions from the database.')
    parser.add_argument('--subject', type=str, required=True,
                        help='The subject to classify (e.g., biology, chemistry).')
    parser.add_argument('--limit', type=int, default=DEFAULT_CLASSIFICATION_LIMIT,
                        help=f'The maximum number of questions to classify (default: {DEFAULT_CLASSIFICATION_LIMIT}).')
    args = parser.parse_args()

    classify_questions(args.subject, args.limit)
