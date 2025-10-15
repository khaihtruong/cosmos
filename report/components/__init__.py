"""
Report Components Package

Components are self-contained features that generate data for reports.
Each component loads data, performs analysis, and returns structured results.
"""

from typing import Dict
from .ai_summary import AISummaryComponent
from .saved_messages import SavedMessagesComponent
from .descriptive_stats import DescriptiveStatsComponent
from .nlp_analysis import NLPAnalysisComponent

__all__ = [
    'AISummaryComponent',
    'SavedMessagesComponent',
    'DescriptiveStatsComponent',
    'NLPAnalysisComponent',
    'get_all_components',
]

# Component registry for dynamic loading
COMPONENT_REGISTRY = {
    'ai_summary': AISummaryComponent,
    'saved_messages': SavedMessagesComponent,
    'descriptive_stats': DescriptiveStatsComponent,
    'nlp_analysis': NLPAnalysisComponent,
}


def get_all_components(window, config: Dict = None):
    """
    Instantiate all registered components for a given window.

    Args:
        window: ChatWindow object or window_id
        config: Optional configuration dict

    Returns:
        Dict mapping component names to component instances
    """
    # Handle both ChatWindow objects and window IDs
    if hasattr(window, 'id'):
        window_id = window.id
        if config is None:
            config = window.get_report_config()
    else:
        window_id = window

    config = config or {}

    # Instantiate all components
    components = {}
    for name, component_class in COMPONENT_REGISTRY.items():
        components[name] = component_class(window_id, config)

    return components
