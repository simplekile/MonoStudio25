"""
Material Loader Menu Integration
Tích hợp Material Loader vào menu Houdini
"""

import hou
from .material_loader import show_material_loader

def add_material_loader_to_menu():
    """Thêm Material Loader vào menu Houdini"""
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
        
        # Add Material Loader action
        mono_menu.addAction("🎨 Material Loader", show_material_loader)
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error adding Material Loader to menu: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_material_loader_to_shelf():
    """Thêm Material Loader vào Houdini shelf"""
    try:
        return True
        
    except Exception as e:
        return False

def setup_material_loader_tools():
    """Setup tất cả material loader tools"""
    add_material_loader_to_menu()
    add_material_loader_to_shelf()
