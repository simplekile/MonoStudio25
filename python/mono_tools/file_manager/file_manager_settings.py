"""
Mono File Manager Settings Dialog
Professional settings dialog with tabbed preview for minibar configuration
"""

import os
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
        """Build Department Structure editor tab"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Description
        desc = QtWidgets.QLabel(
            "Configure standard department folders for new assets.\n"
            "These folders will be created automatically when using 'New Folder' feature."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("QLabel { color: #aaa; padding: 8px; background: #2a2a2a; border-radius: 4px; }")
        layout.addWidget(desc)
        
        # Department list
        dept_group = QtWidgets.QGroupBox("Standard Departments")
        dept_layout = QtWidgets.QVBoxLayout(dept_group)
        
        # List widget
        self.dept_list = QtWidgets.QListWidget()
        self.dept_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        dept_layout.addWidget(self.dept_list)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        add_btn = QtWidgets.QPushButton("➕ Add Department")
        add_btn.clicked.connect(self._add_department)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QtWidgets.QPushButton("✏️ Edit")
        edit_btn.clicked.connect(self._edit_department)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QtWidgets.QPushButton("🗑️ Remove")
        remove_btn.clicked.connect(self._remove_department)
        btn_layout.addWidget(remove_btn)
        
        btn_layout.addStretch()
        
        move_up_btn = QtWidgets.QPushButton("⬆️ Move Up")
        move_up_btn.clicked.connect(self._move_department_up)
        btn_layout.addWidget(move_up_btn)
        
        move_down_btn = QtWidgets.QPushButton("⬇️ Move Down")
        move_down_btn.clicked.connect(self._move_department_down)
        btn_layout.addWidget(move_down_btn)
        
        dept_layout.addLayout(btn_layout)
        layout.addWidget(dept_group)
        
        # Actions
        action_layout = QtWidgets.QHBoxLayout()
        action_layout.addStretch()
        
        save_btn = QtWidgets.QPushButton("💾 Save Configuration")
        save_btn.clicked.connect(self._save_department_config)
        action_layout.addWidget(save_btn)
        
        reset_btn = QtWidgets.QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_department_config)
        action_layout.addWidget(reset_btn)
        
        layout.addLayout(action_layout)
        
        # Load departments
        self._load_departments()
        
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
