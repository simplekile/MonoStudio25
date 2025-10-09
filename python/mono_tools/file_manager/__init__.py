"""
File Manager Package
Professional file management and navigation tools for Houdini
"""

from .file_manager_api import FileManagerWrapper, show_mono_file_manager, show_mono_minibar, MonoFileManager, MonoFileMiniBar
from .file_manager_helpers import (
    parse_ver, 
    increment_version_and_backup,
    scan_project_types,
    scan_departments_for_type,
    collect_files_with_filters,
    find_thumbnail,
    get_supported_file_extensions
)
from .file_manager_models import FileTableModel
from .file_manager_menu_integration import setup_file_manager_tools
from .file_manager_settings import MonoFileManagerSettings

__all__ = [
    'show_mono_file_manager',
    'MonoFileManager',
    'FileManagerWrapper',
    'show_mono_minibar',
    'MonoFileMiniBar',
    'MonoFileManagerSettings',
    'parse_ver',
    'increment_version_and_backup',
    'scan_project_types',
    'scan_departments_for_type',
    'collect_files_with_filters',
    'find_thumbnail',
    'get_supported_file_extensions',
    'FileTableModel',
    'setup_file_manager_tools'
]
