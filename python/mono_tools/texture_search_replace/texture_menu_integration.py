"""
Texture Search & Replace Menu Integration
Tích hợp Texture Search & Replace vào menu Houdini
"""

import hou
from .texture_search_replace import show_texture_search_replace


def add_texture_tools_to_menu():
    """Thêm Texture Search & Replace vào menu Houdini"""
    try:
        return True
        
    except Exception as e:
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
