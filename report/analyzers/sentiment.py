"""
Sentiment Analysis

Uses TextBlob for sentiment polarity analysis of text messages.
"""

from typing import List, Dict, Any
from textblob import TextBlob

from report.base import Analyzer


class SentimentAnalyzer(Analyzer):
    """Analyzes sentiment polarity of text using TextBlob."""

    def analyze(self, texts: List[str]) -> Dict[str, Any]:
        """
        Analyze sentiment of the given texts.

        Args:
            texts: List of text strings to analyze

        Returns:
            Dict containing:
                - average_sentiment: Mean polarity score (-1 to 1)
                - distribution: Count of positive/neutral/negative messages
                - percentages: Percentage breakdown of sentiment
                - scores: Individual polarity scores for each text
        """
        if not texts:
            return self._empty_result()

        sentiments = []
        for text in texts:
            blob = TextBlob(text)
            sentiments.append(blob.sentiment.polarity)

        avg_sentiment = sum(sentiments) / len(sentiments)
        positive_msgs = sum(1 for s in sentiments if s > 0.1)
        negative_msgs = sum(1 for s in sentiments if s < -0.1)
        neutral_msgs = len(sentiments) - positive_msgs - negative_msgs

        return {
            "average_sentiment": avg_sentiment,
            "sentiment_distribution": {
                "positive": positive_msgs,
                "neutral": neutral_msgs,
                "negative": negative_msgs
            },
            "sentiment_percentages": {
                "positive": (positive_msgs / len(sentiments) * 100) if sentiments else 0,
                "neutral": (neutral_msgs / len(sentiments) * 100) if sentiments else 0,
                "negative": (negative_msgs / len(sentiments) * 100) if sentiments else 0
            },
            "scores": sentiments
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "average_sentiment": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
            "sentiment_percentages": {"positive": 0, "neutral": 0, "negative": 0},
            "scores": []
        }
