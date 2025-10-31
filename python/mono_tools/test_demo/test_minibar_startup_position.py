"""Debug MiniBar position on startup"""

import hou
from mono_tools.qt import QtCore, QtWidgets

def debug_startup_position():
    """Show how MiniBar position is calculated on startup"""
    
    print("\n=== MiniBar Startup Position Debug ===\n")
    
    s = QtCore.QSettings("Mono", "FileManager")
    
    # Saved offsets
    offset_x = s.value("minibar_offset_x", -85, type=int)
    offset_y = s.value("minibar_offset_y", 0, type=int)
    
    print(f"📦 Saved Offsets:")
    print(f"  offset_x: {offset_x}")
    print(f"  offset_y: {offset_y}")
    print()
    
    # Houdini main window
    mw = hou.qt.mainWindow()
    if not mw:
        print("❌ Main window not found!")
        return
    
    hou_geo = mw.geometry()
    print(f"🪟 Houdini Window:")
    print(f"  Position: ({hou_geo.x()}, {hou_geo.y()})")
    print(f"  Size: {hou_geo.width()}x{hou_geo.height()}")
    print(f"  Right edge: {hou_geo.x() + hou_geo.width()}")
    print(f"  Top edge: {hou_geo.y()}")
    print()
    
    # MiniBar
    minibar = mw.findChild(QtCore.QObject, "MonoMiniBar")
    if not minibar:
        print("❌ MiniBar not found!")
        return
    
    print(f"📍 Current MiniBar:")
    print(f"  Position: ({minibar.x()}, {minibar.y()})")
    print(f"  Size: {minibar.width()}x{minibar.height()}")
    print(f"  Right edge: {minibar.x() + minibar.width()}")
    print()
    
    # Calculate expected position from offsets
    hou_right = hou_geo.x() + hou_geo.width()
    hou_top = hou_geo.y()
    
    expected_minibar_right = hou_right + offset_x
    expected_minibar_top = hou_top + offset_y
    expected_x = expected_minibar_right - minibar.width()
    expected_y = expected_minibar_top
    
    print(f"🧮 Calculated Position (from offsets):")
    print(f"  Houdini right: {hou_right}")
    print(f"  + offset_x: {offset_x}")
    print(f"  = MiniBar right: {expected_minibar_right}")
    print(f"  - MiniBar width: {minibar.width()}")
    print(f"  = Expected X: {expected_x}")
    print()
    print(f"  Houdini top: {hou_top}")
    print(f"  + offset_y: {offset_y}")
    print(f"  = Expected Y: {expected_y}")
    print()
    
    # Compare
    if minibar.x() == expected_x and minibar.y() == expected_y:
        print("✅ Position MATCHES calculation!")
    else:
        print("⚠️ Position MISMATCH!")
        print(f"  Expected: ({expected_x}, {expected_y})")
        print(f"  Actual:   ({minibar.x()}, {minibar.y()})")
        print(f"  Diff:     ({minibar.x() - expected_x}, {minibar.y() - expected_y})")
    
    # Verify by recalculating offset from current position
    print()
    print(f"🔄 Reverse calculation (current pos → offset):")
    current_minibar_right = minibar.x() + minibar.width()
    current_offset_x = current_minibar_right - hou_right
    current_offset_y = minibar.y() - hou_top
    
    print(f"  Current offset_x: {current_offset_x} (saved: {offset_x})")
    print(f"  Current offset_y: {current_offset_y} (saved: {offset_y})")
    
    if current_offset_x != offset_x or current_offset_y != offset_y:
        print()
        print("⚠️ ISSUE FOUND:")
        print("  Current position does NOT match saved offsets!")
        print("  This means position was changed AFTER restore.")
        print()
        print("💡 Possible causes:")
        print("  1. Window resize after startup")
        print("  2. Screen bounds constraint")
        print("  3. Multiple monitor setup")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    debug_startup_position()

