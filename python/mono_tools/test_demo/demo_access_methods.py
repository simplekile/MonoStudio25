"""
Demo script để show các cách truy cập Texture Search & Replace
"""

def demo_menu_access():
    """Demo truy cập từ menu"""
    print("📋 Demo: Menu Access")
    print("-" * 30)
    print("1. Click on Menu Bar")
    print("2. Look for 'Mono Studio' menu")
    print("3. Click 'Texture Search & Replace'")
    print("✅ Tool will open in dialog window")


def demo_shelf_access():
    """Demo truy cập từ shelf"""
    print("\n📋 Demo: Shelf Access")
    print("-" * 30)
    print("1. Look for 'Mono Studio' shelf tab")
    print("2. Find 'Texture Search & Replace' tool")
    print("3. Click the tool button")
    print("✅ Tool will open in dialog window")


def demo_python_access():
    """Demo truy cập từ Python"""
    print("\n📋 Demo: Python Access")
    print("-" * 30)
    print("1. Open Python Console (Windows > Python Console)")
    print("2. Type: from mono_tools import show_texture_search_replace")
    print("3. Type: show_texture_search_replace()")
    print("✅ Tool will open in dialog window")


def demo_script_access():
    """Demo truy cập từ script file"""
    print("\n📋 Demo: Script File Access")
    print("-" * 30)
    print("1. Open Python Console")
    print("2. Type: exec(open('python/mono_tools/test_demo/demo_texture_search_replace.py').read())")
    print("✅ Demo will run with test scene")


def show_all_access_methods():
    """Show tất cả cách truy cập"""
    print("🎯 Texture Search & Replace - Access Methods")
    print("=" * 60)
    
    demo_menu_access()
    demo_shelf_access()
    demo_python_access()
    demo_script_access()
    
    print("\n" + "=" * 60)
    print("💡 Choose the method that works best for your workflow!")


def test_actual_access():
    """Test thực tế các cách truy cập"""
    print("\n🧪 Testing Actual Access Methods...")
    
    try:
        # Test 1: Direct function call
        print("\n1️⃣ Testing direct function call...")
        from ..texture_search_replace import show_texture_search_replace
        
        if callable(show_texture_search_replace):
            print("✅ Function is callable")
            
            # Try to create dialog (but don't show it)
            try:
                dialog = show_texture_search_replace()
                if dialog:
                    print("✅ Dialog created successfully")
                    dialog.close()  # Close immediately
                else:
                    print("⚠️ Dialog creation returned None")
            except Exception as e:
                print(f"⚠️ Dialog creation failed: {e}")
        else:
            print("❌ Function is not callable")
        
        # Test 2: Menu integration
        print("\n2️⃣ Testing menu integration...")
        try:
            import hou
            main_menu = hou.menuBar()
            mono_menu = None
            
            for action in main_menu.actions():
                if action.text() == "Mono Studio":
                    mono_menu = action.menu()
                    break
            
            if mono_menu:
                print("✅ Mono Studio menu found")
                
                # Check for texture tool
                actions = mono_menu.actions()
                texture_action = None
                
                for action in actions:
                    if action.text() == "Texture Search & Replace":
                        texture_action = action
                        break
                
                if texture_action:
                    print("✅ Texture Search & Replace found in menu")
                else:
                    print("❌ Texture Search & Replace not found in menu")
            else:
                print("❌ Mono Studio menu not found")
                
        except Exception as e:
            print(f"❌ Menu test failed: {e}")
        
        # Test 3: Shelf integration
        print("\n3️⃣ Testing shelf integration...")
        try:
            import hou
            shelves = hou.shelves.shelves()
            mono_shelf = shelves.get("Mono Studio")
            
            if mono_shelf:
                print("✅ Mono Studio shelf found")
                
                tools = mono_shelf.tools()
                texture_tool = None
                
                for tool in tools:
                    if tool.name() == "Texture Search & Replace":
                        texture_tool = tool
                        break
                
                if texture_tool:
                    print("✅ Texture Search & Replace found in shelf")
                else:
                    print("❌ Texture Search & Replace not found in shelf")
            else:
                print("❌ Mono Studio shelf not found")
                
        except Exception as e:
            print(f"❌ Shelf test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def run_demo():
    """Chạy demo đầy đủ"""
    print("🎬 Texture Search & Replace - Access Demo")
    print("=" * 60)
    
    show_all_access_methods()
    
    print("\n🔍 Running actual tests...")
    test_actual_access()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("💡 Use any of the methods above to access the tool.")


if __name__ == "__main__":
    run_demo()
