# Lightweight PySide6 replacement UI for Mono Material Loader
# This file provides a simpler, modern UI using PySide6.
# It intentionally keeps behavior minimal: select texture folder, material library path,
# enable UDIM, choose renderer, and run Create Materials. It reuses the existing
# backend functions in Mono_MaterialLoader.py when available (import guarded).

from __future__ import annotations
import sys
import os
from typing import Optional

# Use Qt shim (PySide6 only)
try:
    from .qt import QtWidgets, QtCore, QtGui  # type: ignore
except Exception:
    # Local import path when executed as a script
    from mono_tools.qt import QtWidgets, QtCore, QtGui  # type: ignore

# Try to import backend functions from refactored modules
parse_texture_filename = None
hou = None

# Import engine registry for dynamic engine discovery
try:
    from .material_loader_registry import (
        get_available_engines,
        get_engine,
        get_engine_display_names,
    )
except ImportError:
    try:
        from mono_tools.material_loader.material_loader_registry import (
            get_available_engines,
            get_engine,
            get_engine_display_names,
        )
    except ImportError:
        # Fallback: provide empty functions
        def get_available_engines():
            return []
        def get_engine(name):
            return None
        def get_engine_display_names():
            return {}

try:
    # Try importing hou first
    try:
        import hou as _hou  # Houdini Python module
        hou = _hou
    except Exception:
        hou = None
    
    # Try to import parser from refactored modules
    if hou:
        try:
            from .material_loader_helpers import parse_texture_filename, fallback_parse_texture_filename
            # Use fallback parser if main parser fails
            if not parse_texture_filename:
                parse_texture_filename = fallback_parse_texture_filename
        except ImportError:
            # Fallback: Try relative imports
            try:
                from mono_tools.material_loader.material_loader_helpers import parse_texture_filename, fallback_parse_texture_filename
                if not parse_texture_filename:
                    parse_texture_filename = fallback_parse_texture_filename
            except ImportError:
                # Legacy: Try to import from utilities folder for backward compatibility
                backend = None
                try:
                    # Method 1: Try utilities.Mono_MaterialLoader (if utilities is a package)
                    from utilities import Mono_MaterialLoader as backend
                except ImportError:
                    try:
                        # Method 2: Try direct import (if on sys.path)
                        import Mono_MaterialLoader as backend
                    except ImportError:
                        try:
                            # Method 3: Try using importlib to load from path
                            import importlib.util
                            import os
                            # Get MONO_STUDIO path from environment
                            mono_studio = os.environ.get('MONO_STUDIO')
                            if mono_studio:
                                backend_path = os.path.join(mono_studio, 'python', 'utilities', 'Mono_MaterialLoader.py')
                                if os.path.exists(backend_path):
                                    spec = importlib.util.spec_from_file_location("Mono_MaterialLoader", backend_path)
                                    if spec and spec.loader:
                                        backend = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(backend)
                        except Exception:
                            backend = None
                
                if backend:
                    parse_texture_filename = getattr(backend, 'parse_texture_filename', None)
except Exception as e:
    # Running outside of Houdini or broken import; backend operations will be disabled.
    parse_texture_filename = None
    # Don't overwrite hou if it was successfully imported
    if hou is None:
        hou = None


# If backend parser is missing, use fallback from helpers
if parse_texture_filename is None:
    try:
        from .material_loader_helpers import fallback_parse_texture_filename
        parse_texture_filename = fallback_parse_texture_filename
    except ImportError:
        try:
            from mono_tools.material_loader.material_loader_helpers import fallback_parse_texture_filename
            parse_texture_filename = fallback_parse_texture_filename
        except ImportError:
            # Last resort: define inline fallback (shouldn't happen if refactoring worked)
            def _inline_fallback_parse_texture_filename(filename: str):
                """Fallback parser if helpers module not available"""
                return None
            parse_texture_filename = _inline_fallback_parse_texture_filename

