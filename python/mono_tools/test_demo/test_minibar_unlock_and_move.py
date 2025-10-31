"""Test MiniBar unlock and move"""

import hou
from mono_tools.qt import QtCore

def unlock_and_test_move():
    """Unlock MiniBar and test position saving"""
    s = QtCore.QSettings("Mono", "FileManager")
    
    print("\n=== Unlock & Move Test ===\n")
    
    # Find MiniBar
    mw = hou.qt.mainWindow()
    minibar = mw.findChild(QtCore.QObject, "MonoMiniBar")
    
    if not minibar:
        print("❌ MiniBar not found!")
        return
    
    print(f"Initial state:")
    print(f"  Position: ({minibar.x()}, {minibar.y()})")
    print(f"  Locked: {minibar._locked}")
    print()
    
    # Unlock
    if minibar._locked:
        print("🔓 Unlocking MiniBar...")
        minibar._locked = False
        minibar.s.setValue("minibar_locked", False)
        minibar.s.sync()
        minibar._update_lock_visual_feedback()
        print("✅ Unlocked!")
    else:
        print("✅ Already unlocked")
    print()
    
    # Get current offset
    old_offset_x = s.value("minibar_offset_x", None)
    old_offset_y = s.value("minibar_offset_y", None)
    print(f"Old offsets: ({old_offset_x}, {old_offset_y})")
    
    # Move to new position (100px down)
    old_pos = minibar.pos()
    new_x = old_pos.x()
    new_y = old_pos.y() + 100
    
    print(f"\n🚀 Moving from ({old_pos.x()}, {old_pos.y()}) to ({new_x}, {new_y})...")
    minibar.move(new_x, new_y)
    
    # Save position
    print("💾 Saving position...")
    minibar._save_relative_position()
    
    # Check if saved
    new_offset_x = s.value("minibar_offset_x", None)
    new_offset_y = s.value("minibar_offset_y", None)
    
    print(f"\nNew offsets: ({new_offset_x}, {new_offset_y})")
    
    if new_offset_x != old_offset_x or new_offset_y != old_offset_y:
        print("✅ Position SAVED successfully!")
        print(f"   Changed: offset_y from {old_offset_y} to {new_offset_y}")
    else:
        print("⚠️ Position NOT saved (offsets unchanged)")
        print("\nDebug info:")
        print(f"  MiniBar pos: ({minibar.x()}, {minibar.y()})")
        print(f"  MiniBar size: {minibar.width()}x{minibar.height()}")
        
        # Calculate expected offset
        mw_geo = mw.geometry()
        minibar_right = minibar.x() + minibar.width()
        hou_right = mw_geo.x() + mw_geo.width()
        expected_offset_x = minibar_right - hou_right
        expected_offset_y = minibar.y() - mw_geo.y()
        
        print(f"  Houdini window: {mw_geo.width()}x{mw_geo.height()} at ({mw_geo.x()}, {mw_geo.y()})")
        print(f"  Expected offset: ({expected_offset_x}, {expected_offset_y})")
    
    print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    unlock_and_test_move()

