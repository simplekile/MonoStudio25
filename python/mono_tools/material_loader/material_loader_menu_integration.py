"""
Material Loader Menu Integration
Tích hợp Material Loader vào menu Houdini
"""

import hou
from .material_loader import show_material_loader

def add_material_loader_to_menu():
    """Thêm Material Loader vào menu Houdini"""
    try:
        return True
        
    except Exception as e:
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
