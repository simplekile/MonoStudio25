"""
File Manager Menu Integration
Tích hợp File Manager vào menu Houdini
"""

import hou
from .file_manager import show_mono_file_manager
from .file_manager_api import show_mono_minibar

def add_file_manager_to_menu():
    """Thêm File Manager vào menu Houdini"""
    try:
        # Tìm hoặc tạo menu Mono Studio
        main_menu = hou.menuBar()
        
        # Tìm menu Mono Studio
        mono_menu = None
        for action in main_menu.actions():
            if action.text() == "Mono Studio":
                mono_menu = action.menu()
                break
        
        # Nếu không tìm thấy, tạo menu mới
        if not mono_menu:
            mono_menu = main_menu.addMenu("Mono Studio")
        
        # Thêm File Manager action
        file_manager_action = mono_menu.addAction("File Manager")
        file_manager_action.triggered.connect(show_mono_file_manager)
        
        # Thêm MiniBar action
        minibar_action = mono_menu.addAction("MiniBar")
        minibar_action.triggered.connect(show_mono_minibar)
        
        print("✅ File Manager đã được thêm vào menu Mono Studio")
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm menu: {e}")
        import traceback
        traceback.print_exc()

def add_file_manager_to_shelf():
    """Thêm File Manager vào Houdini shelf"""
    try:
        shelf = hou.shelves.shelves().get("Mono Studio")
        if not shelf:
            shelf = hou.shelves.shelves().create("Mono Studio")
        
        # File Manager tool
        file_manager_script = """
import hou
from mono_tools import show_mono_file_manager
show_mono_file_manager()
"""
        
        shelf.addTool(
            name="File Manager",
            script=file_manager_script,
            icon="MISC_folder",
            help_text="File management and navigation"
        )
        
        # MiniBar tool
        minibar_script = """
import hou
from mono_tools import show_mono_minibar
show_mono_minibar()
"""
        
        shelf.addTool(
            name="MiniBar",
            script=minibar_script,
            icon="MISC_minibar",
            help_text="Quick file access mini bar"
        )
        
        print("✅ File Manager đã được thêm vào shelf")
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm shelf: {e}")
        import traceback
        traceback.print_exc()

def setup_file_manager_tools():
    """Setup tất cả file manager tools"""
    add_file_manager_to_menu()
    add_file_manager_to_shelf()
