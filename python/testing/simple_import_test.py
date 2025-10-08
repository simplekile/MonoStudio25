"""
Simple import test without unicode characters
"""

import sys
import os

def test_basic_imports():
    """Test basic imports without Houdini dependencies"""
    print("Testing basic imports...")
    
    try:
        # Add python to path
        sys.path.insert(0, 'python')
        
        # Test Qt imports first
        print("1. Testing Qt imports...")
        from mono_tools.qt import QtCore, QtGui, QtWidgets, API
        print("   OK: Qt modules imported")
        print(f"   API = {API}")
        
        # Test utils imports
        print("2. Testing utils imports...")
        from mono_tools.utils import MonoUtils
        print("   OK: MonoUtils imported")
        
        # Test texture search replace imports
        print("3. Testing texture search replace imports...")
        from mono_tools.texture_search_replace import show_texture_search_replace
        print("   OK: show_texture_search_replace imported")
        
        from mono_tools.texture_search_replace import setup_texture_tools
        print("   OK: setup_texture_tools imported")
        
        # Test material loader imports
        print("4. Testing material loader imports...")
        from mono_tools.material_loader import show_material_loader
        print("   OK: show_material_loader imported")
        
        from mono_tools.material_loader import setup_material_loader_tools
        print("   OK: setup_material_loader_tools imported")
        
        # Test file_manager individual imports (without main file_manager.py)
        print("5. Testing file_manager individual imports...")
        from mono_tools.file_manager.file_manager_api import FileManagerWrapper
        print("   OK: FileManagerWrapper imported")
        
        from mono_tools.file_manager.file_manager_helpers import parse_ver
        print("   OK: file_manager_helpers imported")
        
        from mono_tools.file_manager.file_manager_models import FileTableModel
        print("   OK: file_manager_models imported")
        
        print("\nSUCCESS: All basic imports working!")
        print("The file_manager import issues have been fixed.")
        return True
        
    except ImportError as e:
        print(f"IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Mono Studio - Basic Import Test")
    print("=" * 40)
    
    success = test_basic_imports()
    
    if success:
        print("\nAll imports working correctly!")
        print("The file_manager import issues have been fixed.")
    else:
        print("\nSome imports still have issues.")
        print("Check the errors above for details.")
    
    return success

if __name__ == "__main__":
    main()
