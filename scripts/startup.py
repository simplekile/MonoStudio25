"""
Mono Studio Package Startup
This script runs when the package is loaded by Houdini
"""

import hou
import os
import sys

def package_startup():
    """Package startup function called by Houdini"""
    try:
        # Get version info
        try:
            from mono_tools.version import get_version_string
            version_text = get_version_string()
        except:
            version_text = "v2.0.0"
        
        print(f"🎬 Mono Studio {version_text} - Package Loading...")
        
        # Add python path if not already added
        mono_studio_path = os.environ.get('MONO_STUDIO')
        if mono_studio_path:
            python_path = os.path.join(mono_studio_path, 'python')
            if python_path not in sys.path:
                sys.path.insert(0, python_path)
                print(f"📁 Added python path: {python_path}")
        
        print("🔧 Setting up tools...")
        
        # Import and setup tools
        from mono_tools import setup_file_manager_tools, setup_material_loader_tools, setup_texture_tools
        from mono_tools import show_mono_minibar
        
        # Setup all tools
        setup_file_manager_tools()
        setup_material_loader_tools()
        setup_texture_tools()
        
        print("✅ All tools setup complete!")
        
        # Show MiniBar (with startup setting check)
        try:
            print("🔍 Checking MiniBar startup setting...")
            from mono_tools.qt import QtCore
            s = QtCore.QSettings("Mono", "FileManager")
            startup_enabled = s.value("minibar_startup_with_hou", True, type=bool)
            print(f"🔍 Startup setting value: {startup_enabled} (type: {type(startup_enabled)})")
            
            if startup_enabled:
                print("🚀 Startup enabled - creating MiniBar...")
                minibar = show_mono_minibar()
                if minibar:
                    print("✅ MiniBar auto-started successfully!")
                    print(f"🔍 MiniBar object: {minibar}")
                    print(f"🔍 MiniBar visible: {minibar.isVisible()}")
                else:
                    print("⚠️ MiniBar creation returned None")
            else:
                print("🚀 MiniBar startup disabled - skipping")
        except Exception as e:
            print(f"⚠️ MiniBar error: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Mono Studio startup failed: {e}")
        return False

# This function will be called by Houdini when the package loads
print("🚀 Mono Studio startup script loaded!")
print(f"🔍 MONO_STUDIO env: {os.environ.get('MONO_STUDIO')}")
print(f"🔍 Current working directory: {os.getcwd()}")
print(f"🔍 Script file location: {__file__}")

# Test import
try:
    import test_startup
    test_startup.test_function()
except Exception as e:
    print(f"🔍 Test import failed: {e}")

package_startup()
