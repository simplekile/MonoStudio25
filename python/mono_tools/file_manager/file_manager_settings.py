"""
Mono File Manager Settings Dialog
Professional settings dialog with tabbed preview for minibar configuration
"""

import os
import json
from datetime import datetime
from mono_tools.qt import QtCore, QtGui, QtWidgets
import hou
from .file_manager_helpers import (
    scan_project_types, 
    scan_departments_for_type, 
    collect_files_with_filters,
    human_size,
    open_in_explorer,
    list_projects,
    load_department_config,
    save_department_config,
    ORG, APP
)

class SmartLineEdit(QtWidgets.QLineEdit):
    """LineEdit with Chrome-style inline autocomplete suggestions"""
    
    def __init__(self, suggestions_dict=None, parent=None):
        super().__init__(parent)
        self.suggestions_dict = suggestions_dict or {}
        self.current_suggestion = ""
        
    def keyPressEvent(self, event):
        """Handle Tab key to accept suggestion"""
        if event.key() == QtCore.Qt.Key_Tab and self.current_suggestion:
            # Accept suggestion
            self.setText(self.current_suggestion)
            self.current_suggestion = ""
            self.update()
            event.accept()
            # Move to next field
            self.focusNextChild()
            return
        
        super().keyPressEvent(event)
        self._update_suggestion()
    
    def _update_suggestion(self):
        """Find matching suggestion based on typed text"""
        text = self.text().lower().strip()
        
        if not text:
            self.current_suggestion = ""
            self.update()
            return
        
        # Find best match from suggestions
        for key, value in self.suggestions_dict.items():
            if key.startswith(text):
                self.current_suggestion = value
                self.update()
                return
        
        # No match found
        self.current_suggestion = ""
        self.update()
    
    def paintEvent(self, event):
        """Custom paint to show gray suggestion text"""
        super().paintEvent(event)
        
        # Draw suggestion in gray after typed text
        if self.current_suggestion and self.text():
            typed = self.text()
            
            # Check if suggestion matches typed text
            if self.current_suggestion.lower().startswith(typed.lower()):
                painter = QtGui.QPainter(self)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                
                # Calculate position
                fm = self.fontMetrics()
                typed_width = fm.horizontalAdvance(typed)
                
                # Get suggestion part (what's not typed yet)
                suggestion_part = self.current_suggestion[len(typed):]
                
                # Draw gray text
                painter.setPen(QtGui.QColor(128, 128, 128))  # Gray
                
                # Position: after typed text with padding
                x = typed_width + 8  # 8px padding from left
                y = (self.height() + fm.ascent() - fm.descent()) // 2
                
                painter.drawText(x, y, suggestion_part)
                painter.end()

