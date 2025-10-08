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

# Try to import backend functions from the original module if running inside Houdini
create_usd_rs_materials_by_prefix = None
create_karma_subnet_materials_by_prefix = None
parse_texture_filename = None
hou = None
try:
    # local import to avoid failing the module when Houdini isn't present
    import Mono_MaterialLoader as backend
    create_usd_rs_materials_by_prefix = getattr(backend, 'create_usd_rs_materials_by_prefix', None)
    create_karma_subnet_materials_by_prefix = getattr(backend, 'create_karma_subnet_materials_by_prefix', None)
    parse_texture_filename = getattr(backend, 'parse_texture_filename', None)
    try:
        import hou as _hou  # Houdini Python module
        hou = _hou
    except Exception:
        hou = None
except Exception:
    # Running outside of Houdini or broken import; backend operations will be disabled.
    create_usd_rs_materials_by_prefix = None
    create_karma_subnet_materials_by_prefix = None
    parse_texture_filename = None
    hou = None


def _fallback_parse_texture_filename(filename: str):
    """Best-effort parser for common PBR texture naming.
    Returns a 5-tuple: (prefix, ttype, ext, udim, variant)
    Example supported tokens: basecolor|albedo|diffuse, roughness, metallic|metalness,
    normal, height|displacement, specular, emissive, opacity|transparency, ao.
    Detects UDIM tokens: 1001-1999 or <UDIM> in name.
    """
    name = os.path.basename(filename)
    stem, ext = os.path.splitext(name)
    lower = stem.lower()

    # UDIM detection
    udim = None
    for token in ("<udim>", "{udim}"):
        if token in lower:
            udim = token
            break
    if udim is None:
        # 4-digit UDIM near the end
        for part in lower.replace(".", "_").split("_"):
            if part.isdigit() and len(part) == 4 and part.startswith("1"):
                udim = part
                break

    # Texture type mapping
    mapping = {
        "basecolor": "basecolor",
        "albedo": "basecolor",
        "diffuse": "basecolor",
        "color": "basecolor",
        "col": "basecolor",
        "base": "basecolor",
        "roughness": "roughness",
        "rough": "roughness",
        "metallic": "metallic",
        "metalness": "metallic",
        "metal": "metallic",
        "specular": "specular",
        "spec": "specular",
        "normal": "normal",
        "nrml": "normal",
        "nrm": "normal",
        "bump": "height",
        "height": "height",
        "displacement": "height",
        "disp": "height",
        "emissive": "emissive",
        "emit": "emissive",
        "emission": "emissive",
        "opacity": "opacity",
        "alpha": "opacity",
        "transparency": "opacity",
        "trans": "opacity",
        "ao": "occlusion",
        "occlusion": "occlusion",
    }

    detected = None
    token_hit = None
    parts = lower.replace("-", "_").split("_")
    for p in parts[::-1]:  # search from rightmost token
        if p in mapping:
            detected = mapping[p]
            token_hit = p
            break
    if detected is None:
        # Try suffix patterns like _bc, _r, _m, _n, _h, _d
        suffix_map = {
            "bc": "basecolor",
            "r": "roughness",
            "rough": "roughness",
            "m": "metallic",
            "metal": "metallic",
            "n": "normal",
            "norm": "normal",
            "h": "height",
            "d": "height",
            "s": "specular",
            "e": "emissive",
            "emit": "emissive",
            "a": "opacity",
        }
        last = parts[-1]
        if last in suffix_map:
            detected = suffix_map[last]

    prefix = stem
    variant = token_hit or ""
    if detected is None:
        return None
    return (prefix, detected, ext.lstrip("."), udim or "", variant)

# If backend parser is missing, use fallback
if parse_texture_filename is None:
    parse_texture_filename = _fallback_parse_texture_filename

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
        options_row.addStretch()
        form.addRow("Options:", options_row)

        # Renderer selector using segmented buttons (modern look)
        renderer_row = QtWidgets.QHBoxLayout()
        self.renderer_group = QtWidgets.QButtonGroup(self)
        rs_btn = QtWidgets.QPushButton("Redshift")
        rs_btn.setCheckable(True)
        km_btn = QtWidgets.QPushButton("Karma")
        km_btn.setCheckable(True)
        rs_btn.setChecked(True)
        self.renderer_group.addButton(rs_btn, 0)
        self.renderer_group.addButton(km_btn, 1)
        for b in (rs_btn, km_btn):
            b.setMinimumWidth(110)
            b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        renderer_row.addWidget(rs_btn)
        renderer_row.addWidget(km_btn)
        renderer_row.addStretch()
        form.addRow("Renderer:", renderer_row)

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
        folder = self.folder_edit.text().strip()
        matlib = self.matlib_edit.text().strip()
        udim = self.udim_cb.isChecked()
        renderer_idx = self.renderer_group.checkedId()
        renderer = "Karma" if renderer_idx == 1 else "Redshift"

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

        # If backend functions are available, call them; otherwise inform the user.
        if renderer == "Redshift" and create_usd_rs_materials_by_prefix and hou:
            try:
                create_usd_rs_materials_by_prefix(folder, matlib_node, {}, udim, position_offset=(0.0, 0.0))
                QtWidgets.QMessageBox.information(self, "Done", "Redshift materials created (if running inside Houdini).")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", str(e))
        elif renderer == "Karma" and create_karma_subnet_materials_by_prefix and hou:
            try:
                create_karma_subnet_materials_by_prefix(folder, matlib_node, {}, udim, position_offset=(0.0, 0.0))
                QtWidgets.QMessageBox.information(self, "Done", "Karma materials created (if running inside Houdini).")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", str(e))
        else:
            if not hou:
                QtWidgets.QMessageBox.information(self, "Not available", "Houdini Python module (hou) not found. Run this inside Houdini.")
            elif renderer == "Redshift" and not create_usd_rs_materials_by_prefix:
                QtWidgets.QMessageBox.information(self, "Not available", "Missing backend: Mono_MaterialLoader.create_usd_rs_materials_by_prefix. Ensure the backend module is on sys.path.")
            elif renderer == "Karma" and not create_karma_subnet_materials_by_prefix:
                QtWidgets.QMessageBox.information(self, "Not available", "Missing backend: Mono_MaterialLoader.create_karma_subnet_materials_by_prefix. Ensure the backend module is on sys.path.")
            else:
                QtWidgets.QMessageBox.information(self, "Not available", "Creation functions are not available in this environment.")


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
