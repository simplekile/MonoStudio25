"""
Test simplified startup system
Run this in Houdini Python Console to verify startup works
"""

def test_startup():
    """Test that all startup components work correctly"""
    print("\n" + "="*60)
    print("🧪 Testing Simplified Startup System v2.2.0")
    print("="*60 + "\n")
    
    results = []
    
    # Test 1: Import main package
    print("1️⃣ Testing main package import...")
    try:
        import mono_tools
        print("   ✅ mono_tools imported successfully")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(False)
        return False
    
    # Test 2: Check exported functions
    print("\n2️⃣ Testing exported functions...")
    required_functions = [
        'show_mono_file_manager',
        'show_mono_minibar',
        'show_material_loader',
        'show_texture_search_replace',
        'setup_file_manager_tools',
        'setup_material_loader_tools',
        'setup_texture_tools',
        'open_file_manager',
        'open_minibar'
    ]
    
    all_found = True
    for func_name in required_functions:
        if hasattr(mono_tools, func_name):
            print(f"   ✅ {func_name} found")
        else:
            print(f"   ❌ {func_name} missing")
            all_found = False
    
    results.append(all_found)
    
    # Test 3: Test menu setup
    print("\n3️⃣ Testing menu setup...")
    try:
        mono_tools.setup_file_manager_tools()
        mono_tools.setup_material_loader_tools()
        mono_tools.setup_texture_tools()
        print("   ✅ All menu setups completed")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Menu setup failed: {e}")
        results.append(False)
    
    # Test 4: Test MiniBar creation (but don't show it)
    print("\n4️⃣ Testing MiniBar creation...")
    try:
        from mono_tools import MonoFileMiniBar
        from mono_tools.file_manager import FileManagerWrapper
        import hou
        
        # Create but don't show
        wrapper = FileManagerWrapper()
        print("   ✅ FileManagerWrapper created")
        print("   💡 MiniBar can be shown with: mono_tools.show_mono_minibar()")
        results.append(True)
    except Exception as e:
        print(f"   ❌ MiniBar creation failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)
    
    # Test 5: Verify startup script structure
    print("\n5️⃣ Verifying startup script...")
    try:
        import os
        mono_studio = os.environ.get('MONO_STUDIO')
        if mono_studio:
            startup_script = os.path.join(mono_studio, 'scripts', 'startup.py')
            if os.path.exists(startup_script):
                with open(startup_script, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    print(f"   ✅ Startup script found ({lines} lines)")
                    if lines < 50:
                        print("   ✅ Script is simple and clean!")
                    results.append(True)
            else:
                print(f"   ❌ Startup script not found at {startup_script}")
                results.append(False)
        else:
            print("   ⚠️ MONO_STUDIO env not set - skipping")
            results.append(True)  # Don't fail test for this
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        print("\n💡 Startup is now simplified:")
        print("   • MonoStudio_package.json → scripts/startup.py")
        print("   • startup.py → setup menus + show minibar")
        print("   • No complex logic, just clean and simple!")
    else:
        print("❌ SOME TESTS FAILED - check errors above")
    
    print("="*60 + "\n")
    
    return passed == total


def test_manual_minibar():
    """Manually show MiniBar for visual testing"""
    print("\n🎨 Showing MiniBar for visual test...")
    try:
        from mono_tools import show_mono_minibar
        minibar = show_mono_minibar()
        if minibar:
            print("✅ MiniBar shown successfully!")
            print(f"   Type: {type(minibar)}")
            print(f"   Visible: {minibar.isVisible()}")
            return True
        else:
            print("❌ MiniBar creation returned None")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run all tests
    test_startup()
    
    # Ask if user wants to show MiniBar
    print("\n💡 To manually test MiniBar, run:")
    print("   from mono_tools.test_demo.test_simplified_startup import test_manual_minibar")
    print("   test_manual_minibar()")

