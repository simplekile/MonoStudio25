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
        # Get main window
        main_window = hou.qt.mainWindow()
        if not main_window:
            return False
        
        # Find menu bar - it's a child of main window
        from mono_tools.qt import QtWidgets
        menu_bar = main_window.findChild(QtWidgets.QMenuBar)
        if not menu_bar:
            return False
        
        # Find or create Mono Studio menu
        mono_menu = None
        for action in menu_bar.actions():
            if action.text() == "MonoStudio":
                mono_menu = action.menu()
                break
        
        if not mono_menu:
            mono_menu = menu_bar.addMenu("MonoStudio")
        
        # Add File Manager actions
        mono_menu.addAction("⚡ File Manager", show_mono_file_manager)
        mono_menu.addAction("🚀 Show MiniBar", show_minibar_manually)
        mono_menu.addAction("❌ Hide MiniBar", hide_minibar_manually)
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error adding to menu: {e}")
        import traceback
        traceback.print_exc()
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
