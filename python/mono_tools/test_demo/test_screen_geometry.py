"""Debug screen geometry"""

from mono_tools.qt import QtWidgets

def check_screen_geometry():
    """Check screen geometry values"""
    
    print("\n=== Screen Geometry Debug ===\n")
    
    screen = QtWidgets.QApplication.primaryScreen()
    if not screen:
        print("❌ No screen found!")
        return
    
    screen_geo = screen.availableGeometry()
    
    print(f"📺 Primary Screen (availableGeometry):")
    print(f"  x: {screen_geo.x()}")
    print(f"  y: {screen_geo.y()}")
    print(f"  width: {screen_geo.width()}")
    print(f"  height: {screen_geo.height()}")
    print(f"  right(): {screen_geo.right()}")
    print(f"  bottom(): {screen_geo.bottom()}")
    print()
    
    full_geo = screen.geometry()
    print(f"📺 Primary Screen (geometry - full):")
    print(f"  x: {full_geo.x()}")
    print(f"  y: {full_geo.y()}")
    print(f"  width: {full_geo.width()}")
    print(f"  height: {full_geo.height()}")
    print(f"  right(): {full_geo.right()}")
    print(f"  bottom(): {full_geo.bottom()}")
    print()
    
    # Calculate expected values
    print(f"🧮 Calculations:")
    print(f"  Expected right (x + width): {screen_geo.x()} + {screen_geo.width()} = {screen_geo.x() + screen_geo.width()}")
    print(f"  Actual right(): {screen_geo.right()}")
    print(f"  Difference: {screen_geo.right() - (screen_geo.x() + screen_geo.width())}")
    print()
    
    # MiniBar constraint calculation
    min_visible = 50
    max_x = screen_geo.right() - min_visible
    print(f"📍 MiniBar Constraint:")
    print(f"  screen.right() - {min_visible} = {max_x}")
    print(f"  This is the MAXIMUM X position allowed")
    print()
    
    # Expected MiniBar position
    expected_x = 3317  # From debug output
    print(f"🎯 Expected MiniBar X: {expected_x}")
    if expected_x > max_x:
        print(f"  ⚠️ EXCEEDS max_x ({max_x})!")
        print(f"  Will be clamped to: {max_x}")
        print(f"  This explains the position shift!")
    else:
        print(f"  ✅ Within bounds (< {max_x})")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    check_screen_geometry()

