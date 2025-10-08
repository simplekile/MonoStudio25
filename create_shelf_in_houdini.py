#!/usr/bin/env python3
"""
Script để tạo shelf trực tiếp trong Houdini
Chạy trong Houdini Python Console
"""

def create_mono_studio_shelf_in_houdini():
    """Tạo shelf Mono Studio trực tiếp trong Houdini"""
    try:
        import hou
        
        print("Creating Mono Studio shelf in Houdini...")
        
        # Lấy shelf manager
        shelf_manager = hou.shelves.shelves()
        
        # Tạo shelf mới
        shelf_name = "MonoStudio"
        
        # Xóa shelf cũ nếu có
        if shelf_name in shelf_manager:
            print(f"Removing existing shelf: {shelf_name}")
            shelf_manager.remove(shelf_name)
        
        # Tạo shelf mới
        print(f"Creating new shelf: {shelf_name}")
        shelf = shelf_manager.create(shelf_name)
        
        # 1. File Manager Tool
        file_manager_script = """
import hou
from mono_tools import show_mono_file_manager
show_mono_file_manager()
"""
        
        shelf.addTool(
            name="File_Manager",
            label="File Manager",
            script=file_manager_script,
            icon="MISC_folder",
            help_text="Open Mono File Manager"
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
            help_text="Open MiniBar"
        )
        
        # 3. Material Loader Tool
        material_script = """
import hou
from mono_tools import show_material_loader
show_material_loader()
"""
        
        shelf.addTool(
            name="Material_Loader",
            label="Material Loader",
            script=material_script,
            icon="MISC_material",
            help_text="Open Material Loader"
        )
        
        # 4. Texture Tools Tool
        texture_script = """
import hou
from mono_tools import show_texture_search_replace
show_texture_search_replace()
"""
        
        shelf.addTool(
            name="Texture_Tools",
            label="Texture Tools",
            script=texture_script,
            icon="MISC_texture",
            help_text="Open Texture Tools"
        )
        
        # 5. All Tools Tool
        all_tools_script = """
import hou
from mono_tools import show_mono_file_manager, show_mono_minibar, show_material_loader, show_texture_search_replace

show_mono_file_manager()
show_mono_minibar()
show_material_loader()
show_texture_search_replace()

print("All Mono Studio tools opened!")
"""
        
        shelf.addTool(
            name="All_Tools",
            label="All Tools",
            script=all_tools_script,
            icon="MISC_all",
            help_text="Open all Mono Studio tools"
        )
        
        print("✅ Mono Studio shelf created successfully!")
        print(f"📋 Shelf '{shelf_name}' now contains:")
        print("   • File Manager")
        print("   • MiniBar")
        print("   • Material Loader")
        print("   • Texture Tools")
        print("   • All Tools")
        
        # Verify shelf was created
        if shelf_name in shelf_manager:
            print("✅ Shelf verification: SUCCESS")
            return True
        else:
            print("❌ Shelf verification: FAILED")
            return False
        
    except Exception as e:
        print(f"❌ Error creating shelf: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Mono Studio - Direct Shelf Creation")
    print("=" * 40)
    
    success = create_mono_studio_shelf_in_houdini()
    
    if success:
        print("\n🎉 Shelf creation completed!")
        print("💡 Look for 'MonoStudio' shelf tab in Houdini")
    else:
        print("\n❌ Shelf creation failed!")
        print("💡 Please check the error messages above")

if __name__ == "__main__":
    main()
