# Orchestrator API for Mono File Manager (Houdini 21 / Python 3.11 / PySide6)
import os
from mono_tools.qt import QtCore, QtWidgets
import hou
from .fm_manager import MonoFileManager
from .fm_minibar import MonoFileMiniBar
from .fm_helpers import SUBPATH, collect_files

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
    try:
        for widget in hou.qt.mainWindow().findChildren(QtCore.QObject, "MonoMiniBar"):
            if hasattr(widget, 'close') and widget.isVisible():
                print(f"🗑️ Closing existing minibar at {widget.pos()}")
                widget.close(); widget.deleteLater()
    except: pass
    _active_minibar = None
    print("🔄 Creating new minibar...")
    mb=MonoFileMiniBar(manager_factory=_make_manager, parent=hou.qt.mainWindow())
    _active_minibar=mb
    d=_make_manager()
    base=os.path.join(d.root_le.text().strip(), SUBPATH) if d.root_le.text().strip() else ""
    if base and os.path.isdir(base):
        mb.populate(collect_files(base, depth=1))
    return mb

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


