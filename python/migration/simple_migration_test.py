"""
Simple migration test without unicode characters
"""

import os
import sys

def test_folder_structure():
    """Test folder structure after migration"""
    print("Testing folder structure...")
    
    expected_folders = [
        "python/mono_tools/file_manager",
        "python/mono_tools/material_loader",
        "python/mono_tools/texture_search_replace",
        "python/mono_tools/qt",
        "python/mono_tools/utils",
        "python/mono_tools/test_demo"
    ]
    
    missing_folders = []
    for folder in expected_folders:
        if not os.path.exists(folder):
            missing_folders.append(folder)
    
    if missing_folders:
        print("MISSING FOLDERS:")
        for folder in missing_folders:
            print(f"  - {folder}")
        return False
    else:
        print("OK: All expected folders exist")
        return True

def test_init_files():
    """Test __init__.py files"""
    print("\nTesting __init__.py files...")
    
    init_files = [
        "python/mono_tools/file_manager/__init__.py",
        "python/mono_tools/material_loader/__init__.py",
        "python/mono_tools/texture_search_replace/__init__.py",
        "python/mono_tools/qt/__init__.py",
        "python/mono_tools/utils/__init__.py"
    ]
    
    missing_inits = []
    for init_file in init_files:
        if not os.path.exists(init_file):
            missing_inits.append(init_file)
    
    if missing_inits:
        print("MISSING __init__.py files:")
        for init_file in missing_inits:
            print(f"  - {init_file}")
        return False
    else:
        print("OK: All __init__.py files exist")
        return True

def test_imports():
    """Test imports after migration"""
    print("\nTesting imports...")
    
    try:
        # Test main package import
        from mono_tools import show_texture_search_replace
        print("OK: show_texture_search_replace imported")
        
        from mono_tools import show_material_loader
        print("OK: show_material_loader imported")
        
        from mono_tools import show_mono_file_manager
        print("OK: show_mono_file_manager imported")
        
        from mono_tools import QtCore, QtGui, QtWidgets
        print("OK: Qt modules imported")
        
        from mono_tools import MonoUtils
        print("OK: MonoUtils imported")
        
        return True
        
    except ImportError as e:
        print(f"IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False

def test_file_movements():
    """Test that files were moved correctly"""
    print("\nTesting file movements...")
    
    # Check that files are in correct locations
    file_locations = {
        "python/mono_tools/file_manager/file_manager.py": True,
        "python/mono_tools/file_manager/file_manager_api.py": True,
        "python/mono_tools/file_manager/file_manager_helpers.py": True,
        "python/mono_tools/file_manager/file_manager_manager.py": True,
        "python/mono_tools/file_manager/file_manager_minibar.py": True,
        "python/mono_tools/file_manager/file_manager_models.py": True,
        "python/mono_tools/material_loader/material_loader.py": True,
        "python/mono_tools/texture_search_replace/texture_search_replace.py": True,
        "python/mono_tools/texture_search_replace/texture_menu_integration.py": True,
        "python/mono_tools/qt/qt.py": True,
        "python/mono_tools/utils/utils.py": True
    }
    
    missing_files = []
    for file_path, should_exist in file_locations.items():
        if should_exist and not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("MISSING FILES:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("OK: All files in correct locations")
        return True

def test_old_files_removed():
    """Test that old files were removed from root"""
    print("\nTesting old files removed...")
    
    old_files = [
        "python/mono_tools/file_manager.py",
        "python/mono_tools/material_loader.py",
        "python/mono_tools/texture_search_replace.py",
        "python/mono_tools/texture_menu_integration.py",
        "python/mono_tools/qt.py",
        "python/mono_tools/utils.py",
        "python/mono_tools/fm_helpers.py",
        "python/mono_tools/fm_manager.py",
        "python/mono_tools/fm_minibar.py",
        "python/mono_tools/fm_models.py"
    ]
    
    remaining_files = []
    for file_path in old_files:
        if os.path.exists(file_path):
            remaining_files.append(file_path)
    
    if remaining_files:
        print("REMAINING OLD FILES:")
        for file_path in remaining_files:
            print(f"  - {file_path}")
        return False
    else:
        print("OK: All old files removed from root")
        return True

def main():
    """Main test function"""
    print("Mono Studio - Post-Migration Test")
    print("=" * 40)
    
    tests = [
        ("Folder Structure", test_folder_structure),
        ("Init Files", test_init_files),
        ("File Movements", test_file_movements),
        ("Old Files Removed", test_old_files_removed),
        ("Imports", test_imports)
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
