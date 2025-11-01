"""
Mono Studio Tools Package
Professional Houdini production tools suite
"""

__version__ = "2.5.0"
__author__ = "DTA Studio"

# Re-export Qt shim for convenient access (PySide6 preferred, PySide2 fallback)
from .qt import QtCore, QtGui, QtWidgets, API

# Import all tools from their respective packages
from .file_manager import (
    FileManagerWrapper,
    show_mono_file_manager,
    show_mono_minibar,
    MonoFileManager,
    MonoFileMiniBar,
)
from .material_loader import show_material_loader, setup_material_loader_tools
from .texture_search_replace import show_texture_search_replace, setup_texture_tools
from .file_manager import setup_file_manager_tools
from .utils import MonoUtils

# Test and verification functions
try:
    from .test_demo.test_pyside6 import run_all_tests as test_pyside6
    from .test_demo.verify_pyside6 import run_verification as verify_pyside6
    from .test_demo.demo_texture_search_replace import run_full_demo as demo_texture_search_replace
except ImportError:
    # Fallback if test modules not available
    test_pyside6 = None
    verify_pyside6 = None
    demo_texture_search_replace = None

# Export main functions for easy access
__all__ = [
    'FileManagerWrapper',
    'show_mono_file_manager', 
    'show_mono_minibar',
    'MonoFileManager',
    'MonoFileMiniBar',
    'show_material_loader',
    'setup_material_loader_tools',
    'show_texture_search_replace',
    'setup_texture_tools',
    'setup_file_manager_tools',
    'MonoUtils',
    'QtCore', 'QtGui', 'QtWidgets', 'API',
    'test_pyside6', 'verify_pyside6', 'demo_texture_search_replace'
]

# Convenience functions for quick access
def open_file_manager():
    """Open full File Manager dialog"""
    return show_mono_file_manager()

def open_minibar():
    """Open MiniBar"""
    return show_mono_minibar()