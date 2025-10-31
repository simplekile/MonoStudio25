"""
Mono Studio Package Startup
Simple and clean startup for Houdini package
"""

# Debug: Write to file to verify script execution
import os
debug_file = os.path.join(os.path.dirname(__file__), '..', 'startup_debug.log')
with open(debug_file, 'w', encoding='utf-8') as f:
    f.write("Startup script executed!\n")
    import sys
    f.write(f"Python: {sys.version}\n")
    f.write(f"Script: {__file__}\n")

import hou
from mono_tools.qt import QtCore

print("🚀 Mono Studio v2.3.0 - Loading...")
print(f"📍 Script path: {__file__}")

# Setup menus
try:
    from mono_tools import (
        setup_file_manager_tools, 
        setup_material_loader_tools, 
        setup_texture_tools,
        show_mono_minibar
    )
    
    setup_file_manager_tools()
    setup_material_loader_tools()
    setup_texture_tools()
    print("✅ Menus loaded!")
    
except Exception as e:
    print(f"❌ Menu setup failed: {e}")
    import traceback
    traceback.print_exc()

# Auto-show MiniBar after UI ready (with delay to ensure Houdini UI is loaded)
def delayed_minibar_show():
    try:
        minibar = show_mono_minibar()
        if minibar:
            print("✅ MiniBar ready!")
            print("🎉 Mono Studio ready!")
        else:
            print("⚠️ MiniBar creation failed")
    except Exception as e:
        print(f"❌ MiniBar error: {e}")
        import traceback
        traceback.print_exc()

# Delay 500ms để Houdini UI load xong
QtCore.QTimer.singleShot(500, delayed_minibar_show)
