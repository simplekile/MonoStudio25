"""
Test imports after fixing file_manager imports
"""

import sys
import os

def test_imports():
    """Test all imports after fixing file_manager"""
    print("Testing imports after fixing file_manager...")
    
    try:
        # Add python to path
        sys.path.insert(0, 'python')
        
        # Test main package import
        print("1. Testing main package import...")
        from mono_tools import show_mono_file_manager
        print("   ✅ show_mono_file_manager imported")
        
        from mono_tools import show_material_loader
        print("   ✅ show_material_loader imported")
        
        from mono_tools import show_texture_search_replace
        print("   ✅ show_texture_search_replace imported")
        
        # Test file_manager package imports
        print("2. Testing file_manager package imports...")
        from mono_tools.file_manager import FileManagerWrapper
        print("   ✅ FileManagerWrapper imported")
        
        from mono_tools.file_manager import MonoFileManager
        print("   ✅ MonoFileManager imported")
        
        from mono_tools.file_manager import show_mono_minibar
        print("   ✅ show_mono_minibar imported")
        
        # Test individual file imports
        print("3. Testing individual file imports...")
        from mono_tools.file_manager.file_manager_api import FileManagerWrapper
        print("   ✅ file_manager_api imported")
        
        from mono_tools.file_manager.file_manager_manager import MonoFileManager
        print("   ✅ file_manager_manager imported")
        
        from mono_tools.file_manager.file_manager_minibar import MonoFileMiniBar
        print("   ✅ file_manager_minibar imported")
        
        from mono_tools.file_manager.file_manager_helpers import parse_ver
        print("   ✅ file_manager_helpers imported")
        
        from mono_tools.file_manager.file_manager_models import FileTableModel
        print("   ✅ file_manager_models imported")
        
        # Test Qt imports
        print("4. Testing Qt imports...")
        from mono_tools.qt import QtCore, QtGui, QtWidgets, API
        print("   ✅ Qt modules imported")
        print(f"   API = {API}")
        
        # Test utils imports
        print("5. Testing utils imports...")
        from mono_tools.utils import MonoUtils
        print("   ✅ MonoUtils imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Mono Studio - Import Test After Fix")
    print("=" * 40)
    
    success = test_imports()
    
    if success:
        print("\n✅ All imports working correctly!")
        print("The file_manager import issues have been fixed.")
    else:
        print("\n❌ Some imports still have issues.")
        print("Check the errors above for details.")
    
    return success

if __name__ == "__main__":
    main()
