"""
Test to verify package script execution
Run this in Houdini Python Console
"""

print("\n" + "="*70)
print("🔍 PACKAGE SCRIPT EXECUTION TEST")
print("="*70 + "\n")

import os
import sys

# Check MONO_STUDIO env
mono_studio = os.environ.get('MONO_STUDIO')
print(f"1️⃣ MONO_STUDIO: {mono_studio}")

if not mono_studio:
    print("❌ Package not loaded!")
else:
    print("✅ Package loaded")
    
    # Check if startup_debug.log exists
    debug_log = os.path.join(mono_studio, 'startup_debug.log')
    print(f"\n2️⃣ Debug log: {debug_log}")
    print(f"   Exists: {os.path.exists(debug_log)}")
    
    if os.path.exists(debug_log):
        print("✅ Startup script WAS executed!")
        print("\n📄 Log content:")
        with open(debug_log, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ Startup script was NOT executed!")
        print("\n💡 This means:")
        print("   - Package loaded (env vars set)")
        print("   - But 'script' field in package.json not executed")
        print("   - This is the problem!")
    
    # Check HOUDINI_SCRIPT_PATH
    script_path = os.environ.get('HOUDINI_SCRIPT_PATH', '')
    print(f"\n3️⃣ HOUDINI_SCRIPT_PATH:")
    for p in script_path.split(';'):
        if p.strip():
            print(f"   - {p}")
    
    # Check if startup.py exists
    startup_py = os.path.join(mono_studio, 'scripts', 'startup.py')
    print(f"\n4️⃣ Startup script: {startup_py}")
    print(f"   Exists: {os.path.exists(startup_py)}")
    
    if os.path.exists(startup_py):
        print("   ✅ File exists")
        # Try to execute it manually
        print("\n5️⃣ Trying manual execution...")
        try:
            with open(startup_py, 'r', encoding='utf-8') as f:
                code = f.read()
            exec(compile(code, startup_py, 'exec'))
            print("   ✅ Manual execution successful!")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

print("\n" + "="*70 + "\n")

