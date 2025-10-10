"""
Mono Studio - UI Ready Startup
This runs after UI is fully loaded - perfect for UI tools like MiniBar
Only runs in interactive Houdini sessions (not batch mode)
"""

print("🎬 Mono Studio v2.2.0 - UI Ready startup")

try:
    import sys
    import os
    
    # Check if MONO_STUDIO environment is available
    mono_studio = os.environ.get('MONO_STUDIO')
    if not mono_studio:
        print("⚠️ MONO_STUDIO not set - package might not be loaded")
    else:
        print(f"✅ MONO_STUDIO: {mono_studio}")
    
    # Add Python paths (should already be set by package.json, but double check)
    python_path = os.path.join(mono_studio, "python")
    if python_path not in sys.path:
        sys.path.insert(0, python_path)
        print(f"📁 Added python path: {python_path}")
    
    # Setup menus first
    print("🔧 Setting up menus...")
    from mono_tools import (
        setup_file_manager_tools,
        setup_material_loader_tools,
        setup_texture_tools
    )
    
    setup_file_manager_tools()
    setup_material_loader_tools()
    setup_texture_tools()
    print("✅ Menus loaded!")
    
    # Import MiniBar function (UI is already ready!)
    from mono_tools import show_mono_minibar
    import hou
    
    # No need for QTimer delay - UI is already ready at this point!
    print("🎯 Creating MiniBar (UI ready)...")
    minibar = show_mono_minibar()
    
    if minibar:
        # MiniBar will use its own positioning logic (default or saved position)
        minibar.raise_()
        print("✅ MiniBar ready!")
        print("🎉 Mono Studio ready!")
        print("💡 Tips: Click shot → open file | Click ⚡ → full manager")
    else:
        print("❌ MiniBar creation failed")
    
except Exception as e:
    print(f"❌ UI Ready startup failed: {e}")
    import traceback
    traceback.print_exc()

