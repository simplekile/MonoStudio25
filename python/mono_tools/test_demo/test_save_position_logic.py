"""Test save position logic step by step"""

import hou
from mono_tools.qt import QtCore

def test_save_logic():
    """Test how position is saved"""
    
    print("\n=== Save Position Logic Test ===\n")
    
    mw = hou.qt.mainWindow()
    minibar = mw.findChild(QtCore.QObject, "MonoMiniBar")
    
    if not minibar:
        print("❌ MiniBar not found!")
        return
    
    s = QtCore.QSettings("Mono", "FileManager")
    
    # Get current state
    hou_geo = mw.geometry()
    my_pos = minibar.pos()
    
    print("📊 Current State:")
    print(f"  Houdini window:")
    print(f"    Position: ({hou_geo.x()}, {hou_geo.y()})")
    print(f"    Size: {hou_geo.width()}x{hou_geo.height()}")
    print(f"    Right edge: {hou_geo.x() + hou_geo.width()}")
    print(f"    Top edge: {hou_geo.y()}")
    print()
    print(f"  MiniBar:")
    print(f"    Position: ({my_pos.x()}, {my_pos.y()})")
    print(f"    Size: {minibar.width()}x{minibar.height()}")
    print(f"    Right edge: {my_pos.x() + minibar.width()}")
    print(f"    Top edge: {my_pos.y()}")
    print()
    
    # Calculate offset (same logic as _save_relative_position)
    hou_right = hou_geo.x() + hou_geo.width()
    hou_top = hou_geo.y()
    minibar_right = my_pos.x() + minibar.width()
    minibar_top = my_pos.y()
    
    offset_x = minibar_right - hou_right
    offset_y = minibar_top - hou_top
    
    print("🧮 Calculated Offsets (what SHOULD be saved):")
    print(f"  Houdini right: {hou_right}")
    print(f"  MiniBar right: {minibar_right}")
    print(f"  offset_x = {minibar_right} - {hou_right} = {offset_x}")
    print()
    print(f"  Houdini top: {hou_top}")
    print(f"  MiniBar top: {minibar_top}")
    print(f"  offset_y = {minibar_top} - {hou_top} = {offset_y}")
    print()
    
    # Current saved values
    saved_offset_x = s.value("minibar_offset_x", None)
    saved_offset_y = s.value("minibar_offset_y", None)
    
    print(f"💾 Currently Saved Offsets:")
    print(f"  offset_x: {saved_offset_x}")
    print(f"  offset_y: {saved_offset_y}")
    print()
    
    # Compare
    if offset_x == saved_offset_x and offset_y == saved_offset_y:
        print("✅ Saved offsets MATCH current position!")
    else:
        print("⚠️ Saved offsets DO NOT match current position!")
        print(f"  Should save: ({offset_x}, {offset_y})")
        print(f"  Currently saved: ({saved_offset_x}, {saved_offset_y})")
        print()
        
        # Test restoration with these offsets
        print("🔄 If we restore using saved offsets:")
        restored_minibar_right = hou_right + saved_offset_x
        restored_x = restored_minibar_right - minibar.width()
        restored_y = hou_top + saved_offset_y
        print(f"  Would restore to: ({restored_x}, {restored_y})")
        print(f"  Current position: ({my_pos.x()}, {my_pos.y()})")
        print(f"  Difference: ({restored_x - my_pos.x()}, {restored_y - my_pos.y()})")
    
    print()
    print("💡 To fix: Manually save current position")
    print("   Run: minibar._save_relative_position()")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_save_logic()

