"""
AI Summary Component

Generates AI-powered summaries of conversations using Llama models.
Extracts key themes and clinical progress notes from chat transcripts.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from report.base import ReportComponent
from llm_chat.models import Model
from llm_chat.services.llm_interface import LLMInterface


class AISummaryComponent(ReportComponent):
    """AI-powered conversation summary component using Llama models."""

    def generate(self) -> Optional[Dict[str, Any]]:
        """
        Generate AI summary using the smallest available Llama model.

        Returns:
            Dict containing:
                - summary: 2-3 paragraph overview
                - themes: List of key themes identified
                - progress_notes: Clinical notes
                - generated_with: Model name used
                - error: Error message if generation failed
            Or None if no Llama models are available.
        """
        if not self.messages:
            return {
                "summary": "No messages to summarize.",
                "themes": [],
                "progress_notes": "",
                "generated_with": "No model"
            }

        try:
            model = self._select_llama_model()
            if model is None:
                # No Llama models available, skip AI summary
                return None

            conversation_text = self._prepare_conversation_text()
            prompt = self._build_prompt(conversation_text)

            # Use LLMInterface to call the model
            messages = [{"role": "user", "content": prompt}]
            response_text, _ = LLMInterface.call_llm(model, messages)

            return self._parse_ai_response(response_text, model.name)

        except Exception as e:
            return {
                "summary": f"Error generating AI summary: {str(e)}",
                "themes": [],
                "progress_notes": "",
                "error": str(e)
            }

    def _select_llama_model(self) -> Optional[Model]:
        """
        Select the smallest available Llama model.

        Returns:
            Model object if a Llama model is available, None otherwise.
        """
        available_models = Model.query.filter(
            Model.provider == 'local',
            Model.name.ilike('%llama%'),
            Model.visible == True
        ).all()

        if not available_models:
            print("No Llama models available for AI summary generation")
            return None

        # Check actual availability
        available_models = [m for m in available_models if m.check_availability()]

        if not available_models:
            print("No Llama models currently available for AI summary generation")
            return None

        priority_patterns = [
            'llama3.2:1b',
            'llama3.2:3b',
            'llama3.2',
            'llama2:7b',
            'llama3.1:8b',
            'llama3:8b',
            'llama2',
            'llama3.1',
            'llama3',
        ]

        for pattern in priority_patterns:
            for model in available_models:
                if pattern.lower() in model.name.lower():
                    print(f"Selected Llama model for AI summary: {model.name}")
                    return model

        print(f"Selected Llama model for AI summary: {available_models[0].name}")
        return available_models[0]

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
