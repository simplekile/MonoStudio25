"""
Test script để kiểm tra PySide6 compatibility
"""

def test_pyside6_import():
    """Test import PySide6 modules"""
    try:
        print("🧪 Testing PySide6 imports...")
        
        # Test basic PySide6 imports
        from PySide6 import QtCore, QtGui, QtWidgets
        print("✅ PySide6 basic imports successful")
        
        # Test Qt version
        print(f"📦 Qt version: {QtCore.qVersion()}")
        
        # Test creating a simple widget
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication([])
        
        widget = QtWidgets.QWidget()
        widget.setWindowTitle("PySide6 Test")
        print("✅ QWidget creation successful")
        
        # Test Houdini integration
        try:
            import hou
            print("✅ Houdini integration available")
            
            # Test Houdini Qt integration
            main_window = hou.qt.mainWindow()
            if main_window:
                print("✅ Houdini main window accessible")
            else:
                print("⚠️ Houdini main window not available")
                
        except ImportError:
            print("⚠️ Houdini not available (running outside Houdini)")
        
        return True
        
    except ImportError as e:
        print(f"❌ PySide6 import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_texture_search_replace_import():
    """Test import texture search replace tool"""
    try:
        print("\n🧪 Testing Texture Search & Replace import...")
        
        from ..texture_search_replace import show_texture_search_replace
        print("✅ Texture Search & Replace import successful")
        
        # Test function signature
        import inspect
        sig = inspect.signature(show_texture_search_replace)
        print(f"📝 Function signature: {sig}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_qt_widget_creation():
    """Test creating Qt widgets"""
    try:
        print("\n🧪 Testing Qt widget creation...")
        
        from PySide6 import QtWidgets, QtCore
        
        # Create application if needed
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication([])
        
        # Test creating dialog
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Test Dialog")
        dialog.resize(400, 300)
        print("✅ QDialog creation successful")
        
        # Test creating layout
        layout = QtWidgets.QVBoxLayout(dialog)
        print("✅ QVBoxLayout creation successful")
        
        # Test creating widgets
        label = QtWidgets.QLabel("Test Label")
        button = QtWidgets.QPushButton("Test Button")
        line_edit = QtWidgets.QLineEdit()
        
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        
        print("✅ Widget creation and layout successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Widget creation test failed: {e}")
        return False


def run_all_tests():
    """Chạy tất cả tests"""
    print("🚀 PySide6 Compatibility Tests")
    print("=" * 50)
    
    tests = [
        ("PySide6 Import", test_pyside6_import),
        ("Texture Search Replace Import", test_texture_search_replace_import),
        ("Qt Widget Creation", test_qt_widget_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PySide6 is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    run_all_tests()
