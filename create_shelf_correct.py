#!/usr/bin/env python3
"""
Tạo shelf MonoStudio đúng cách cho Houdini 21
"""

def create_mono_studio_shelf_correct():
    """Tạo shelf MonoStudio đúng cách"""
    try:
        import hou
        
        print("Creating MonoStudio shelf...")
        
        # Lấy shelf manager
        shelf_manager = hou.shelves.shelves()
        
        # Kiểm tra xem MonoStudio đã tồn tại chưa
        if "MonoStudio" in shelf_manager:
            print("MonoStudio shelf already exists, removing...")
            del shelf_manager["MonoStudio"]
        
        # Tạo shelf mới bằng cách thêm vào dict
        print("Creating new MonoStudio shelf...")
        
        # Tạo shelf object (có thể cần import từ hou.shelves)
        try:
            # Thử cách 1: Tạo shelf object trực tiếp
            shelf = hou.shelves.Shelf("MonoStudio")
            shelf_manager["MonoStudio"] = shelf
            print("✅ Created shelf using hou.shelves.Shelf()")
        except:
            try:
                # Thử cách 2: Tạo shelf object khác
                shelf = hou.shelves.ShelfSet("MonoStudio")
                shelf_manager["MonoStudio"] = shelf
                print("✅ Created shelf using hou.shelves.ShelfSet()")
            except:
                try:
                    # Thử cách 3: Tạo shelf object khác nữa
                    shelf = hou.shelves.ShelfTab("MonoStudio")
                    shelf_manager["MonoStudio"] = shelf
                    print("✅ Created shelf using hou.shelves.ShelfTab()")
                except Exception as e:
                    print(f"❌ All shelf creation methods failed: {e}")
                    return False
        
        # Thêm tools vào shelf
        print("Adding tools to shelf...")
        
        # 1. File Manager Tool
        file_manager_script = """
import hou
from mono_tools import show_mono_file_manager
show_mono_file_manager()
"""
        
        try:
            shelf.addTool(
                name="File_Manager",
                label="File Manager",
                script=file_manager_script,
                icon="MISC_folder",
                help_text="Open Mono File Manager"
            )
            print("✅ Added File Manager tool")
        except Exception as e:
            print(f"❌ Failed to add File Manager tool: {e}")
        
        # 2. MiniBar Tool
        minibar_script = """
import hou
from mono_tools import show_mono_minibar
show_mono_minibar()
"""
        
        try:
            shelf.addTool(
                name="MiniBar",
                label="MiniBar",
                script=minibar_script,
                icon="MISC_minibar",
                help_text="Open MiniBar"
            )
            print("✅ Added MiniBar tool")
        except Exception as e:
            print(f"❌ Failed to add MiniBar tool: {e}")
        
        # 3. Material Loader Tool
        material_script = """
import hou
from mono_tools import show_material_loader
show_material_loader()
"""
        
        try:
            shelf.addTool(
                name="Material_Loader",
                label="Material Loader",
                script=material_script,
                icon="MISC_material",
                help_text="Open Material Loader"
            )
            print("✅ Added Material Loader tool")
        except Exception as e:
            print(f"❌ Failed to add Material Loader tool: {e}")
        
        # 4. Texture Tools Tool
        texture_script = """
import hou
from mono_tools import show_texture_search_replace
show_texture_search_replace()
"""
        
        try:
            shelf.addTool(
                name="Texture_Tools",
                label="Texture Tools",
                script=texture_script,
                icon="MISC_texture",
                help_text="Open Texture Tools"
            )
            print("✅ Added Texture Tools tool")
        except Exception as e:
            print(f"❌ Failed to add Texture Tools tool: {e}")
        
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
        
        try:
            shelf.addTool(
                name="All_Tools",
                label="All Tools",
                script=all_tools_script,
                icon="MISC_all",
                help_text="Open all Mono Studio tools"
            )
            print("✅ Added All Tools tool")
        except Exception as e:
            print(f"❌ Failed to add All Tools tool: {e}")
        
        # Verify shelf was created
        if "MonoStudio" in shelf_manager:
            print("✅ MonoStudio shelf created successfully!")
            print("📋 Available shelves:", list(shelf_manager.keys()))
            return True
        else:
            print("❌ MonoStudio shelf creation failed!")
            return False
        
    except Exception as e:
        print(f"❌ Error creating shelf: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Mono Studio - Correct Shelf Creation")
    print("=" * 40)
    
    success = create_mono_studio_shelf_correct()
    
    if success:
        print("\n🎉 Shelf creation completed!")
        print("💡 Look for 'MonoStudio' shelf tab in Houdini")
    else:
        print("\n❌ Shelf creation failed!")
        print("💡 Try manual creation in Houdini UI")

if __name__ == "__main__":
    main()