class AssetTypeDialog(QtWidgets.QDialog):
    """Custom dialog for adding/editing asset types - File Manager style"""
    
    def __init__(self, parent=None, mode="add", current_data=None):
        super().__init__(parent)
        self.mode = mode
        self.current_data = current_data
        
        self.setWindowTitle("Add Asset Type" if mode == "add" else "Edit Asset Type")
        self.setMinimumSize(400, 300)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        
        self._build_ui()
        self._apply_styling()
        
        if mode == "edit" and current_data:
            self._load_current_data()
    
    def _build_ui(self):
        """Build the dialog UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QtWidgets.QLabel("Asset Type Configuration")
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Input fields
        fields_layout = QtWidgets.QFormLayout()
        fields_layout.setSpacing(10)
        
        # Load asset type suggestions from external file
        suggestions = self._load_asset_type_suggestions()
        
        # Smart folder name input with autocomplete
        self.folder_edit = SmartLineEdit(suggestions, self)
        self.folder_edit.setPlaceholderText("Type: char, prop, env...")
        self.folder_edit.textChanged.connect(self._on_folder_changed)
        fields_layout.addRow("📁 Folder Name:", self.folder_edit)
        
        # Hint for Tab key
        hint = QtWidgets.QLabel("💡 Press Tab to accept suggestion")
        hint.setStyleSheet("QLabel { color: #888; font-size: 9pt; font-style: italic; margin-left: 20px; }")
        fields_layout.addRow("", hint)
        
        # Prefix (auto-generated, but editable)
        self.prefix_edit = QtWidgets.QLineEdit()
        self.prefix_edit.setPlaceholderText("Auto-generated from folder")
        self.prefix_edit.textChanged.connect(self._update_preview)
        fields_layout.addRow("🔤 Prefix:", self.prefix_edit)
        
        layout.addLayout(fields_layout)
        
        # Preview
        preview_group = QtWidgets.QGroupBox("Preview")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        
        self.preview_label = QtWidgets.QLabel("Folder: _vehicles\nDisplay: Vehicles\nPrefix: veh_")
        self.preview_label.setStyleSheet("""
            QLabel {
                background: #1e1e1e;
                color: #ddd;
                padding: 10px;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QtWidgets.QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _apply_styling(self):
        """Apply File Manager style"""
        self.setStyleSheet("""
            QDialog {
                background: #2a2a2a;
                color: #e5e5e5;
            }
            QLineEdit {
                background: #1e1e1e;
                border: 2px solid #555;
                border-radius: 4px;
                padding: 8px;
                color: #e5e5e5;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #106ebe;
            }
            QPushButton:pressed {
                background: #005a9e;
            }
            QPushButton#cancel_btn {
                background: #6c757d;
            }
            QPushButton#cancel_btn:hover {
                background: #5a6268;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        self.cancel_btn.setObjectName("cancel_btn")
    
    def _load_asset_type_suggestions(self):
        """Load asset type suggestions from external JSON file"""
        try:
            # Get the directory of this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            suggestions_file = os.path.join(current_dir, 'asset_type_suggestions.json')
            
            if os.path.exists(suggestions_file):
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('asset_type_suggestions', {})
            else:
                # Fallback to default suggestions
                return {
                    'char': '_characters',
                    'prop': '_props',
                    'env': '_environments',
                    'veh': '_vehicles',
                    'weap': '_weapons',
                    'fx': '_fx'
                }
        except Exception as e:
            print(f"Error loading asset type suggestions: {e}")
            return {}
    
    def _load_prefix_mapping(self):
        """Load prefix mapping from external JSON file"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            suggestions_file = os.path.join(current_dir, 'asset_type_suggestions.json')
            
            if os.path.exists(suggestions_file):
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('prefix_mapping', {})
            else:
                # Fallback to default mapping
                return {
                    '_characters': 'char_',
                    '_props': 'prop_',
                    '_environments': 'env_',
                    '_vehicles': 'veh_',
                    '_weapons': 'weap_',
                    '_fx': 'fx_'
                }
        except Exception as e:
            print(f"Error loading prefix mapping: {e}")
            return {}
    
    def _load_display_name_mapping(self):
        """Load display name mapping from external JSON file"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            suggestions_file = os.path.join(current_dir, 'asset_type_suggestions.json')
            
            if os.path.exists(suggestions_file):
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('display_name_mapping', {})
            else:
                # Fallback to default mapping
                return {
                    '_characters': 'Character',
                    '_props': 'Prop',
                    '_environments': 'Environment',
                    '_vehicles': 'Vehicle',
                    '_weapons': 'Weapon',
                    '_fx': 'FX'
                }
        except Exception as e:
            print(f"Error loading display name mapping: {e}")
            return {}
    
    def _on_folder_changed(self, text):
        """Auto-generate prefix from folder name"""
        if not text.strip():
            self.prefix_edit.clear()
            self._update_preview()
            return
        
        # Use suggestion if available, otherwise use typed text
        folder = self.folder_edit.current_suggestion if self.folder_edit.current_suggestion else text.strip()
        
        # Load prefix mapping from external file
        prefix_mapping = self._load_prefix_mapping()
        prefix = prefix_mapping.get(folder, folder.replace('_', '') + '_')
        
        self.prefix_edit.setText(prefix)
        self._update_preview()
    
    def _update_preview(self):
        """Update preview with folder structure and example"""
        folder = self.folder_edit.current_suggestion or self.folder_edit.text() or "_characters"
        prefix = self.prefix_edit.text() or "char_"
        
        preview = f"Folder: 01_assets/{folder}/\n"
        preview += f"Prefix: {prefix}\n"
        preview += f"Example: {prefix}Hero_v001.hip"
        
        self.preview_label.setText(preview)
    
    def _load_current_data(self):
        """Load current data for editing"""
        if self.current_data:
            self.folder_edit.setText(self.current_data.get('id', ''))
            self.prefix_edit.setText(self.current_data.get('prefix', ''))
            self._update_preview()
    
    def get_values(self):
        """Get the entered values (folder_id, prefix only)"""
        return (
            self.folder_edit.text().strip(),
            self.prefix_edit.text().strip()
        )

class CustomTemplateDialog(QtWidgets.QDialog):
    """Dialog for editing custom template structure"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Template")
        self.setMinimumSize(700, 600)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Description
        desc = QtWidgets.QLabel(
            "Advanced editor - Add/Edit/Remove departments and configure software folders."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("QLabel { color: #aaa; padding: 8px; background: #2a2a2a; border-radius: 4px; }")
        layout.addWidget(desc)
        
        # Department list
        dept_group = QtWidgets.QGroupBox("Departments")
        dept_layout = QtWidgets.QVBoxLayout(dept_group)
        
        self.dept_list = QtWidgets.QListWidget()
        dept_layout.addWidget(self.dept_list)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        add_btn = QtWidgets.QPushButton("➕ Add")
        add_btn.clicked.connect(self._add_department)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QtWidgets.QPushButton("✏️ Edit")
        edit_btn.clicked.connect(self._edit_department)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QtWidgets.QPushButton("🗑️ Remove")
        remove_btn.clicked.connect(self._remove_department)
        btn_layout.addWidget(remove_btn)
        
        btn_layout.addStretch()
        
        move_up_btn = QtWidgets.QPushButton("⬆️ Up")
        move_up_btn.clicked.connect(self._move_up)
        btn_layout.addWidget(move_up_btn)
        
        move_down_btn = QtWidgets.QPushButton("⬇️ Down")
        move_down_btn.clicked.connect(self._move_down)
        btn_layout.addWidget(move_down_btn)
        
        dept_layout.addLayout(btn_layout)
        layout.addWidget(dept_group)
        
        # Dialog buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._save_and_close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Load current config
        self._load_departments()
    
    def _load_departments(self):
        """Load departments from config"""
        self.dept_list.clear()
        config = load_department_config()
        if config and 'standard_departments' in config:
            for dept in config['standard_departments']:
                item = QtWidgets.QListWidgetItem(f"{dept.get('icon', '📁')} {dept['id']} - {dept['name']}")
                item.setData(QtCore.Qt.UserRole, dept)
                self.dept_list.addItem(item)
    
    def _add_department(self):
        """Add new department"""
        hou.ui.displayMessage("Add department feature - to be implemented", title="Coming Soon")
    
    def _edit_department(self):
        """Edit selected department"""
        hou.ui.displayMessage("Edit department feature - to be implemented", title="Coming Soon")
    
    def _remove_department(self):
        """Remove selected department"""
        current_row = self.dept_list.currentRow()
        if current_row >= 0:
            self.dept_list.takeItem(current_row)
    
    def _move_up(self):
        """Move department up"""
        current_row = self.dept_list.currentRow()
        if current_row > 0:
            item = self.dept_list.takeItem(current_row)
            self.dept_list.insertItem(current_row - 1, item)
            self.dept_list.setCurrentRow(current_row - 1)
    
    def _move_down(self):
        """Move department down"""
        current_row = self.dept_list.currentRow()
        if current_row < self.dept_list.count() - 1 and current_row >= 0:
            item = self.dept_list.takeItem(current_row)
            self.dept_list.insertItem(current_row + 1, item)
            self.dept_list.setCurrentRow(current_row + 1)
    
    def _save_and_close(self):
        """Save configuration and close"""
        departments = []
        for i in range(self.dept_list.count()):
            item = self.dept_list.item(i)
            dept = item.data(QtCore.Qt.UserRole)
            departments.append(dept)
        
        config = {
            "standard_departments": departments,
            "version": "2.0",
            "last_modified": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Also preserve asset_types if exists
        current_config = load_department_config()
        if current_config and 'asset_types' in current_config:
            config['asset_types'] = current_config['asset_types']
        
        success, message = save_department_config(config)
        if success:
            hou.ui.displayMessage("Template saved!", severity=hou.severityType.Message)
            self.accept()
        else:
            hou.ui.displayMessage(f"Save failed:\n{message}", severity=hou.severityType.Error)

class FileTableModel(QtGui.QStandardItemModel):
    """Table model for file preview (working files only)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels([
            "Asset/Shot", "Ver", "File Name", "Department", "Modified", "Size"
        ])
        self.files_data = []  # Store file data for reference
    
    def populate_files(self, files_data, is_assets=True):
        """Populate model with file data"""
        self.clear()
        self.setHorizontalHeaderLabels([
            "Asset/Shot", "Ver", "File Name", "Department", "Modified", "Size"
        ])
        self.files_data = files_data
        
        for filepath, asset_name, dept_name, file_info in files_data:
            # Asset/Shot column
            asset_item = QtGui.QStandardItem(asset_name or "Unknown")
            asset_item.setData(filepath, QtCore.Qt.UserRole + 1)  # File path
            
            # Version column
            ver_item = QtGui.QStandardItem(file_info.get('version', ''))
            
            # File name column
            filename_item = QtGui.QStandardItem(file_info.get('filename', ''))
            
            # Department column
            dept_item = QtGui.QStandardItem(dept_name or "Unknown")
            
            # Modified column
            modified_time = datetime.fromtimestamp(file_info.get('modified', 0))
            modified_item = QtGui.QStandardItem(modified_time.strftime("%Y-%m-%d %H:%M"))
            
            # Size column
            size_item = QtGui.QStandardItem(human_size(file_info.get('size', 0)))
            
            # Add row
            self.appendRow([
                asset_item, ver_item, filename_item, 
                dept_item, modified_item, size_item
            ])
    
    def get_file_data(self, row):
        """Get file data for a specific row"""
        if 0 <= row < len(self.files_data):
            return self.files_data[row]
        return None

class MonoFileManagerSettings(QtWidgets.QDialog):
    """Settings dialog for minibar configuration"""
    
    # Signal for settings changes
    settings_changed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mono File Manager Settings")
        self.setMinimumSize(1000, 700)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        
        # Settings
        self.s = QtCore.QSettings(ORG, APP)
        self.project_types = []
        self.current_type = None
        self.current_department = None
        self.publish_mode = False
        
        self._build_ui()
        self._apply_styling()
        self._load_settings()
        
        # Load scale setting
        self._load_scale_setting()
        
        # Note: MiniBar always auto-starts (no setting needed)
        
        # Auto-scan if root is set
        if self.root_le.text().strip():
            QtCore.QTimer.singleShot(100, self._scan_project)
    
    def _build_ui(self):
        """Build the simplified UI with tabs"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Title and Version
        title_layout = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("Mono File Manager Settings")
        font = title.font()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # Version info
        try:
            from mono_tools import __version__
            self.version_label = QtWidgets.QLabel(f"v{__version__}")
            self.version_label.setStyleSheet("QLabel { color: #888; font-size: 12px; }")
            self.version_label.setToolTip(f"Mono Studio v{__version__}")
            title_layout.addWidget(self.version_label)
        except Exception as e:
            print(f"⚠️ Error loading version: {e}")
            self.version_label = QtWidgets.QLabel("v2.2.0")
            self.version_label.setStyleSheet("QLabel { color: #888; font-size: 12px; }")
            title_layout.addWidget(self.version_label)
        
        layout.addLayout(title_layout)
        
        # Main tabs (cleaner organization)
        self.main_tabs = QtWidgets.QTabWidget()
        self.main_tabs.setTabPosition(QtWidgets.QTabWidget.North)
        
        # Tab 1: Project & Files
        self.project_tab = self._build_project_tab()
        self.main_tabs.addTab(self.project_tab, "📁 Project & Files")
        
        # Tab 2: Project Structure
        self.dept_tab = self._build_department_tab()
        self.main_tabs.addTab(self.dept_tab, "🏗️ Project Structure")
        
        # Tab 3: UI Settings
        self.ui_tab = self._build_ui_settings_tab()
        self.main_tabs.addTab(self.ui_tab, "🎨 UI Settings")
        
        layout.addWidget(self.main_tabs)
        
        # Status bar
        self.status_bar = QtWidgets.QLabel("Ready")
        self.status_bar.setStyleSheet("QLabel { background: #2a2a2a; color: #e5e5e5; padding: 4px 8px; border-radius: 4px; }")
        layout.addWidget(self.status_bar)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _build_project_tab(self):
        """Build Project & Files tab"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Project settings
        project_group = QtWidgets.QGroupBox("Project Settings")
        project_layout = QtWidgets.QGridLayout(project_group)
        
        # Project root
        project_layout.addWidget(QtWidgets.QLabel("Project Root:"), 0, 0)
        self.root_le = QtWidgets.QLineEdit()
        self.root_le.setPlaceholderText("Select project root directory...")
        project_layout.addWidget(self.root_le, 0, 1)
        
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_root)
        project_layout.addWidget(browse_btn, 0, 2)
        
        # Current project
        project_layout.addWidget(QtWidgets.QLabel("Current Project:"), 1, 0)
        self.project_cb = QtWidgets.QComboBox()
        self.project_cb.setMinimumWidth(200)
        project_layout.addWidget(self.project_cb, 1, 1)
        
        # Scan button
        self.scan_btn = QtWidgets.QPushButton("Scan Project")
        self.scan_btn.clicked.connect(self._scan_project)
        project_layout.addWidget(self.scan_btn, 1, 2)
        
        layout.addWidget(project_group)
        
        # File preview tabs
        self.tabs_widget = QtWidgets.QTabWidget()
        self.tabs_widget.setTabPosition(QtWidgets.QTabWidget.North)
        layout.addWidget(self.tabs_widget)
        
        return tab
    
    def _build_department_tab(self):
        """Build Project Structure tab with template selection"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Description
        desc = QtWidgets.QLabel(
            "Configure folder structure for new assets.\n"
            "Choose a template or customize your own structure."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("QLabel { color: #aaa; padding: 8px; background: #2a2a2a; border-radius: 4px; }")
        layout.addWidget(desc)
        
        # Asset Types section
        asset_type_group = QtWidgets.QGroupBox("📦 Asset Types")
        asset_type_layout = QtWidgets.QVBoxLayout(asset_type_group)
        
        # List widget for asset types
        self.asset_type_list = QtWidgets.QListWidget()
        self.asset_type_list.setMaximumHeight(120)
        asset_type_layout.addWidget(self.asset_type_list)
        
        # Buttons for asset types
        asset_btn_layout = QtWidgets.QHBoxLayout()
        
        add_type_btn = QtWidgets.QPushButton("➕ Add Type")
        add_type_btn.clicked.connect(self._add_asset_type)
        asset_btn_layout.addWidget(add_type_btn)
        
        edit_type_btn = QtWidgets.QPushButton("✏️ Edit")
        edit_type_btn.clicked.connect(self._edit_asset_type)
        asset_btn_layout.addWidget(edit_type_btn)
        
        remove_type_btn = QtWidgets.QPushButton("🗑️ Remove")
        remove_type_btn.clicked.connect(self._remove_asset_type)
        asset_btn_layout.addWidget(remove_type_btn)
        
        asset_btn_layout.addStretch()
        
        asset_type_layout.addLayout(asset_btn_layout)
        layout.addWidget(asset_type_group)
        
        # Load asset types
        self._load_asset_types()
        
        # Template selection
        template_group = QtWidgets.QGroupBox("📋 Folder Template")
        template_layout = QtWidgets.QHBoxLayout(template_group)
        
        template_layout.addWidget(QtWidgets.QLabel("Select Template:"))
        
        self.template_combo = QtWidgets.QComboBox()
        self.template_combo.addItems([
            "Default (7 departments + publish folders)",
            "Simple (3 departments: modeling, rigging, surfacing)",
            "Custom (edit your own)"
        ])
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        template_layout.addWidget(self.template_combo, 1)
        
        customize_btn = QtWidgets.QPushButton("✏️ Customize")
        customize_btn.clicked.connect(self._customize_template)
        template_layout.addWidget(customize_btn)
        
        layout.addWidget(template_group)
        
        # Structure preview
        preview_group = QtWidgets.QGroupBox("📁 Folder Structure Preview")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        
        self.structure_preview = QtWidgets.QTextEdit()
        self.structure_preview.setReadOnly(True)
        self.structure_preview.setMaximumHeight(400)
        self.structure_preview.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #ddd;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        preview_layout.addWidget(self.structure_preview)
        
        layout.addWidget(preview_group)
        
        # Load saved template or default
        config = load_department_config()
        active_template = config.get('active_template', 0) if config else 0
        self.template_combo.setCurrentIndex(active_template)
        self._load_template_preview(active_template)
        
        layout.addStretch()
        
        # Save/Apply buttons
        action_layout = QtWidgets.QHBoxLayout()
        action_layout.addStretch()
        
        apply_btn = QtWidgets.QPushButton("💾 Apply Template")
        apply_btn.setToolTip("Save and apply selected template as default structure")
        apply_btn.clicked.connect(self._apply_template)
        action_layout.addWidget(apply_btn)
        
        layout.addLayout(action_layout)
        
        return tab
    
    def _build_ui_settings_tab(self):
        """Build UI Settings tab"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # UI Scale settings
        scale_group = QtWidgets.QGroupBox("MiniBar Scale")
        scale_layout = QtWidgets.QGridLayout(scale_group)
        
        # Scale slider
        scale_layout.addWidget(QtWidgets.QLabel("Scale:"), 0, 0)
        self.scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.scale_slider.setMinimum(50)
        self.scale_slider.setMaximum(200)
        self.scale_slider.setValue(100)
        self.scale_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.scale_slider.setTickInterval(25)
        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        scale_layout.addWidget(self.scale_slider, 0, 1)
        
        self.scale_label = QtWidgets.QLabel("100%")
        self.scale_label.setMinimumWidth(50)
        self.scale_label.setAlignment(QtCore.Qt.AlignCenter)
        scale_layout.addWidget(self.scale_label, 0, 2)
        
        # Apply/Reset buttons
        apply_btn = QtWidgets.QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_scale)
        scale_layout.addWidget(apply_btn, 0, 3)
        
        reset_btn = QtWidgets.QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_scale)
        scale_layout.addWidget(reset_btn, 0, 4)
        
        layout.addWidget(scale_group)
        layout.addStretch()
        
        return tab
    
    # ================ Asset Type Methods ================
    
    def _load_asset_types(self):
        """Load asset types from config"""
        self.asset_type_list.clear()
        
        config = load_department_config()
        if config and 'asset_types' in config:
            for atype in config['asset_types']:
                type_id = atype.get('id', '')
                type_name = atype.get('name', '')
                prefix = atype.get('prefix', '')
                icon = atype.get('icon', '📁')
                
                item = QtWidgets.QListWidgetItem(f"{icon} {type_id} → {prefix}... ({type_name})")
                item.setData(QtCore.Qt.UserRole, atype)  # Store full type data
                item.setToolTip(f"Folder: {type_id}\nPrefix: {prefix}\nName: {type_name}")
                self.asset_type_list.addItem(item)
    
    def _add_asset_type(self):
        """Add new asset type - smart autocomplete dialog"""
        dialog = AssetTypeDialog(self, mode="add")
        if dialog.exec_():
            type_id, prefix = dialog.get_values()
            
            if not type_id or not prefix:
                hou.ui.displayMessage("Folder name and prefix are required.", severity=hou.severityType.Warning)
                return
            
            # Generate display name from folder using mapping
            display_mapping = self._load_display_name_mapping()
            type_name = display_mapping.get(type_id, type_id.replace('_', '').title())
            
            # Add to config
            config = load_department_config()
            if not config:
                config = {}
            if 'asset_types' not in config:
                config['asset_types'] = []
            
            new_type = {
                "id": type_id,
                "name": type_name,
                "prefix": prefix,
                "icon": "📁",
                "description": f"{type_name} assets"
            }
            
            config['asset_types'].append(new_type)
            config['version'] = "2.0"
            config['last_modified'] = datetime.now().strftime("%Y-%m-%d")
            
            success, message = save_department_config(config)
            if success:
                self._load_asset_types()
                hou.ui.displayMessage(f"Asset type added!\n\n{type_id} → {prefix}...", severity=hou.severityType.Message)
            else:
                hou.ui.displayMessage(f"Failed to save:\n{message}", severity=hou.severityType.Error)
    
    def _edit_asset_type(self):
        """Edit selected asset type"""
        current_item = self.asset_type_list.currentItem()
        if not current_item:
            hou.ui.displayMessage("Please select an asset type to edit.", severity=hou.severityType.Warning)
            return
        
        atype = current_item.data(QtCore.Qt.UserRole)
        
        # Open edit dialog
        dialog = AssetTypeDialog(self, mode="edit", current_data=atype)
        if dialog.exec_():
            type_id, prefix = dialog.get_values()
            
            if not type_id or not prefix:
                hou.ui.displayMessage("Folder name and prefix are required.", severity=hou.severityType.Warning)
                return
            
            # Generate display name from folder using mapping
            display_mapping = self._load_display_name_mapping()
            type_name = display_mapping.get(type_id, type_id.replace('_', '').title())
            
            # Update config
            config = load_department_config()
            if config and 'asset_types' in config:
                for at in config['asset_types']:
                    if at['id'] == atype['id']:
                        at['id'] = type_id  # Allow changing folder name
                        at['name'] = type_name
                        at['prefix'] = prefix
                        break
                
                config['version'] = "2.0"
                config['last_modified'] = datetime.now().strftime("%Y-%m-%d")
                
                success, message = save_department_config(config)
                if success:
                    self._load_asset_types()
                    hou.ui.displayMessage(f"Asset type updated!", severity=hou.severityType.Message)
                else:
                    hou.ui.displayMessage(f"Failed to save:\n{message}", severity=hou.severityType.Error)
    
    def _remove_asset_type(self):
        """Remove selected asset type"""
        current_row = self.asset_type_list.currentRow()
        if current_row < 0:
            hou.ui.displayMessage("Please select an asset type to remove.", severity=hou.severityType.Warning)
            return
        
        current_item = self.asset_type_list.currentItem()
        atype = current_item.data(QtCore.Qt.UserRole)
        
        result = hou.ui.displayMessage(
            f"Remove asset type?\n\n{atype['id']} - {atype['name']}",
            buttons=("Remove", "Cancel"),
            severity=hou.severityType.Warning
        )
        
        if result == 0:
            config = load_department_config()
            if config and 'asset_types' in config:
                config['asset_types'] = [at for at in config['asset_types'] if at['id'] != atype['id']]
                config['version'] = "2.0"
                config['last_modified'] = datetime.now().strftime("%Y-%m-%d")
                
                success, message = save_department_config(config)
                if success:
                    self._load_asset_types()
                    hou.ui.displayMessage("Asset type removed!", severity=hou.severityType.Message)
                else:
                    hou.ui.displayMessage(f"Failed to save:\n{message}", severity=hou.severityType.Error)
    
    # ================ Template Methods ================
    
    def _on_template_changed(self, index):
        """Handle template selection change"""
        self._load_template_preview(index)
    
    def _load_template_preview(self, template_index):
        """Load and display template structure preview"""
        if template_index == 0:  # Default
            preview = self._get_default_template_preview()
        elif template_index == 1:  # Simple
            preview = self._get_simple_template_preview()
        else:  # Custom
            preview = self._get_custom_template_preview()
        
        self.structure_preview.setPlainText(preview)
    
    def _get_default_template_preview(self):
        """Get default template structure"""
        config = load_department_config()
        
        preview = "Example: Hero_Phoenix/\n\n"
        
        if config and 'standard_departments' in config:
            for dept in config['standard_departments']:
                dept_id = dept['id']
                dept_name = dept['name']
                icon = dept.get('icon', '📁')
                software_folders = dept.get('software_folders', [])
                create_publish = dept.get('create_publish', False)
                subdepartments = dept.get('subdepartments', [])
                
                preview += f"{icon} {dept_id}/ ({dept_name})\n"
                
                # Software subfolders
                for sw in software_folders:
                    preview += f"  ├─ {sw}/\n"
                
                # Subdepartments
                for i, subdept in enumerate(subdepartments):
                    subdept_id = subdept['id']
                    subdept_name = subdept.get('name', subdept_id)
                    subdept_publish = subdept.get('create_publish', False)
                    
                    is_last_subdept = (i == len(subdepartments) - 1) and not create_publish
                    branch = "└─" if is_last_subdept else "├─"
                    
                    if subdept_publish:
                        preview += f"  {branch} {subdept_id}/ ({subdept_name})\n"
                        preview += f"  │  └─ _publish/\n"
                    else:
                        preview += f"  {branch} {subdept_id}/ ({subdept_name})\n"
                
                # Publish folder at department level
                if create_publish:
                    preview += f"  └─ _publish/\n"
                
                preview += "\n"
        
        return preview
    
    def _get_simple_template_preview(self):
        """Get simple template structure"""
        return """Example: Hero_Phoenix/

🎨 01_modeling/ (Modeling)
  ├─ houdini/
  ├─ maya/
  ├─ zbrush/
  ├─ 01_sculpt/
  │  └─ _publish/
  ├─ 02_retopo/
  │  └─ _publish/
  ├─ 03_uv/
  └─ _publish/

🦴 02_rigging/ (Rigging)
  └─ _publish/

🎭 03_surfacing/ (Surfacing)
  ├─ houdini/
  ├─ substance/
  ├─ mari/
  ├─ 01_texture/
  └─ _publish/
"""
    
    def _get_custom_template_preview(self):
        """Get custom template structure (from saved config)"""
        return self._get_default_template_preview() + "\n[Custom configuration - click 'Customize' to edit]"
    
    def _customize_template(self):
        """Open advanced editor for custom template"""
        dialog = CustomTemplateDialog(self)
        if dialog.exec_():
            # Reload preview
            self.template_combo.setCurrentIndex(2)  # Set to Custom
            self._load_template_preview(2)
    
    def _apply_template(self):
        """Apply selected template as default structure"""
        template_index = self.template_combo.currentIndex()
        template_name = self.template_combo.currentText()
        
        # Load current config
        config = load_department_config()
        if not config:
            config = {}
        
        # Set active template
        config['active_template'] = template_index
        
        # If Simple template selected, update departments
        if template_index == 1:  # Simple
            config['standard_departments'] = [
                {
                    "id": "01_modeling",
                    "name": "Modeling",
                    "icon": "🎨",
                    "description": "Geometry and modeling work",
                    "software_folders": ["houdini", "maya", "zbrush"],
                    "create_publish": True
                },
                {
                    "id": "02_rigging",
                    "name": "Rigging",
                    "icon": "🦴",
                    "description": "Character rigging and setup",
                    "software_folders": [],
                    "create_publish": True
                },
                {
                    "id": "03_surfacing",
                    "name": "Surfacing",
                    "icon": "🎭",
                    "description": "Materials and texturing",
                    "software_folders": ["houdini", "substance", "mari"],
                    "create_publish": True
                }
            ]
        # Default and Custom keep current departments
        
        config['version'] = "2.0"
        config['last_modified'] = datetime.now().strftime("%Y-%m-%d")
        
        # Save
        success, message = save_department_config(config)
        
        if success:
            hou.ui.displayMessage(
                f"Template applied!\n\n{template_name}\n\nNew folders will use this structure.",
                severity=hou.severityType.Message,
                title="Template Saved"
            )
        else:
            hou.ui.displayMessage(
                f"Failed to save:\n{message}",
                severity=hou.severityType.Error,
                title="Save Error"
            )
    
    # ================ Department Editor Methods ================
    
    def _load_departments(self):
        """Load departments from config file"""
        self.dept_list.clear()
        
        config = load_department_config()
        if config and 'standard_departments' in config:
            for dept in config['standard_departments']:
                dept_id = dept.get('id', '')
                dept_name = dept.get('name', '')
                icon = dept.get('icon', '📁')
                desc = dept.get('description', '')
                
                item = QtWidgets.QListWidgetItem(f"{icon} {dept_id} - {dept_name}")
                item.setData(QtCore.Qt.UserRole, dept)  # Store full dept data
                item.setToolTip(desc)
                self.dept_list.addItem(item)
    
    def _add_department(self):
        """Add new department"""
        # Ask for department ID
        result = hou.ui.readInput(
            "Enter department ID (e.g., 08_cfx):",
            buttons=("Next", "Cancel"),
            title="Add Department"
        )
        
        if result[0] != 0:
            return
        
        dept_id = result[1].strip()
        if not dept_id:
            return
        
        # Ask for department name
        result = hou.ui.readInput(
            f"Department ID: {dept_id}\n\nEnter department name (e.g., CFX):",
            buttons=("Next", "Cancel"),
            title="Add Department"
        )
        
        if result[0] != 0:
            return
        
        dept_name = result[1].strip()
        if not dept_name:
            dept_name = dept_id
        
        # Ask for description
        result = hou.ui.readInput(
            f"Department: {dept_id} - {dept_name}\n\nEnter description (optional):",
            buttons=("Add", "Cancel"),
            title="Add Department"
        )
        
        if result[0] != 0:
            return
        
        description = result[1].strip()
        
        # Add to list
        new_dept = {
            "id": dept_id,
            "name": dept_name,
            "icon": "📁",
            "description": description
        }
        
        item = QtWidgets.QListWidgetItem(f"📁 {dept_id} - {dept_name}")
        item.setData(QtCore.Qt.UserRole, new_dept)
        item.setToolTip(description)
        self.dept_list.addItem(item)
    
    def _edit_department(self):
        """Edit selected department"""
        current_item = self.dept_list.currentItem()
        if not current_item:
            hou.ui.displayMessage("Please select a department to edit.", severity=hou.severityType.Warning)
            return
        
        dept = current_item.data(QtCore.Qt.UserRole)
        
        # Edit name
        result = hou.ui.readInput(
            f"Department ID: {dept['id']}\n\nEnter new name:",
            buttons=("Save", "Cancel"),
            initial_contents=dept.get('name', ''),
            title="Edit Department"
        )
        
        if result[0] != 0:
            return
        
        dept['name'] = result[1].strip()
        
        # Update display
        current_item.setText(f"{dept.get('icon', '📁')} {dept['id']} - {dept['name']}")
        current_item.setData(QtCore.Qt.UserRole, dept)
    
    def _remove_department(self):
        """Remove selected department"""
        current_row = self.dept_list.currentRow()
        if current_row < 0:
            hou.ui.displayMessage("Please select a department to remove.", severity=hou.severityType.Warning)
            return
        
        current_item = self.dept_list.currentItem()
        dept = current_item.data(QtCore.Qt.UserRole)
        
        result = hou.ui.displayMessage(
            f"Remove department?\n\n{dept['id']} - {dept['name']}",
            buttons=("Remove", "Cancel"),
            severity=hou.severityType.Warning
        )
        
        if result == 0:
            self.dept_list.takeItem(current_row)
    
    def _move_department_up(self):
        """Move selected department up in list"""
        current_row = self.dept_list.currentRow()
        if current_row > 0:
            item = self.dept_list.takeItem(current_row)
            self.dept_list.insertItem(current_row - 1, item)
            self.dept_list.setCurrentRow(current_row - 1)
    
    def _move_department_down(self):
        """Move selected department down in list"""
        current_row = self.dept_list.currentRow()
        if current_row < self.dept_list.count() - 1 and current_row >= 0:
            item = self.dept_list.takeItem(current_row)
            self.dept_list.insertItem(current_row + 1, item)
            self.dept_list.setCurrentRow(current_row + 1)
    
    def _save_department_config(self):
        """Save department configuration to file"""
        try:
            # Collect all departments from list
            departments = []
            for i in range(self.dept_list.count()):
                item = self.dept_list.item(i)
                dept = item.data(QtCore.Qt.UserRole)
                departments.append(dept)
            
            # Build config
            config = {
                "standard_departments": departments,
                "version": "1.0",
                "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to file
            success, message = save_department_config(config)
            
            if success:
                hou.ui.displayMessage(
                    f"Configuration saved!\n\n{len(departments)} departments saved.",
                    severity=hou.severityType.Message,
                    title="Save Successful"
                )
                self.status_bar.setText(f"Saved {len(departments)} departments")
            else:
                hou.ui.displayMessage(
                    message,
                    severity=hou.severityType.Error,
                    title="Save Failed"
                )
        
        except Exception as e:
            hou.ui.displayMessage(
                f"Failed to save configuration:\n{str(e)}",
                severity=hou.severityType.Error,
                title="Save Error"
            )
    
    def _reset_department_config(self):
        """Reset to default departments"""
        result = hou.ui.displayMessage(
            "Reset to default department structure?\n\nThis will reload the default 7 departments.",
            buttons=("Reset", "Cancel"),
            severity=hou.severityType.Warning
        )
        
        if result == 0:
            self._load_departments()
    
    # ================  End Department Methods ================
    
    def _apply_styling(self):
        """Apply styling to dialog"""
        self.setStyleSheet("""
            QDialog { background: #232323; color: #e5e5e5; }
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #3a3a3a; 
                border-radius: 8px; 
                margin-top: 10px; 
                padding-top: 10px; 
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
            QLineEdit, QComboBox { 
                background: #2c2c2c; 
                color: #e5e5e5; 
                border: 1px solid #3a3a3a; 
                border-radius: 6px; 
                padding: 4px 6px; 
            }
            QPushButton { 
                background: #3a3a3a; 
                color: #fff; 
                border: 1px solid #4a4a4a; 
                border-radius: 8px; 
                padding: 6px 10px; 
                min-width: 80px;
            }
            QPushButton:hover { background: #4a4a4a; }
            QTabWidget::pane { border: 1px solid #3a3a3a; background: #1e1e1e; }
            QTabBar::tab { 
                background: #2a2a2a; 
                color: #e5e5e5; 
                padding: 8px 16px; 
                margin-right: 2px; 
            }
            QTabBar::tab:selected { background: #3a3a3a; }
            QTableView { 
                background: #1e1e1e; 
                alternate-background-color: #242424; 
                gridline-color: #3a3a3a; 
                selection-background-color: #3d5a99; 
                selection-color: #fff; 
            }
            QHeaderView::section { 
                background: #2a2a2a; 
                color: #dcdcdc; 
                border: 0; 
                padding: 6px; 
            }
        """)
    
    def _browse_root(self):
        """Browse for project root directory"""
        current_path = self.root_le.text() or os.path.expanduser("~")
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Project Root", current_path
        )
        if directory:
            self.root_le.setText(directory)
            self._load_projects()
    
    def _load_projects(self):
        """Load available projects from root directory"""
        root = self.root_le.text().strip()
        if not root:
            return
        
        projects = list_projects(root)
        self.project_cb.clear()
        self.project_cb.addItems(projects)
        
        # Restore last selected project
        last_project = self.s.value("current_project", "", type=str)
        if last_project and last_project in projects:
            self.project_cb.setCurrentText(last_project)
    
    def _scan_project(self):
        """Scan project and populate tabs"""
        root = self.root_le.text().strip()
        project = self.project_cb.currentText().strip()
        
        if not root or not project:
            self.status_bar.setText("Please select project root and current project")
            return
        
        project_path = os.path.join(root, project)
        if not os.path.isdir(project_path):
            self.status_bar.setText(f"Project directory not found: {project_path}")
            return
        
        self.status_bar.setText("Scanning project...")
        QtWidgets.QApplication.processEvents()
        
        try:
            # Scan project types
            self.project_types = scan_project_types(project_path)
            
            # Clear existing tabs
            self.tabs_widget.clear()
            
            # Create tabs for each type
            for type_name, type_path, is_assets in self.project_types:
                tab_widget = self._create_type_tab(type_name, type_path, is_assets, project_path)
                self.tabs_widget.addTab(tab_widget, type_name)
            
            # Save settings
            self.s.setValue("project_root", root)
            self.s.setValue("current_project", project)
            self.s.sync()
            
            self.status_bar.setText(f"Found {len(self.project_types)} types, {sum(len(scan_departments_for_type(project_path, t[0], t[2])) for t in self.project_types)} departments")
            
        except Exception as e:
            self.status_bar.setText(f"Error scanning project: {str(e)}")
            print(f"⚠️ Error scanning project: {e}")
    
    def _create_type_tab(self, type_name, type_path, is_assets, project_path):
        """Create a tab widget for a specific type"""
        tab_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Department filter
        dept_layout = QtWidgets.QHBoxLayout()
        dept_layout.addWidget(QtWidgets.QLabel("Department:"))
        
        self.dept_cb = QtWidgets.QComboBox()
        self.dept_cb.addItem("All")
        
        # Load departments for this type
        departments = scan_departments_for_type(project_path, type_name, is_assets)
        for dept in departments:
            self.dept_cb.addItem(dept)
        
        dept_layout.addWidget(self.dept_cb)
        dept_layout.addStretch()
        
        layout.addLayout(dept_layout)
        
        # Table view
        self.table_view = QtWidgets.QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_view.doubleClicked.connect(self._on_file_double_clicked)
        
        # Set up model
        self.table_model = FileTableModel()
        self.table_view.setModel(self.table_model)
        
        # Set column widths (no thumbnail column)
        self.table_view.setColumnWidth(0, 150)  # Asset/Shot
        self.table_view.setColumnWidth(1, 60)   # Version
        self.table_view.setColumnWidth(2, 250)  # File Name
        self.table_view.setColumnWidth(3, 120)  # Department
        self.table_view.setColumnWidth(4, 120)  # Modified
        self.table_view.setColumnWidth(5, 80)   # Size
        
        layout.addWidget(self.table_view)
        
        # Statistics
        self.stats_label = QtWidgets.QLabel("No files found")
        self.stats_label.setStyleSheet("QLabel { color: #888; font-style: italic; }")
        layout.addWidget(self.stats_label)
        
        # Store references for later use
        tab_widget.type_name = type_name
        tab_widget.type_path = type_path
        tab_widget.is_assets = is_assets
        tab_widget.project_path = project_path
        tab_widget.dept_cb = self.dept_cb
        tab_widget.table_view = self.table_view
        tab_widget.table_model = self.table_model
        tab_widget.stats_label = self.stats_label
        
        # Connect department change
        self.dept_cb.currentTextChanged.connect(lambda dept: self._refresh_tab_files(tab_widget))
        
        # Initial file load
        self._refresh_tab_files(tab_widget)
        
        return tab_widget
    
    def _refresh_tab_files(self, tab_widget):
        """Refresh files for a specific tab"""
        try:
            # Get current settings
            department = tab_widget.dept_cb.currentText()
            if department == "All":
                department = None
            
            # Collect files (working files only)
            files_data = collect_files_with_filters(
                tab_widget.project_path,
                tab_widget.type_name,
                department
            )
            
            # Update table model
            tab_widget.table_model.populate_files(files_data, tab_widget.is_assets)
            
            # Update statistics
            file_count = len(files_data)
            dept_count = len(set(f[2] for f in files_data))  # Unique departments
            
            tab_widget.stats_label.setText(
                f"Working files: {file_count} scene files in {dept_count} departments"
            )
            
        except Exception as e:
            print(f"⚠️ Error refreshing tab files: {e}")
            tab_widget.stats_label.setText(f"Error loading files: {str(e)}")
    
    def _on_file_double_clicked(self, index):
        """Handle double-click on file - open in Houdini"""
        tab_widget = self.tabs_widget.currentWidget()
        if not tab_widget:
            return
        
        file_data = tab_widget.table_model.get_file_data(index.row())
        if not file_data:
            return
        
        filepath, asset_name, dept_name, file_info = file_data
        
        # Open in Houdini (all files are .hip files)
        self._open_houdini_file(filepath)
    
    def _open_houdini_file(self, filepath):
        """Open file in Houdini"""
        try:
            if not os.path.exists(filepath):
                hou.ui.displayMessage(f"File not found:\n{filepath}", 
                                     severity=hou.severityType.Warning)
                return
            
            # Check for unsaved changes
            if hou.hipFile.hasUnsavedChanges():
                choice = hou.ui.displayMessage(
                    "Current scene has unsaved changes.\nSave before opening new file?",
                    buttons=("Save & Open", "Open Without Saving", "Cancel"),
                    severity=hou.severityType.ImportantMessage,
                    default_choice=0,
                    close_choice=2
                )
                if choice == 0:  # Save & Open
                    try:
                        hou.hipFile.save()
                    except hou.OperationFailed as e:
                        hou.ui.displayMessage(f"Cannot save file:\n{str(e)}", 
                                             severity=hou.severityType.Error)
                        return
                elif choice == 2:  # Cancel
                    return
            
            # Open file
            hou.hipFile.load(filepath, suppress_save_prompt=True)
            hou.ui.setStatusMessage(f"Opened: {os.path.basename(filepath)}", 
                                   severity=hou.severityType.Message)
            
        except Exception as e:
            hou.ui.displayMessage(f"Error opening file:\n{str(e)}", 
                                 severity=hou.severityType.Error)
    
    def _load_scale_setting(self):
        """Load saved scale setting"""
        try:
            scale = self.s.value("minibar_ui_scale", 100, type=int)
            self.scale_slider.setValue(scale)
            self.scale_label.setText(f"{scale}%")
        except Exception as e:
            print(f"⚠️ Error loading scale setting: {e}")
    
    def _on_scale_changed(self, value):
        """Handle scale slider change"""
        self.scale_label.setText(f"{value}%")
    
    def _apply_scale(self):
        """Apply scale to MiniBar"""
        try:
            scale = self.scale_slider.value()
            print(f"🔍 Applying UI scale: {scale}%")
            
            self.s.setValue("minibar_ui_scale", scale)
            self.s.sync()
            print(f"🔍 Scale saved to settings: {scale}%")
            
            # Emit signal to update MiniBar
            self.settings_changed.emit()
            print(f"🔍 Settings changed signal emitted")
            
            hou.ui.displayMessage(
                f"UI Scale set to {scale}%.\n\nRestart MiniBar to apply changes.",
                severity=hou.severityType.Message
            )
            
        except Exception as e:
            print(f"⚠️ Error applying scale: {e}")
            import traceback
            traceback.print_exc()
            hou.ui.displayMessage(f"Error applying scale:\n{str(e)}", 
                                 severity=hou.severityType.Error)
    
    def _reset_scale(self):
        """Reset scale to 100%"""
        self.scale_slider.setValue(100)
        self.scale_label.setText("100%")
        self._apply_scale()
    
    def _load_settings(self):
        """Load saved settings"""
        # Load project root
        root = self.s.value("project_root", "", type=str)
        if root:
            self.root_le.setText(root)
            self._load_projects()
        
        # Load current project
        project = self.s.value("current_project", "", type=str)
        if project:
            self.project_cb.setCurrentText(project)
