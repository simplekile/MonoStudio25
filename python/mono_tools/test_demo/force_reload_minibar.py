"""Force reload MiniBar module and restart"""

import hou
import sys

def force_reload_minibar():
    """Force reload MiniBar module to get latest code"""
    
    print("\n=== Force Reload MiniBar ===\n")
    
    try:
        # Close current MiniBar
        print("1. Closing current MiniBar...")
        mw = hou.qt.mainWindow()
        from mono_tools.qt import QtCore
        minibar = mw.findChild(QtCore.QObject, "MonoMiniBar")
        if minibar:
            minibar.close()
            minibar.deleteLater()
            print("   ✅ Closed")
        else:
            print("   ℹ️ No MiniBar open")
        
        # Remove cached modules
        print("\n2. Clearing module cache...")
        modules_to_remove = []
        for name in sys.modules:
            if 'mono_tools' in name and 'minibar' in name:
                modules_to_remove.append(name)
        
        for name in modules_to_remove:
            print(f"   Removing: {name}")
            del sys.modules[name]
        
        if modules_to_remove:
            print(f"   ✅ Removed {len(modules_to_remove)} modules")
        else:
            print("   ℹ️ No minibar modules in cache")
        
        # Reimport and reopen
        print("\n3. Reloading MiniBar...")
        import mono_tools
        if hasattr(mono_tools, 'open_minibar'):
            mono_tools.open_minibar()
            print("   ✅ MiniBar reopened with latest code!")
        else:
            print("   ⚠️ open_minibar not found, trying manual import...")
            from mono_tools.file_manager import file_manager_minibar
            # Will need to call show manually
            print("   ℹ️ Module imported, call mono_tools.open_minibar() to show")
        
        print("\n✅ Reload complete!")
        print("\n💡 Now run debug script again:")
        print('   execfile("D:/Dropbox/Stock/Plugin/HOU/MonoStudio25/python/mono_tools/test_demo/test_minibar_startup_position.py")')
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    force_reload_minibar()

