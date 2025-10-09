# Orchestrator API for Mono File Manager (Houdini 21 / Python 3.11 / PySide6)
import os
from mono_tools.qt import QtCore, QtWidgets
import hou
from .file_manager_manager import MonoFileManager
from .file_manager_minibar import MonoFileMiniBar
from .file_manager_helpers import SUBPATH, collect_files

_active_dialog=None
_active_minibar=None

def _make_manager():
    global _active_dialog
    if _active_dialog and _active_dialog.isVisible():
        return _active_dialog
    for w in QtWidgets.QApplication.topLevelWidgets():
        if w.__class__.__name__ == 'MonoFileManager':
            _active_dialog=w; return w
    d=MonoFileManager(hou.qt.mainWindow()); _active_dialog=d; return d

def show_mono_file_manager():
    d=_make_manager(); d.show(); d.raise_(); d.activateWindow(); return d

def show_mono_minibar():
    global _active_minibar
    print("🔍 show_mono_minibar() called")
    
    # Debug call stack
    import traceback
    print("🔍 Call stack:")
    for line in traceback.format_stack():
        print(f"  {line.strip()}")
    
    try:
        print("🔍 Checking for existing minibar...")
        existing_minibars = hou.qt.mainWindow().findChildren(QtCore.QObject, "MonoMiniBar")
        print(f"🔍 Found {len(existing_minibars)} existing minibars")
        
        for i, widget in enumerate(existing_minibars):
            print(f"🔍 Minibar {i}: {widget}, visible: {widget.isVisible() if hasattr(widget, 'isVisible') else 'N/A'}")
            if hasattr(widget, 'close') and widget.isVisible():
                print(f"🗑️ Closing existing minibar at {widget.pos()}")
                widget.close(); widget.deleteLater()
    except Exception as e:
        print(f"🔍 Error checking existing minibar: {e}")
    
    _active_minibar = None
    print("🔄 Creating new minibar...")
    
    try:
        mb=MonoFileMiniBar(manager_factory=_make_manager, parent=hou.qt.mainWindow())
        print(f"🔍 MiniBar created: {mb}")
        _active_minibar=mb
        
        print("🔍 Getting manager...")
        d=_make_manager()
        print(f"🔍 Manager: {d}")
        
        print("🔍 Checking project root...")
        base=os.path.join(d.root_le.text().strip(), SUBPATH) if d.root_le.text().strip() else ""
        print(f"🔍 Project base: {base}")
        
        if base and os.path.isdir(base):
            print("🔍 Populating minibar with files...")
            mb.populate(collect_files(base, depth=1))
        else:
            print("🔍 No valid project root - minibar will be empty")
        
        print(f"🔍 Returning minibar: {mb}")
        return mb
        
    except Exception as e:
        print(f"⚠️ Error creating minibar: {e}")
        import traceback
        traceback.print_exc()
        return None

class FileManagerWrapper:
    def __init__(self):
        self.minibar=None
    def show_minibar(self):
        try:
            self.minibar=show_mono_minibar(); return True
        except Exception as e:
            print(f"❌ Could not show minibar: {e}"); return False

def create_mono_file_manager():
    return show_mono_file_manager()

__all__ = [
    'MonoFileManager',
    'MonoFileMiniBar',
    'show_mono_file_manager',
    'show_mono_minibar',
    'FileManagerWrapper',
    'create_mono_file_manager',
]


