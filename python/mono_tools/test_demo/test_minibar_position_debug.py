"""Test MiniBar position saving/loading"""

import hou
from mono_tools.qt import QtCore

def test_minibar_position():
    """Check if MiniBar position is being saved"""
    s = QtCore.QSettings("Mono", "FileManager")
    
    print("\n=== MiniBar Position Debug ===\n")
    
    # Check saved values
    offset_x = s.value("minibar_offset_x", None)
    offset_y = s.value("minibar_offset_y", None)
    
    print(f"Saved Offsets:")
    print(f"  offset_x: {offset_x}")
    print(f"  offset_y: {offset_y}")
    print()
    
    # Check if MiniBar is open
    try:
        import mono_tools.file_manager.file_manager_minibar as minibar_module
        
        # Find MiniBar instance
        mw = hou.qt.mainWindow()
        minibar = mw.findChild(QtCore.QObject, "MonoMiniBar")
        
        if minibar:
            print(f"✅ MiniBar found!")
            print(f"  Current position: ({minibar.x()}, {minibar.y()})")
            print(f"  Size: {minibar.width()}x{minibar.height()}")
            print(f"  Locked: {minibar._locked}")
            print()
            
            # Test save
            print("Testing save...")
            minibar._save_relative_position()
            
            # Re-read
            new_offset_x = s.value("minibar_offset_x", None)
            new_offset_y = s.value("minibar_offset_y", None)
            
            print(f"After save:")
            print(f"  offset_x: {new_offset_x}")
            print(f"  offset_y: {new_offset_y}")
            
            if new_offset_x == offset_x and new_offset_y == offset_y:
                print("⚠️ Position not changed after save!")
            else:
                print("✅ Position saved successfully!")
        else:
            print("❌ MiniBar not found - open it first!")
            print("\nTo open: import mono_tools; mono_tools.open_minibar()")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    test_minibar_position()

