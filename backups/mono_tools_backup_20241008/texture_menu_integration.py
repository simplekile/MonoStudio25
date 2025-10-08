"""
Texture Search & Replace Menu Integration
Tích hợp Texture Search & Replace vào menu Houdini
"""

import hou
from .texture_search_replace import show_texture_search_replace


def add_texture_tools_to_menu():
    """Thêm Texture Search & Replace vào menu Houdini"""
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
        
        # Thêm Texture Search & Replace action
        texture_action = mono_menu.addAction("Texture Search & Replace")
        texture_action.triggered.connect(show_texture_search_replace)
        
        # Thêm separator
        mono_menu.addSeparator()
        
        print("✅ Texture Search & Replace đã được thêm vào menu Mono Studio")
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm menu: {e}")
        import traceback
        traceback.print_exc()


def add_to_shelf():
    """Thêm Texture Search & Replace vào shelf"""
    try:
        # Lấy shelf hiện tại
        shelf = hou.shelves.shelves().get("Mono Studio")
        if not shelf:
            # Tạo shelf mới nếu chưa có
            shelf = hou.shelves.shelves().create("Mono Studio")
        
        # Tạo script cho shelf tool
        script = """
import hou
from mono_tools.texture_search_replace import show_texture_search_replace
show_texture_search_replace()
"""
        
        # Thêm tool vào shelf
        shelf.addTool(
            name="Texture Search & Replace",
            script=script,
            icon="MISC_texture",
            help_text="Tìm kiếm và thay thế đường dẫn texture"
        )
        
        print("✅ Texture Search & Replace đã được thêm vào shelf Mono Studio")
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm vào shelf: {e}")


def setup_texture_tools():
    """Thiết lập tất cả texture tools"""
    add_texture_tools_to_menu()
    add_to_shelf()


# Auto-setup khi import
if __name__ == "__main__":
    setup_texture_tools()
