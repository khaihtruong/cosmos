"""
Keyword Extraction

Identifies emotional keywords and question patterns in text.
"""

from typing import List, Dict, Any

from report.base import Analyzer


class KeywordAnalyzer(Analyzer):
    """Analyzes emotional keywords and question frequency in text."""

    # Predefined emotional keyword categories
    EMOTIONAL_KEYWORDS = {
        'positive': ['happy', 'great', 'good', 'wonderful', 'excited', 'love', 'thank', 'grateful', 'joy'],
        'negative': ['sad', 'angry', 'frustrated', 'worried', 'anxious', 'hate', 'bad', 'upset', 'depressed'],
        'uncertainty': ['maybe', 'perhaps', 'might', 'could', 'possibly', 'unsure', "don't know", 'confused']
    }

    def analyze(self, texts: List[str]) -> Dict[str, Any]:
        """
        Analyze emotional keywords and questions in the given texts.

        Args:
            texts: List of text strings to analyze

        Returns:
            Dict containing:
                - emotional_keywords: Count per category
                - question_frequency: Percentage of texts with questions
                - question_count: Total number of questions
        """
        if not texts:
            return self._empty_result()

        keyword_counts = {category: 0 for category in self.EMOTIONAL_KEYWORDS}
        question_count = 0

        for text in texts:
            text_lower = text.lower()

            # Count emotional keywords
            for category, keywords in self.EMOTIONAL_KEYWORDS.items():
                keyword_counts[category] += sum(
                    1 for keyword in keywords if keyword in text_lower
                )

            # Count questions
            if '?' in text:
                question_count += 1

        question_ratio = (question_count / len(texts) * 100) if texts else 0

        return {
            "emotional_keywords": keyword_counts,
            "question_frequency": question_ratio,
            "question_count": question_count,
            "total_texts": len(texts)
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "emotional_keywords": {"positive": 0, "negative": 0, "uncertainty": 0},
            "question_frequency": 0,
            "question_count": 0,
            "total_texts": 0
        }
