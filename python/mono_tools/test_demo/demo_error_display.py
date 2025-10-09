#!/usr/bin/env python3
"""
Demo script for error display functionality
Shows how to use the new error display system
"""

def demo_error_display():
    """Demo the error display system"""
    try:
        print("🎬 Mono Studio Error Display Demo")
        print("=" * 50)
        
        # Import required modules
        from mono_tools.file_manager.file_manager_manager import MonoFileManager
        from mono_tools.qt import QtWidgets, QtCore
        import sys
        import os
        
        print("📋 Error Display Features:")
        print("   • Status bar at bottom of UI")
        print("   • Real-time status updates")
        print("   • Error messages with details button")
        print("   • Full error dialog with traceback")
        print("   • Copy error to clipboard")
        print("   • Graceful error handling")
        
        print("\n🔧 Creating File Manager...")
        
        # Create a simple Qt application for demo
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        
        # Create file manager
        manager = MonoFileManager()
        
        print("✅ File Manager created successfully!")
        print("\n📊 Status Bar Components:")
        print(f"   • Status Bar: {manager.status_bar is not None}")
        print(f"   • Status Label: {manager.status_label is not None}")
        print(f"   • Error Details Button: {manager.error_details_btn is not None}")
        
        print("\n🧪 Testing Status Display...")
        
        # Test normal status
        manager._show_status("🔍 Demo: Scanning files...", is_error=False)
        print("   ✅ Normal status displayed")
        
        # Simulate some work
        QtCore.QTimer.singleShot(1000, lambda: manager._show_status("✅ Demo: Found 25 files", is_error=False))
        
        # Test error status
        QtCore.QTimer.singleShot(2000, lambda: manager._show_error("Demo: Directory not found: /invalid/path"))
        
        # Test error with traceback
        QtCore.QTimer.singleShot(3000, lambda: demo_error_with_traceback(manager))
        
        print("\n💡 Demo Instructions:")
        print("   1. Watch the status bar at the bottom")
        print("   2. Try clicking '📋 Details' when error appears")
        print("   3. Try various operations to see error handling")
        print("   4. Check how errors are displayed vs normal status")
        
        # Show the manager
        manager.show()
        
        print("\n🎉 Demo ready! Check the File Manager window.")
        print("   • Status bar shows at the bottom")
        print("   • Error messages appear in red")
        print("   • Click '📋 Details' for full error info")
        
        return manager
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def demo_error_with_traceback(manager):
    """Demo error with traceback"""
    try:
        import traceback
        
        # Create a fake error with traceback
        try:
            # This will cause an error
            result = 1 / 0
        except Exception as e:
            error_msg = f"Demo error: Division by zero in calculation"
            traceback_str = traceback.format_exc()
            manager._show_error(error_msg, error_obj=e, traceback_str=traceback_str)
            
    except Exception as e:
        print(f"⚠️ Error in demo: {e}")

def main():
    """Main function"""
    print("🎬 Mono Studio Error Display Demo")
    print("=" * 60)
    
    manager = demo_error_display()
    
    if manager:
        print("\n✅ Demo completed successfully!")
        print("💡 The error display system is working!")
    else:
        print("\n❌ Demo failed!")
        print("💡 Check the error messages above")

if __name__ == "__main__":
    main()
