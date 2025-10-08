"""
Script để migrate tất cả tools sang folder structure
"""

import os
import shutil
from pathlib import Path

def create_folder_structure():
    """Tạo folder structure cho tất cả tools"""
    print("Creating folder structure for all tools...")
    
    mono_tools_path = Path("python/mono_tools")
    
    # Define tool folders to create
    tool_folders = [
        "texture_search_replace",
        "material_loader", 
        "qt",
        "utils"
    ]
    
    # Create folders
    for folder in tool_folders:
        folder_path = mono_tools_path / folder
        folder_path.mkdir(exist_ok=True)
        print(f"  Created: {folder_path}")
    
    print("✅ All tool folders created")

def move_files_to_folders():
    """Di chuyển files vào folders tương ứng"""
    print("\nMoving files to folders...")
    
    mono_tools_path = Path("python/mono_tools")
    
    # Define file movements
    file_movements = {
        "texture_search_replace": [
            "texture_search_replace.py",
            "texture_menu_integration.py"
        ],
        "material_loader": [
            "material_loader.py"
        ],
        "qt": [
            "qt.py"
        ],
        "utils": [
            "utils.py"
        ]
    }
    
    # Move files
    for folder, files in file_movements.items():
        for file in files:
            src = mono_tools_path / file
            dst = mono_tools_path / folder / file
            
            if src.exists():
                shutil.move(str(src), str(dst))
                print(f"  Moved: {file} -> {folder}/")
            else:
                print(f"  Warning: {file} not found")
    
    print("✅ All files moved to folders")

def create_init_files():
    """Tạo __init__.py files cho các tool folders"""
    print("\nCreating __init__.py files...")
    
    mono_tools_path = Path("python/mono_tools")
    
    # Texture Search & Replace
    texture_init = """# Texture Search & Replace Package
from .texture_search_replace import show_texture_search_replace
from .texture_menu_integration import setup_texture_tools

__all__ = [
    'show_texture_search_replace',
    'setup_texture_tools'
]
"""
    
    with open(mono_tools_path / "texture_search_replace" / "__init__.py", "w") as f:
        f.write(texture_init)
    print("  Created: texture_search_replace/__init__.py")
    
    # Material Loader
    material_init = """# Material Loader Package
from .material_loader import show_material_loader

__all__ = [
    'show_material_loader'
]
"""
    
    with open(mono_tools_path / "material_loader" / "__init__.py", "w") as f:
        f.write(material_init)
    print("  Created: material_loader/__init__.py")
    
    # Qt Utilities
    qt_init = """# Qt Utilities Package
from .qt import QtCore, QtGui, QtWidgets, API as QT_API

__all__ = [
    'QtCore', 'QtGui', 'QtWidgets', 'QT_API'
]
"""
    
    with open(mono_tools_path / "qt" / "__init__.py", "w") as f:
        f.write(qt_init)
    print("  Created: qt/__init__.py")
    
    # General Utils
    utils_init = """# General Utilities Package
from .utils import MonoUtils

__all__ = [
    'MonoUtils'
]
"""
    
    with open(mono_tools_path / "utils" / "__init__.py", "w") as f:
        f.write(utils_init)
    print("  Created: utils/__init__.py")
    
    print("✅ All __init__.py files created")

