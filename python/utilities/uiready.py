"""
Mono Studio - UI Ready Startup (Recommended Method)
Place in: $HOUDINI_USER_PREF_DIR/python3.11libs/uiready.py
OR: $MONO_STUDIO/python3.11libs/uiready.py

This runs after UI is fully loaded - perfect for UI tools like MiniBar
Only runs in interactive Houdini sessions (not batch mode)
"""

print("🎬 Mono Studio - UI Ready startup method")

try:
    import sys
    import os
    
    # Check if MONO_STUDIO environment is available
    mono_studio = os.environ.get('MONO_STUDIO')
    if not mono_studio:
        # Fallback: set paths manually (updated to MonoStudio25)
        mono_studio = "d:/Dropbox/Stock/Plugin/HOU/MonoStudio25"
        os.environ['MONO_STUDIO'] = mono_studio
        print(f"🔧 Set MONO_STUDIO fallback: {mono_studio}")
    
    # Add Python paths
    python_path = os.path.join(mono_studio, "python")
    if python_path not in sys.path:
        sys.path.insert(0, python_path)
        print(f"📁 Added python path: {python_path}")
    
    # Confirm Qt backend via shim, then import tools
    from mono_tools.qt import API as QT_API
    print(f"🧩 Qt API selected: PySide{QT_API}")
    # Import orchestrator API (preferred) and log resolution
    from mono_tools import show_mono_minibar
    import inspect, importlib
    provider_mod = importlib.import_module(show_mono_minibar.__module__)
    provider_file = getattr(provider_mod, "__file__", "<unknown>")
    print(f"🔎 show_mono_minibar provider: {show_mono_minibar.__module__} -> {provider_file}")
    import hou
    
    print("📦 Modules imported successfully")
    
    # No need for QTimer delay - UI is already ready!
    print("🎯 Creating MiniBar (UI ready)...")
    minibar = show_mono_minibar()
    
    if minibar:
        # Let MiniBar use its own positioning logic (default or saved position)
        minibar.raise_()
        print("✅ Mono Studio MiniBar loaded via uiready.py!")
        print("💡 Click shot name → open file | Click ⚡ → full manager")
    else:
        print("❌ MiniBar creation failed")
    
except Exception as e:
    print(f"❌ UI Ready startup failed: {e}")
    import traceback
    traceback.print_exc()