"""
Renderers Package

Renderers convert structured data into output formats (HTML, PDF, etc.).
They handle presentation logic but don't do any data processing.
"""

from .html_renderer import HTMLRenderer
from .pdf_renderer import PDFRenderer

__all__ = [
    'HTMLRenderer',
    'PDFRenderer',
]
