"""
Test script để kiểm tra Menu và Shelf integration
"""

def test_menu_integration():
    """Test menu integration"""
    print("🔍 Testing Menu Integration...")
    
    try:
        import hou
        
        # Kiểm tra menu Mono Studio có tồn tại không
        main_menu = hou.menuBar()
        mono_menu = None
        
        for action in main_menu.actions():
            if action.text() == "Mono Studio":
                mono_menu = action.menu()
                break
        
        if mono_menu:
            print("✅ Mono Studio menu found")
            
            # Kiểm tra Texture Search & Replace action
            actions = mono_menu.actions()
            texture_action = None
            
            for action in actions:
                if action.text() == "Texture Search & Replace":
                    texture_action = action
                    break
            
            if texture_action:
                print("✅ Texture Search & Replace action found in menu")
                print("💡 Access via: Menu Bar > Mono Studio > Texture Search & Replace")
                return True
            else:
                print("❌ Texture Search & Replace action not found in menu")
                return False
        else:
            print("❌ Mono Studio menu not found")
            return False
            
    except Exception as e:
        print(f"❌ Menu test failed: {e}")
        return False


def test_shelf_integration():
    """Test shelf integration"""
    print("\n🔍 Testing Shelf Integration...")
    
    try:
        import hou
        
        # Kiểm tra shelf Mono Studio
        shelves = hou.shelves.shelves()
        mono_shelf = shelves.get("Mono Studio")
        
        if mono_shelf:
            print("✅ Mono Studio shelf found")
            
            # Kiểm tra tools trong shelf
            tools = mono_shelf.tools()
            texture_tool = None
            
            for tool in tools:
                if tool.name() == "Texture Search & Replace":
                    texture_tool = tool
                    break
            
            if texture_tool:
                print("✅ Texture Search & Replace tool found in shelf")
                print("💡 Access via: Shelf > Mono Studio > Texture Search & Replace")
                return True
            else:
                print("❌ Texture Search & Replace tool not found in shelf")
                return False
        else:
            print("❌ Mono Studio shelf not found")
            return False
            
    except Exception as e:
        print(f"❌ Shelf test failed: {e}")
        return False


def test_direct_function_call():
    """Test gọi function trực tiếp"""
    print("\n🔍 Testing Direct Function Call...")
    
    try:
        from ..texture_search_replace import show_texture_search_replace
        
        # Test function có thể gọi được không
        if callable(show_texture_search_replace):
            print("✅ Function is callable")
            print("💡 Access via: Python Console > from mono_tools import show_texture_search_replace")
            return True
        else:
            print("❌ Function is not callable")
            return False
            
    except Exception as e:
        print(f"❌ Direct function test failed: {e}")
        return False


def test_all_access_methods():
    """Test tất cả cách truy cập"""
    print("🚀 Testing All Access Methods for Texture Search & Replace")
    print("=" * 60)
    
    tests = [
        ("Menu Integration", test_menu_integration),
        ("Shelf Integration", test_shelf_integration),
        ("Direct Function Call", test_direct_function_call),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{total} access methods working")
    
    if passed == total:
        print("🎉 All access methods working! Tool is fully integrated.")
    elif passed > 0:
        print("⚠️ Some access methods working. Check failed methods above.")
    else:
        print("❌ No access methods working. Check integration setup.")
    
    return passed == total


def show_access_instructions():
    """Hiển thị hướng dẫn truy cập"""
    print("\n📋 How to Access Texture Search & Replace:")
    print("-" * 50)
    
    print("\n1️⃣ From Menu:")
    print("   Menu Bar > Mono Studio > Texture Search & Replace")
    
    print("\n2️⃣ From Shelf:")
    print("   Shelf > Mono Studio > Texture Search & Replace")
    
    print("\n3️⃣ From Python Console:")
    print("   from mono_tools import show_texture_search_replace")
    print("   show_texture_search_replace()")
    
    print("\n4️⃣ From Python Script:")
    print("   exec(open('python/mono_tools/test_demo/demo_texture_search_replace.py').read())")


if __name__ == "__main__":
    test_all_access_methods()
    show_access_instructions()
