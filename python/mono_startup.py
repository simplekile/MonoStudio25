"""
Mono Studio - Alternative startup method
Place this in the main python folder
"""

print("🔄 Mono Studio alternative startup loading...")

try:
    # Add paths first
    import sys
    import os
    
    mono_studio = r"d:\Dropbox\Stock\Plugin\HOU\MonoStudio"
    startup_path = os.path.join(mono_studio, "python", "startup")
    
    if startup_path not in sys.path:
        sys.path.insert(0, startup_path)
        print(f"📁 Added startup path: {startup_path}")
    
    # Import and run
    import auto_load
    print("✅ Alternative startup method successful!")
    
except Exception as e:
    print(f"❌ Alternative startup failed: {e}")
    import traceback
    traceback.print_exc()