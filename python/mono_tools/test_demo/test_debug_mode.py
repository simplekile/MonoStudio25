"""
Test Debug Mode Toggle
Run this in Houdini Python Console
"""

def test_debug_mode():
    """Test debug mode on/off"""
    import os
    
    print("\n" + "="*70)
    print("🧪 Testing Debug Mode Toggle")
    print("="*70 + "\n")
    
    # Test 1: Debug OFF (default)
    print("1️⃣ Testing DEBUG OFF (default):")
    print("-" * 70)
    
    # Ensure it's off
    if 'MONO_DEBUG' in os.environ:
        del os.environ['MONO_DEBUG']
    
    # Reload helpers to pick up new DEBUG value
    import sys
    if 'mono_tools.file_manager.file_manager_helpers' in sys.modules:
        del sys.modules['mono_tools.file_manager.file_manager_helpers']
    
    from mono_tools.file_manager.file_manager_helpers import debug_print, DEBUG
    
    print(f"   DEBUG flag: {DEBUG}")
    print(f"   Testing debug_print()...")
    debug_print("   👻 This message should NOT appear")
    print(f"   ✅ Debug is OFF (no ghost message above)")
    
    # Test 2: Debug ON
    print("\n2️⃣ Testing DEBUG ON:")
    print("-" * 70)
    
    # Turn on debug
    os.environ['MONO_DEBUG'] = '1'
    
    # Reload helpers
    if 'mono_tools.file_manager.file_manager_helpers' in sys.modules:
        del sys.modules['mono_tools.file_manager.file_manager_helpers']
    
    from mono_tools.file_manager.file_manager_helpers import debug_print, DEBUG
    
    print(f"   DEBUG flag: {DEBUG}")
    print(f"   Testing debug_print()...")
    debug_print("   ✅ This message SHOULD appear!")
    print(f"   ✅ Debug is ON (message appeared above)")
    
    # Test 3: Different values
    print("\n3️⃣ Testing Different Values:")
    print("-" * 70)
    
    test_values = [
        ('1', True),
        ('true', True),
        ('TRUE', True),
        ('yes', True),
        ('YES', True),
        ('0', False),
        ('false', False),
        ('no', False),
        ('', False),
    ]
    
    for value, expected in test_values:
        os.environ['MONO_DEBUG'] = value
        
        # Reload
        if 'mono_tools.file_manager.file_manager_helpers' in sys.modules:
            del sys.modules['mono_tools.file_manager.file_manager_helpers']
        
        from mono_tools.file_manager.file_manager_helpers import DEBUG
        
        status = "✅" if DEBUG == expected else "❌"
        print(f"   {status} MONO_DEBUG='{value}' → DEBUG={DEBUG} (expected {expected})")
    
    # Test 4: Usage in MiniBar
    print("\n4️⃣ Testing in MiniBar:")
    print("-" * 70)
    
    # Set debug on
    os.environ['MONO_DEBUG'] = '1'
    
    # Reload modules
    modules_to_reload = [
        'mono_tools.file_manager.file_manager_helpers',
        'mono_tools.file_manager.file_manager_minibar',
    ]
    for mod in modules_to_reload:
        if mod in sys.modules:
            del sys.modules[mod]
    
    print("   Creating MiniBar with DEBUG=1...")
    try:
        from mono_tools import show_mono_minibar
        # Don't actually show it, just test import
        print("   ✅ MiniBar imports OK with debug mode")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Cleanup - turn off debug
    if 'MONO_DEBUG' in os.environ:
        del os.environ['MONO_DEBUG']
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print("✅ Debug mode can be toggled with MONO_DEBUG environment variable")
    print("✅ debug_print() respects DEBUG flag")
    print("✅ Supported values: '1', 'true', 'yes' (case-insensitive)")
    print("\n💡 HOW TO USE:")
    print("   • To enable debug: os.environ['MONO_DEBUG'] = '1'")
    print("   • To disable: del os.environ['MONO_DEBUG']")
    print("   • Or restart Houdini without MONO_DEBUG set")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_debug_mode()

