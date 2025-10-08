#!/usr/bin/env python3
"""
Mono Studio - Professional Shelf Setup
Tự động setup shelf cho Houdini
"""

import os
import shutil
import platform
from pathlib import Path

def get_houdini_shelves_path():
    """Tìm thư mục Houdini shelves"""
    system = platform.system()
    
    if system == "Windows":
        # Windows paths
        possible_paths = [
            os.path.expanduser("~/Documents/houdini21.0/shelves"),
            os.path.expanduser("~/Documents/houdini20.5/shelves"),
            os.path.expanduser("~/Documents/houdini20.0/shelves"),
            os.path.expanduser("~/Documents/houdini19.5/shelves"),
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            os.path.expanduser("~/Library/Preferences/houdini/21.0/shelves"),
            os.path.expanduser("~/Library/Preferences/houdini/20.5/shelves"),
            os.path.expanduser("~/Library/Preferences/houdini/20.0/shelves"),
        ]
    else:  # Linux
        possible_paths = [
            os.path.expanduser("~/.houdini/21.0/shelves"),
            os.path.expanduser("~/.houdini/20.5/shelves"),
            os.path.expanduser("~/.houdini/20.0/shelves"),
        ]
    
    # Tìm thư mục tồn tại
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Tạo thư mục mới nếu không tìm thấy
    default_path = possible_paths[0]
    os.makedirs(default_path, exist_ok=True)
    return default_path

def setup_mono_studio_shelf():
    """Setup Mono Studio shelf chuyên nghiệp"""
    print("Mono Studio - Professional Shelf Setup")
    print("=" * 50)
    
    try:
        # 1. Tìm thư mục Houdini shelves
        shelves_path = get_houdini_shelves_path()
        print(f"Houdini shelves path: {shelves_path}")
        
        # 2. Tạo thư mục nếu chưa có
        os.makedirs(shelves_path, exist_ok=True)
        
        # 3. Copy file shelf
        source_file = "shelves/MonoStudio.shelf"
        dest_file = os.path.join(shelves_path, "MonoStudio.shelf")
        
        if os.path.exists(source_file):
            shutil.copy2(source_file, dest_file)
            print(f"Copied shelf file to: {dest_file}")
        else:
            print(f"Source file not found: {source_file}")
            return False
        
        # 4. Tạo file backup
        backup_file = os.path.join(shelves_path, "MonoStudio.shelf.backup")
        if os.path.exists(dest_file) and not os.path.exists(backup_file):
            shutil.copy2(dest_file, backup_file)
            print(f"Created backup: {backup_file}")
        
        # 5. Verify installation
        if os.path.exists(dest_file):
            print("Shelf installation completed successfully!")
            print("\nNext steps:")
            print("1. Restart Houdini")
            print("2. Look for 'Mono Studio' shelf tab")
            print("3. Use the tools:")
            print("   - File Manager - Project navigation")
            print("   - MiniBar - Quick file access")
            print("   - Material Loader - Material management")
            print("   - Texture Tools - Search & replace")
            print("   - All Tools - Open everything")
            
            return True
        else:
            print("Shelf installation failed!")
            return False
            
    except Exception as e:
        print(f"Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_advanced_shelf():
    """Tạo shelf nâng cao với nhiều tính năng"""
    advanced_shelf_content = '''version 1.0
toolbar MonoStudio
{
    tool File_Manager
    {
        label "File Manager"
        icon "MISC_folder"
        script
        {
            import hou
            from mono_tools import show_mono_file_manager
            show_mono_file_manager()
        }
    }
    
    tool MiniBar
    {
        label "MiniBar"
        icon "MISC_minibar"
        script
        {
            import hou
            from mono_tools import show_mono_minibar
            show_mono_minibar()
        }
    }
    
    tool Material_Loader
    {
        label "Material Loader"
        icon "MISC_material"
        script
        {
            import hou
            from mono_tools import show_material_loader
            show_material_loader()
        }
    }
    
    tool Texture_Tools
    {
        label "Texture Tools"
        icon "MISC_texture"
        script
        {
            import hou
            from mono_tools import show_texture_search_replace
            show_texture_search_replace()
        }
    }
    
    separator
    
    tool All_Tools
    {
        label "All Tools"
        icon "MISC_all"
        script
        {
            import hou
            from mono_tools import show_mono_file_manager, show_mono_minibar, show_material_loader, show_texture_search_replace
            
            # Show all tools
            show_mono_file_manager()
            show_mono_minibar()
            show_material_loader()
            show_texture_search_replace()
            
            print("🎬 All Mono Studio tools opened!")
        }
    }
    
    tool Refresh_Tools
    {
        label "Refresh Tools"
        icon "MISC_refresh"
        script
        {
            import hou
            import importlib
            import sys
            
            # Reload mono_tools modules
            modules_to_reload = [
                'mono_tools',
                'mono_tools.file_manager',
                'mono_tools.file_manager.file_manager_api',
                'mono_tools.file_manager.file_manager_minibar',
                'mono_tools.material_loader',
                'mono_tools.texture_search_replace'
            ]
            
            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
            
            print("🔄 Mono Studio tools refreshed!")
        }
    }
    
    tool Help
    {
        label "Help"
        icon "MISC_help"
        script
        {
            import hou
            hou.ui.displayMessage(
                "Mono Studio v2.0.0\\n\\n"
                "Available Tools:\\n"
                "• File Manager - Project navigation\\n"
                "• MiniBar - Quick file access\\n"
                "• Material Loader - Material management\\n"
                "• Texture Tools - Search & replace\\n\\n"
                "For more info, visit: https://github.com/simplekile/MonoStudio25",
                severity=hou.severityType.Message
            )
        }
    }
}'''
    
    # Lưu file shelf nâng cao
    with open("shelves/MonoStudioAdvanced.shelf", "w", encoding="utf-8") as f:
        f.write(advanced_shelf_content)
    
    print("Created advanced shelf: MonoStudioAdvanced.shelf")

def main():
    """Main function"""
    print("Starting professional shelf setup...")
    
    # Setup basic shelf
    success = setup_mono_studio_shelf()
    
    # Create advanced shelf
    create_advanced_shelf()
    
    if success:
        print("\nSetup completed successfully!")
        print("Professional shelf installation done!")
    else:
        print("\nSetup failed!")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()
