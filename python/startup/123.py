# Mono Studio Auto-startup
# File này sẽ tự động chạy khi Houdini khởi động

print("🔄 Loading Mono Studio startup script...")

try:
    # Add current directory to path first
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"📁 Added current dir to path: {current_dir}")
    
    # Import startup module
    print("📁 Importing auto_load module...")
    import auto_load
    print("🎬 Mono Studio startup completed!")
    
except Exception as e:
    print(f"❌ Mono Studio startup error: {e}")
    import traceback
    traceback.print_exc()