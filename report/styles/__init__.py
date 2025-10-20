"""
Styles Package

CSS styling for report rendering. Separated from rendering logic
to allow easy customization and theming.
"""

from .base_styles import get_base_css
from .pdf_styles import get_pdf_css


def get_html_styles(standalone: bool = False) -> str:
    """Get CSS for HTML rendering."""
    return get_base_css()


def get_pdf_styles() -> str:
    """Get CSS for PDF rendering (includes print optimizations)."""
    return get_base_css() + get_pdf_css()


__all__ = [
    'get_html_styles',
    'get_pdf_styles',
]
