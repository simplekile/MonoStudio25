"""
Mono Studio Startup Script
Auto-loads Mono Studio tools when Houdini starts
"""

import hou
import os
import sys

def setup_mono_studio():
    """Setup Mono Studio tools in Houdini"""
    try:
        print("🎬 Mono Studio v2.0.0 - Initializing...")
        
        # Add python path if not already added
        mono_studio_path = os.environ.get('MONO_STUDIO')
        if mono_studio_path:
            python_path = os.path.join(mono_studio_path, 'python')
            if python_path not in sys.path:
                sys.path.insert(0, python_path)
                print(f"📁 Added python path: {python_path}")
        
        # Import and setup tools
        from mono_tools import setup_file_manager_tools, setup_material_loader_tools, setup_texture_tools
        from mono_tools import show_mono_minibar
        
        print("🔧 Setting up tools...")
        
        # Setup all tools
        setup_file_manager_tools()
        setup_material_loader_tools()
        setup_texture_tools()
        
        print("✅ All tools setup complete!")
        
        # Show MiniBar
        try:
            minibar = show_mono_minibar()
            if minibar:
                print("✅ MiniBar loaded successfully!")
            else:
                print("⚠️ MiniBar not loaded")
        except Exception as e:
            print(f"⚠️ MiniBar error: {e}")
        
        print("🎉 Mono Studio ready!")
        return True
        
    except Exception as e:
        print(f"❌ Mono Studio startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run setup
if __name__ == "__main__":
    setup_mono_studio()
else:
    # Auto-run when imported
    setup_mono_studio()
