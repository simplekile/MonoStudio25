"""
New Folder Dialog - Custom UI for creating asset/shot folders
Compatible with Houdini 21+ (PySide6)
"""

from mono_tools.qt import QtCore, QtGui, QtWidgets
import os


class NewFolderDialog(QtWidgets.QDialog):
    """Custom dialog for creating asset or shot folder structure"""
    
    def __init__(self, parent=None, all_types=None, asset_types=None):
        super().__init__(parent)
        
        self.all_types = all_types or []
        self.asset_types = asset_types or []
        
        self.setWindowTitle("Create New Folder")
        self.setMinimumWidth(550)
        self.setMinimumHeight(600)
        self.setModal(True)
        
        self._setup_ui()
        self._apply_style()
        self._update_form_visibility()
    
    def _setup_ui(self):
        """Setup UI elements"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QtWidgets.QLabel("Create New Folder")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e5e5e5;")
        layout.addWidget(title_label)
        
        # Folder type selection (Radio buttons)
        type_group = QtWidgets.QGroupBox("Folder Type")
        type_layout = QtWidgets.QHBoxLayout()
        type_layout.setSpacing(20)
        
        self.asset_radio = QtWidgets.QRadioButton("🎨 Asset Folder")
        self.shot_radio = QtWidgets.QRadioButton("🎬 Shot Folder")
        self.asset_radio.setChecked(True)  # Default
        
        type_layout.addWidget(self.asset_radio)
        type_layout.addWidget(self.shot_radio)
        type_layout.addStretch()
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Connect radio buttons
        self.asset_radio.toggled.connect(self._update_form_visibility)
        
        # Asset form (conditional)
        self.asset_form = QtWidgets.QWidget()
        asset_layout = QtWidgets.QFormLayout(self.asset_form)
        asset_layout.setSpacing(12)
        asset_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        self.asset_type_combo = QtWidgets.QComboBox()
        self.asset_type_combo.setMinimumWidth(350)
        self.asset_type_combo.currentIndexChanged.connect(self._update_preview)
        asset_layout.addRow("Asset Type:", self.asset_type_combo)
        
        self.asset_name_edit = QtWidgets.QLineEdit()
        self.asset_name_edit.setMinimumWidth(350)
        self.asset_name_edit.setPlaceholderText("e.g., Hero, Table, Tree")
        self.asset_name_edit.textChanged.connect(self._update_preview)
        asset_layout.addRow("Asset Name:", self.asset_name_edit)
        
        layout.addWidget(self.asset_form)
        
        # Shot form (conditional)
        self.shot_form = QtWidgets.QWidget()
        shot_layout = QtWidgets.QFormLayout(self.shot_form)
        shot_layout.setSpacing(12)
        shot_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        self.shot_name_edit = QtWidgets.QLineEdit()
        self.shot_name_edit.setMinimumWidth(350)
        self.shot_name_edit.setPlaceholderText("e.g., sq010_sh0010")
        self.shot_name_edit.textChanged.connect(self._update_preview)
        shot_hint = QtWidgets.QLabel("Format: sq###_sh#### (Sequence + Shot number)")
        shot_hint.setStyleSheet("font-size: 10px; color: #666;")
        shot_name_layout = QtWidgets.QVBoxLayout()
        shot_name_layout.setSpacing(4)
        shot_name_layout.addWidget(self.shot_name_edit)
        shot_name_layout.addWidget(shot_hint)
        shot_layout.addRow("Shot Name:", shot_name_layout)
        
        layout.addWidget(self.shot_form)
        
        # Preview section
        layout.addSpacing(8)
        preview_label = QtWidgets.QLabel("Folder Structure Preview:")
        preview_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #e5e5e5;")
        layout.addWidget(preview_label)
        
        self.preview_text = QtWidgets.QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(350)
        self.preview_text.setMaximumHeight(400)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: #aaa;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.preview_text)
        
        # Folder count
        self.folder_count_label = QtWidgets.QLabel()
        self.folder_count_label.setStyleSheet("font-size: 11px; color: #999;")
        layout.addWidget(self.folder_count_label)
        
        # Buttons
        layout.addSpacing(8)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        
        self.create_btn = QtWidgets.QPushButton("Create Folder")
        self.create_btn.setMinimumWidth(140)
        self.create_btn.setDefault(True)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.create_btn)
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self._on_create)
        
        # Populate data
        self._populate_types()
        self._update_preview()
    
    def _apply_style(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QDialog {
                background: #2b2b2b;
            }
            QLabel {
                color: #e5e5e5;
            }
            QGroupBox {
                color: #e5e5e5;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QRadioButton {
                color: #e5e5e5;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #4a4a4a;
                background: #1e1e1e;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #3d5a99;
                background: #3d5a99;
            }
            QRadioButton::indicator:checked::after {
                content: '';
                width: 8px;
                height: 8px;
                border-radius: 4px;
                background: white;
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
    
    def _populate_types(self):
        """Populate asset type dropdown with scanned types"""
        # Only populate with asset types (exclude Shots)
        if self.all_types:
            for type_name, is_assets in self.all_types:
                if is_assets:  # Only asset types
                    # Get icon from config
                    icon = '📁'
                    display_name = type_name
                    
                    if self.asset_types:
                        for atype in self.asset_types:
                            if atype['id'] == type_name:
                                icon = atype.get('icon', '📁')
                                display_name = atype.get('name', type_name)
                                break
                    
                    self.asset_type_combo.addItem(f"{icon} {display_name}", type_name)
    
    def _update_form_visibility(self):
        """Show/hide forms based on folder type selection"""
        is_asset = self.asset_radio.isChecked()
        
        self.asset_form.setVisible(is_asset)
        self.shot_form.setVisible(not is_asset)
        
        # Update preview
        self._update_preview()
    
    def _update_preview(self):
        """Update folder structure preview"""
        is_asset = self.asset_radio.isChecked()
        
        if is_asset:
            self._update_asset_preview()
        else:
            self._update_shot_preview()
    
    def _update_asset_preview(self):
        """Update preview for asset folder"""
        asset_type = self.asset_type_combo.currentData()
        asset_name = self.asset_name_edit.text().strip()
        
        if not asset_type or not asset_name:
            self.preview_text.setPlainText("Fill all fields to see preview...")
            self.folder_count_label.setText("")
            return
        
        # Get prefix from config
        prefix = ""
        if self.asset_types:
            for atype in self.asset_types:
                if atype['id'] == asset_type:
                    prefix = atype.get('prefix', '')
                    break
        
        full_asset_name = f"{prefix}{asset_name}" if prefix else asset_name
        
        # Load department config
        from mono_tools.file_manager.file_manager_helpers import load_department_config
        config = load_department_config()
        
        preview = f"01_assets/{asset_type}/{full_asset_name}/\n"
        
        total_folders = 0
        
        if config and 'standard_departments' in config:
            departments = config['standard_departments']
            
            for i, dept in enumerate(departments):
                dept_id = dept['id']
                dept_name = dept.get('name', dept_id)
                icon = dept.get('icon', '📁')
                subdepartments = dept.get('subdepartments', [])
                create_publish = dept.get('create_publish', False)
                
                is_last_dept = (i == len(departments) - 1)
                branch = "└─" if is_last_dept else "├─"
                indent = "     " if is_last_dept else "  │  "
                
                preview += f"  {branch} {icon} {dept_id}/ ({dept_name})\n"
                total_folders += 1
                
                # Show subdepartments
                if subdepartments:
                    for j, subdept in enumerate(subdepartments):
                        subdept_id = subdept['id']
                        subdept_name = subdept.get('name', subdept_id)
                        subdept_has_publish = subdept.get('create_publish', False)
                        
                        is_last_subdept = (j == len(subdepartments) - 1) and not create_publish
                        subdept_branch = "└─" if is_last_subdept else "├─"
                        
                        preview += f"{indent}{subdept_branch} {subdept_id}/ ({subdept_name})\n"
                        total_folders += 1
                        
                        # Subdepartment publish folder
                        if subdept_has_publish:
                            pub_indent = indent + ("     " if is_last_subdept else "  │  ")
                            preview += f"{pub_indent}└─ _publish/\n"
                            total_folders += 1
                
                # Department publish folder
                if create_publish:
                    preview += f"{indent}└─ _publish/\n"
                    total_folders += 1
        
        self.preview_text.setPlainText(preview)
        self.folder_count_label.setText(f"Total: {len(departments) if config else 0} departments, {total_folders} folders")
    
    def _update_shot_preview(self):
        """Update preview for shot folder"""
        shot_name = self.shot_name_edit.text().strip()
        
        if not shot_name:
            self.preview_text.setPlainText("Enter shot name to see preview...")
            self.folder_count_label.setText("")
            return
        
        # Load shot departments config
        from mono_tools.file_manager.file_manager_helpers import load_department_config
        config = load_department_config()
        
        preview = f"02_shots/{shot_name}/\n"
        
        total_folders = 0
        
        if config and 'shot_departments' in config:
            shot_departments = config['shot_departments']
            
            for i, dept in enumerate(shot_departments):
                dept_id = dept['id']
                dept_name = dept.get('name', dept_id)
                icon = dept.get('icon', '📁')
                subdepartments = dept.get('subdepartments', [])
                create_publish = dept.get('create_publish', False)
                
                is_last_dept = (i == len(shot_departments) - 1)
                branch = "└─" if is_last_dept else "├─"
                indent = "     " if is_last_dept else "  │  "
                
                preview += f"  {branch} {icon} {dept_id}/ ({dept_name})\n"
                total_folders += 1
                
                # Show subdepartments
                if subdepartments:
                    for j, subdept in enumerate(subdepartments):
                        subdept_id = subdept['id']
                        subdept_name = subdept.get('name', subdept_id)
                        subdept_has_publish = subdept.get('create_publish', False)
                        
                        is_last_subdept = (j == len(subdepartments) - 1) and not create_publish
                        subdept_branch = "└─" if is_last_subdept else "├─"
                        
                        preview += f"{indent}{subdept_branch} {subdept_id}/ ({subdept_name})\n"
                        total_folders += 1
                        
                        # Subdepartment publish folder
                        if subdept_has_publish:
                            pub_indent = indent + ("     " if is_last_subdept else "  │  ")
                            preview += f"{pub_indent}└─ _publish/\n"
                            total_folders += 1
                
                # Department publish folder
                if create_publish:
                    preview += f"{indent}└─ _publish/\n"
                    total_folders += 1
        
        self.preview_text.setPlainText(preview)
        self.folder_count_label.setText(f"Total: {len(shot_departments) if config else 0} departments, {total_folders} folders")
    
    def _on_create(self):
        """Validate and accept"""
        is_asset = self.asset_radio.isChecked()
        
        if is_asset:
            # Validate asset fields
            if not self.asset_type_combo.currentData():
                QtWidgets.QMessageBox.warning(self, "New Folder", "Please select asset type")
                return
            
            asset_name = self.asset_name_edit.text().strip()
            if not asset_name:
                QtWidgets.QMessageBox.warning(self, "New Folder", "Please enter asset name")
                return
        else:
            # Validate shot fields
            shot_name = self.shot_name_edit.text().strip()
            if not shot_name:
                QtWidgets.QMessageBox.warning(self, "New Folder", "Please enter shot name")
                return
            
            # Validate shot name format
            if '_' not in shot_name:
                result = QtWidgets.QMessageBox.question(
                    self, 
                    "New Folder",
                    "Shot name should follow format: sq###_sh####\n\nContinue anyway?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                if result != QtWidgets.QMessageBox.Yes:
                    return
        
        # All valid - accept
        self.accept()
    
    def get_values(self):
        """Get all values from dialog"""
        is_asset = self.asset_radio.isChecked()
        
        if is_asset:
            return {
                'is_asset': True,
                'asset_type': self.asset_type_combo.currentData(),
                'asset_name': self.asset_name_edit.text().strip(),
                'shot_name': None
            }
        else:
            return {
                'is_asset': False,
                'asset_type': None,
                'asset_name': None,
                'shot_name': self.shot_name_edit.text().strip()
            }

