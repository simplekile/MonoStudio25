"""
File Manager Menu Integration
Tích hợp File Manager vào menu Houdini
"""

import hou
from .file_manager import show_mono_file_manager
from .file_manager_api import show_mono_minibar

# Global reference to MiniBar instance
_minibar_instance = None

def add_file_manager_to_menu():
    """Thêm File Manager vào menu Houdini"""
    try:
        # Add to Houdini menu
        main_menu = hou.ui.mainMenuBar()
        if main_menu:
            # Create MonoStudio menu
            mono_menu = main_menu.addMenu("MonoStudio")
            
            # File Manager submenu
            file_menu = mono_menu.addMenu("File Manager")
            
            # Settings Dialog
            file_menu.addAction("⚡ Settings Dialog", show_mono_file_manager)
            
            # MiniBar actions
            file_menu.addSeparator()
            file_menu.addAction("🚀 Show MiniBar", show_minibar_manually)
            file_menu.addAction("❌ Hide MiniBar", hide_minibar_manually)
            
            return True
        return False
        
    except Exception as e:
        print(f"⚠️ Error adding to menu: {e}")
        return False

def show_minibar_manually():
    """Show MiniBar manually"""
    global _minibar_instance
    try:
        if _minibar_instance is None:
            _minibar_instance = show_mono_minibar()
        else:
            _minibar_instance.show_minibar()
    except Exception as e:
        print(f"⚠️ Error showing MiniBar: {e}")

def hide_minibar_manually():
    """Hide MiniBar manually"""
    global _minibar_instance
    try:
        if _minibar_instance:
            _minibar_instance.hide()
    except Exception as e:
        print(f"⚠️ Error hiding MiniBar: {e}")

# Removed toggle_startup - always auto-start

def add_file_manager_to_shelf():
    """Thêm File Manager vào Houdini shelf"""
    try:
        return True
        
    except Exception as e:
        return False

def setup_file_manager_tools():
    """Setup tất cả file manager tools"""
    add_file_manager_to_menu()
    add_file_manager_to_shelf()
