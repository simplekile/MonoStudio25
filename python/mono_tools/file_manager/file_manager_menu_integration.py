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
        # Sử dụng cách đơn giản hơn - chỉ tạo shelf nếu có thể
        print("ℹ️ Shelf integration temporarily disabled - using direct access")
        print("💡 Use: from mono_tools import show_mono_file_manager, show_mono_minibar")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm shelf: {e}")
        return False

def setup_file_manager_tools():
    """Setup tất cả file manager tools"""
    add_file_manager_to_menu()
    add_file_manager_to_shelf()
