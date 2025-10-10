"""
Mono Studio - UI Ready Startup
This runs after UI is fully loaded - perfect for UI tools like MiniBar
Only runs in interactive Houdini sessions (not batch mode)
"""

try:
    import sys
    import os
    
    # Check if MONO_STUDIO environment is available
    mono_studio = os.environ.get('MONO_STUDIO')
    if not mono_studio:
        print("⚠️ Mono Studio: MONO_STUDIO not set - package might not be loaded")
        raise EnvironmentError("MONO_STUDIO environment variable not set")
    
    # Add Python paths (should already be set by package.json, but double check)
    python_path = os.path.join(mono_studio, "python")
    if python_path not in sys.path:
        sys.path.insert(0, python_path)
    
    # Setup menus first
    from mono_tools import (
        setup_file_manager_tools,
        setup_material_loader_tools,
        setup_texture_tools,
        show_mono_minibar
    )
    
    setup_file_manager_tools()
    setup_material_loader_tools()
    setup_texture_tools()
    
    # Import Houdini
    import hou
    
    # Create MiniBar (UI is already ready at this point!)
    minibar = show_mono_minibar()
    
    if minibar:
        # MiniBar will use its own positioning logic (default or saved position)
        minibar.raise_()
    
except Exception as e:
    # Only print errors
    print(f"❌ Mono Studio startup error: {e}")
    import traceback
    traceback.print_exc()

