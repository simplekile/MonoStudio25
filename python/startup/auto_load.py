"""
Auto-load script for Mono Studio
Runs automatically when Houdini starts
"""

def auto_load_mono_studio():
    """Auto-load Mono Studio tools"""
    try:
        print("🎬 Mono Studio v2.0.0 - Initializing...")
        
        # Add python path
        import sys
        import os
        python_path = os.path.join(os.path.dirname(__file__), '..')
        if python_path not in sys.path:
            sys.path.insert(0, python_path)
        print(f"📁 Added python path: {python_path}")
        
        # Import and setup tools
        from mono_tools import setup_file_manager_tools, setup_material_loader_tools, setup_texture_tools
        from mono_tools import show_mono_minibar, show_texture_search_replace, show_material_loader
        from mono_tools.qt import QtCore
        import hou
        
        # Setup all tools menus (silently)
        print("🔧 Setting up tools...")
        setup_texture_tools()
        setup_file_manager_tools()
        setup_material_loader_tools()
        
        # Delay để đảm bảo Houdini UI đã load xong
        def delayed_show():
            try:
                # Check if MiniBar should auto-start
                from mono_tools.qt import QtCore
                s = QtCore.QSettings("Mono", "FileManager")
                startup_enabled = s.value("minibar_startup_with_hou", True, type=bool)
                
                if not startup_enabled:
                    print("🚀 MiniBar startup disabled - skipping auto-start")
                    print("✅ All tools setup complete!")
                    print("🎉 Mono Studio ready!")
                    return
                
                print("🚀 Auto-starting MiniBar...")
                minibar = show_mono_minibar()
                if minibar:
                    # MiniBar will position itself using _get_default_position()
                    minibar.raise_()
                    print("✅ All tools setup complete!")
                    print("✅ MiniBar auto-started successfully!")
                    print("🎉 Mono Studio ready!")
                else:
                    print("⚠️ MiniBar creation failed")
            except Exception as e:
                print(f"❌ MiniBar error: {e}")
        
        # Delay 500ms để Houdini UI load xong
        QtCore.QTimer.singleShot(500, delayed_show)
        return True
        
    except Exception as e:
        print(f"❌ Auto-load failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Execute auto-load only when run directly
if __name__ == "__main__":
    auto_load_mono_studio()