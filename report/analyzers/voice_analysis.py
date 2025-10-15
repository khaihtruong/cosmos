"""
Voice Analysis

Analyzes active vs passive voice usage in text using spaCy dependency parsing.
"""

from typing import List, Dict, Any

from report.base import Analyzer


class VoiceAnalyzer(Analyzer):
    """Analyzes active vs passive voice in text using spaCy."""

    def __init__(self):
        """Initialize with spaCy model."""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None

    def analyze(self, texts: List[str]) -> Dict[str, Any]:
        """
        Analyze voice (active vs passive) in the given texts.

        Args:
            texts: List of text strings to analyze

        Returns:
            Dict containing:
                - active_ratio: Percentage of active voice
                - passive_ratio: Percentage of passive voice
                - total_verbs: Total verb count analyzed
                - active_count: Count of active verbs
                - passive_count: Count of passive verbs
        """
        if not texts or not self.nlp:
            return self._empty_result()

        active_count = 0
        passive_count = 0

        for text in texts:
            doc = self.nlp(text)
            for token in doc:
                # Passive voice is indicated by auxiliary + past participle
                if token.dep_ == "auxpass":
                    passive_count += 1
                elif token.pos_ == "VERB":
                    active_count += 1

        total_voice = active_count + passive_count
        active_ratio = (active_count / total_voice * 100) if total_voice > 0 else 0
        passive_ratio = (passive_count / total_voice * 100) if total_voice > 0 else 0

        return {
            "active_ratio": active_ratio,
            "passive_ratio": passive_ratio,
            "total_verbs": total_voice,
            "active_count": active_count,
            "passive_count": passive_count
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "active_ratio": 0,
            "passive_ratio": 0,
            "total_verbs": 0,
            "active_count": 0,
            "passive_count": 0
        }