class SimpleMaterialLoader(QtWidgets.QWidget):
    """A minimal, modern UI for material creation.

    Inputs:
      - Texture folder
      - Material library path (text)
      - UDIM checkbox
      - Renderer selector
      - Create button

    The UI aims to be visually lighter and easier to use than the original form.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Mono Material Loader — Simple")
        self.setMinimumSize(640, 320)
        self._is_creating = False  # Guard to prevent duplicate execution

        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QtWidgets.QLabel("Mono Material Loader")
        header.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignRight)

        # Folder chooser with compact button
        folder_row = QtWidgets.QHBoxLayout()
        self.folder_edit = QtWidgets.QLineEdit()
        browse = QtWidgets.QPushButton("Browse")
        browse.clicked.connect(self._on_browse)
        folder_row.addWidget(self.folder_edit)
        folder_row.addWidget(browse)
        form.addRow("Texture Folder:", folder_row)

        # Material library path (free text)
        self.matlib_edit = QtWidgets.QLineEdit("/stage/materiallibrary1")
        form.addRow("Material Library:", self.matlib_edit)

        # Options row
        options_row = QtWidgets.QHBoxLayout()
        self.udim_cb = QtWidgets.QCheckBox("Enable UDIM")
        self.udim_cb.setChecked(True)
        options_row.addWidget(self.udim_cb)

        # Debug checkbox (controls connection logging)
        self.debug_cb = QtWidgets.QCheckBox("Debug connections")
        default_debug = os.environ.get("MONO_MATERIAL_DEBUG_CONNECTIONS", "0") == "1"
        self.debug_cb.setChecked(default_debug)
        options_row.addWidget(self.debug_cb)

        # Debug log file picker
        file_row = QtWidgets.QHBoxLayout()
        self.debug_file_edit = QtWidgets.QLineEdit(os.environ.get("MONO_MATERIAL_DEBUG_FILE", "").strip())
        browse_debug = QtWidgets.QPushButton("File...")
        browse_debug.setMaximumWidth(70)
        browse_debug.clicked.connect(self._on_browse_debug_file)
        file_row.addWidget(self.debug_file_edit)
        file_row.addWidget(browse_debug)
        form.addRow("Debug log file:", file_row)
        options_row.addStretch()
        form.addRow("Options:", options_row)

        # Renderer selector using segmented buttons (dynamic based on available engines)
        renderer_row = QtWidgets.QHBoxLayout()
        self.renderer_group = QtWidgets.QButtonGroup(self)
        
        # Get available engines from registry
        available_engines = get_available_engines()
        display_names = get_engine_display_names()
        
        if not available_engines:
            # Fallback: show default engines if registry is empty
            available_engines = ["redshift", "karma"]
            display_names = {"redshift": "Redshift", "karma": "Karma"}
        
        # Create buttons dynamically
        for idx, engine_name in enumerate(available_engines):
            btn = QtWidgets.QPushButton(display_names.get(engine_name, engine_name.title()))
            btn.setCheckable(True)
            if idx == 0:
                btn.setChecked(True)  # First engine is default
            self.renderer_group.addButton(btn, idx)
            btn.setMinimumWidth(110)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            renderer_row.addWidget(btn)
        
        renderer_row.addStretch()
        form.addRow("Renderer:", renderer_row)
        
        # Store engine names for lookup
        self._engine_names = available_engines

        layout.addLayout(form)

        # Live types preview (compact)
        self.preview = QtWidgets.QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(120)
        self.preview.setPlaceholderText("Detected texture types will appear here when you choose a folder.")
        layout.addWidget(self.preview)

        # Action buttons
        button_row = QtWidgets.QHBoxLayout()
        self.create_btn = QtWidgets.QPushButton("Create Materials")
        self.create_btn.setStyleSheet("background-color: #2196F3; color: white; padding:6px;")
        self.create_btn.clicked.connect(self._on_create)
        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_row.addStretch()
        button_row.addWidget(self.create_btn)
        button_row.addWidget(self.close_btn)
        layout.addLayout(button_row)

        # Signals
        self.folder_edit.textChanged.connect(self._update_preview_types)

    def _on_browse(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select texture folder")
        if folder:
            self.folder_edit.setText(os.path.normpath(folder))

    def _on_browse_debug_file(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Select debug log file", filter="Log Files (*.log *.txt);;All Files (*.*)")
        if file_path:
            self.debug_file_edit.setText(os.path.normpath(file_path))

    def _update_preview_types(self):
        folder = self.folder_edit.text().strip()
        types = set()
        if folder and os.path.isdir(folder) and parse_texture_filename:
            try:
                entries = os.listdir(folder)
            except Exception as e:
                self.preview.setPlainText(f"Error reading folder: {e}")
                return
            sample = entries[:1000]
            for f in sample:
                p = os.path.join(folder, f)
                if not os.path.isfile(p):
                    continue
                parsed = parse_texture_filename(f)
                if not parsed:
                    continue
                try:
                    # Accept tuples of len>=2
                    ttype = parsed[1]
                    if ttype:
                        types.add(str(ttype))
                except Exception:
                    continue
        if types:
            self.preview.setPlainText("Detected texture types:\n" + "\n".join(sorted(types)))
        else:
            self.preview.setPlainText("No texture types detected or parser not available.")

    def _on_create(self):
        # Prevent duplicate execution
        if self._is_creating:
            return
        
        folder = self.folder_edit.text().strip()
        matlib = self.matlib_edit.text().strip()
        udim = self.udim_cb.isChecked()
        debug_enabled = self.debug_cb.isChecked()
        debug_file = self.debug_file_edit.text().strip()
        renderer_idx = self.renderer_group.checkedId()
        
        # Debug: Print engine selection info
        print(f"DEBUG: Renderer button index: {renderer_idx}")
        print(f"DEBUG: Available engines: {self._engine_names}")
        print(f"DEBUG: Engine names length: {len(self._engine_names)}")
        
        # Get engine name from registry
        if 0 <= renderer_idx < len(self._engine_names):
            engine_name = self._engine_names[renderer_idx]
            print(f"DEBUG: Selected engine name: {engine_name}")
        else:
            # Fallback to first available engine
            engine_name = self._engine_names[0] if self._engine_names else "karma"
            print(f"DEBUG: Using fallback engine: {engine_name}")

        # Basic validation
        if not folder or not os.path.isdir(folder):
            QtWidgets.QMessageBox.warning(self, "Folder missing", "Please choose a valid texture folder.")
            return

        if not matlib:
            QtWidgets.QMessageBox.warning(self, "Material library", "Please enter the material library node path.")
            return

        # Validate Houdini and matlib node
        matlib_node = None
        if hou:
            matlib_node = hou.node(matlib)
            if matlib_node is None:
                QtWidgets.QMessageBox.warning(self, "Material library", "Node path not found in the scene.")
                return

        # Disable button and set creating flag
        self._is_creating = True
        self.create_btn.setEnabled(False)
        self.create_btn.setText("Creating...")
        
        try:
            # Update debug environment flag before running engine
            os.environ["MONO_MATERIAL_DEBUG_CONNECTIONS"] = "1" if debug_enabled else "0"
            os.environ["MONO_MATERIAL_DEBUG_FILE"] = debug_file if debug_file else ""
            print(f"DEBUG: Connection logging {'enabled' if debug_enabled else 'disabled'}")
            if debug_file:
                print(f"DEBUG: Connection log file: {debug_file}")

            # Get engine info from registry
            engine_info = get_engine(engine_name)
            
            if not engine_info:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Engine not found", 
                    f"Engine '{engine_name}' is not registered. Available engines: {', '.join(get_available_engines())}"
                )
                return
            
            if not hou:
                QtWidgets.QMessageBox.information(
                    self, 
                    "Not available", 
                    "Houdini Python module (hou) not found. Run this inside Houdini."
                )
                return
            
            create_function = engine_info.get("create_function")
            if not create_function:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Engine error",
                    f"Engine '{engine_name}' is registered but has no create function."
                )
                return
            
            # Call the engine's create function
            try:
                print(f"DEBUG: Calling create function for engine: {engine_name}")
                print(f"DEBUG: Function: {create_function}")
                create_function(folder, matlib_node, {}, udim, position_offset=(0.0, 0.0))
                display_name = engine_info.get("display_name", engine_name.title())
                QtWidgets.QMessageBox.information(
                    self, 
                    "Done", 
                    f"{display_name} materials created successfully."
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to create materials:\n{str(e)}")
                import traceback
                print(f"DEBUG: Exception traceback:\n{traceback.format_exc()}")
        finally:
            # Re-enable button and reset flag
            self._is_creating = False
            self.create_btn.setEnabled(True)
            self.create_btn.setText("Create Materials")


def show_material_loader(parent: Optional[QtWidgets.QWidget] = None):
    """Create and show the SimpleMaterialLoader window. Returns the widget instance."""
    app = QtWidgets.QApplication.instance()
    owns_app = False
    if app is None:
        app = QtWidgets.QApplication([])
        owns_app = True

    win = SimpleMaterialLoader(parent)
    win.show()

    # Keep a global reference to avoid premature GC in host environments
    try:
        global _material_loader_window
        _material_loader_window = win
    except Exception:
        pass

    # Enter event loop only if we created the application (script mode)
    if owns_app:
        app.exec()
    return win


if __name__ == '__main__':
    show_material_loader()
