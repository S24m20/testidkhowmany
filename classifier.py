import json
import os
import re
import torch
from sentence_transformers import SentenceTransformer, util
import numpy as np
from config import CURRICULUM_FOLDER

class Classifier:
    def __init__(self, subject):
        self.subject = subject
        self.curriculum = self._load_curriculum()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self._precompute_curriculum_embeddings()

    def _load_curriculum(self):
        """Loads the curriculum JSON for the specified subject."""
        filepath = os.path.join(CURRICULUM_FOLDER, f"{self.subject}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Curriculum file not found for subject: {self.subject}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _precompute_curriculum_embeddings(self):
        """Pre-computes sentence embeddings for all curriculum objectives."""
        print("Pre-computing curriculum embeddings...")
        for grade, grade_data in self.curriculum.get('grades', {}).items():
            for unit in grade_data.get('units', []):
                for sub_unit in unit.get('sub_units', []):
                    objectives = sub_unit.get('objectives', [])
                    if objectives:
                        sub_unit['embeddings'] = self.model.encode(objectives, convert_to_tensor=True)
        print("Embeddings pre-computed.")

    def _semantic_match(self, question_text, sub_unit):
        """Calculates the semantic similarity between a question and a sub-unit."""
        if 'embeddings' not in sub_unit or len(sub_unit['objectives']) == 0:
            return 0.0

        question_embedding = self.model.encode(question_text, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(question_embedding, sub_unit['embeddings'])
        return torch.max(similarities).item()

    def _keyword_match(self, question_text, sub_unit):
        """Calculates a score based on keyword matching."""
        score = 0
        key_concepts = sub_unit.get('key_concepts', [])
        for concept in key_concepts:
            if re.search(r'\b' + re.escape(concept) + r'\b', question_text, re.IGNORECASE):
                score += 1
        return score / len(key_concepts) if key_concepts else 0.0

    def _ethiopian_context_score(self, question_text, sub_unit):
        """Calculates a score based on the presence of Ethiopian context."""
        score = 0
        context_terms = sub_unit.get('ethiopian_context', [])
        for term in context_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', question_text, re.IGNORECASE):
                score += 1
        return score / len(context_terms) if context_terms else 0.0

    def classify_question(self, question):
        """Classifies a single question against the curriculum."""
        best_match = {
            'confidence': 0.0,
            'grade': None,
            'unit': None,
            'subunit': None,
            'curriculum_id': None,
            'method': None
        }

        question_text = question['question_text']

        for grade, grade_data in self.curriculum.get('grades', {}).items():
            for unit in grade_data.get('units', []):
                for sub_unit in unit.get('sub_units', []):
                    semantic_score = self._semantic_match(question_text, sub_unit)
                    keyword_score = self._keyword_match(question_text, sub_unit)

                    # Combine scores (you can adjust the weights)
                    combined_score = (0.6 * semantic_score) + (0.4 * keyword_score)

                    if combined_score > best_match['confidence']:
                        best_match = {
                            'confidence': combined_score,
                            'grade': grade,
                            'unit': unit['unit_title'],
                            'subunit': sub_unit['sub_unit_title'],
                            'curriculum_id': f"{self.subject}-{grade}-{unit['unit_title']}-{sub_unit['sub_unit_title']}",
                            'method': 'semantic_keyword_hybrid',
                            'ethiopian_context_score': self._ethiopian_context_score(question_text, sub_unit)
                        }

        return self._determine_confidence_level(best_match)

    def _determine_confidence_level(self, result):
        """Determines the confidence level and need for review."""
        confidence = result['confidence']
        if confidence > 0.8:
            result['confidence_level'] = 'High'
            result['needs_review'] = False
            result['review_priority'] = 'Low'
        elif confidence > 0.6:
            result['confidence_level'] = 'Medium'
            result['needs_review'] = True
            result['review_priority'] = 'Medium'
        else:
            result['confidence_level'] = 'Low'
            result['needs_review'] = True
            result['review_priority'] = 'High'
        return result

if __name__ == '__main__':
    # Example usage:
    classifier = Classifier('biology')
    sample_question = {
        'question_text': 'Which organelle is known as the powerhouse of the cell?',
        'options': ['Nucleus', 'Mitochondria', 'Ribosome', 'Endoplasmic Reticulum'],
        'correct_answer': 'B'
    }
    result = classifier.classify_question(sample_question)
    print(json.dumps(result, indent=2))
