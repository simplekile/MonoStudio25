"""
Material Loader Menu Integration
Tích hợp Material Loader vào menu Houdini
"""

import hou
from .material_loader import show_material_loader

def add_material_loader_to_menu():
    """Thêm Material Loader vào menu Houdini"""
    try:
        # Tìm hoặc tạo menu Mono Studio
        main_menu = hou.ui.mainMenuBar()
        
        # Tìm menu Mono Studio
        mono_menu = None
        for action in main_menu.actions():
            if action.text() == "Mono Studio":
                mono_menu = action.menu()
                break
        
        # Nếu không tìm thấy, tạo menu mới
        if not mono_menu:
            mono_menu = main_menu.addMenu("Mono Studio")
        
        # Thêm Material Loader action
        material_action = mono_menu.addAction("Material Loader")
        material_action.triggered.connect(show_material_loader)
        
        print("✅ Material Loader đã được thêm vào menu Mono Studio")
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm menu: {e}")
        import traceback
        traceback.print_exc()

def add_material_loader_to_shelf():
    """Thêm Material Loader vào Houdini shelf"""
    try:
        shelf_tabs = hou.shelves.shelves()
        shelf = shelf_tabs.get("Mono Studio")
        if not shelf:
            shelf = shelf_tabs.create("Mono Studio")
        
        script = """
import hou
from mono_tools import show_material_loader
show_material_loader()
"""
        
        shelf.addTool(
            name="Material Loader",
            script=script,
            icon="MISC_material",
            help_text="Material creation and loading"
        )
        print("✅ Material Loader đã được thêm vào shelf")
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm shelf: {e}")
        import traceback
        traceback.print_exc()

def setup_material_loader_tools():
    """Setup tất cả material loader tools"""
    add_material_loader_to_menu()
    add_material_loader_to_shelf()
