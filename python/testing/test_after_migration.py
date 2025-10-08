"""
Script test sau khi migration
"""

import os
import sys

def test_imports():
    """Test tất cả imports sau migration"""
    print("Testing imports after migration...")
    
    try:
        # Test main package import
        from mono_tools import show_texture_search_replace
        print("✅ show_texture_search_replace imported")
        
        from mono_tools import show_material_loader
        print("✅ show_material_loader imported")
        
        from mono_tools import show_mono_file_manager
        print("✅ show_mono_file_manager imported")
        
        from mono_tools import QtCore, QtGui, QtWidgets
        print("✅ Qt modules imported")
        
        from mono_tools import MonoUtils
        print("✅ MonoUtils imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_folder_structure():
    """Test folder structure sau migration"""
    print("\nTesting folder structure...")
    
    expected_folders = [
        "python/mono_tools/texture_search_replace",
        "python/mono_tools/material_loader",
        "python/mono_tools/file_manager",
        "python/mono_tools/qt",
        "python/mono_tools/utils",
        "python/mono_tools/test_demo"
    ]
    
    missing_folders = []
    for folder in expected_folders:
        if not os.path.exists(folder):
            missing_folders.append(folder)
    
    if missing_folders:
        print("❌ Missing folders:")
        for folder in missing_folders:
            print(f"   - {folder}")
        return False
    else:
        print("✅ All expected folders exist")
        return True

def test_init_files():
    """Test __init__.py files"""
    print("\nTesting __init__.py files...")
    
    init_files = [
        "python/mono_tools/texture_search_replace/__init__.py",
        "python/mono_tools/material_loader/__init__.py",
        "python/mono_tools/file_manager/__init__.py",
        "python/mono_tools/qt/__init__.py",
        "python/mono_tools/utils/__init__.py"
    ]
    
    missing_inits = []
    for init_file in init_files:
        if not os.path.exists(init_file):
            missing_inits.append(init_file)
    
    if missing_inits:
        print("❌ Missing __init__.py files:")
        for init_file in missing_inits:
            print(f"   - {init_file}")
        return False
    else:
        print("✅ All __init__.py files exist")
        return True

def test_tool_functions():
    """Test tool functions có thể gọi được không"""
    print("\nTesting tool functions...")
    
    try:
        from mono_tools import show_texture_search_replace, show_material_loader, show_mono_file_manager
        
        # Test if functions are callable
        if callable(show_texture_search_replace):
            print("✅ show_texture_search_replace is callable")
        else:
            print("❌ show_texture_search_replace is not callable")
            return False
        
        if callable(show_material_loader):
            print("✅ show_material_loader is callable")
        else:
            print("❌ show_material_loader is not callable")
            return False
        
        if callable(show_mono_file_manager):
            print("✅ show_mono_file_manager is callable")
        else:
            print("❌ show_mono_file_manager is not callable")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing functions: {e}")
        return False

def test_consistency():
    """Test consistency sau migration"""
    print("\nTesting consistency...")
    
    try:
        # Import consistency check script
        sys.path.insert(0, "python")
        from simple_consistency_check import main as consistency_check
        
        print("Running consistency check...")
        consistency_check()
        
        return True
        
    except Exception as e:
        print(f"❌ Error running consistency check: {e}")
        return False

def main():
    """Main test function"""
    print("Mono Studio - Post-Migration Test")
    print("=" * 40)
    
    tests = [
        ("Folder Structure", test_folder_structure),
        ("Init Files", test_init_files),
        ("Imports", test_imports),
        ("Tool Functions", test_tool_functions),
        ("Consistency", test_consistency)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Migration successful!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration has issues - check the errors above")
