"""
New File Dialog - Custom UI for creating new files
Compatible with Houdini 21+ (PySide6)
"""

from mono_tools.qt import QtCore, QtGui, QtWidgets
import os


class NewFileDialog(QtWidgets.QDialog):
    """Custom dialog for creating new file with auto-filled selections"""
    
    def __init__(self, parent=None, type_name=None, department=None, subdepartment=None, 
                 username=None, is_assets=True, asset_types=None, departments=None, all_types=None):
        super().__init__(parent)
        
        self.type_name = type_name
        self.department = department
        self.subdepartment = subdepartment
        self.username = username
        self.is_assets = is_assets
        self.asset_types = asset_types or []
        self.departments = departments or []
        self.all_types = all_types or []  # All scanned types from project
        
        self.setWindowTitle("New File")
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
        title_label = QtWidgets.QLabel("Create New File")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e5e5e5;")
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
        
        # User workspace
        self.user_edit = QtWidgets.QLineEdit()
        self.user_edit.setMinimumWidth(300)
        self.user_edit.setPlaceholderText("e.g., john, mary")
        user_hint = QtWidgets.QLabel("(lowercase, auto-detected)")
        user_hint.setStyleSheet("font-size: 10px; color: #666;")
        user_layout = QtWidgets.QVBoxLayout()
        user_layout.setSpacing(4)
        user_layout.addWidget(self.user_edit)
        user_layout.addWidget(user_hint)
        form_layout.addRow("User Workspace:", user_layout)
        
        # Asset/Shot name
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setMinimumWidth(300)
        if self.is_assets:
            self.name_edit.setPlaceholderText("e.g., Hero, Table, Tree")
            name_label = "Asset Name:"
        else:
            self.name_edit.setPlaceholderText("e.g., Sh010, Sh020")
            name_label = "Shot Name:"
        form_layout.addRow(name_label, self.name_edit)
        
        layout.addLayout(form_layout)
        
        # Preview path
        layout.addSpacing(8)
        preview_label = QtWidgets.QLabel("File will be created at:")
        preview_label.setStyleSheet("font-size: 11px; color: #999;")
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
        self.dept_combo.currentIndexChanged.connect(self._update_preview)
        self.subdept_combo.currentIndexChanged.connect(self._update_preview)
        self.user_edit.textChanged.connect(self._update_preview)
        self.name_edit.textChanged.connect(self._update_preview)
        
        # Buttons
        layout.addSpacing(8)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        
        self.create_btn = QtWidgets.QPushButton("Create File")
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
        self.setStyleSheet("""
            QDialog {
                background: #2b2b2b;
            }
            QLabel {
                color: #e5e5e5;
            }
            QComboBox {
                background: #1e1e1e;
                color: #e5e5e5;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 6px;
                min-height: 24px;
            }
            QComboBox:hover {
                border: 1px solid #4a4a4a;
            }
            QComboBox:focus {
                border: 1px solid #3d5a99;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #999;
                margin-right: 6px;
            }
            QLineEdit {
                background: #1e1e1e;
                color: #e5e5e5;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 6px;
                min-height: 24px;
            }
            QLineEdit:focus {
                border: 1px solid #3d5a99;
            }
            QPushButton {
                background: #3a3a3a;
                color: #e5e5e5;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 32px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
            QPushButton:pressed {
                background: #2a2a2a;
            }
            QPushButton:default {
                background: #3d5a99;
                border: 1px solid #4d6a99;
            }
            QPushButton:default:hover {
                background: #4d6a99;
            }
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
        
        # Load appropriate departments based on type
        from mono_tools.file_manager.file_manager_helpers import load_department_config
        config = load_department_config()
        
        if config:
            if is_assets and 'standard_departments' in config:
                # Load asset departments
                for dept in config['standard_departments']:
                    icon = dept.get('icon', '📁')
                    name = dept.get('name', dept['id'])
                    dept_id = dept['id']
                    self.dept_combo.addItem(f"{icon} {dept_id} - {name}", dept_id)
            elif not is_assets and 'shot_departments' in config:
                # Load shot departments
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
        
        # Update subdepartments
        self._on_dept_changed()
    
    def _on_dept_changed(self):
        """Update subdepartment options when department changes"""
        self.subdept_combo.clear()
        self.subdept_combo.addItem("(None - Department root)", None)
        
        current_dept = self.dept_combo.currentData()
        if current_dept:
            # Get subdepartments for this department
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
    
    def _update_preview(self):
        """Update file path preview"""
        # Get current values
        type_data = self.type_combo.currentData()
        dept_id = self.dept_combo.currentData()
        subdept_id = self.subdept_combo.currentData()
        username = self.user_edit.text().strip()
        name = self.name_edit.text().strip()
        
        if not type_data or not dept_id or not username or not name:
            self.path_preview.setText("Fill all fields to see preview...")
            return
        
        # Extract type info
        type_id, is_assets = type_data
        
        # Build preview path
        if is_assets:
            # Guess prefix
            prefix = ""
            if 'character' in type_id.lower():
                prefix = "char_"
            elif 'prop' in type_id.lower():
                prefix = "prop_"
            elif 'environment' in type_id.lower():
                prefix = "env_"
            
            asset_name = f"{prefix}{name}" if prefix else name
            
            path_parts = ["01_assets", type_id, asset_name, dept_id]
            if subdept_id:
                path_parts.append(subdept_id)
            path_parts.append(username)
            
            # Generate filename
            from mono_tools.file_manager.file_manager_helpers import generate_new_filename
            filename = generate_new_filename(type_id, asset_name, dept_id, "v001", ".hip")
            path_parts.append(filename)
        else:
            # Shots
            path_parts = ["02_shots", dept_id]
            if subdept_id:
                path_parts.append(subdept_id)
            path_parts.append(username)
            
            # Generate filename for shots
            shot_name = name
            filename = f"Shots_{shot_name}_{dept_id.split('_')[-1]}_v001.hip"
            path_parts.append(filename)
        
        preview_path = os.path.join(*path_parts)
        self.path_preview.setText(preview_path)
    
    def _on_create(self):
        """Validate and accept"""
        # Validate all fields
        type_data = self.type_combo.currentData()
        if not type_data:
            QtWidgets.QMessageBox.warning(self, "New File", "Please select a type")
            return
        
        type_id, is_assets = type_data
        
        if not self.dept_combo.currentData():
            QtWidgets.QMessageBox.warning(self, "New File", "Please select a department")
            return
        
        username = self.user_edit.text().strip()
        if not username:
            QtWidgets.QMessageBox.warning(self, "New File", "Please enter username")
            return
        
        # Validate username
        from mono_tools.file_manager.file_manager_helpers import validate_username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            QtWidgets.QMessageBox.warning(self, "New File", f"Invalid username:\n{error_msg}")
            return
        
        name = self.name_edit.text().strip()
        if not name:
            label = "Asset name" if is_assets else "Shot name"
            QtWidgets.QMessageBox.warning(self, "New File", f"Please enter {label}")
            return
        
        # All valid - accept
        self.accept()
    
    def get_values(self):
        """Get all values from dialog"""
        type_data = self.type_combo.currentData()
        type_id, is_assets = type_data if type_data else (None, True)
        
        return {
            'type': type_id,
            'is_assets': is_assets,
            'department': self.dept_combo.currentData(),
            'subdepartment': self.subdept_combo.currentData(),
            'username': self.user_edit.text().strip().lower(),
            'name': self.name_edit.text().strip()
        }

