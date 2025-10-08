"""
Test basic imports without Houdini dependencies
"""

import sys
import os

def test_basic_imports():
    """Test basic imports without Houdini"""
    print("Testing basic imports...")
    
    try:
        # Add python to path
        sys.path.insert(0, 'python')
        
        # Test Qt imports
        from mono_tools.qt import QtCore, QtGui, QtWidgets, API
        print("OK: Qt modules imported")
        print(f"  API = {API}")
        
        # Test utils
        from mono_tools.utils import MonoUtils
        print("OK: MonoUtils imported")
        
        # Test file manager imports
        from mono_tools.file_manager import show_mono_file_manager
        print("OK: show_mono_file_manager imported")
        
        from mono_tools.file_manager import FileManagerWrapper
        print("OK: FileManagerWrapper imported")
        
        # Test material loader imports
        from mono_tools.material_loader import show_material_loader
        print("OK: show_material_loader imported")
        
        # Test texture search replace imports
        from mono_tools.texture_search_replace import show_texture_search_replace
        print("OK: show_texture_search_replace imported")
        
        from mono_tools.texture_search_replace import setup_texture_tools
        print("OK: setup_texture_tools imported")
        
        # Test setup functions
        from mono_tools.file_manager import setup_file_manager_tools
        print("OK: setup_file_manager_tools imported")
        
        from mono_tools.material_loader import setup_material_loader_tools
        print("OK: setup_material_loader_tools imported")
        
        print("\nSUCCESS: All basic imports working!")
        return True
        
    except ImportError as e:
        print(f"IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_package_structure():
    """Test package structure"""
    print("\nTesting package structure...")
    
    # Check main package
    if os.path.exists("python/mono_tools/__init__.py"):
        print("OK: Main __init__.py exists")
    else:
        print("ERROR: Main __init__.py missing")
        return False
    
    # Check tool packages
    tool_packages = [
        "file_manager",
        "material_loader", 
        "texture_search_replace",
        "qt",
        "utils"
    ]
    
    for package in tool_packages:
        package_path = f"python/mono_tools/{package}"
        init_path = f"{package_path}/__init__.py"
        
        if os.path.exists(package_path) and os.path.exists(init_path):
            print(f"OK: {package} package exists")
        else:
            print(f"ERROR: {package} package missing")
            return False
    
    print("SUCCESS: All packages exist!")
    return True

def main():
    """Main test function"""
    print("Mono Studio - Basic Import Test")
    print("=" * 40)
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Basic Imports", test_basic_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                print(f"PASS: {test_name}")
                passed += 1
            else:
                print(f"FAIL: {test_name}")
        except Exception as e:
            print(f"ERROR: {test_name} - {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! Migration successful!")
    else:
        print("ISSUES: Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if success:
        print("\nMigration completed successfully!")
    else:
        print("\nMigration has issues - check the errors above")
