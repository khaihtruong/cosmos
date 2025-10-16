"""
AI Summary Component

Generates AI-powered summaries of conversations using Google's Gemini models.
Extracts key themes and clinical progress notes from chat transcripts.
"""

import os
from datetime import datetime
from typing import Dict, Any
import google.generativeai as genai

from report.base import ReportComponent
from llm_chat.models import Model


class AISummaryComponent(ReportComponent):
    """AI-powered conversation summary component using Gemini."""

    def generate(self) -> Dict[str, Any]:
        """
        Generate AI summary using Gemini.

        Returns:
            Dict containing:
                - summary: 2-3 paragraph overview
                - themes: List of key themes identified
                - progress_notes: Clinical notes
                - generated_with: Model name used
                - error: Error message if generation failed
        """
        if not self.messages:
            return {
                "summary": "No messages to summarize.",
                "themes": [],
                "progress_notes": "",
                "generated_with": "No model"
            }

        try:
            model = self._select_gemini_model()
            conversation_text = self._prepare_conversation_text()
            prompt = self._build_prompt(conversation_text)

            response = model.generate_content(prompt)
            return self._parse_ai_response(response.text, model.name)

        except Exception as e:
            return {
                "summary": f"Error generating AI summary: {str(e)}",
                "themes": [],
                "progress_notes": "",
                "error": str(e)
            }

    def _select_gemini_model(self):
        """Select the best available Gemini model."""
        google_key = os.getenv('GOOGLE_API_KEY')
        if not google_key or google_key.strip() == '' or google_key == 'your_google_api_key_here':
            raise ValueError("Google API key not configured")

        genai.configure(api_key=google_key)

        # Check available models in database
        available_models = Model.query.filter(
            Model.name.like('gemini%'),
            Model.is_active == True
        ).all()

        # Prioritize models
        priority_order = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']

        for model_name in priority_order:
            model = next((m for m in available_models if m.name == model_name), None)
            if model:
                return genai.GenerativeModel(model_name)

        # Fallback to any available Gemini model
        if available_models:
            model = available_models[0]
            return genai.GenerativeModel(model.name)

        raise ValueError("No Gemini models available")

    def _prepare_conversation_text(self) -> str:
        """Prepare conversation text for AI analysis."""
        text_parts = []
        for conv in self.conversations:
            conv_messages = [m for m in self.messages if m.conversation_id == conv.id]
            if conv_messages:
                text_parts.append(f"\n--- Conversation: {conv.title} ---")
                for msg in sorted(conv_messages, key=lambda x: x.timestamp):
                    timestamp = datetime.fromtimestamp(msg.timestamp).strftime('%Y-%m-%d %H:%M')
                    text_parts.append(f"[{timestamp}] {msg.role}: {msg.content}")
        return "\n".join(text_parts)

    def _build_prompt(self, conversation_text: str) -> str:
        """Build the prompt for AI summary generation."""
        return f"""
        Please analyze this series of chat conversations from a therapy/support window and provide:
        1. A comprehensive summary (2-3 paragraphs)
        2. Key themes identified (list up to 5)
        3. Brief progress notes suitable for clinical documentation

        Conversations:
        {conversation_text}

        Format your response as:
        SUMMARY:
        [Your summary here]

        THEMES:
        - Theme 1
        - Theme 2
        [etc]

        PROGRESS NOTES:
        [Your clinical notes here]
        """

    def _parse_ai_response(self, response_text: str, model_name: str) -> Dict[str, Any]:
        """Parse the AI response into structured data."""
        summary = ""
        themes = []
        progress_notes = ""

        current_section = None
        for line in response_text.split('\n'):
            if 'SUMMARY:' in line:
                current_section = 'summary'
            elif 'THEMES:' in line:
                current_section = 'themes'
            elif 'PROGRESS NOTES:' in line:
                current_section = 'progress'
            elif current_section == 'summary' and line.strip():
                summary += line.strip() + " "
            elif current_section == 'themes' and line.strip().startswith('-'):
                themes.append(line.strip()[1:].strip())
            elif current_section == 'progress' and line.strip():
                progress_notes += line.strip() + " "

        return {
            "summary": summary.strip(),
            "themes": themes,
            "progress_notes": progress_notes.strip(),
            "generated_with": model_name
        }
