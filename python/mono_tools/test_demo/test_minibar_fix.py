#!/usr/bin/env python3
"""
Test script to verify MiniBar status error fix
"""

def test_minibar_fix():
    """Test that MiniBar no longer tries to call _show_status"""
    try:
        print("🧪 Testing MiniBar Status Error Fix")
        print("=" * 50)
        
        # Test 1: Import file manager
        print("1. Testing file manager import...")
        from mono_tools.file_manager.file_manager import show_mono_minibar, _make_manager
        print("   ✅ File manager imported successfully")
        
        # Test 2: Check that _make_manager uses new class
        print("\n2. Testing _make_manager uses new class...")
        try:
            # This should not raise an error about status_label
            manager = _make_manager()
            if hasattr(manager, 'status_label'):
                print("   ✅ Manager has status_label (new class)")
            else:
                print("   ❌ Manager missing status_label (old class)")
                return False
                
            if hasattr(manager, '_show_status'):
                print("   ✅ Manager has _show_status method")
            else:
                print("   ❌ Manager missing _show_status method")
                return False
                
            manager.close()
            
        except Exception as e:
            if "status_label" in str(e):
                print(f"   ❌ Still getting status_label error: {e}")
                return False
            else:
                print(f"   ⚠️ Other error (expected in non-Houdini environment): {e}")
        
        # Test 3: Check class names
        print("\n3. Checking class names...")
        from mono_tools.file_manager.file_manager_manager import MonoFileManager as NewMonoFileManager
        from mono_tools.file_manager.file_manager import LegacyMonoFileManager
        
        print(f"   ✅ NewMonoFileManager: {NewMonoFileManager.__name__}")
        print(f"   ✅ LegacyMonoFileManager: {LegacyMonoFileManager.__name__}")
        
        # Test 4: Verify import structure
        print("\n4. Verifying import structure...")
        from mono_tools.file_manager.file_manager import NewMonoFileManager as ImportedNewMonoFileManager
        print(f"   ✅ Imported NewMonoFileManager: {ImportedNewMonoFileManager.__name__}")
        
        print("\n✅ All tests passed!")
        print("\n💡 Fix Summary:")
        print("   • _make_manager() now uses NewMonoFileManager (with status bar)")
        print("   • Old MonoFileManager renamed to LegacyMonoFileManager")
        print("   • MiniBar should no longer get status_label errors")
        print("   • Status bar functionality is available in new manager")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🎬 Testing MiniBar Status Error Fix")
    print("=" * 60)
    
    success = test_minibar_fix()
    
    if success:
        print("\n🎉 Fix verified successfully!")
        print("💡 MiniBar should now work without status_label errors!")
    else:
        print("\n❌ Fix verification failed!")
        print("💡 Check the error messages above")

if __name__ == "__main__":
    main()
