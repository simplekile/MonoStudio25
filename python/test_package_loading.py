#!/usr/bin/env python3
"""
Test package loading
"""

def test_package_loading():
    """Test if package is loaded correctly"""
    print("🧪 Testing package loading...")
    
    try:
        import hou
        print("✅ Houdini module imported successfully")
        
        # Check environment variables
        import os
        mono_studio = os.environ.get('MONO_STUDIO')
        print(f"🔍 MONO_STUDIO env: {mono_studio}")
        
        if mono_studio:
            print("✅ MONO_STUDIO environment variable is set")
        else:
            print("❌ MONO_STUDIO environment variable is not set")
        
        # Check if we can import our modules
        try:
            from mono_tools.file_manager.file_manager_minibar import MonoFileMiniBar
            print("✅ MonoFileMiniBar imported successfully")
        except Exception as e:
            print(f"❌ Failed to import MonoFileMiniBar: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing package loading: {e}")
        return False

if __name__ == "__main__":
    test_package_loading()