def update_main_init():
    """Cập nhật main __init__.py file"""
    print("\nUpdating main __init__.py...")
    
    main_init_content = '''"""
Mono Studio Tools Package
Professional Houdini production tools suite
"""

__version__ = "2.0.0"
__author__ = "DTA Studio"

# Re-export Qt shim for convenient access (PySide6 preferred, PySide2 fallback)
from .qt import QtCore, QtGui, QtWidgets, API as QT_API

# Import all tools
from .file_manager import (
    FileManagerWrapper,
    show_mono_file_manager,
    show_mono_minibar,
    MonoFileManager,
    MonoFileMiniBar,
)
from .material_loader import show_material_loader  
from .texture_search_replace import show_texture_search_replace, setup_texture_tools
from .utils import MonoUtils

# Test and verification functions
try:
    from .test_demo.test_pyside6 import run_all_tests as test_pyside6
    from .test_demo.verify_pyside6 import run_verification as verify_pyside6
    from .test_demo.demo_texture_search_replace import run_full_demo as demo_texture_search_replace
except ImportError:
    # Fallback if test modules not available
    test_pyside6 = None
    verify_pyside6 = None
    demo_texture_search_replace = None

# Export main functions for easy access
__all__ = [
    'FileManagerWrapper',
    'show_mono_file_manager', 
    'show_mono_minibar',
    'MonoFileManager',
    'MonoFileMiniBar',
    'show_material_loader',
    'show_texture_search_replace',
    'setup_texture_tools',
    'MonoUtils',
    'QtCore', 'QtGui', 'QtWidgets', 'QT_API',
    'test_pyside6', 'verify_pyside6', 'demo_texture_search_replace',
    'initialize'
]

# Auto-initialize when package loads
def initialize():
    """Initialize Mono Studio tools"""
    print("🎬 Mono Studio v2.0.0 - Initializing...")
    
    try:
        # Show MiniBar instead of just creating wrapper
        minibar = show_mono_minibar()
        
        if minibar:
            print("✅ Mono Studio MiniBar loaded successfully!")
            print("💡 Tips:")
            print("   • Click shot name to open file in Houdini")
            print("   • Click ⚡ button for full File Manager")
            print("   • Right-click handle for options")
            return True
        else:
            print("⚠️ MiniBar not loaded - check Houdini environment")
            return False
        
    except Exception as e:
        print(f"❌ Failed to initialize Mono Studio: {e}")
        # Fallback to wrapper approach
        try:
            file_manager = FileManagerWrapper()
            file_manager.show_minibar()
            print("✅ Fallback mode: Using compatibility wrapper")
            return True
        except:
            return False

# Convenience functions for manual usage
def open_file_manager():
    """Open full File Manager dialog"""
    return show_mono_file_manager()

def open_minibar():
    """Open MiniBar (if not already shown)"""
    return show_mono_minibar()

# Auto-run disabled - using startup script instead
# Use: import mono_tools; mono_tools.initialize() to run manually
# Or use: mono_tools.open_minibar() for quick access
'''
    
    with open("python/mono_tools/__init__.py", "w") as f:
        f.write(main_init_content)
    
    print("✅ Main __init__.py updated")

def create_material_menu_integration():
    """Tạo material menu integration file"""
    print("\nCreating material menu integration...")
    
    material_menu_content = '''"""
Material Loader Menu Integration
Tích hợp Material Loader vào menu Houdini
"""

import hou
from .material_loader import show_material_loader

def add_material_loader_to_menu():
    """Thêm Material Loader vào menu Houdini"""
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
        
        # Thêm Material Loader action
        material_action = mono_menu.addAction("Material Loader")
        material_action.triggered.connect(show_material_loader)
        
        print("✅ Material Loader đã được thêm vào menu Mono Studio")
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm menu: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main migration function"""
    print("Mono Studio - All Tools Folder Migration")
    print("=" * 50)
    
    try:
        # Step 1: Create folder structure
        create_folder_structure()
        
        # Step 2: Move files to folders
        move_files_to_folders()
        
        # Step 3: Create __init__.py files
        create_init_files()
        
        # Step 4: Update main __init__.py
        update_main_init()
        
        # Step 5: Create missing menu integration
        create_material_menu_integration()
        
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        print("\nNew structure:")
        print("python/mono_tools/")
        print("├── texture_search_replace/")
        print("├── material_loader/")
        print("├── file_manager/")
        print("├── qt/")
        print("├── utils/")
        print("└── test_demo/")
        
        print("\nNext steps:")
        print("1. Test all imports work correctly")
        print("2. Test menu and shelf integration")
        print("3. Update documentation")
        print("4. Run consistency check")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
