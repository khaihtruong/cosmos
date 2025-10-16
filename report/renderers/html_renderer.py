"""
HTML Renderer

Converts report data into HTML format for web display or PDF generation.
"""

from datetime import datetime
from typing import Dict, Any

from report.base import Renderer
from report.styles import get_html_styles


class HTMLRenderer(Renderer):
    """Renders reports as HTML."""

    def render_full_report(self, report_data: Dict[str, Any], standalone: bool = False) -> str:
        """
        Render complete report as HTML.

        Args:
            report_data: Full report data including metadata and components
            standalone: If True, include full HTML document structure

        Returns:
            Complete HTML report as string
        """
        css = get_html_styles(standalone=standalone)
        html_parts = []

        # Add wrapper div
        html_parts.append('<div class="unified-report">')

        # Add header
        html_parts.append(self.render_header(report_data))

        # Add components
        html_parts.append('<div class="report-content">')

        if 'components' in report_data:
            for component_name, component_data in report_data['components'].items():
                html_parts.append(f'<div class="report-section" data-component="{component_name}">')
                html_parts.append(self.render_component(component_name, component_data))
                html_parts.append('</div>')

        html_parts.append('</div>')
        html_parts.append('</div>')

        if standalone:
            # For PDF or download, include full HTML document
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Report - {report_data.get('window_title', 'Chat Session')}</title>
                <style>{css}</style>
            </head>
            <body>
                {''.join(html_parts)}
            </body>
            </html>
            """
        else:
            # For modal display, just return the styled content
            return f"<style>{css}</style>{''.join(html_parts)}"

    def render_header(self, report_data: Dict[str, Any]) -> str:
        """Render report header with metadata."""
        generated_date = datetime.fromtimestamp(
            report_data.get('generated_at', 0)
        ).strftime('%B %d, %Y')

        summary = report_data.get('summary', {})

        return f"""
        <div class="report-header">
            <h2>{report_data.get('window_title', 'Chat Session Report')}</h2>
            {f'<p class="window-description">{report_data.get("window_description")}</p>' if report_data.get('window_description') else ''}
            <div class="report-meta">
                <div class="meta-item">
                    <div class="meta-label">Generated</div>
                    <div class="meta-value">{generated_date}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Conversations</div>
                    <div class="meta-value">{summary.get('total_conversations', 0)}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Total Messages</div>
                    <div class="meta-value">{summary.get('total_user_messages', 0) + summary.get('total_model_messages', 0)}</div>
                </div>
            </div>
        </div>
        """

    def render_component(self, component_name: str, data: Dict[str, Any]) -> str:
        """
        Render a single component's data.

        Args:
            component_name: Name of the component
            data: Component's generated data

        Returns:
            HTML string for the component
        """
        # Route to specific component renderer
        if component_name == 'ai_summary':
            return self._render_ai_summary(data)
        elif component_name == 'saved_messages':
            return self._render_saved_messages(data)
        elif component_name == 'descriptive_stats':
            return self._render_descriptive_stats(data)
        elif component_name == 'nlp_analysis':
            return self._render_nlp_analysis(data)
        else:
            return f'<p>Unknown component: {component_name}</p>'

    def _render_ai_summary(self, data: Dict[str, Any]) -> str:
        """Render AI summary component."""
        html = f"""
        <div class="report-component ai-summary">
            <div class="component-header">
                <span class="component-icon">🤖</span>
                <h3 class="component-title">AI Summary</h3>
            </div>
            <div class="summary-content">
                <p class="summary-text">{data.get('summary', 'No summary available')}</p>
        """

        if data.get('themes'):
            html += """
                <div class="themes-section">
                    <h4>Key Themes Identified:</h4>
                    <ul class="themes-list">
            """
            for theme in data['themes']:
                html += f"<li>{theme}</li>"
            html += "</ul></div>"

        if data.get('progress_notes'):
            html += f"""
                <div class="progress-notes">
                    <h4>Progress Notes:</h4>
                    <p>{data['progress_notes']}</p>
                </div>
            """

        html += f"""
                <p class="generated-by">Generated with {data.get('generated_with', 'AI')}</p>
            </div>
        </div>
        """
        return html

    def _render_saved_messages(self, data: Dict[str, Any]) -> str:
        """Render saved messages component."""
        html = f"""
        <div class="report-component saved-messages">
            <div class="component-header">
                <span class="component-icon">💾</span>
                <h3 class="component-title">Saved Messages ({data['total_count']})</h3>
            </div>
            <div class="messages-content">
        """

        if data['selections']:
            for selection in data['selections']:
                html += f"""
                <div class="saved-message">
                    <p class="message-text">"{selection['text']}"</p>
                    {f'<p class="message-note">Note: {selection["note"]}</p>' if selection.get('note') else ''}
                    <p class="message-date">{selection['created_at_formatted']}</p>
                </div>
                """
        else:
            html += "<p class='no-data'>No saved messages</p>"

        html += """
            </div>
        </div>
        """
        return html

    def _render_descriptive_stats(self, data: Dict[str, Any]) -> str:
        """Render descriptive statistics component."""
        return f"""
        <div class="report-component descriptive-stats">
            <div class="component-header">
                <span class="component-icon">📊</span>
                <h3 class="component-title">Conversation Statistics</h3>
            </div>
            <div class="stats-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-value">{data['total_messages']}</span>
                        <span class="stat-label">Total Messages</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{data['user_messages']}</span>
                        <span class="stat-label">User Messages</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{data['assistant_messages']}</span>
                        <span class="stat-label">AI Responses</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{data['session_duration_hours']}h</span>
                        <span class="stat-label">Session Duration</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{round(data['avg_words_per_user_message'])}</span>
                        <span class="stat-label">Avg Words/User Msg</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{data['total_words']:,}</span>
                        <span class="stat-label">Total Words</span>
                    </div>
                </div>
            </div>
        </div>
        """

    def _render_nlp_analysis(self, data: Dict[str, Any]) -> str:
        """Render NLP analysis component."""
        sentiment_label = self._get_sentiment_label(data['average_sentiment'])

        return f"""
        <div class="report-component nlp-analysis">
            <div class="component-header">
                <span class="component-icon">🧠</span>
                <h3 class="component-title">Language Analysis</h3>
            </div>
            <div class="nlp-content">
                <div class="nlp-grid">
                    <div class="nlp-card">
                        <h4 class="nlp-title">Sentiment Analysis</h4>
                        <div class="sentiment-score">
                            Overall: {data['average_sentiment']:.2f} ({sentiment_label})
                        </div>
                        <div class="progress-bars">
                            <div class="progress-item">
                                <span>Positive ({data['sentiment_percentages']['positive']:.0f}%)</span>
                                <div class="progress-bar">
                                    <div class="progress-fill progress-positive" style="width: {data['sentiment_percentages']['positive']:.0f}%"></div>
                                </div>
                            </div>
                            <div class="progress-item">
                                <span>Neutral ({data['sentiment_percentages']['neutral']:.0f}%)</span>
                                <div class="progress-bar">
                                    <div class="progress-fill progress-neutral" style="width: {data['sentiment_percentages']['neutral']:.0f}%"></div>
                                </div>
                            </div>
                            <div class="progress-item">
                                <span>Negative ({data['sentiment_percentages']['negative']:.0f}%)</span>
                                <div class="progress-bar">
                                    <div class="progress-fill progress-negative" style="width: {data['sentiment_percentages']['negative']:.0f}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="nlp-card">
                        <h4 class="nlp-title">Voice Analysis</h4>
                        <div class="progress-bars">
                            <div class="progress-item">
                                <span>Active Voice ({data['voice_analysis']['active_ratio']:.0f}%)</span>
                                <div class="progress-bar">
                                    <div class="progress-fill progress-active" style="width: {data['voice_analysis']['active_ratio']:.0f}%"></div>
                                </div>
                            </div>
                            <div class="progress-item">
                                <span>Passive Voice ({data['voice_analysis']['passive_ratio']:.0f}%)</span>
                                <div class="progress-bar">
                                    <div class="progress-fill progress-passive" style="width: {data['voice_analysis']['passive_ratio']:.0f}%"></div>
                                </div>
                            </div>
                        </div>
                        <p class="nlp-note">Questions: {data['question_frequency']:.0f}% of messages</p>
                    </div>
                </div>
            </div>
        </div>
        """

    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label from score."""
        if score > 0.3:
            return "Positive"
        elif score < -0.3:
            return "Negative"
        else:
            return "Neutral"
