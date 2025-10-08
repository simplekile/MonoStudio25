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
        # Sử dụng cách đơn giản hơn - chỉ tạo menu nếu có thể
        print("ℹ️ Menu integration temporarily disabled - using direct access")
        print("💡 Use: from mono_tools import show_mono_file_manager, show_mono_minibar")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm menu: {e}")
        return False

def add_file_manager_to_shelf():
    """Thêm File Manager vào Houdini shelf"""
    try:
        # Thử tạo shelf bằng cách đơn giản
        shelf_manager = hou.shelves.shelves()
        shelf_name = "Mono Studio"
        
        # Tạo hoặc lấy shelf
        shelf = shelf_manager.get(shelf_name)
        if not shelf:
            shelf = shelf_manager.create(shelf_name)
            print(f"✅ Created shelf: {shelf_name}")
        else:
            print(f"✅ Using existing shelf: {shelf_name}")
        
        # Thêm File Manager tool
        file_manager_script = """
import hou
from mono_tools import show_mono_file_manager
show_mono_file_manager()
"""
        
        shelf.addTool(
            name="File Manager",
            label="File Manager",
            script=file_manager_script,
            icon="MISC_folder",
            help_text="Open Mono File Manager"
        )
        
        # Thêm MiniBar tool
        minibar_script = """
import hou
from mono_tools import show_mono_minibar
show_mono_minibar()
"""
        
        shelf.addTool(
            name="MiniBar",
            label="MiniBar",
            script=minibar_script,
            icon="MISC_minibar",
            help_text="Open MiniBar"
        )
        
        print("✅ File Manager tools added to shelf")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm shelf: {e}")
        print("💡 Use: from mono_tools import show_mono_file_manager, show_mono_minibar")
        return False

def setup_file_manager_tools():
    """Setup tất cả file manager tools"""
    add_file_manager_to_menu()
    add_file_manager_to_shelf()
