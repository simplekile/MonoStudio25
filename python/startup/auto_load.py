"""
Auto-load script for Mono Studio
Runs automatically when Houdini starts
"""

def auto_load_mono_studio():
    """Auto-load Mono Studio tools"""
    try:
        print("🚀 Auto-loading Mono Studio...")
        print("📦 Importing required modules...")
        
        # Import and show MiniBar
        from mono_tools.file_manager import show_mono_minibar
        from mono_tools.texture_search_replace import show_texture_search_replace, setup_texture_tools
        from mono_tools.material_loader import show_material_loader
        from mono_tools.file_manager import setup_file_manager_tools
        from mono_tools.material_loader import setup_material_loader_tools
        from mono_tools.qt import QtCore
        import hou
        print("✅ All modules imported successfully")
        
        # Setup all tools menus
        print("🔧 Setting up all tools...")
        setup_texture_tools()
        setup_file_manager_tools()
        setup_material_loader_tools()
        
        # Delay để đảm bảo Houdini UI đã load xong
        def delayed_show():
            try:
                print("🎯 Creating MiniBar...")
                minibar = show_mono_minibar()
                if minibar:
                    print("✅ MiniBar instance created")
                    
                    # Đảm bảo MiniBar ở vị trí đúng
                    main_window = hou.qt.mainWindow()
                    if main_window:
                        geo = main_window.geometry()
                        # Đặt ở góc phải trên
                        new_x = geo.x() + geo.width() - minibar.width() - 20
                        new_y = geo.y() + 50
                        minibar.move(new_x, new_y)
                        minibar._save_relative_position()
                        print(f"📍 MiniBar positioned at ({new_x}, {new_y})")
                    
                    minibar.raise_()
                    print("✅ Mono Studio MiniBar loaded!")
                    print("💡 Tips: Click shot name → open file | Click ⚡ → full manager")
                    print("🔍 Texture Search & Replace available in Mono Studio menu")
                else:
                    print("⚠️ MiniBar creation returned None")
            except Exception as e:
                print(f"❌ MiniBar error: {e}")
                import traceback
                traceback.print_exc()
        
        # Delay 500ms để Houdini UI load xong
        print("⏱️ Setting 500ms delay for UI initialization...")
        QtCore.QTimer.singleShot(500, delayed_show)
        return True
        
    except Exception as e:
        print(f"❌ Auto-load failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Execute auto-load
auto_load_mono_studio()