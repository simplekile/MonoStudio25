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
        print("🔍 package_startup() called")
        
        # Get version info
        try:
            from mono_tools.version import get_version_string
            version_text = get_version_string()
            print(f"🔍 Version loaded: {version_text}")
        except Exception as e:
            print(f"🔍 Version load failed: {e}")
            version_text = "v2.0.0"
        
        print(f"🎬 Mono Studio {version_text} - Package Loading...")
        
        # Add python path if not already added
        mono_studio_path = os.environ.get('MONO_STUDIO')
        print(f"🔍 MONO_STUDIO env: {mono_studio_path}")
        
        if mono_studio_path:
            python_path = os.path.join(mono_studio_path, 'python')
            print(f"🔍 Python path: {python_path}")
            if python_path not in sys.path:
                sys.path.insert(0, python_path)
                print(f"📁 Added python path: {python_path}")
            else:
                print(f"🔍 Python path already in sys.path")
        else:
            print("⚠️ MONO_STUDIO environment variable not set")
        
        print("🔧 Setting up tools...")
        
        # Import and setup tools
        try:
            from mono_tools import setup_file_manager_tools, setup_material_loader_tools, setup_texture_tools
            from mono_tools import show_mono_minibar
            print("🔍 Imports successful")
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
        
        # Setup all tools
        try:
            setup_file_manager_tools()
            print("🔍 File manager tools setup")
        except Exception as e:
            print(f"❌ File manager setup failed: {e}")
        
        try:
            setup_material_loader_tools()
            print("🔍 Material loader tools setup")
        except Exception as e:
            print(f"❌ Material loader setup failed: {e}")
        
        try:
            setup_texture_tools()
            print("🔍 Texture tools setup")
        except Exception as e:
            print(f"❌ Texture tools setup failed: {e}")
        
        print("✅ All tools setup complete!")
        
        # Show MiniBar (always auto-start)
        try:
            print("🔍 Creating MiniBar...")
            minibar = show_mono_minibar()
            if minibar:
                print("✅ MiniBar auto-started successfully!")
                print(f"🔍 MiniBar type: {type(minibar)}")
                print(f"🔍 MiniBar visible: {minibar.isVisible()}")
            else:
                print("⚠️ MiniBar creation returned None")
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
print(f"🔍 Script file: {__file__}")
print(f"🔍 Working directory: {os.getcwd()}")
print(f"🔍 Python path: {sys.path[:3]}...")
package_startup()
