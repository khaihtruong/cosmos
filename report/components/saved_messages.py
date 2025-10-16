"""
Saved Messages Component

Retrieves and formats messages that users have explicitly saved/highlighted
during their conversations.
"""

from datetime import datetime
from typing import Dict, Any

from report.base import ReportComponent
from llm_chat.models import SavedSelection


class SavedMessagesComponent(ReportComponent):
    """Component for retrieving saved message selections."""

    def generate(self) -> Dict[str, Any]:
        """
        Get saved message selections from conversations.

        Returns:
            Dict containing:
                - selections: List of saved messages with metadata
                - total_count: Number of saved messages
        """
        conv_ids = [c.id for c in self.conversations]

        if not conv_ids:
            return {"selections": [], "total_count": 0}

        selections = SavedSelection.query.filter(
            SavedSelection.conversation_id.in_(conv_ids)
        ).order_by(SavedSelection.created_at.desc()).all()

        selections_data = []
        for selection in selections:
            selections_data.append({
                "id": selection.id,
                "text": selection.selection_text,
                "note": selection.note,
                "conversation_id": selection.conversation_id,
                "created_at": selection.created_at,
                "created_at_formatted": datetime.fromtimestamp(
                    selection.created_at
                ).strftime('%Y-%m-%d %H:%M')
            })

        return {
            "selections": selections_data,
            "total_count": len(selections_data)
        }
