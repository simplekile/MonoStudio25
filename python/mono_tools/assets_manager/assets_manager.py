"""
Assets Manager - Main Dialog

Main window for browsing and managing published assets.

Phase 2: Basic UI implementation
Compatible with Houdini 21+ (PySide6)
"""

import os
from typing import Optional, List, Dict

# Import Qt (use project's Qt wrapper or PySide6 directly)
try:
    from ..qt import QtCore, QtGui, QtWidgets
except (ImportError, ValueError):  # ValueError for relative import in non-package
    try:
        from mono_tools.qt import QtCore, QtGui, QtWidgets
    except ImportError:
        from PySide6 import QtCore, QtGui, QtWidgets

# Import core modules (Phase 1)
try:
    from .assets_manager_database import AssetDatabase
    from .assets_manager_scanner import AssetScanner
    from .assets_manager_metadata import MetadataManager
except (ImportError, ValueError):  # ValueError for relative import in non-package
    # Try absolute imports
    try:
        from mono_tools.assets_manager.assets_manager_database import AssetDatabase
        from mono_tools.assets_manager.assets_manager_scanner import AssetScanner
        from mono_tools.assets_manager.assets_manager_metadata import MetadataManager
    except ImportError:
        # Direct module imports (when loaded via importlib)
        import sys
        if 'assets_manager_database' in sys.modules:
            AssetDatabase = sys.modules['assets_manager_database'].AssetDatabase
        if 'assets_manager_scanner' in sys.modules:
            AssetScanner = sys.modules['assets_manager_scanner'].AssetScanner
        if 'assets_manager_metadata' in sys.modules:
            MetadataManager = sys.modules['assets_manager_metadata'].MetadataManager

# Debug flag
DEBUG = os.environ.get('MONO_DEBUG', '0').lower() in ('1', 'true', 'yes')

def debug_print(*args, **kwargs):
    """Print only if DEBUG mode is enabled"""
    if DEBUG:
        print(*args, **kwargs)


