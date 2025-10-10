"""
Debug startup issues
Run this in Houdini Python Console to check what's wrong
"""

def debug_startup():
    """Comprehensive startup debugging"""
    print("\n" + "="*70)
    print("🔍 MONO STUDIO STARTUP DEBUGGING")
    print("="*70 + "\n")
    
    import sys
    import os
    
    # 1. Check Environment Variables
    print("1️⃣ CHECKING ENVIRONMENT VARIABLES:")
    print("-" * 70)
    mono_studio = os.environ.get('MONO_STUDIO')
    mono_version = os.environ.get('MONO_VERSION')
    pythonpath = os.environ.get('PYTHONPATH', '')
    
    print(f"   MONO_STUDIO: {mono_studio}")
    print(f"   MONO_VERSION: {mono_version}")
    print(f"   PYTHONPATH contains MonoStudio: {'MonoStudio' in pythonpath}")
    
    if not mono_studio:
        print("   ❌ MONO_STUDIO not set!")
        print("   → Package might not be loaded!")
        return False
    else:
        print("   ✅ Environment variables OK")
    
    # 2. Check Python Path
    print("\n2️⃣ CHECKING PYTHON PATH:")
    print("-" * 70)
    mono_in_path = False
    for p in sys.path:
        if 'MonoStudio' in p:
            print(f"   ✅ {p}")
            mono_in_path = True
    
    if not mono_in_path:
        print("   ❌ MonoStudio python path not in sys.path!")
        print("   → Imports will fail!")
        return False
    
    # 3. Check Files Exist
    print("\n3️⃣ CHECKING FILES:")
    print("-" * 70)
    if mono_studio:
        startup_script = os.path.join(mono_studio, 'scripts', 'startup.py')
        package_json = os.path.join(mono_studio, 'MonoStudio_package.json')
        
        print(f"   Package JSON: {os.path.exists(package_json)}")
        print(f"   Startup Script: {os.path.exists(startup_script)}")
        
        if os.path.exists(startup_script):
            print(f"   ✅ Startup script exists at: {startup_script}")
        else:
            print(f"   ❌ Startup script NOT found!")
            return False
    
    # 4. Test Import mono_tools
    print("\n4️⃣ TESTING IMPORTS:")
    print("-" * 70)
    try:
        import mono_tools
        print(f"   ✅ mono_tools imported")
        print(f"   Version: {mono_tools.__version__}")
    except Exception as e:
        print(f"   ❌ Cannot import mono_tools: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Test Import Qt
    print("\n5️⃣ TESTING QT:")
    print("-" * 70)
    try:
        from mono_tools.qt import QtCore, QtWidgets
        print(f"   ✅ Qt imported")
    except Exception as e:
        print(f"   ❌ Cannot import Qt: {e}")
        return False
    
    # 6. Test Setup Functions
    print("\n6️⃣ TESTING SETUP FUNCTIONS:")
    print("-" * 70)
    try:
        from mono_tools import (
            setup_file_manager_tools,
            setup_material_loader_tools,
            setup_texture_tools,
            show_mono_minibar
        )
        print(f"   ✅ All setup functions imported")
    except Exception as e:
        print(f"   ❌ Cannot import setup functions: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 7. Check if startup was executed
    print("\n7️⃣ CHECKING IF STARTUP RAN:")
    print("-" * 70)
    print("   Check Houdini console for these messages:")
    print("   - '🚀 Mono Studio v2.2.0 - Loading...'")
    print("   - '✅ Menus loaded!'")
    print("   - '✅ MiniBar ready!'")
    print("   - '🎉 Mono Studio ready!'")
    print()
    print("   If you DON'T see these messages:")
    print("   → startup.py was NOT executed by Houdini")
    print("   → Package might not be installed correctly")
    
    # 8. Manual execution test
    print("\n8️⃣ MANUAL EXECUTION TEST:")
    print("-" * 70)
    print("   Would you like to manually run startup sequence? (y/n)")
    print("   If yes, run: debug_manual_startup()")
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print("✅ If all checks passed above, startup should work")
    print("❌ If any check failed, that's the problem!")
    print()
    print("💡 NEXT STEPS:")
    print("   1. Check Houdini console for startup messages")
    print("   2. Check Houdini menu bar for 'Mono Studio' menu")
    print("   3. Look for MiniBar widget on screen")
    print("   4. If nothing shows, run: debug_manual_startup()")
    print("="*70 + "\n")
    
    return True


def debug_manual_startup():
    """Manually execute startup sequence to see errors"""
    print("\n" + "="*70)
    print("🚀 MANUAL STARTUP EXECUTION")
    print("="*70 + "\n")
    
    try:
        print("1️⃣ Importing modules...")
        from mono_tools import (
            setup_file_manager_tools,
            setup_material_loader_tools,
            setup_texture_tools,
            show_mono_minibar
        )
        print("   ✅ Imports OK")
        
        print("\n2️⃣ Setting up menus...")
        setup_file_manager_tools()
        print("   ✅ File Manager menu setup")
        
        setup_material_loader_tools()
        print("   ✅ Material Loader menu setup")
        
        setup_texture_tools()
        print("   ✅ Texture tools menu setup")
        
        print("\n3️⃣ Creating MiniBar...")
        minibar = show_mono_minibar()
        if minibar:
            print("   ✅ MiniBar created and shown!")
            print(f"   Type: {type(minibar)}")
            print(f"   Visible: {minibar.isVisible()}")
        else:
            print("   ❌ MiniBar creation returned None")
        
        print("\n" + "="*70)
        print("✅ MANUAL STARTUP COMPLETED!")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURING MANUAL STARTUP: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70)
        return False


def check_package_loaded():
    """Check if Houdini loaded the package"""
    print("\n" + "="*70)
    print("📦 CHECKING PACKAGE STATUS")
    print("="*70 + "\n")
    
    import os
    
    # Check environment
    mono_studio = os.environ.get('MONO_STUDIO')
    
    if not mono_studio:
        print("❌ Package NOT loaded!")
        print("\n💡 SOLUTION:")
        print("   1. Check package file location:")
        print("      - Windows: C:/Users/[USER]/Documents/houdini21.0/packages/")
        print("      - Or: $HOUDINI_USER_PREF_DIR/packages/")
        print()
        print("   2. Package file should be named:")
        print("      - MonoStudio25.json")
        print()
        print("   3. Package content should point to:")
        print("      - D:/Dropbox/Stock/Plugin/HOU/MonoStudio25")
        print()
        print("   4. Restart Houdini after placing package file")
        return False
    
    print(f"✅ Package loaded from: {mono_studio}")
    
    # Check if startup script was called
    print("\n🔍 To verify startup script ran:")
    print("   1. Look in Houdini console (View → Console)")
    print("   2. Search for '🚀 Mono Studio'")
    print("   3. If found → startup ran")
    print("   4. If NOT found → startup did NOT run")
    
    return True


if __name__ == "__main__":
    print("Run in Houdini Python Console:")
    print("  from mono_tools.test_demo.test_startup_debug import *")
    print("  debug_startup()")

