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
from .styles import (
    get_menu_style,
    get_dialog_style,
    get_note_style,
    get_note_font_size,
    COLOR_BG,
    COLOR_BG_DARK,
    COLOR_BG_DARKER,
    COLOR_TEXT_DIM,
    COLOR_SELECTED,
)

__all__ = [
    'MonoBaseDialog',
    'SmartLineEdit',
    'ConfigManager',
    'ChoiceDialog',
    'InputDialog',
    'NewFileDialog',
    'NewFolderDialog',
    'get_menu_style',
    'get_dialog_style',
    'get_note_style',
    'get_note_font_size',
    'COLOR_BG',
    'COLOR_BG_DARK',
    'COLOR_BG_DARKER',
    'COLOR_TEXT_DIM',
    'COLOR_SELECTED',
]

