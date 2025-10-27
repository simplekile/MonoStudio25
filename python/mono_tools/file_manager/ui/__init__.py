"""
UI Components Package
Reusable UI components for MonoStudio with consistent styling
"""

from .base_dialog import MonoBaseDialog
from .smart_input import SmartLineEdit
from .config_manager import ConfigManager
from .choice_dialog import ChoiceDialog, InputDialog
from .new_file_dialog import NewFileDialog
from .new_folder_dialog import NewFolderDialog

__all__ = [
    'MonoBaseDialog',
    'SmartLineEdit',
    'ConfigManager',
    'ChoiceDialog',
    'InputDialog',
    'NewFileDialog',
    'NewFolderDialog',
]

