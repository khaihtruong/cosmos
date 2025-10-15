"""
NLP Analysis Component

Performs comprehensive linguistic analysis on user messages including
sentiment analysis, voice analysis, and keyword extraction.
"""

from typing import Dict, Any

from report.base import ReportComponent
from report.analyzers import SentimentAnalyzer, VoiceAnalyzer, KeywordAnalyzer


class NLPAnalysisComponent(ReportComponent):
    """Component for NLP analysis of conversation messages."""

    def generate(self) -> Dict[str, Any]:
        """
        Generate comprehensive NLP analysis.

        Returns:
            Dict containing:
                - average_sentiment: Overall sentiment score
                - sentiment_distribution: Breakdown of positive/neutral/negative
                - sentiment_percentages: Percentage breakdown
                - voice_analysis: Active vs passive voice ratios
                - question_frequency: Percentage of messages with questions
                - emotional_keywords: Counts of emotional word categories
                - message_count: Number of messages analyzed
        """
        user_messages = [m for m in self.messages if m.role == 'user']

        if not user_messages:
            return self._empty_analysis()

        # Extract message texts
        message_texts = [msg.content for msg in user_messages]

        # Run analyzers
        sentiment_analyzer = SentimentAnalyzer()
        voice_analyzer = VoiceAnalyzer()
        keyword_analyzer = KeywordAnalyzer()

        sentiment_results = sentiment_analyzer.analyze(message_texts)
        voice_results = voice_analyzer.analyze(message_texts)
        keyword_results = keyword_analyzer.analyze(message_texts)

        # Combine results
        return {
            "average_sentiment": sentiment_results["average_sentiment"],
            "sentiment_distribution": sentiment_results["sentiment_distribution"],
            "sentiment_percentages": sentiment_results["sentiment_percentages"],
            "voice_analysis": {
                "active_ratio": voice_results["active_ratio"],
                "passive_ratio": voice_results["passive_ratio"],
                "total_verbs": voice_results["total_verbs"]
            },
            "question_frequency": keyword_results["question_frequency"],
            "emotional_keywords": keyword_results["emotional_keywords"],
            "message_count": len(user_messages)
        }

    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            "average_sentiment": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
            "sentiment_percentages": {"positive": 0, "neutral": 0, "negative": 0},
            "voice_analysis": {"active_ratio": 0, "passive_ratio": 0, "total_verbs": 0},
            "question_frequency": 0,
            "emotional_keywords": {"positive": 0, "negative": 0, "uncertainty": 0},
            "message_count": 0
        }
