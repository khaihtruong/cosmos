"""
Descriptive Statistics Component

Calculates basic conversation statistics like message counts, word counts,
session duration, and activity patterns.
"""

from datetime import datetime
from typing import Dict, Any

from report.base import ReportComponent


class DescriptiveStatsComponent(ReportComponent):
    """Component for generating descriptive statistics about conversations."""

    def generate(self) -> Dict[str, Any]:
        """
        Generate descriptive statistics.

        Returns:
            Dict containing:
                - user_messages: Count of user messages
                - assistant_messages: Count of assistant messages
                - total_messages: Total message count
                - avg_words_per_user_message: Average words in user messages
                - avg_words_per_assistant_message: Average words in assistant messages
                - total_words: Total word count across all messages
                - session_duration_hours: Duration from first to last message
                - messages_by_day: Daily message breakdown
                - longest_user_message: Longest user message word count
                - shortest_user_message: Shortest user message word count
                - conversations_count: Number of conversations
                - average_messages_per_chat: Average messages per conversation
        """
        if not self.messages:
            return self._empty_stats()

        user_messages = [m for m in self.messages if m.role == 'user']
        assistant_messages = [m for m in self.messages if m.role == 'assistant']

        # Word counts
        user_words = [len(m.content.split()) for m in user_messages]
        assistant_words = [len(m.content.split()) for m in assistant_messages]

        # Time analysis
        if self.messages:
            first_message = min(self.messages, key=lambda m: m.timestamp)
            last_message = max(self.messages, key=lambda m: m.timestamp)
            duration_hours = (last_message.timestamp - first_message.timestamp) / 3600
        else:
            duration_hours = 0

        # Messages by day
        messages_by_day = {}
        for msg in self.messages:
            day = datetime.fromtimestamp(msg.timestamp).strftime('%Y-%m-%d')
            if day not in messages_by_day:
                messages_by_day[day] = {"user": 0, "assistant": 0}
            messages_by_day[day][msg.role] += 1

        return {
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_messages": len(self.messages),
            "avg_words_per_user_message": sum(user_words) / len(user_words) if user_words else 0,
            "avg_words_per_assistant_message": sum(assistant_words) / len(assistant_words) if assistant_words else 0,
            "total_words": sum(user_words) + sum(assistant_words),
            "session_duration_hours": round(duration_hours, 2),
            "messages_by_day": messages_by_day,
            "longest_user_message": max(user_words) if user_words else 0,
            "shortest_user_message": min(user_words) if user_words else 0,
            "conversations_count": len(self.conversations),
            "average_messages_per_chat": len(self.messages) / len(self.conversations) if self.conversations else 0
        }

    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics structure."""
        return {
            "user_messages": 0,
            "assistant_messages": 0,
            "total_messages": 0,
            "avg_words_per_user_message": 0,
            "avg_words_per_assistant_message": 0,
            "total_words": 0,
            "session_duration_hours": 0,
            "messages_by_day": {},
            "longest_user_message": 0,
            "shortest_user_message": 0,
            "conversations_count": 0,
            "average_messages_per_chat": 0
        }
