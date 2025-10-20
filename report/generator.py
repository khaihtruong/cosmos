"""
Report Generator

Main orchestrator for report generation. Coordinates components,
renderers, and output formats.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import time
import json
import os

# Suppress Google gRPC warnings about ALTS credentials
os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '0'
import logging
logging.getLogger('absl').setLevel(logging.ERROR)

# PDF generation - optional dependency
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"Warning: WeasyPrint not available for PDF generation: {e}")

from sqlalchemy.exc import OperationalError
from llm_chat.models import ChatWindow, Conversation, Message, Report
from llm_chat.extensions import db
from report.components import get_all_components
from report.renderers.html_renderer import HTMLRenderer
from report.renderers.pdf_renderer import PDFRenderer


class UnifiedReportGenerator:
    """Main unified report generator that orchestrates all components."""

    def __init__(self, window_id: int):
        """
        Initialize generator for a chat window.

        Args:
            window_id: ChatWindow ID to generate report for
        """
        self.window_id = window_id
        self.window = ChatWindow.query.get(window_id)
        if not self.window:
            raise ValueError(f"ChatWindow with id {window_id} not found")

        self.config = self.window.get_report_config()
        self.html_renderer = HTMLRenderer()
        self.pdf_renderer = PDFRenderer()
        self.components_data = {}

    def generate(self) -> Dict[str, Any]:
        """Generate all configured report components."""
        # Build metadata
        report_data = {
            'window_id': self.window_id,
            'window_title': self.window.title,
            'window_description': self.window.description or '',
            'patient_id': self.window.patient_id,
            'provider_id': self.window.provider_id,
            'start_date': self.window.start_date,
            'end_date': self.window.end_date,
            'generated_at': time.time(),
            'components': {}
        }

        # Execute all registered components
        components = get_all_components(self.window)
        for component_name, component in components.items():
            if self.config.get(component_name, False):
                try:
                    component_data = component.generate()
                    report_data['components'][component_name] = component_data
                    self.components_data[component_name] = (component, component_data)
                except Exception as e:
                    print(f"Error generating {component_name}: {e}")
                    report_data['components'][component_name] = {'error': str(e)}

        # Add summary statistics
        if 'descriptive_stats' in report_data['components']:
            stats = report_data['components']['descriptive_stats']
            report_data['summary'] = {
                'total_conversations': stats.get('conversations_count', 0),
                'total_user_messages': stats.get('user_messages', 0),
                'total_model_messages': stats.get('assistant_messages', 0),
                'average_messages_per_chat': stats.get('average_messages_per_chat', 0)
            }
        else:
            report_data['summary'] = {
                'total_conversations': 0,
                'total_user_messages': 0,
                'total_model_messages': 0,
                'average_messages_per_chat': 0
            }

        return report_data

    def render_html(self, report_data: Dict[str, Any] = None, standalone: bool = False) -> str:
        """Render report as HTML."""
        if not report_data:
            report_data = self.generate()

        return self.html_renderer.render_full_report(report_data, standalone=standalone)

    def render_pdf(self, report_data: Dict[str, Any] = None) -> str:
        """Render report optimized for PDF generation."""
        if not report_data:
            report_data = self.generate()

        return self.pdf_renderer.render_full_report(report_data, standalone=True)

    @classmethod
    def save_report(cls, window_id: int) -> Report:
        """Generate and save report to database with retry logic for SQLite locks."""
        generator = cls(window_id)
        report_data = generator.generate()

        # Save to database with retry logic for SQLite
        report = Report(
            window_id=window_id,
            patient_id=report_data['patient_id'],
            provider_id=report_data['provider_id'],
            report_type='unified',
            report_data=json.dumps(report_data),
            generated_at=report_data['generated_at']
        )

        # Retry up to 3 times with exponential backoff for SQLite lock issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db.session.add(report)
                db.session.commit()
                return report
            except OperationalError as e:
                db.session.rollback()
                if 'database is locked' in str(e) and attempt < max_retries - 1:
                    # Wait with exponential backoff: 0.5s, 1s, 2s
                    wait_time = 0.5 * (2 ** attempt)
                    print(f"Database locked, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed or different error
                    raise

    @classmethod
    def export_html(cls, window_id: int, filename: str = None) -> str:
        """Export report as standalone HTML file."""
        generator = cls(window_id)
        report_data = generator.generate()
        html_content = generator.render_html(report_data, standalone=True)

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return filename

        return html_content

    @classmethod
    def export_pdf(cls, window_id: int, filename: str = None) -> bytes:
        """Export report as PDF using weasyprint."""
        if not WEASYPRINT_AVAILABLE:
            raise ImportError("weasyprint is required for PDF generation. Install with: pip install weasyprint")

        generator = cls(window_id)
        report_data = generator.generate()
        html_content = generator.render_pdf(report_data)

        # Generate PDF using weasyprint
        html_doc = weasyprint.HTML(string=html_content)

        if filename:
            # Save to specified file
            html_doc.write_pdf(filename)
            with open(filename, 'rb') as f:
                return f.read()
        else:
            # Return PDF bytes
            return html_doc.write_pdf()