class MonoAssetsManager(QtWidgets.QDialog):
    """
    Main Assets Manager dialog
    
    Features (Phase 2):
    - Project settings
    - Asset browser (grid view)
    - Preview panel
    - Basic search
    - Filter by type/format
    """
    
    def __init__(self, parent=None):
        """
        Initialize Assets Manager dialog
        
        Args:
            parent: Parent widget (usually hou.qt.mainWindow() or None for standalone)
        """
        # Try to get Houdini main window if no parent provided
        if parent is None:
            try:
                import hou
                parent = hou.qt.mainWindow()
                debug_print("🏠 Using Houdini main window as parent")
            except ImportError:
                debug_print("🏠 Standalone mode (no Houdini)")
                pass
        
        super().__init__(parent)
        
        # Settings
        self.settings = QtCore.QSettings("Mono", "AssetsManager")
        
        # Core components (Phase 1)
        self.database = None  # Will be created when project is set
        self.scanner = None
        self.metadata_mgr = MetadataManager()
        
        # Current state
        self.current_project = None
        self.current_assets = []
        self.selected_asset = None
        
        # Setup UI
        self.setWindowTitle("Mono Assets Manager")
        self.setMinimumSize(1024, 768)
        self.setup_ui()
        self.load_settings()
        
        debug_print("✅ Assets Manager initialized")
    
    def setup_ui(self):
        """Setup user interface"""
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # 1. Toolbar section
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # 2. Search and filter section
        search_filter = self.create_search_filter_bar()
        main_layout.addWidget(search_filter)
        
        # 3. Main content: Browser + Preview (splitter)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        
        # Browser (left side)
        self.browser_widget = self.create_browser_widget()
        splitter.addWidget(self.browser_widget)
        
        # Preview panel (right side)
        self.preview_widget = self.create_preview_widget()
        splitter.addWidget(self.preview_widget)
        
        # Set splitter sizes (70% browser, 30% preview)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        
        # 4. Status bar
        self.status_bar = self.create_status_bar()
        main_layout.addWidget(self.status_bar)
        
        # Apply stylesheet
        self.apply_stylesheet()
        
        debug_print("✅ UI setup complete")
    
    def create_toolbar(self):
        """Create toolbar with project settings"""
        toolbar = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Project root
        layout.addWidget(QtWidgets.QLabel("Project Root:"))
        self.project_root_edit = QtWidgets.QLineEdit()
        self.project_root_edit.setPlaceholderText("Select project root directory...")
        layout.addWidget(self.project_root_edit, 1)
        
        self.browse_btn = QtWidgets.QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_project_root)
        layout.addWidget(self.browse_btn)
        
        # Project dropdown
        layout.addWidget(QtWidgets.QLabel("Project:"))
        self.project_combo = QtWidgets.QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        layout.addWidget(self.project_combo)
        
        # Scan button
        self.scan_btn = QtWidgets.QPushButton("Scan Project")
        self.scan_btn.clicked.connect(self.scan_project)
        self.scan_btn.setEnabled(False)
        layout.addWidget(self.scan_btn)
        
        # Refresh button
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_browser)
        self.refresh_btn.setEnabled(False)
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
        
        return toolbar
    
    def create_search_filter_bar(self):
        """Create search and filter bar"""
        search_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(search_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Search box
        layout.addWidget(QtWidgets.QLabel("🔍 Search:"))
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Type to search assets...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_edit, 1)
        
        # Type filter
        layout.addWidget(QtWidgets.QLabel("Type:"))
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItem("All Types")
        self.type_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.type_combo)
        
        # Format filter
        layout.addWidget(QtWidgets.QLabel("Format:"))
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItem("All Formats")
        self.format_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.format_combo)
        
        # View mode
        self.view_btn_group = QtWidgets.QButtonGroup()
        
        self.grid_view_btn = QtWidgets.QPushButton("Grid")
        self.grid_view_btn.setCheckable(True)
        self.grid_view_btn.setChecked(True)
        self.grid_view_btn.clicked.connect(lambda: self.set_view_mode('grid'))
        self.view_btn_group.addButton(self.grid_view_btn)
        layout.addWidget(self.grid_view_btn)
        
        self.list_view_btn = QtWidgets.QPushButton("List")
        self.list_view_btn.setCheckable(True)
        self.list_view_btn.clicked.connect(lambda: self.set_view_mode('list'))
        self.view_btn_group.addButton(self.list_view_btn)
        layout.addWidget(self.list_view_btn)
        
        return search_widget
    
    def create_browser_widget(self):
        """Create asset browser widget"""
        browser = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(browser)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget to switch between views
        self.view_stack = QtWidgets.QStackedWidget()
        
        # Placeholder (index 0)
        self.placeholder_label = QtWidgets.QLabel(
            "No project selected\n\n"
            "Select a project root and scan to view assets"
        )
        self.placeholder_label.setAlignment(QtCore.Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #888; font-size: 14px;")
        self.view_stack.addWidget(self.placeholder_label)
        
        # List view (index 1)
        self.asset_list = QtWidgets.QListWidget()
        self.asset_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.asset_list.itemSelectionChanged.connect(self.on_asset_selected)
        self.asset_list.itemDoubleClicked.connect(self.on_asset_double_clicked)
        self.view_stack.addWidget(self.asset_list)
        
        # Grid view (index 2) - Phase 3
        try:
            from .assets_manager_browser import AssetGridView
            self.asset_grid = AssetGridView()
            self.asset_grid.assetSelected.connect(self.on_grid_asset_selected)
            self.asset_grid.assetDoubleClicked.connect(self.on_grid_asset_double_clicked)
            self.view_stack.addWidget(self.asset_grid)
            self.has_grid_view = True
            debug_print("✅ Grid view available")
        except Exception as e:
            debug_print(f"⚠️ Grid view not available: {e}")
            self.asset_grid = None
            self.has_grid_view = False
        
        layout.addWidget(self.view_stack)
        
        # Show placeholder initially
        self.view_stack.setCurrentIndex(0)
        self.current_view_mode = 'placeholder'
        
        return browser
    
    def create_preview_widget(self):
        """Create preview panel widget"""
        preview = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(preview)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Title
        title_label = QtWidgets.QLabel("Preview")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Thumbnail placeholder (Phase 3)
        self.thumbnail_label = QtWidgets.QLabel()
        self.thumbnail_label.setFixedSize(256, 256)
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet(
            "background: #2a2a2a; border: 1px solid #444; border-radius: 4px;"
        )
        self.thumbnail_label.setText("No thumbnail\n(Phase 3)")
        layout.addWidget(self.thumbnail_label, 0, QtCore.Qt.AlignHCenter)
        
        # Metadata display
        self.metadata_text = QtWidgets.QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setPlaceholderText("Select an asset to view details...")
        layout.addWidget(self.metadata_text, 1)
        
        # Action buttons (Phase 4)
        button_layout = QtWidgets.QHBoxLayout()
        
        self.import_btn = QtWidgets.QPushButton("Import")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.import_asset)
        self.import_btn.setToolTip("Import asset into Houdini (Phase 4)")
        button_layout.addWidget(self.import_btn)
        
        self.reference_btn = QtWidgets.QPushButton("Reference")
        self.reference_btn.setEnabled(False)
        self.reference_btn.clicked.connect(self.reference_asset)
        self.reference_btn.setToolTip("Reference asset (Phase 4)")
        button_layout.addWidget(self.reference_btn)
        
        self.copy_path_btn = QtWidgets.QPushButton("Copy Path")
        self.copy_path_btn.setEnabled(False)
        self.copy_path_btn.clicked.connect(self.copy_asset_path)
        button_layout.addWidget(self.copy_path_btn)
        
        layout.addLayout(button_layout)
        
        return preview
    
    def create_status_bar(self):
        """Create status bar"""
        status = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(status)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label, 1)
        
        self.asset_count_label = QtWidgets.QLabel("0 assets")
        layout.addWidget(self.asset_count_label)
        
        return status
    
    def apply_stylesheet(self):
        """Apply dark theme stylesheet"""
        self.setStyleSheet("""
            QDialog {
                background: #1e1e1e;
                color: #e5e5e5;
            }
            QLabel {
                color: #e5e5e5;
            }
            QLineEdit, QComboBox, QTextEdit, QListWidget {
                background: #2a2a2a;
                color: #e5e5e5;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #5a9fd4;
            }
            QPushButton {
                background: #3a3a3a;
                color: #e5e5e5;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #4a4a4a;
                border: 1px solid #5a9fd4;
            }
            QPushButton:pressed {
                background: #2a2a2a;
            }
            QPushButton:disabled {
                background: #2a2a2a;
                color: #666;
                border: 1px solid #333;
            }
            QPushButton:checked {
                background: #5a9fd4;
                color: #fff;
                border: 1px solid #5a9fd4;
            }
            QListWidget {
                background: #252525;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background: #3d5a80;
            }
            QListWidget::item:hover {
                background: #333;
            }
        """)
    
    # ==================== Event Handlers ====================
    
    def browse_project_root(self):
        """Browse for project root directory"""
        current = self.project_root_edit.text()
        if not current or not os.path.isdir(current):
            current = os.path.expanduser("~")
        
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Project Root Directory",
            current
        )
        
        if path:
            self.project_root_edit.setText(path)
            self.load_projects(path)
            self.save_settings()
    
    def load_projects(self, root_path):
        """Load available projects from root path"""
        try:
            self.project_combo.clear()
            
            if not os.path.isdir(root_path):
                return
            
            # List directories in root path
            projects = []
            for item in os.listdir(root_path):
                item_path = os.path.join(root_path, item)
                if os.path.isdir(item_path):
                    # Check if it looks like a project (has 01_assets or 02_shots)
                    has_assets = os.path.isdir(os.path.join(item_path, "01_assets"))
                    has_shots = os.path.isdir(os.path.join(item_path, "02_shots"))
                    if has_assets or has_shots:
                        projects.append(item)
            
            if projects:
                self.project_combo.addItems(sorted(projects))
                self.scan_btn.setEnabled(True)
                debug_print(f"📁 Found {len(projects)} project(s)")
            else:
                self.project_combo.addItem("No projects found")
                self.scan_btn.setEnabled(False)
        
        except Exception as e:
            debug_print(f"❌ Error loading projects: {e}")
    
    def on_project_changed(self, project_name):
        """Handle project selection change"""
        if project_name and project_name != "No projects found":
            self.current_project = project_name
            self.scan_btn.setEnabled(True)
            debug_print(f"📁 Selected project: {project_name}")
    
    def scan_project(self):
        """Scan selected project for assets"""
        try:
            root = self.project_root_edit.text()
            project = self.project_combo.currentText()
            
            if not root or not project or project == "No projects found":
                QtWidgets.QMessageBox.warning(
                    self,
                    "No Project Selected",
                    "Please select a project root and project first."
                )
                return
            
            project_path = os.path.join(root, project)
            
            # Update status
            self.status_label.setText("Scanning project...")
            QtWidgets.QApplication.processEvents()
            
            # Initialize scanner
            self.scanner = AssetScanner(project_path)
            
            # Scan for assets
            assets = self.scanner.scan_project()
            
            # Initialize database
            db_path = os.path.join(project_path, ".assets_cache", "assets.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.database = AssetDatabase(db_path)
            
            # Add assets to database
            for asset in assets:
                # Load metadata
                metadata = self.metadata_mgr.read_metadata(asset['filepath'])
                asset['metadata'] = metadata
                asset['tags'] = ','.join(metadata.get('tags', []))
                asset['description'] = metadata.get('description', '')
                
                # Add to database
                self.database.add_asset(asset)
            
            self.current_assets = assets
            
            # Update UI
            self.populate_browser(assets)
            self.update_filters()
            self.refresh_btn.setEnabled(True)
            
            # Update status
            self.status_label.setText(f"Scan complete: {len(assets)} assets found")
            self.asset_count_label.setText(f"{len(assets)} assets")
            
            debug_print(f"✅ Scan complete: {len(assets)} assets")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Scan Error",
                f"Error scanning project:\n{str(e)}"
            )
            self.status_label.setText("Scan failed")
            debug_print(f"❌ Scan error: {e}")
            import traceback
            traceback.print_exc()
    
    def populate_browser(self, assets: List[Dict]):
        """Populate browser with assets"""
        if not assets:
            self.view_stack.setCurrentIndex(0)  # Show placeholder
            self.current_view_mode = 'placeholder'
            return
        
        # Populate based on current view mode
        if self.current_view_mode == 'grid' and self.has_grid_view:
            self.populate_grid_view(assets)
        else:
            self.populate_list_view(assets)
    
    def populate_list_view(self, assets: List[Dict]):
        """Populate list view with assets"""
        self.asset_list.clear()
        self.view_stack.setCurrentIndex(1)  # Show list view
        self.current_view_mode = 'list'
        
        for asset in assets:
            filename = asset.get('filename', 'Unknown')
            asset_type = asset.get('asset_type', '')
            version = asset.get('version', '')
            file_format = asset.get('file_format', '')
            
            # Create display text
            display_text = f"{filename}"
            if version:
                display_text += f" ({version})"
            if asset_type:
                display_text += f" [{asset_type}]"
            
            item = QtWidgets.QListWidgetItem(display_text)
            item.setData(QtCore.Qt.UserRole, asset)  # Store asset data
            
            # Add icon based on format
            if file_format == 'usd':
                item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
            
            self.asset_list.addItem(item)
        
        debug_print(f"📋 Populated list view with {len(assets)} assets")
    
    def populate_grid_view(self, assets: List[Dict]):
        """Populate grid view with assets"""
        if not self.has_grid_view:
            debug_print("⚠️ Grid view not available, falling back to list")
            self.populate_list_view(assets)
            return
        
        self.asset_grid.populate(assets)
        self.view_stack.setCurrentIndex(2)  # Show grid view
        self.current_view_mode = 'grid'
        
        debug_print(f"🎨 Populated grid view with {len(assets)} assets")
    
    def update_filters(self):
        """Update filter dropdowns based on current assets"""
        if not self.database:
            return
        
        # Update type filter
        types = self.database.get_all_asset_types()
        self.type_combo.clear()
        self.type_combo.addItem("All Types")
        self.type_combo.addItems(sorted(types))
        
        # Update format filter
        formats = self.database.get_all_file_formats()
        self.format_combo.clear()
        self.format_combo.addItem("All Formats")
        self.format_combo.addItems(sorted(formats))
        
        debug_print(f"📊 Filters updated: {len(types)} types, {len(formats)} formats")
    
    def on_search_changed(self, text):
        """Handle search text change"""
        self.apply_filters()
    
    def on_filter_changed(self):
        """Handle filter change"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply current search and filters"""
        if not self.database:
            return
        
        try:
            search_text = self.search_edit.text().strip()
            asset_type = self.type_combo.currentText()
            file_format = self.format_combo.currentText()
            
            # Build filter parameters
            kwargs = {}
            if search_text:
                kwargs['search_text'] = search_text
            if asset_type and asset_type != "All Types":
                kwargs['asset_type'] = asset_type
            if file_format and file_format != "All Formats":
                kwargs['file_format'] = file_format
            
            # Search database
            results = self.database.search_assets(**kwargs)
            
            # Update browser
            self.populate_browser(results)
            self.asset_count_label.setText(f"{len(results)} assets")
            
            debug_print(f"🔍 Filter applied: {len(results)} results")
            
        except Exception as e:
            debug_print(f"❌ Filter error: {e}")
    
    def on_asset_selected(self):
        """Handle asset selection"""
        selected_items = self.asset_list.selectedItems()
        if not selected_items:
            self.selected_asset = None
            self.update_preview(None)
            return
        
        item = selected_items[0]
        asset = item.data(QtCore.Qt.UserRole)
        self.selected_asset = asset
        self.update_preview(asset)
        
        # Enable action buttons
        self.import_btn.setEnabled(True)
        self.reference_btn.setEnabled(True)
        self.copy_path_btn.setEnabled(True)
    
    def on_asset_double_clicked(self, item):
        """Handle asset double-click (list view)"""
        asset = item.data(QtCore.Qt.UserRole)
        self._handle_double_click(asset)
    
    def on_grid_asset_selected(self, asset_data: Dict):
        """Handle grid view asset selection"""
        self.selected_asset = asset_data
        self.update_preview(asset_data)
        
        # Enable action buttons
        self.import_btn.setEnabled(True)
        self.reference_btn.setEnabled(True)
        self.copy_path_btn.setEnabled(True)
    
    def on_grid_asset_double_clicked(self, asset_data: Dict):
        """Handle grid view asset double-click"""
        self._handle_double_click(asset_data)
    
    def _handle_double_click(self, asset):
        """Common handler for double-click"""
        # Phase 4: Import asset
        debug_print(f"🖱️ Double-clicked: {asset.get('filename')}")
        QtWidgets.QMessageBox.information(
            self,
            "Import Asset",
            f"Import functionality will be available in Phase 4\n\n"
            f"Asset: {asset.get('filename')}"
        )
    
    def update_preview(self, asset: Optional[Dict]):
        """Update preview panel with asset details"""
        if not asset:
            self.metadata_text.clear()
            self.thumbnail_label.setText("No thumbnail\n(Phase 3)")
            return
        
        # Build metadata display
        lines = []
        lines.append(f"<b>Asset:</b> {asset.get('asset_name', 'Unknown')}")
        lines.append(f"<b>Filename:</b> {asset.get('filename', 'Unknown')}")
        lines.append(f"<b>Version:</b> {asset.get('version', 'Unknown')}")
        lines.append(f"<b>Type:</b> {asset.get('asset_type', 'Unknown')}")
        lines.append(f"<b>Department:</b> {asset.get('department', 'Unknown')}")
        lines.append(f"<b>Format:</b> {asset.get('file_format', 'Unknown')}")
        
        # File info
        file_size = asset.get('file_size', 0)
        if file_size:
            size_mb = file_size / (1024 * 1024)
            lines.append(f"<b>Size:</b> {size_mb:.2f} MB")
        
        lines.append(f"<b>Modified:</b> {asset.get('modified_date', 'Unknown')}")
        
        # Description
        description = asset.get('description', '')
        if description:
            lines.append("")
            lines.append(f"<b>Description:</b>")
            lines.append(description)
        
        # Tags
        tags = asset.get('tags', '')
        if tags:
            lines.append("")
            lines.append(f"<b>Tags:</b> {tags}")
        
        # Path
        lines.append("")
        lines.append(f"<b>Path:</b>")
        lines.append(f"<small>{asset.get('filepath', 'Unknown')}</small>")
        
        self.metadata_text.setHtml("<br>".join(lines))
        
        # Thumbnail (Phase 3)
        self.thumbnail_label.setText(f"Thumbnail\n(Phase 3)\n\n{asset.get('file_format', '').upper()}")
    
    def set_view_mode(self, mode: str):
        """Set view mode (grid or list)"""
        debug_print(f"🔄 View mode: {mode}")
        
        if mode == 'grid' and not self.has_grid_view:
            QtWidgets.QMessageBox.information(
                self,
                "Grid View",
                "Grid view is not available.\nMake sure assets_manager_browser.py is imported correctly."
            )
            self.list_view_btn.setChecked(True)
            self.grid_view_btn.setChecked(False)
            return
        
        # Switch view mode
        self.current_view_mode = mode
        
        # Re-populate with current assets
        if self.current_assets:
            self.populate_browser(self.current_assets)
    
    def refresh_browser(self):
        """Refresh browser (re-apply current filters)"""
        self.apply_filters()
        self.status_label.setText("Refreshed")
    
    # ==================== Actions (Phase 4) ====================
    
    def import_asset(self):
        """Import selected asset (Phase 4)"""
        if not self.selected_asset:
            return
        
        QtWidgets.QMessageBox.information(
            self,
            "Import Asset",
            f"Import functionality will be available in Phase 4\n\n"
            f"Asset: {self.selected_asset.get('filename')}"
        )
    
    def reference_asset(self):
        """Reference selected asset (Phase 4)"""
        if not self.selected_asset:
            return
        
        QtWidgets.QMessageBox.information(
            self,
            "Reference Asset",
            f"Reference functionality will be available in Phase 4\n\n"
            f"Asset: {self.selected_asset.get('filename')}"
        )
    
    def copy_asset_path(self):
        """Copy asset path to clipboard"""
        if not self.selected_asset:
            return
        
        path = self.selected_asset.get('filepath', '')
        if path:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(path)
            self.status_label.setText(f"Copied: {os.path.basename(path)}")
            debug_print(f"📋 Copied path: {path}")
    
    # ==================== Settings ====================
    
    def load_settings(self):
        """Load saved settings"""
        try:
            # Load project root
            root = self.settings.value("project_root", "", type=str)
            if root:
                self.project_root_edit.setText(root)
                self.load_projects(root)
            
            # Load last project
            project = self.settings.value("current_project", "", type=str)
            if project:
                index = self.project_combo.findText(project)
                if index >= 0:
                    self.project_combo.setCurrentIndex(index)
            
            debug_print("✅ Settings loaded")
        
        except Exception as e:
            debug_print(f"⚠️ Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings"""
        try:
            self.settings.setValue("project_root", self.project_root_edit.text())
            self.settings.setValue("current_project", self.project_combo.currentText())
            self.settings.sync()
            debug_print("✅ Settings saved")
        
        except Exception as e:
            debug_print(f"⚠️ Error saving settings: {e}")
    
    def closeEvent(self, event):
        """Handle dialog close"""
        self.save_settings()
        
        # Close database
        if self.database:
            self.database.close()
        
        super().closeEvent(event)


# ==================== Public API ====================

def show_mono_assets_manager(parent=None):
    """
    Show Assets Manager dialog
    
    Args:
        parent: Parent widget (None for standalone, hou.qt.mainWindow() for Houdini)
        
    Returns:
        MonoAssetsManager instance
    """
    dialog = MonoAssetsManager(parent)
    dialog.show()
    return dialog


if __name__ == "__main__":
    # Standalone test
    import sys
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    dialog = show_mono_assets_manager()
    sys.exit(app.exec())

