"""
Mono Studio Tools Package
Professional Houdini production tools suite
"""

__version__ = "2.0.0"
__author__ = "DTA Studio"

# Re-export Qt shim for convenient access (PySide6 preferred, PySide2 fallback)
from .qt import QtCore, QtGui, QtWidgets, API as QT_API

# Import all tools
from .file_manager_api import (
    FileManagerWrapper,
    show_mono_file_manager,
    show_mono_minibar,
    MonoFileManager,
    MonoFileMiniBar,
)
from .material_loader import show_material_loader  
from .utils import MonoUtils

# Export main functions for easy access
__all__ = [
    'FileManagerWrapper',
    'show_mono_file_manager', 
    'show_mono_minibar',
    'MonoFileManager',
    'MonoFileMiniBar',
    'show_material_loader',
    'MonoUtils',
    'QtCore', 'QtGui', 'QtWidgets', 'QT_API',
    'initialize'
]

# Auto-initialize when package loads
def initialize():
    """Initialize Mono Studio tools"""
    print("🎬 Mono Studio v2.0.0 - Initializing...")
    
    try:
        # Show MiniBar instead of just creating wrapper
        minibar = show_mono_minibar()
        
        if minibar:
            print("✅ Mono Studio MiniBar loaded successfully!")
            print("💡 Tips:")
            print("   • Click shot name to open file in Houdini")
            print("   • Click ⚡ button for full File Manager")
            print("   • Right-click handle for options")
            return True
        else:
            print("⚠️ MiniBar not loaded - check Houdini environment")
            return False
        
    except Exception as e:
        print(f"❌ Failed to initialize Mono Studio: {e}")
        # Fallback to wrapper approach
        try:
            file_manager = FileManagerWrapper()
            file_manager.show_minibar()
            print("✅ Fallback mode: Using compatibility wrapper")
            return True
        except:
            return False

# Convenience functions for manual usage
def open_file_manager():
    """Open full File Manager dialog"""
    return show_mono_file_manager()

def open_minibar():
    """Open MiniBar (if not already shown)"""
    return show_mono_minibar()

# Auto-run disabled - using startup script instead
# Use: import mono_tools; mono_tools.initialize() to run manually
# Or use: mono_tools.open_minibar() for quick access