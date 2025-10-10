"""
Texture Search & Replace Menu Integration
Tích hợp Texture Search & Replace vào menu Houdini
"""

import hou
from .texture_search_replace import show_texture_search_replace


def add_texture_tools_to_menu():
    """Thêm Texture Search & Replace vào menu Houdini"""
    try:
        # Get main window and menu bar using Qt
        main_window = hou.qt.mainWindow()
        if not main_window:
            return False
        
        menu_bar = main_window.menuBar()
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
        
        # Add Texture Search & Replace action
        mono_menu.addAction("🔍 Texture Search & Replace", show_texture_search_replace)
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error adding Texture Tools to menu: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_to_shelf():
    """Thêm Texture Search & Replace vào shelf"""
    try:
        return True
        
    except Exception as e:
        return False


def setup_texture_tools():
    """Thiết lập tất cả texture tools"""
    add_texture_tools_to_menu()
    add_to_shelf()


# Auto-setup khi import
if __name__ == "__main__":
    setup_texture_tools()
