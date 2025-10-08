"""
Quick test script để kiểm tra tất cả cách truy cập Texture Search & Replace
Chạy script này trong Houdini để test nhanh
"""

def test_texture_access():
    """Test tất cả cách truy cập Texture Search & Replace"""
    print("🔍 Testing Texture Search & Replace Access Methods")
    print("=" * 60)
    
    try:
        # Test 1: Import function
        print("1️⃣ Testing function import...")
        from mono_tools import show_texture_search_replace
        print("✅ Function imported successfully")
        
        # Test 2: Check if callable
        print("\n2️⃣ Testing function callability...")
        if callable(show_texture_search_replace):
            print("✅ Function is callable")
        else:
            print("❌ Function is not callable")
            return False
        
        # Test 3: Try to create dialog
        print("\n3️⃣ Testing dialog creation...")
        try:
            dialog = show_texture_search_replace()
            if dialog:
                print("✅ Dialog created successfully")
                print("💡 Dialog is ready to use")
                
                # Close dialog immediately for testing
                dialog.close()
                print("✅ Dialog closed successfully")
            else:
                print("❌ Dialog creation returned None")
                return False
        except Exception as e:
            print(f"❌ Dialog creation failed: {e}")
            return False
        
        # Test 4: Check menu integration
        print("\n4️⃣ Testing menu integration...")
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
                    print("💡 Access via: Menu Bar > Mono Studio > Texture Search & Replace")
                else:
                    print("❌ Texture Search & Replace not found in menu")
            else:
                print("❌ Mono Studio menu not found")
        except Exception as e:
            print(f"❌ Menu test failed: {e}")
        
        # Test 5: Check shelf integration
        print("\n5️⃣ Testing shelf integration...")
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
                    print("💡 Access via: Shelf > Mono Studio > Texture Search & Replace")
                else:
                    print("❌ Texture Search & Replace not found in shelf")
            else:
                print("❌ Mono Studio shelf not found")
        except Exception as e:
            print(f"❌ Shelf test failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Texture Search & Replace is ready to use!")
        print("\n📋 Access Methods:")
        print("   • Menu: Menu Bar > Mono Studio > Texture Search & Replace")
        print("   • Shelf: Shelf > Mono Studio > Texture Search & Replace")
        print("   • Python: from mono_tools import show_texture_search_replace")
        print("   • Script: exec(open('python/mono_tools/test_demo/demo_texture_search_replace.py').read())")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_usage_examples():
    """Show usage examples"""
    print("\n📚 Usage Examples:")
    print("-" * 30)
    
    print("\n🔹 Basic Usage:")
    print("   1. Open Texture Search & Replace")
    print("   2. Set search pattern: D:/OldProject/")
    print("   3. Set replace pattern: E:/NewProject/")
    print("   4. Click Preview to see changes")
    print("   5. Click Apply Changes to apply")
    
    print("\n🔹 Regex Usage:")
    print("   1. Enable 'Use Regular Expression'")
    print("   2. Search: (\\d{4})\\.(exr|jpg|png)")
    print("   3. Replace: <UDIM>.\\2")
    print("   4. This converts UDIM numbers to <UDIM> tags")
    
    print("\n🔹 Scope Options:")
    print("   • Current Network: Only current network")
    print("   • Selected Nodes: Only selected nodes")
    print("   • Entire Scene: All nodes in scene")


if __name__ == "__main__":
    print("🚀 Texture Search & Replace - Access Test")
    print("Running in Houdini environment...")
    print()
    
    if test_texture_access():
        show_usage_examples()
    else:
        print("\n❌ Test failed. Check your Houdini environment and Mono Studio setup.")
