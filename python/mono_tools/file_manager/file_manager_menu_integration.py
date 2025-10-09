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
            
            # Startup toggle
            file_menu.addSeparator()
            startup_enabled = hou.userPref("minibar_startup_with_hou", True)
            if startup_enabled:
                file_menu.addAction("🚀 ✓ Startup with Houdini", toggle_startup)
            else:
                file_menu.addAction("🚀 Startup with Houdini", toggle_startup)
            
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

def toggle_startup():
    """Toggle startup with Houdini"""
    try:
        current = hou.userPref("minibar_startup_with_hou", True)
        new_value = not current
        hou.setUserPref("minibar_startup_with_hou", new_value)
        
        status = "enabled" if new_value else "disabled"
        hou.ui.displayMessage(
            f"MiniBar startup with Houdini {status}.\n\nRestart Houdini to apply changes.",
            severity=hou.severityType.Message
        )
    except Exception as e:
        print(f"⚠️ Error toggling startup: {e}")

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
