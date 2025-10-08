"""
File Manager Package
Professional file management and navigation tools for Houdini
"""

from .file_manager import show_mono_file_manager, MonoFileManager
from .file_manager_api import FileManagerWrapper, show_mono_minibar
from .file_manager_minibar import MonoFileMiniBar
from .file_manager_helpers import parse_ver, increment_version_and_backup
from .file_manager_models import FileTableModel
from .file_manager_menu_integration import setup_file_manager_tools

__all__ = [
    'show_mono_file_manager',
    'MonoFileManager',
    'FileManagerWrapper',
    'show_mono_minibar',
    'MonoFileMiniBar',
    'parse_ver',
    'increment_version_and_backup',
    'FileTableModel',
    'setup_file_manager_tools'
]
