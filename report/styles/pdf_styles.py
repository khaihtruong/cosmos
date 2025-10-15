"""
PDF-Specific Styles

Additional CSS rules optimized for PDF generation and printing.
These styles are added on top of the base styles.
"""


def get_pdf_css() -> str:
    """Get PDF-specific CSS additions."""
    return """
    @page {
        size: A4;
        margin: 1cm;
    }

    .unified-report.print-mode {
        box-shadow: none;
        border-radius: 0;
    }

    .unified-report .report-section {
        page-break-inside: avoid;
    }

    .unified-report .report-header.print-header {
        page-break-after: avoid;
    }

    .unified-report .stats-grid,
    .unified-report .nlp-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    @media print {
        .unified-report {
            max-width: 100%;
        }
    }
    """
