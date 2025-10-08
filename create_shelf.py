#!/usr/bin/env python3
"""
Script để tạo Houdini shelf cho Mono Studio tools
Chạy script này trong Houdini Python Console
"""

def create_mono_studio_shelf():
    """Tạo shelf Mono Studio với tất cả tools"""
    try:
        import hou
        
        # Lấy shelf manager
        shelf_manager = hou.shelves.shelves()
        
        # Tạo shelf mới hoặc lấy shelf hiện tại
        shelf_name = "Mono Studio"
        shelf = shelf_manager.get(shelf_name)
        
        if not shelf:
            print(f"📦 Creating new shelf: {shelf_name}")
            shelf = shelf_manager.create(shelf_name)
        else:
            print(f"📦 Using existing shelf: {shelf_name}")
        
        # Clear existing tools (optional)
        # shelf.clear()
        
        # 1. File Manager Tool
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
            help_text="Open Mono File Manager for project navigation"
        )
        
        # 2. MiniBar Tool
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
            help_text="Open MiniBar for quick file access"
        )
        
        # 3. Material Loader Tool
        material_script = """
import hou
from mono_tools import show_material_loader
show_material_loader()
"""
        
        shelf.addTool(
            name="Material Loader",
            label="Material Loader",
            script=material_script,
            icon="MISC_material",
            help_text="Open Material Loader for material management"
        )
        
        # 4. Texture Tools Tool
        texture_script = """
import hou
from mono_tools import show_texture_search_replace
show_texture_search_replace()
"""
        
        shelf.addTool(
            name="Texture Tools",
            label="Texture Tools",
            script=texture_script,
            icon="MISC_texture",
            help_text="Open Texture Search & Replace tools"
        )
        
        # 5. All Tools Tool
        all_tools_script = """
import hou
from mono_tools import show_mono_file_manager, show_mono_minibar, show_material_loader, show_texture_search_replace

# Show all tools
show_mono_file_manager()
show_mono_minibar()
show_material_loader()
show_texture_search_replace()

print("🎬 All Mono Studio tools opened!")
"""
        
        shelf.addTool(
            name="All Tools",
            label="All Tools",
            script=all_tools_script,
            icon="MISC_all",
            help_text="Open all Mono Studio tools at once"
        )
        
        print("✅ Mono Studio shelf created successfully!")
        print(f"📋 Shelf '{shelf_name}' now contains:")
        print("   • File Manager")
        print("   • MiniBar")
        print("   • Material Loader")
        print("   • Texture Tools")
        print("   • All Tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating shelf: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🎬 Mono Studio - Shelf Creator")
    print("=" * 40)
    
    success = create_mono_studio_shelf()
    
    if success:
        print("\n🎉 Shelf creation completed!")
        print("💡 You can now use the Mono Studio shelf in Houdini")
    else:
        print("\n❌ Shelf creation failed!")
        print("💡 Please check the error messages above")

if __name__ == "__main__":
    main()
