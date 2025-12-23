"""
Create Task Dialog - Custom UI for creating new tasks
Compatible with Houdini 21+ (PySide6)
"""

from mono_tools.qt import QtCore, QtGui, QtWidgets
import os
from .styles import (
    COLOR_BG, COLOR_BG_DARK, COLOR_INPUT_BG, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_BORDER, COLOR_SELECTED, COLOR_BUTTON, COLOR_BUTTON_HOVER
)


class CreateTaskDialog(QtWidgets.QDialog):
    """Custom dialog for creating new task with auto-filled selections"""
    
    def __init__(self, parent=None, type_name=None, department=None, subdepartment=None, 
                 username=None, is_assets=True, asset_types=None, departments=None, all_types=None,
                 project_path=None):
        super().__init__(parent)
        
        self.type_name = type_name
        self.department = department
        self.subdepartment = subdepartment
        self.username = username
        self.is_assets = is_assets
        self.asset_types = asset_types or []
        self.departments = departments or []
        self.all_types = all_types or []  # All scanned types from project
        self.project_path = project_path  # For hybrid department loading
        
        self.setWindowTitle("Create Task")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self._setup_ui()
        self._apply_style()
        self._populate_fields()
    
    def _setup_ui(self):
        """Setup UI elements"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QtWidgets.QLabel("Create Task")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLOR_TEXT};")
        layout.addWidget(title_label)
        
        # Form layout
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # Type selector
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.setMinimumWidth(300)
        form_layout.addRow("Type:", self.type_combo)
        
        # Department selector
        self.dept_combo = QtWidgets.QComboBox()
        self.dept_combo.setMinimumWidth(300)
        self.dept_combo.currentIndexChanged.connect(self._on_dept_changed)
        form_layout.addRow("Department:", self.dept_combo)
        
        # Subdepartment selector (optional)
        self.subdept_combo = QtWidgets.QComboBox()
        self.subdept_combo.setMinimumWidth(300)
        self.subdept_row = form_layout.rowCount()
        form_layout.addRow("Subdepartment:", self.subdept_combo)
        
        # User workspace with checkbox
        self.user_checkbox = QtWidgets.QCheckBox("Use user workspace")
        self.user_checkbox.setChecked(False)  # Default disabled - will auto-enable if user folders found
        self.user_edit = QtWidgets.QLineEdit()
        self.user_edit.setMinimumWidth(300)
        self.user_edit.setPlaceholderText("e.g., john, mary")
        user_hint = QtWidgets.QLabel("(lowercase, auto-detected)")
        user_hint.setStyleSheet(f"font-size: 10px; color: {COLOR_TEXT_DIM};")
        user_layout = QtWidgets.QVBoxLayout()
        user_layout.setSpacing(4)
        user_checkbox_layout = QtWidgets.QHBoxLayout()
        user_checkbox_layout.addWidget(self.user_checkbox)
        user_checkbox_layout.addStretch()
        user_layout.addLayout(user_checkbox_layout)
        user_layout.addWidget(self.user_edit)
        user_layout.addWidget(user_hint)
        form_layout.addRow("User Workspace:", user_layout)
        
        # Connect checkbox to enable/disable user_edit
        self.user_checkbox.toggled.connect(self.user_edit.setEnabled)
        self.user_checkbox.toggled.connect(self._update_preview)
        
        # Asset/Shot name
        # For assets: use ComboBox to select from existing assets
        # For shots: use LineEdit
        if self.is_assets:
            self.name_combo = QtWidgets.QComboBox()
            self.name_combo.setMinimumWidth(300)
            self.name_combo.setEditable(True)  # Allow typing new asset name
            self.name_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
            self.name_combo.lineEdit().setPlaceholderText("Select or type asset name...")
            self.name_edit = None  # Not used for assets
            name_label = "Asset Name:"
        else:
            self.name_edit = QtWidgets.QLineEdit()
            self.name_edit.setMinimumWidth(300)
            self.name_edit.setPlaceholderText("e.g., Sh010, Sh020")
            self.name_combo = None  # Not used for shots
            name_label = "Shot Name:"
        
        if self.is_assets:
            form_layout.addRow(name_label, self.name_combo)
        else:
            form_layout.addRow(name_label, self.name_edit)
        
        layout.addLayout(form_layout)
        
        # Preview path
        layout.addSpacing(8)
        preview_label = QtWidgets.QLabel("File will be created at:")
        preview_label.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_DIM};")
        layout.addWidget(preview_label)
        
        self.path_preview = QtWidgets.QLabel()
        self.path_preview.setStyleSheet("""
            background: #1a1a1a; 
            color: #4a9eff; 
            border: 1px solid #3a3a3a; 
            border-radius: 4px; 
            padding: 8px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10px;
        """)
        self.path_preview.setWordWrap(True)
        layout.addWidget(self.path_preview)
        
        # Connect signals to update preview
        self.type_combo.currentIndexChanged.connect(self._update_preview)
        self.dept_combo.currentIndexChanged.connect(self._check_user_workspaces)
        self.subdept_combo.currentIndexChanged.connect(self._check_user_workspaces)
        self.dept_combo.currentIndexChanged.connect(self._update_preview)
        self.subdept_combo.currentIndexChanged.connect(self._update_preview)
        self.user_edit.textChanged.connect(self._update_preview)
        if self.is_assets:
            self.name_combo.currentTextChanged.connect(self._check_user_workspaces)
            self.name_combo.lineEdit().textChanged.connect(self._check_user_workspaces)
            self.name_combo.currentTextChanged.connect(self._update_preview)
            self.name_combo.lineEdit().textChanged.connect(self._update_preview)
        else:
            self.name_edit.textChanged.connect(self._update_preview)
        
        # Buttons
        layout.addSpacing(8)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        
        self.create_btn = QtWidgets.QPushButton("Create Task")
        self.create_btn.setMinimumWidth(120)
        self.create_btn.setDefault(True)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.create_btn)
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self._on_create)
    
    def _apply_style(self):
        """Apply consistent styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {COLOR_BG_DARK};
            }}
            QLabel {{
                color: {COLOR_TEXT};
            }}
            QComboBox {{
                background: {COLOR_INPUT_BG};
                color: {COLOR_TEXT};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 6px;
                min-height: 24px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border: 1px solid #4a4a4a;
            }}
            QComboBox:focus {{
                border: 1px solid {COLOR_SELECTED};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {COLOR_TEXT_DIM};
                margin-right: 6px;
            }}
            QLineEdit {{
                background: {COLOR_INPUT_BG};
                color: {COLOR_TEXT};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 6px;
                min-height: 24px;
                font-size: 12px;
            }}
            QLineEdit:disabled {{
                background: #252525;
                color: #666;
            }}
            QCheckBox {{
                color: {COLOR_TEXT};
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #4a4a4a;
                background: {COLOR_INPUT_BG};
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {COLOR_SELECTED};
                background: {COLOR_SELECTED};
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_SELECTED};
            }}
            QPushButton {{
                background: {COLOR_BUTTON};
                color: {COLOR_TEXT};
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background: {COLOR_BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background: {COLOR_BG};
            }}
            QPushButton:default {{
                background: {COLOR_SELECTED};
                border: 1px solid #4d6a99;
            }}
            QPushButton:default:hover {{
                background: #4d6a99;
            }}
        """)
    
    def _populate_fields(self):
        """Populate fields with auto-filled data from MiniBar"""
        # Populate type combo - show ALL types from project scan
        # This allows user to switch type in dialog
        
        if self.all_types:
            # Use scanned types from project (includes only existing types)
            for type_name, is_assets in self.all_types:
                # Get icon from asset_types config if available
                icon = '📁'
                display_name = type_name
                
                if is_assets and self.asset_types:
                    for atype in self.asset_types:
                        if atype['id'] == type_name:
                            icon = atype.get('icon', '📁')
                            display_name = atype.get('name', type_name)
                            break
                
                if not is_assets:
                    icon = '🎬'
                    display_name = type_name
                
                self.type_combo.addItem(f"{icon} {display_name}", (type_name, is_assets))
        else:
            # Fallback: use asset_types + Shots
            if self.asset_types:
                for atype in self.asset_types:
                    icon = atype.get('icon', '📁')
                    name = atype.get('name', atype['id'])
                    self.type_combo.addItem(f"{icon} {name}", (atype['id'], True))
            
            # Add Shots
            self.type_combo.addItem("🎬 Shots", ("Shots", False))
        
        # Select current type if available
        if self.type_name:
            for i in range(self.type_combo.count()):
                type_id, _ = self.type_combo.itemData(i)
                if type_id == self.type_name:
                    self.type_combo.setCurrentIndex(i)
                    break
        
        # Connect type change to update departments
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        
        # Trigger initial department load
        self._on_type_changed()
        
        # Populate user workspace
        if self.username:
            self.user_edit.setText(self.username)
        
        # Populate asset names if assets
        if self.is_assets and self.project_path and self.type_name:
            self._populate_asset_names()
        
        # Update subdepartment options based on department
        self._on_dept_changed()
        
        # Update preview
        self._update_preview()
    
    def _on_type_changed(self):
        """Update departments when type changes"""
        self.dept_combo.clear()
        
        current_type_data = self.type_combo.currentData()
        if not current_type_data:
            return
        
        type_id, is_assets = current_type_data
        
        # Get departments with metadata: scan from folders + merge with config
        from mono_tools.file_manager.file_manager_helpers import get_departments_with_metadata
        
        if self.project_path:
            # Use hybrid approach: scan from folders + merge with config
            departments = get_departments_with_metadata(self.project_path, type_id, is_assets)
            for dept in departments:
                icon = dept.get('icon', '📁')
                name = dept.get('name', dept['id'])
                dept_id = dept['id']
                self.dept_combo.addItem(f"{icon} {dept_id} - {name}", dept_id)
        else:
            # Fallback to config only if can't get project_path
            from mono_tools.file_manager.file_manager_helpers import load_department_config
            config = load_department_config()
            if config:
                if is_assets and 'standard_departments' in config:
                    for dept in config['standard_departments']:
                        icon = dept.get('icon', '📁')
                        name = dept.get('name', dept['id'])
                        dept_id = dept['id']
                        self.dept_combo.addItem(f"{icon} {dept_id} - {name}", dept_id)
                elif not is_assets and 'shot_departments' in config:
                    for dept in config['shot_departments']:
                        icon = dept.get('icon', '📁')
                        name = dept.get('name', dept['id'])
                        dept_id = dept['id']
                        self.dept_combo.addItem(f"{icon} {dept_id} - {name}", dept_id)
        
        # Try to select previously selected department if still valid
        if self.department:
            for i in range(self.dept_combo.count()):
                if self.dept_combo.itemData(i) == self.department:
                    self.dept_combo.setCurrentIndex(i)
                    break
        
        # Update subdepartments and asset names
        self._on_dept_changed()
        if is_assets and self.project_path:
            self._populate_asset_names()
        
        # Check for user workspaces
        self._check_user_workspaces()
    
    def _populate_asset_names(self):
        """Populate asset name combo from existing assets in project"""
        if not self.is_assets or not self.name_combo:
            return
        
        current_type_data = self.type_combo.currentData()
        if not current_type_data:
            return
        
        type_id, is_assets = current_type_data
        if not is_assets:
            return
        
        # Clear and populate asset names
        self.name_combo.clear()
        self.name_combo.lineEdit().clear()
        
        if self.project_path:
            from mono_tools.file_manager.file_manager_helpers import list_asset_names
            asset_names = list_asset_names(self.project_path, type_id)
            
            # Add asset names to combo (full names with prefix)
            for asset_name in asset_names:
                self.name_combo.addItem(asset_name)
    
    def _on_dept_changed(self):
        """Update subdepartment options when department changes"""
        self.subdept_combo.clear()
        self.subdept_combo.addItem("(None - Department root)", None)
        
        current_dept = self.dept_combo.currentData()
        if current_dept:
            # Get subdepartments with metadata: scan from folders + merge with config
            if self.project_path:
                current_type_data = self.type_combo.currentData()
                if current_type_data:
                    type_id, is_assets = current_type_data
                    from mono_tools.file_manager.file_manager_helpers import get_subdepartments_with_metadata
                    subdepts = get_subdepartments_with_metadata(self.project_path, type_id, current_dept, is_assets)
                    
                    if subdepts:
                        for subdept in subdepts:
                            subdept_id = subdept['id']
                            subdept_name = subdept.get('name', subdept_id)
                            self.subdept_combo.addItem(f"{subdept_id} - {subdept_name}", subdept_id)
                else:
                    # Fallback to config only
                    from mono_tools.file_manager.file_manager_helpers import get_subdepartments_for_department
                    subdepts = get_subdepartments_for_department(current_dept)
                    
                    if subdepts:
                        for subdept in subdepts:
                            subdept_id = subdept['id']
                            subdept_name = subdept.get('name', subdept_id)
                            self.subdept_combo.addItem(f"{subdept_id} - {subdept_name}", subdept_id)
            else:
                # Fallback to config only if no project_path
                from mono_tools.file_manager.file_manager_helpers import get_subdepartments_for_department
                subdepts = get_subdepartments_for_department(current_dept)
                
                if subdepts:
                    for subdept in subdepts:
                        subdept_id = subdept['id']
                        subdept_name = subdept.get('name', subdept_id)
                        self.subdept_combo.addItem(f"{subdept_id} - {subdept_name}", subdept_id)
            
            # Select current subdepartment if available
            if self.subdepartment:
                for i in range(self.subdept_combo.count()):
                    if self.subdept_combo.itemData(i) == self.subdepartment:
                        self.subdept_combo.setCurrentIndex(i)
                        break
        
        self._update_preview()
        self._check_user_workspaces()
    
    def _check_user_workspaces(self):
        """Check for user workspace folders and auto-enable checkbox if found"""
        if not self.project_path:
            return
        
        # Get current values
        type_data = self.type_combo.currentData()
        if not type_data:
            return
        
        type_id, is_assets = type_data
        dept_id = self.dept_combo.currentData()
        subdept_id = self.subdept_combo.currentData()
        
        # For assets, need asset name
        if is_assets:
            if not self.name_combo:
                return
            asset_name = self.name_combo.currentText().strip() or self.name_combo.lineEdit().text().strip()
            if not asset_name:
                # No asset name yet - disable checkbox
                self.user_checkbox.setChecked(False)
                self.user_edit.clear()
                return
        else:
            # For shots, asset_name is not needed
            asset_name = None
        
        if not dept_id:
            # No department selected - disable checkbox
            self.user_checkbox.setChecked(False)
            self.user_edit.clear()
            return
        
        # Scan for user workspaces
        from mono_tools.file_manager.file_manager_helpers import scan_user_workspaces_in_path
        user_folders = scan_user_workspaces_in_path(
            self.project_path, type_id, asset_name, dept_id, subdept_id, is_assets
        )
        
        if user_folders:
            # Found user folders - auto-enable checkbox
            self.user_checkbox.setChecked(True)
            
            # If username was already set, keep it if it's still valid
            current_username = self.user_edit.text().strip()
            if current_username and current_username in user_folders:
                # Keep current username
                return
            
            # Auto-fill with first user folder found (or current username if provided)
            if self.username and self.username in user_folders:
                self.user_edit.setText(self.username)
            elif user_folders:
                # Use first user folder
                self.user_edit.setText(user_folders[0])
        else:
            # No user folders found - disable checkbox
            self.user_checkbox.setChecked(False)
            # Don't clear username if user manually typed it
    
    def _update_preview(self):
        """Update file path preview"""
        # Get current values
        type_data = self.type_combo.currentData()
        dept_id = self.dept_combo.currentData()
        subdept_id = self.subdept_combo.currentData()
        
        # Get username only if checkbox is checked
        username = None
        if self.user_checkbox.isChecked():
            username = self.user_edit.text().strip()
        
        # Get name from combo or edit
        if self.is_assets and self.name_combo:
            name = self.name_combo.currentText().strip() or self.name_combo.lineEdit().text().strip()
        elif not self.is_assets and self.name_edit:
            name = self.name_edit.text().strip()
        else:
            name = ""
        
        if not type_data or not dept_id or not name:
            self.path_preview.setText("Fill all fields to see preview...")
            return
        
        # If user workspace is enabled but username is empty, still show preview
        # (will be validated in _on_create)
        
        # Extract type info
        type_id, is_assets = type_data
        
        # Use centralized helpers
        from mono_tools.file_manager.file_manager_helpers import (
            ensure_asset_name_has_prefix,
            build_file_preview_path,
            generate_new_filename
        )
        
        if is_assets:
            # Ensure prefix
            asset_name = ensure_asset_name_has_prefix(type_id, name)
        else:
            asset_name = name
        
        # Generate filename (use subdepartment name if provided)
        filename = generate_new_filename(type_id, asset_name, dept_id, "v001", ".hip", subdept_id)
        
        # Build preview path using centralized helper
        preview_path = build_file_preview_path(
            type_id, asset_name, dept_id, subdept_id, username, is_assets, filename
        )
        
        self.path_preview.setText(preview_path)
    
    def _on_create(self):
        """Validate and accept"""
        # Validate all fields
        type_data = self.type_combo.currentData()
        if not type_data:
            QtWidgets.QMessageBox.warning(self, "Create Task", "Please select a type")
            return
        
        type_id, is_assets = type_data
        
        if not self.dept_combo.currentData():
            QtWidgets.QMessageBox.warning(self, "Create Task", "Please select a department")
            return
        
        # Validate username only if checkbox is checked
        username = None
        if self.user_checkbox.isChecked():
            username = self.user_edit.text().strip()
            if not username:
                QtWidgets.QMessageBox.warning(self, "Create Task", "Please enter username")
                return
            
            # Validate username
            from mono_tools.file_manager.file_manager_helpers import validate_username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                QtWidgets.QMessageBox.warning(self, "Create Task", f"Invalid username:\n{error_msg}")
                return
        
        # Get name from combo or edit
        if is_assets and self.name_combo:
            name = self.name_combo.currentText().strip() or self.name_combo.lineEdit().text().strip()
        elif not is_assets and self.name_edit:
            name = self.name_edit.text().strip()
        else:
            name = ""
        
        if not name:
            label = "Asset name" if is_assets else "Shot name"
            QtWidgets.QMessageBox.warning(self, "Create Task", f"Please enter {label}")
            return
        
        # All valid - accept
        self.accept()
    
    def get_values(self):
        """Get all values from dialog"""
        type_data = self.type_combo.currentData()
        type_id, is_assets = type_data if type_data else (None, True)
        
        # Get username only if checkbox is checked
        username = None
        if self.user_checkbox.isChecked():
            username = self.user_edit.text().strip().lower()
        
        # Get name from combo or edit
        if is_assets and self.name_combo:
            name = self.name_combo.currentText().strip() or self.name_combo.lineEdit().text().strip()
        elif not is_assets and self.name_edit:
            name = self.name_edit.text().strip()
        else:
            name = ""
        
        return {
            'type': type_id,
            'is_assets': is_assets,
            'department': self.dept_combo.currentData(),
            'subdepartment': self.subdept_combo.currentData(),
            'username': username,
            'name': name
        }

