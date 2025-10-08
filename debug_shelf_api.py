#!/usr/bin/env python3
"""
Debug Houdini shelf API để tìm cách đúng
"""

def debug_houdini_shelf_api():
    """Debug Houdini shelf API"""
    try:
        import hou
        
        print("=== Houdini Shelf API Debug ===")
        
        # 1. Kiểm tra hou.shelves
        print("1. hou.shelves type:", type(hou.shelves))
        print("   hou.shelves methods:", [m for m in dir(hou.shelves) if not m.startswith('_')])
        
        # 2. Kiểm tra hou.shelves.shelves()
        shelves_obj = hou.shelves.shelves()
        print("2. hou.shelves.shelves() type:", type(shelves_obj))
        print("   Available methods:", [m for m in dir(shelves_obj) if not m.startswith('_')])
        
        # 3. Kiểm tra nội dung shelves
        if hasattr(shelves_obj, 'keys'):
            print("3. Available shelves:", list(shelves_obj.keys()))
        else:
            print("3. shelves_obj is not a dict-like object")
        
        # 4. Thử các cách khác
        print("\n4. Trying alternative methods...")
        
        # Thử hou.shelves.create()
        try:
            print("   Trying hou.shelves.create()...")
            result = hou.shelves.create("TestShelf")
            print("   ✅ hou.shelves.create() works:", type(result))
        except Exception as e:
            print("   ❌ hou.shelves.create() failed:", e)
        
        # Thử hou.shelves.new()
        try:
            print("   Trying hou.shelves.new()...")
            result = hou.shelves.new("TestShelf2")
            print("   ✅ hou.shelves.new() works:", type(result))
        except Exception as e:
            print("   ❌ hou.shelves.new() failed:", e)
        
        # Thử hou.shelves.add()
        try:
            print("   Trying hou.shelves.add()...")
            result = hou.shelves.add("TestShelf3")
            print("   ✅ hou.shelves.add() works:", type(result))
        except Exception as e:
            print("   ❌ hou.shelves.add() failed:", e)
        
        # 5. Kiểm tra shelf object nếu có
        if hasattr(shelves_obj, 'keys') and len(shelves_obj) > 0:
            first_shelf = list(shelves_obj.values())[0]
            print("5. First shelf type:", type(first_shelf))
            print("   First shelf methods:", [m for m in dir(first_shelf) if not m.startswith('_')])
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_houdini_shelf_api()
