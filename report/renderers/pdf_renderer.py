"""
PDF Renderer

Extends HTML renderer with PDF-specific optimizations for print layout.
"""

from typing import Dict, Any

from .html_renderer import HTMLRenderer
from report.styles import get_pdf_styles


class PDFRenderer(HTMLRenderer):
    """Renders reports optimized for PDF generation."""

    def render_full_report(self, report_data: Dict[str, Any], standalone: bool = True) -> str:
        """
        Render complete report as HTML optimized for PDF.

        Args:
            report_data: Full report data including metadata and components
            standalone: Always True for PDF (needs full document)

        Returns:
            PDF-optimized HTML as string
        """
        css = get_pdf_styles()
        html_parts = []

        html_parts.append('<div class="unified-report print-mode">')
        html_parts.append(self.render_header(report_data))

        html_parts.append('<div class="report-content">')
        if 'components' in report_data:
            for component_name, component_data in report_data['components'].items():
                html_parts.append(
                    f'<div class="report-section print-section" data-component="{component_name}">'
                )
                html_parts.append(self.render_component(component_name, component_data))
                html_parts.append('</div>')

        html_parts.append('</div>')
        html_parts.append('</div>')

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
