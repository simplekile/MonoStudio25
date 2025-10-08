"""
Verification script để kiểm tra PySide6 compatibility
Chạy script này trong Houdini để verify tất cả components
"""

def verify_pyside6():
    """Verify PySide6 is working correctly"""
    print("🔍 Verifying PySide6 compatibility...")
    
    try:
        # Test PySide6 import
        from PySide6 import QtCore, QtGui, QtWidgets
        print("✅ PySide6 import successful")
        
        # Test Qt version
        qt_version = QtCore.qVersion()
        print(f"📦 Qt version: {qt_version}")
        
        # Check if we're in Houdini
        try:
            import hou
            print("✅ Houdini environment detected")
            
            # Test Houdini Qt integration
            main_window = hou.qt.mainWindow()
            if main_window:
                print("✅ Houdini main window accessible")
            else:
                print("⚠️ Houdini main window not available")
                
        except ImportError:
            print("⚠️ Not running in Houdini environment")
        
        return True
        
    except ImportError as e:
        print(f"❌ PySide6 import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def verify_texture_tool():
    """Verify texture search replace tool"""
    print("\n🔍 Verifying Texture Search & Replace tool...")
    
    try:
        from ..texture_search_replace import show_texture_search_replace
        print("✅ Texture Search & Replace import successful")
        
        # Test function exists and is callable
        if callable(show_texture_search_replace):
            print("✅ Function is callable")
        else:
            print("❌ Function is not callable")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def verify_menu_integration():
    """Verify menu integration"""
    print("\n🔍 Verifying menu integration...")
    
    try:
        from ..texture_menu_integration import setup_texture_tools
        print("✅ Menu integration import successful")
        
        # Test function exists and is callable
        if callable(setup_texture_tools):
            print("✅ Setup function is callable")
        else:
            print("❌ Setup function is not callable")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def verify_qt_widgets():
    """Verify Qt widgets can be created"""
    print("\n🔍 Verifying Qt widget creation...")
    
    try:
        from PySide6 import QtWidgets, QtCore
        
        # Create application if needed
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication([])
        
        # Test creating a simple dialog
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Verification Test")
        dialog.resize(300, 200)
        
        # Test creating layout and widgets
        layout = QtWidgets.QVBoxLayout(dialog)
        
        label = QtWidgets.QLabel("Test Label")
        button = QtWidgets.QPushButton("Test Button")
        line_edit = QtWidgets.QLineEdit()
        
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        
        print("✅ Qt widgets creation successful")
        
        # Clean up
        dialog.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Widget creation failed: {e}")
        return False


def run_verification():
    """Run all verification tests"""
    print("🚀 Mono Studio - PySide6 Verification")
    print("=" * 60)
    
    tests = [
        ("PySide6 Compatibility", verify_pyside6),
        ("Texture Search & Replace Tool", verify_texture_tool),
        ("Menu Integration", verify_menu_integration),
        ("Qt Widget Creation", verify_qt_widgets),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verifications passed! Ready for Houdini 21.")
        print("💡 You can now use Texture Search & Replace tool.")
    else:
        print("⚠️ Some verifications failed. Check the errors above.")
        print("💡 Make sure you're running in Houdini 21+ environment.")
    
    return passed == total


if __name__ == "__main__":
    run_verification()
