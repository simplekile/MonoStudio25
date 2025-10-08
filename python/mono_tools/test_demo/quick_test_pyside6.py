"""
Quick test script cho PySide6 compatibility
Chạy script này trong Houdini để test nhanh
"""

def quick_test():
    """Quick test PySide6 và Texture Search & Replace"""
    print("⚡ Quick PySide6 Test")
    print("=" * 40)
    
    try:
        # Test 1: PySide6 import
        print("1️⃣ Testing PySide6...")
        from PySide6 import QtCore, QtGui, QtWidgets
        print(f"   ✅ PySide6 OK - Qt version: {QtCore.qVersion()}")
        
        # Test 2: Houdini integration
        print("\n2️⃣ Testing Houdini integration...")
        import hou
        main_window = hou.qt.mainWindow()
        if main_window:
            print("   ✅ Houdini main window accessible")
        else:
            print("   ⚠️ Houdini main window not available")
        
        # Test 3: Texture Search & Replace
        print("\n3️⃣ Testing Texture Search & Replace...")
        from mono_tools.texture_search_replace import show_texture_search_replace
        print("   ✅ Texture Search & Replace import OK")
        
        # Test 4: Menu integration
        print("\n4️⃣ Testing menu integration...")
        from mono_tools.texture_menu_integration import setup_texture_tools
        print("   ✅ Menu integration import OK")
        
        # Test 5: Create test dialog
        print("\n5️⃣ Testing dialog creation...")
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication([])
        
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("PySide6 Test")
        dialog.resize(300, 200)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel("PySide6 is working!")
        button = QtWidgets.QPushButton("Close")
        button.clicked.connect(dialog.close)
        
        layout.addWidget(label)
        layout.addWidget(button)
        
        print("   ✅ Dialog creation OK")
        
        # Show dialog briefly
        dialog.show()
        dialog.raise_()
        print("   ✅ Dialog displayed")
        
        # Clean up
        dialog.close()
        
        print("\n" + "=" * 40)
        print("🎉 All tests passed! PySide6 is working correctly.")
        print("💡 Texture Search & Replace is ready to use.")
        print("🔍 Access via: Mono Studio menu > Texture Search & Replace")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running in Houdini 21+")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_texture_tool():
    """Test Texture Search & Replace tool specifically"""
    print("\n🔍 Testing Texture Search & Replace tool...")
    
    try:
        from mono_tools.texture_search_replace import show_texture_search_replace
        
        # Try to create the dialog
        dialog = show_texture_search_replace()
        if dialog:
            print("✅ Texture Search & Replace dialog created successfully")
            print("💡 Dialog is ready to use")
            return True
        else:
            print("❌ Failed to create dialog")
            return False
            
    except Exception as e:
        print(f"❌ Error testing texture tool: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Mono Studio - Quick PySide6 Test")
    print("Running in Houdini environment...")
    print()
    
    # Run quick test
    if quick_test():
        print("\n🎯 Running Texture Search & Replace test...")
        test_texture_tool()
    else:
        print("\n❌ Quick test failed. Check your Houdini environment.")
