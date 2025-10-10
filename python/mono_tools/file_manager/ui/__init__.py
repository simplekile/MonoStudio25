"""
UI Components Package
Reusable UI components for MonoStudio with consistent styling
"""

from .base_dialog import MonoBaseDialog
from .smart_input import SmartLineEdit
from .config_manager import ConfigManager

__all__ = [
    'MonoBaseDialog',
    'SmartLineEdit',
    'ConfigManager',
]

