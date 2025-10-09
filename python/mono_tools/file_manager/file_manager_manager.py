import os
from mono_tools.qt import QtCore, QtGui, QtWidgets
import hou
try:
    from .file_manager_helpers import ORG, APP, SUBPATH, collect_files, parse_ver, infer_shot, list_projects, DEFAULT_ROOT, load_tabs_settings, save_tabs_settings
    from .file_manager_helpers import collect_asset_files_hybrid, list_asset_types, list_asset_names, list_departments, infer_asset_name, infer_department
    from .file_manager_models import FileTableModel, AssetTableModel
    from .file_manager_helpers import open_in_explorer
except ImportError:
    from file_manager_helpers import ORG, APP, SUBPATH, collect_files, parse_ver, infer_shot, list_projects, DEFAULT_ROOT, load_tabs_settings, save_tabs_settings
    from file_manager_helpers import collect_asset_files_hybrid, list_asset_types, list_asset_names, list_departments, infer_asset_name, infer_department
    from file_manager_models import FileTableModel, AssetTableModel
    from file_manager_helpers import open_in_explorer

class MonoFileManager(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mono File Manager")
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setMinimumWidth(920); self.setMinimumHeight(520)
        self.s=QtCore.QSettings(ORG,APP)
        # Initialize attributes
        self.table = None
        self.depth_sb = None
        self.tabs_conf = []
        self._minibar_ref=None
        self._build_ui(); self._restore(); QtCore.QTimer.singleShot(0,self._center)

    def _build_ui(self):
        title=QtWidgets.QLabel("Mono File Manager"); f=title.font(); f.setPointSize(18); f.setBold(True); title.setFont(f)
        # Project root and dropdown
        self.root_le=QtWidgets.QLineEdit(); self.root_le.setText(self.s.value("root_dir", DEFAULT_ROOT, type=str))
        b_browse=QtWidgets.QPushButton("Browse…"); b_browse.clicked.connect(self._browse)
        self.project_cb=QtWidgets.QComboBox(); self._reload_projects()
        self.project_cb.currentIndexChanged.connect(self._on_project_changed)
        # Type tabs (Assets/Shots)
        self.type_tabs = QtWidgets.QTabWidget()
        self.type_tabs.currentChanged.connect(self._on_type_changed)
        
        # Create Assets and Shots type tabs
        self.assets_tab = QtWidgets.QWidget()
        self.shots_tab = QtWidgets.QWidget()
        
        # Asset filtering controls
        self.asset_type_cb = QtWidgets.QComboBox()
        self.asset_type_cb.currentTextChanged.connect(self._on_asset_type_changed)
        self.asset_name_cb = QtWidgets.QComboBox()
        self.asset_name_cb.currentTextChanged.connect(self._on_asset_name_changed)
        self.department_cb = QtWidgets.QComboBox()
        self.department_cb.currentTextChanged.connect(self._on_department_changed)
        self.department_cb.addItem("All Departments")
        
        # Custom department input
        self.custom_dept_le = QtWidgets.QLineEdit()
        self.custom_dept_le.setPlaceholderText("Custom department...")
        self.custom_dept_le.setVisible(False)
        self.custom_dept_le.textChanged.connect(self._on_custom_department_changed)
        
        # Tabs for subpaths within each type
        self.assets_tabs = QtWidgets.QTabWidget(); self.assets_tabs.setMovable(True); self.assets_tabs.setTabsClosable(True)
        self.assets_tabs.tabBarDoubleClicked.connect(self._rename_tab)
        self.assets_tabs.tabCloseRequested.connect(self._remove_tab)
        self.assets_tabs.tabBar().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assets_tabs.tabBar().customContextMenuRequested.connect(self._show_tab_context_menu)
        
        self.shots_tabs = QtWidgets.QTabWidget(); self.shots_tabs.setMovable(True); self.shots_tabs.setTabsClosable(True)
        self.shots_tabs.tabBarDoubleClicked.connect(self._rename_tab)
        self.shots_tabs.tabCloseRequested.connect(self._remove_tab)
        self.shots_tabs.tabBar().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.shots_tabs.tabBar().customContextMenuRequested.connect(self._show_tab_context_menu)
        
        # Per-tab control row
        self.depth_sb=QtWidgets.QSpinBox(); self.depth_sb.setRange(1,10); self.depth_sb.setValue(1)
        self._init_type_tabs()
        # Initialize current_tabs reference
        self.current_tabs = self.shots_tabs  # Default to shots
        exts_lbl=QtWidgets.QLabel(".hip, .hiplc, .hipnc (fixed)")
        b_add_tab=QtWidgets.QPushButton("+ Tab"); b_add_tab.clicked.connect(self._add_tab)
        b_scan=QtWidgets.QPushButton("Scan"); b_scan.clicked.connect(self.scan)
        b_refresh=QtWidgets.QPushButton("Refresh"); b_refresh.clicked.connect(self.scan)
        b_open=QtWidgets.QPushButton("Open in Explorer"); b_open.clicked.connect(self._open_selected)
        b_copy=QtWidgets.QPushButton("Copy Path"); b_copy.clicked.connect(self._copy_selected)
        row=QtWidgets.QHBoxLayout(); row.addWidget(b_scan); row.addWidget(b_refresh); row.addStretch(1); row.addWidget(b_open); row.addWidget(b_copy)
        # Global table will be created per tab
        self.table = None
        
        # Status bar components
        self.status_bar = QtWidgets.QWidget()
        self.status_bar.setFixedHeight(30)
        self.status_bar.setStyleSheet("""
            QWidget { background:#1a1a1a; border-top:1px solid #3a3a3a; }
            QLabel { color:#e5e5e5; padding:4px 8px; }
            QPushButton { background:#3a3a3a; color:#fff; border:1px solid #4a4a4a; border-radius:4px; padding:2px 6px; font-size:11px; }
            QPushButton:hover { background:#4a4a4a; }
        """)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("color:#e5e5e5; padding:4px 8px;")
        
        # Error details button
        self.error_details_btn = QtWidgets.QPushButton("📋 Details")
        self.error_details_btn.setFixedSize(80, 24)
        self.error_details_btn.setVisible(False)
        self.error_details_btn.clicked.connect(self._show_error_details)
        
        # Status bar layout
        status_layout = QtWidgets.QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(8, 2, 8, 2)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.error_details_btn)
        
        # Store error details
        self._last_error = None
        self._error_traceback = None
        
        g=QtWidgets.QGridLayout(); g.setVerticalSpacing(6); g.setHorizontalSpacing(8)
        g.addWidget(QtWidgets.QLabel("Project Root"),0,0); g.addWidget(self.root_le,0,1); g.addWidget(b_browse,0,2); g.addWidget(self.project_cb,0,3)
        g.addWidget(QtWidgets.QLabel("Type"),1,0); g.addWidget(self.type_tabs,1,1,1,3)
        
        # Asset filtering row (only visible when Assets tab is selected)
        self.asset_type_lbl = QtWidgets.QLabel("Asset Type"); g.addWidget(self.asset_type_lbl,2,0); g.addWidget(self.asset_type_cb,2,1)
        self.asset_name_lbl = QtWidgets.QLabel("Asset Name"); g.addWidget(self.asset_name_lbl,2,2); g.addWidget(self.asset_name_cb,2,3)
        self.department_lbl = QtWidgets.QLabel("Department"); g.addWidget(self.department_lbl,3,0); g.addWidget(self.department_cb,3,1)
        self.custom_dept_lbl = QtWidgets.QLabel("Custom Dept"); g.addWidget(self.custom_dept_lbl,3,2); g.addWidget(self.custom_dept_le,3,3)
        
        g.addWidget(QtWidgets.QLabel("Depth"),4,0); g.addWidget(self.depth_sb,4,1); g.addWidget(exts_lbl,4,2); g.addWidget(b_add_tab,4,3)
        lay=QtWidgets.QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(10)
        lay.addWidget(title); lay.addLayout(g); lay.addLayout(row)
        lay.addWidget(self.status_bar)
        
        self.setStyleSheet("""
        QDialog { background:#232323; color:#e5e5e5; }
        QLabel { color:#e5e5e5; }
        QLineEdit, QSpinBox { background:#2c2c2c; color:#e5e5e5; border:1px solid #3a3a3a; border-radius:6px; padding:4px 6px; }
        QPushButton { background:#3a3a3a; color:#fff; border:1px solid #4a4a4a; border-radius:8px; padding:6px 10px; }
        QPushButton:hover { background:#4a4a4a; }
        QTableView { background:#1e1e1e; alternate-background-color:#242424; gridline-color:#3a3a3a; selection-background-color:#3d5a99; selection-color:#fff; }
        QHeaderView::section { background:#2a2a2a; color:#dcdcdc; border:0; padding:6px; }
        """)
        
        # Initialize asset filtering after UI is completely built
        self._init_asset_filtering()

    def _center(self):
        sc=QtWidgets.QApplication.primaryScreen()
        if sc: self.move(sc.availableGeometry().center()-self.rect().center())
    def _browse(self):
        d=QtWidgets.QFileDialog.getExistingDirectory(self,"Select Project Root", self.root_le.text() or os.path.expanduser("~"))
        if d:
            self.root_le.setText(d); self._reload_projects(); self._save()
    def _save(self):
        self.s.setValue("root_dir", self.root_le.text());
        save_tabs_settings(self.s, self.tabs_conf); self.s.sync()
    def _restore(self):
        self.root_le.setText(self.s.value("root_dir", DEFAULT_ROOT, type=str))
    def _target_dir(self):
        root=self.root_le.text().strip();
        project=self.project_cb.currentText().strip();
        subpath=self._current_subpath();
        if root and project and subpath:
            return os.path.join(root, project, subpath)
        elif root and subpath:
            return os.path.join(root, subpath)
        else:
            return ""
    def scan(self):
        try:
            self._show_status("🔍 Scanning files...", is_error=False)
            
            model = self._active_model()
            if not model: 
                self._show_error("No active model found")
                return
                
            model.removeRows(0,model.rowCount())
            
            # Check if we're in Assets mode
            current_widget = self.current_tabs.currentWidget() if self.current_tabs else None
            is_asset_mode = (self.type_tabs.currentIndex() == 0 and 
                           current_widget and 
                           getattr(current_widget, 'is_asset_tab', False))
            
            files_found = 0
            
            if is_asset_mode:
                # Asset scanning mode
                base = self._get_asset_base_dir()
                if not base or not os.path.isdir(base):
                    error_msg = f"Asset directory not found: {base or '<empty>'}"
                    self._show_error(error_msg)
                    return
                
                # Get filter parameters - use tab settings if available, otherwise use UI controls
                if hasattr(current_widget, 'asset_type') and current_widget.asset_type:
                    asset_type = current_widget.asset_type
                else:
                    asset_type = self.asset_type_cb.currentText()
                    if asset_type == "All Types":
                        asset_type = None
                
                if hasattr(current_widget, 'department') and current_widget.department:
                    department = current_widget.department
                else:
                    department = self.department_cb.currentText()
                    # Handle custom department
                    if department == "Custom...":
                        department = self.custom_dept_le.text().strip()
                        if not department:
                            department = None
                    elif department == "All Departments":
                        department = None
                
                # Always use UI control for asset name (can be overridden by user)
                asset_name = self.asset_name_cb.currentText()
                if asset_name == "All Assets":
                    asset_name = None
                
                # Collect asset files using hybrid approach
                asset_files = collect_asset_files_hybrid(base, asset_type, department, asset_name)
                
                # Filter by asset name if specified
                if asset_name:
                    asset_files = [(fp, an, dept) for fp, an, dept in asset_files if an == asset_name]
                
                # Group files by (asset_name, department)
                grouped_files = {}
                for filepath, asset_name, dept_name in asset_files:
                    try:
                        st = os.stat(filepath)
                        name = os.path.basename(filepath)
                        name_no_ext, ext = os.path.splitext(name)
                        folder = os.path.basename(os.path.dirname(filepath))
                        ver = parse_ver(name) or "—"
                        
                        group_key = (asset_name, dept_name)
                        if group_key not in grouped_files:
                            grouped_files[group_key] = []
                        
                        grouped_files[group_key].append((ver, name, ext, folder, st.st_mtime, st.st_size, filepath))
                        files_found += 1
                    except Exception as e:
                        print(f"⚠️ Error processing asset file {filepath}: {e}")
                        continue
                
                # Add grouped assets to model
                for (asset_name, dept_name), versions_data in grouped_files.items():
                    if isinstance(model, AssetTableModel):
                        model.add_asset_group(asset_name, dept_name, versions_data)
                
                # Sort by modification time (descending)
                proxy = self._active_proxy()
                if isinstance(model, AssetTableModel):
                    proxy.sort(AssetTableModel.COL_MOD, QtCore.Qt.DescendingOrder)
                    if self.table:
                        for c in (AssetTableModel.COL_ASSET, AssetTableModel.COL_DEPT, AssetTableModel.COL_VER, AssetTableModel.COL_EXT, AssetTableModel.COL_SIZE):
                            self.table.resizeColumnToContents(c)
                else:
                    proxy.sort(FileTableModel.COL_MOD, QtCore.Qt.DescendingOrder)
                    if self.table:
                        for c in (FileTableModel.COL_SHOT, FileTableModel.COL_VER, FileTableModel.COL_EXT, FileTableModel.COL_SIZE):
                            self.table.resizeColumnToContents(c)
            else:
                # Regular shots scanning mode
                base = self._target_dir()
                
                if not base or not os.path.isdir(base):
                    error_msg = f"Directory not found: {base or '<empty>'}"
                    self._show_error(error_msg)
                    return
                    
                for f in collect_files(base, depth=self.depth_sb.value()):
                    try:
                        st=os.stat(f)
                        name=os.path.basename(f); ext=os.path.splitext(name)[1].lower()
                        ver=parse_ver(name); shot=infer_shot(f); folder=os.path.dirname(f)
                        model.add_row(shot,ver,name,ext,folder,st.st_mtime,st.st_size,f)
                        files_found += 1
                    except Exception as e:
                        # Log individual file errors but continue scanning
                        print(f"⚠️ Error processing file {f}: {e}")
                        continue
                        
                proxy=self._active_proxy(); proxy.sort(FileTableModel.COL_MOD, QtCore.Qt.DescendingOrder)
                if self.table:
                    for c in (FileTableModel.COL_SHOT,FileTableModel.COL_VER,FileTableModel.COL_EXT,FileTableModel.COL_SIZE): 
                        self.table.resizeColumnToContents(c)
            
            self._save()
            
            if hasattr(self, "_minibar_ref") and self._minibar_ref:
                self._minibar_ref.populate_from_model(model)
                
            self._show_status(f"✅ Found {files_found} files", is_error=False)
            
        except Exception as e:
            import traceback
            error_msg = f"Scan failed: {str(e)}"
            traceback_str = traceback.format_exc()
            self._show_error(error_msg, error_obj=e, traceback_str=traceback_str)
    
    def _get_asset_base_dir(self):
        """Get base directory for asset scanning"""
        root = self.root_le.text().strip()
        if not root:
            return ""
            
        project = self.project_cb.currentText().strip()
        if project:
            return os.path.join(root, project)
        else:
            return root

    # ---- Projects ----
    def _reload_projects(self):
        root=self.root_le.text().strip() or DEFAULT_ROOT
        items=list_projects(root)
        self.project_cb.blockSignals(True)
        self.project_cb.clear(); self.project_cb.addItems(items)
        # restore selection
        sel=self.s.value("selected_project","",type=str)
        if sel:
            idx=self.project_cb.findText(sel)
            if idx>=0: self.project_cb.setCurrentIndex(idx)
        self.project_cb.blockSignals(False)

    def _on_project_changed(self, idx):
        name=self.project_cb.currentText()
        if name:
            self.s.setValue("selected_project", name); self.s.sync()
            # Reload asset types when project changes
            self._reload_asset_types()
            # Auto-scan when project changes
            QtCore.QTimer.singleShot(100, self.scan)

    # ---- Type Tabs ----
    def _init_type_tabs(self):
        # Initialize tabs_conf
        self.tabs_conf = load_tabs_settings(self.s)
        
        # Setup Assets tab
        assets_layout = QtWidgets.QVBoxLayout(self.assets_tab)
        assets_layout.addWidget(self.assets_tabs)
        self.type_tabs.addTab(self.assets_tab, "Assets")
        
        # Setup Shots tab  
        shots_layout = QtWidgets.QVBoxLayout(self.shots_tab)
        shots_layout.addWidget(self.shots_tabs)
        self.type_tabs.addTab(self.shots_tab, "Shots")
        
        # Initialize sub-tabs for each type
        self._init_assets_tabs()
        self._init_shots_tabs()
        
        # Set default type
        current_type = self.s.value("current_type", "Shots", type=str)
        if current_type == "Assets":
            self.type_tabs.setCurrentIndex(0)
        else:
            self.type_tabs.setCurrentIndex(1)

    def _init_assets_tabs(self):
        """Initialize Assets sub-tabs"""
        assets_configs = [
            {"name": "models", "is_asset_tab": True, "asset_type": "_characters", "department": "01_modeling"},
            {"name": "rigging", "is_asset_tab": True, "asset_type": "_characters", "department": "02_rigging"},
            {"name": "surfacing", "is_asset_tab": True, "asset_type": "_characters", "department": "03_surfacing"},
            {"name": "lookdev", "is_asset_tab": True, "asset_type": "_characters", "department": "04_lookdev"},
            {"name": "groom", "is_asset_tab": True, "asset_type": "_characters", "department": "05_groom"}
        ]
        for conf in assets_configs:
            self._create_type_tab(self.assets_tabs, conf)

    def _init_shots_tabs(self):
        """Initialize Shots sub-tabs"""
        shots_configs = [
            {"name": "lighting", "subpath": "02_shots/03_lighting", "depth": 1},
            {"name": "animation", "subpath": "02_shots/02_animation", "depth": 1},
            {"name": "comp", "subpath": "02_shots/04_comp", "depth": 1}
        ]
        for conf in shots_configs:
            self._create_type_tab(self.shots_tabs, conf)

    def _init_asset_filtering(self):
        """Initialize asset filtering controls"""
        # Load asset types
        self._reload_asset_types()
        
        # Set up visibility based on current type
        self._update_asset_filter_visibility()
    
    def _reload_asset_types(self):
        """Reload asset types from current project"""
        root = self.root_le.text().strip()
        if not root:
            return
            
        project = self.project_cb.currentText().strip()
        if project:
            base_dir = os.path.join(root, project)
        else:
            base_dir = root
            
        asset_types = list_asset_types(base_dir)
        
        self.asset_type_cb.blockSignals(True)
        self.asset_type_cb.clear()
        self.asset_type_cb.addItem("All Types")
        self.asset_type_cb.addItems(asset_types)
        self.asset_type_cb.blockSignals(False)
        
        # Reset other dropdowns
        self.asset_name_cb.clear()
        self.asset_name_cb.addItem("All Assets")
        self.department_cb.clear()
        self.department_cb.addItem("All Departments")
    
    def _reload_asset_names(self):
        """Reload asset names for selected asset type"""
        root = self.root_le.text().strip()
        if not root:
            return
            
        project = self.project_cb.currentText().strip()
        if project:
            base_dir = os.path.join(root, project)
        else:
            base_dir = root
            
        asset_type = self.asset_type_cb.currentText()
        if asset_type == "All Types":
            asset_names = []
        else:
            asset_names = list_asset_names(base_dir, asset_type)
        
        self.asset_name_cb.blockSignals(True)
        self.asset_name_cb.clear()
        self.asset_name_cb.addItem("All Assets")
        self.asset_name_cb.addItems(asset_names)
        self.asset_name_cb.blockSignals(False)
    
    def _reload_departments(self):
        """Reload departments for selected asset"""
        root = self.root_le.text().strip()
        if not root:
            return
            
        project = self.project_cb.currentText().strip()
        if project:
            base_dir = os.path.join(root, project)
        else:
            base_dir = root
            
        asset_type = self.asset_type_cb.currentText()
        asset_name = self.asset_name_cb.currentText()
        
        if asset_type == "All Types" or asset_name == "All Assets":
            departments = []
        else:
            departments = list_departments(base_dir, asset_type, asset_name)
        
        self.department_cb.blockSignals(True)
        self.department_cb.clear()
        self.department_cb.addItem("All Departments")
        self.department_cb.addItems(departments)
        self.department_cb.addItem("Custom...")
        self.department_cb.blockSignals(False)
    
    def _update_asset_filter_visibility(self):
        """Update visibility of asset filtering controls"""
        is_assets = self.type_tabs.currentIndex() == 0
        
        # Show/hide asset filtering controls
        self.asset_type_cb.setVisible(is_assets)
        self.asset_name_cb.setVisible(is_assets)
        self.department_cb.setVisible(is_assets)
        self.custom_dept_le.setVisible(is_assets)
        
        # Show/hide asset filtering labels (with safety checks)
        if hasattr(self, 'asset_type_lbl') and self.asset_type_lbl:
            self.asset_type_lbl.setVisible(is_assets)
        if hasattr(self, 'asset_name_lbl') and self.asset_name_lbl:
            self.asset_name_lbl.setVisible(is_assets)
        if hasattr(self, 'department_lbl') and self.department_lbl:
            self.department_lbl.setVisible(is_assets)
        if hasattr(self, 'custom_dept_lbl') and self.custom_dept_lbl:
            self.custom_dept_lbl.setVisible(is_assets)
    
    def _on_asset_type_changed(self, text):
        """Handle asset type selection change"""
        self._reload_asset_names()
        self._reload_departments()
        if self.type_tabs.currentIndex() == 0:  # Assets tab
            self.scan()
    
    def _on_asset_name_changed(self, text):
        """Handle asset name selection change"""
        self._reload_departments()
        if self.type_tabs.currentIndex() == 0:  # Assets tab
            self.scan()
    
    def _on_department_changed(self, text):
        """Handle department selection change"""
        if text == "Custom...":
            if hasattr(self, 'custom_dept_le') and self.custom_dept_le:
                self.custom_dept_le.setVisible(True)
                self.custom_dept_le.setFocus()
        else:
            if hasattr(self, 'custom_dept_le') and self.custom_dept_le:
                self.custom_dept_le.setVisible(False)
            if self.type_tabs.currentIndex() == 0:  # Assets tab
                self.scan()
    
    def _on_custom_department_changed(self, text):
        """Handle custom department input change"""
        if hasattr(self, 'type_tabs') and self.type_tabs.currentIndex() == 0:  # Assets tab
            self.scan()

    def _on_type_changed(self, idx):
        """Handle type tab change"""
        if idx == 0:  # Assets
            self.current_tabs = self.assets_tabs
            # Reload asset types when switching to Assets tab
            self._reload_asset_types()
        else:  # Shots
            self.current_tabs = self.shots_tabs
        
        self.s.setValue("current_type", "Assets" if idx == 0 else "Shots")
        self.s.sync()
        
        # Update visibility of asset filtering controls
        self._update_asset_filter_visibility()
        
        # Update current tab reference and scan
        self._bind_active_tab()
        if self.table:  # Only scan if table is available
            self.scan()

    # ---- Tabs ----
    def _init_tabs(self):
        # This method is now handled by _init_type_tabs
        pass

    def _create_type_tab(self, parent_tabs, conf):
        """Create a tab within a type (Assets or Shots)"""
        name=conf.get("name","lighting"); subpath=conf.get("subpath",SUBPATH); depth=int(conf.get("depth",1))
        w=QtWidgets.QWidget(); lay=QtWidgets.QVBoxLayout(w); lay.setContentsMargins(0,0,0,0)
        
        # Determine if this is an asset tab or shot tab
        is_asset_tab = conf.get("is_asset_tab", False) or parent_tabs == self.assets_tabs
        
        # Create appropriate table model
        if is_asset_tab:
            model = AssetTableModel(self)
        else:
            model = FileTableModel(self)
            
        proxy=QtCore.QSortFilterProxyModel(self); proxy.setSourceModel(model); proxy.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        table=QtWidgets.QTableView(); table.setModel(proxy); table.setSortingEnabled(True)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows); table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        table.doubleClicked.connect(self._dbl_open); table.verticalHeader().setVisible(False); table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        
        # Add version delegate for asset tabs
        if is_asset_tab:
            from .file_manager_models import VersionComboBoxDelegate
            version_delegate = VersionComboBoxDelegate(table)
            table.setItemDelegateForColumn(AssetTableModel.COL_VER, version_delegate)
        
        # Store references
        w.model=model; w.proxy=proxy; w.table=table; w.depth=depth; w.is_asset_tab=is_asset_tab
        if not is_asset_tab:
            w.subpath=subpath
        else:
            # For asset tabs, store filter settings instead of subpath
            w.asset_type=conf.get("asset_type")
            w.department=conf.get("department")
        lay.addWidget(table)
        
        # Connect tab change events
        parent_tabs.currentChanged.connect(self._on_tab_changed)
        
        idx=parent_tabs.addTab(w, name); return idx

    def _create_tab(self, conf):
        """Legacy method - now redirects to _create_type_tab"""
        return self._create_type_tab(self.current_tabs, conf)

    def _on_tab_changed(self, idx):
        self._bind_active_tab()
        if self.table:  # Only scan if table is available
            self.scan()

    def _bind_active_tab(self):
        if not hasattr(self, 'current_tabs'):
            self.current_tabs = self.shots_tabs  # Default to shots
        
        if not self.current_tabs:
            return
            
        w=self.current_tabs.currentWidget()
        if not w: return
        self.table = w.table; self.depth_sb.setValue(getattr(w,'depth',1))

    def _active_model(self):
        if not hasattr(self, 'current_tabs'):
            self.current_tabs = self.shots_tabs
        w=self.current_tabs.currentWidget(); return getattr(w,'model',None)
    
    def _active_proxy(self):
        if not hasattr(self, 'current_tabs'):
            self.current_tabs = self.shots_tabs
        w=self.current_tabs.currentWidget(); return getattr(w,'proxy',None)
        
    def _current_subpath(self):
        if not hasattr(self, 'current_tabs'):
            self.current_tabs = self.shots_tabs
        w=self.current_tabs.currentWidget(); return getattr(w,'subpath',SUBPATH)

    def _add_tab(self):
        if not hasattr(self, 'current_tabs'):
            self.current_tabs = self.shots_tabs
            
        name, ok = QtWidgets.QInputDialog.getText(self, "New Tab", "Tab name:", text="new")
        if not ok or not name.strip(): return
        sub, ok2 = QtWidgets.QInputDialog.getText(self, "Subpath", "Relative subpath:", text=SUBPATH)
        if not ok2 or not sub.strip(): return
        conf={"name":name.strip(),"subpath":sub.strip(),"depth":1}
        self._create_type_tab(self.current_tabs, conf)
        # Update tabs configuration after adding
        self._update_tabs_config()

    def _remove_tab(self, idx):
        if not hasattr(self, 'current_tabs'):
            self.current_tabs = self.shots_tabs
            
        if self.current_tabs.count()<=1: return
        name=self.current_tabs.tabText(idx)
        self.current_tabs.removeTab(idx)
        # Update tabs configuration after removal
        self._update_tabs_config()

    def _rename_tab(self, idx):
        if not hasattr(self, 'current_tabs'):
            self.current_tabs = self.shots_tabs
            
        if idx<0: return
        w=self.current_tabs.widget(idx); old_name=self.current_tabs.tabText(idx)
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename Tab", "Tab name:", text=old_name)
        if not ok or not new_name.strip(): return
        new_sub, ok2 = QtWidgets.QInputDialog.getText(self, "Edit Subpath", "Relative subpath:", text=getattr(w,'subpath',SUBPATH))
        if not ok2 or not new_sub.strip(): return
        self.current_tabs.setTabText(idx, new_name.strip()); w.subpath=new_sub.strip()
        # Update tabs configuration after rename
        self._update_tabs_config()

    def _show_tab_context_menu(self, pos):
        """Show context menu for tab right-click"""
        # Determine which tab widget was clicked
        sender = self.sender()
        if sender == self.assets_tabs.tabBar():
            tab_widget = self.assets_tabs
        elif sender == self.shots_tabs.tabBar():
            tab_widget = self.shots_tabs
        else:
            return
        
        # Get tab index at click position
        tab_index = tab_widget.tabBar().tabAt(pos)
        if tab_index < 0:
            return
        
        # Create context menu
        menu = QtWidgets.QMenu(self)
        
        # Get current tab info
        tab_widget_obj = tab_widget.widget(tab_index)
        current_name = tab_widget.tabText(tab_index)
        current_subpath = getattr(tab_widget_obj, 'subpath', '')
        
        # Add menu actions
        rename_action = menu.addAction("✏️ Rename Tab")
        edit_subpath_action = menu.addAction("📁 Edit Subpath")
        menu.addSeparator()
        duplicate_action = menu.addAction("📋 Duplicate Tab")
        menu.addSeparator()
        close_action = menu.addAction("❌ Close Tab")
        
        # Show menu and handle action
        action = menu.exec_(tab_widget.tabBar().mapToGlobal(pos))
        
        if action == rename_action:
            # Temporarily set current_tabs for rename
            old_current = self.current_tabs
            self.current_tabs = tab_widget
            self._rename_tab(tab_index)
            self.current_tabs = old_current
        elif action == edit_subpath_action:
            self._edit_tab_subpath(tab_index, tab_widget)
        elif action == duplicate_action:
            self._duplicate_tab(tab_index, tab_widget)
        elif action == close_action:
            # Temporarily set current_tabs for remove
            old_current = self.current_tabs
            self.current_tabs = tab_widget
            self._remove_tab(tab_index)
            self.current_tabs = old_current

    def _edit_tab_subpath(self, idx, tab_widget):
        """Edit subpath for specific tab"""
        if idx < 0 or idx >= tab_widget.count():
            return
        
        w = tab_widget.widget(idx)
        current_subpath = getattr(w, 'subpath', '')
        
        new_subpath, ok = QtWidgets.QInputDialog.getText(
            self, 
            "Edit Subpath", 
            f"Edit subpath for tab '{tab_widget.tabText(idx)}':", 
            text=current_subpath
        )
        
        if ok and new_subpath.strip():
            w.subpath = new_subpath.strip()
            # Update tabs configuration
            self._update_tabs_config()
            # Refresh the current view
            if tab_widget == self.current_tabs:
                self.scan()

    def _duplicate_tab(self, idx, tab_widget):
        """Duplicate a tab with its configuration"""
        if idx < 0 or idx >= tab_widget.count():
            return
        
        w = tab_widget.widget(idx)
        original_name = tab_widget.tabText(idx)
        original_subpath = getattr(w, 'subpath', '')
        original_depth = getattr(w, 'depth', 1)
        
        # Create new tab configuration
        new_conf = {
            'name': f"{original_name}_copy",
            'subpath': original_subpath,
            'depth': original_depth
        }
        
        # Add new tab
        self._create_type_tab(tab_widget, new_conf)
        self._update_tabs_config()

    def _update_tabs_config(self):
        """Update tabs configuration in settings"""
        try:
            # Collect all tab configurations
            all_tabs_conf = []
            
            # Collect assets tabs
            for i in range(self.assets_tabs.count()):
                w = self.assets_tabs.widget(i)
                all_tabs_conf.append({
                    'name': self.assets_tabs.tabText(i),
                    'subpath': getattr(w, 'subpath', ''),
                    'depth': getattr(w, 'depth', 1),
                    'type': 'assets'
                })
            
            # Collect shots tabs
            for i in range(self.shots_tabs.count()):
                w = self.shots_tabs.widget(i)
                all_tabs_conf.append({
                    'name': self.shots_tabs.tabText(i),
                    'subpath': getattr(w, 'subpath', ''),
                    'depth': getattr(w, 'depth', 1),
                    'type': 'shots'
                })
            
            # Save to settings
            save_tabs_settings(self.s, all_tabs_conf)
            self.s.sync()
            
        except Exception as e:
            print(f"⚠️ Error updating tabs config: {e}")

    def _show_status(self, message, is_error=False):
        """Show status message in status bar"""
        try:
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText(message)
                if is_error:
                    self.status_label.setStyleSheet("color:#ff6b6b; padding:4px 8px;")
                    if hasattr(self, 'error_details_btn') and self.error_details_btn:
                        self.error_details_btn.setVisible(True)
                else:
                    self.status_label.setStyleSheet("color:#e5e5e5; padding:4px 8px;")
                    if hasattr(self, 'error_details_btn') and self.error_details_btn:
                        self.error_details_btn.setVisible(False)
        except Exception as e:
            print(f"⚠️ Error showing status: {e}")

    def _show_error(self, error_msg, error_obj=None, traceback_str=None):
        """Show error in status bar and store details"""
        try:
            # Store error details
            self._last_error = error_msg
            self._error_traceback = traceback_str
            
            # Show short error message in status bar
            short_msg = error_msg[:50] + "..." if len(error_msg) > 50 else error_msg
            self._show_status(f"❌ {short_msg}", is_error=True)
            
        except Exception as e:
            print(f"⚠️ Error showing error: {e}")

    def _show_error_details(self):
        """Show full error details dialog"""
        try:
            if not self._last_error:
                return
            
            # Create error details dialog
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Error Details")
            dialog.setModal(True)
            dialog.resize(600, 400)
            
            # Layout
            layout = QtWidgets.QVBoxLayout(dialog)
            
            # Error message
            error_label = QtWidgets.QLabel("Error Message:")
            error_label.setStyleSheet("font-weight: bold; color:#ff6b6b; margin-top:10px;")
            layout.addWidget(error_label)
            
            error_text = QtWidgets.QTextEdit()
            error_text.setPlainText(self._last_error)
            error_text.setReadOnly(True)
            error_text.setStyleSheet("""
                QTextEdit { 
                    background:#2c2c2c; 
                    color:#e5e5e5; 
                    border:1px solid #3a3a3a; 
                    border-radius:4px; 
                    padding:8px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """)
            layout.addWidget(error_text)
            
            # Traceback if available
            if self._error_traceback:
                traceback_label = QtWidgets.QLabel("Traceback:")
                traceback_label.setStyleSheet("font-weight: bold; color:#ff6b6b; margin-top:10px;")
                layout.addWidget(traceback_label)
                
                traceback_text = QtWidgets.QTextEdit()
                traceback_text.setPlainText(self._error_traceback)
                traceback_text.setReadOnly(True)
                traceback_text.setStyleSheet("""
                    QTextEdit { 
                        background:#1a1a1a; 
                        color:#ff6b6b; 
                        border:1px solid #3a3a3a; 
                        border-radius:4px; 
                        padding:8px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size:11px;
                    }
                """)
                layout.addWidget(traceback_text)
            
            # Buttons
            button_layout = QtWidgets.QHBoxLayout()
            
            copy_btn = QtWidgets.QPushButton("📋 Copy Error")
            copy_btn.clicked.connect(lambda: self._copy_error_to_clipboard())
            
            close_btn = QtWidgets.QPushButton("❌ Close")
            close_btn.clicked.connect(dialog.close)
            
            button_layout.addWidget(copy_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            # Show dialog
            dialog.exec_()
            
        except Exception as e:
            print(f"⚠️ Error showing error details: {e}")

    def _copy_error_to_clipboard(self):
        """Copy error details to clipboard"""
        try:
            import hou
            clipboard = hou.qt.mainWindow().clipboard()
            
            error_text = f"Error: {self._last_error}\n\n"
            if self._error_traceback:
                error_text += f"Traceback:\n{self._error_traceback}"
            
            clipboard.setText(error_text)
            self._show_status("✅ Error copied to clipboard", is_error=False)
            
        except Exception as e:
            print(f"⚠️ Error copying to clipboard: {e}")

    def _selected_fullpath(self):
        idxs = self.table.selectionModel().selectedRows()
        if not idxs: return None
        src = self.proxy.mapToSource(idxs[0])
        
        # Determine which column contains the file path based on model type
        if isinstance(self.model, AssetTableModel):
            col_idx = AssetTableModel.COL_ASSET
        else:
            col_idx = FileTableModel.COL_SHOT
            
        item = self.model.item(src.row(), col_idx)
        if not item: return None
        return item.data(QtCore.Qt.UserRole+1)
    def _dbl_open(self, proxy_index):
        try:
            if not proxy_index.isValid(): 
                return
                
            src_index = self.proxy.mapToSource(proxy_index)
            
            # Determine which column contains the file path based on model type
            if isinstance(self.model, AssetTableModel):
                col_idx = AssetTableModel.COL_ASSET
            else:
                col_idx = FileTableModel.COL_SHOT
                
            item = self.model.item(src_index.row(), col_idx)
            
            if item:
                fp = item.data(QtCore.Qt.UserRole+1)
                if fp:
                    folder_path = os.path.dirname(fp)
                    open_in_explorer(folder_path)
                    self._show_status(f"📁 Opened folder: {os.path.basename(folder_path)}", is_error=False)
                else:
                    self._show_error("No file path found for selected item")
            else:
                self._show_error("No item found for selection")
                
        except Exception as e:
            import traceback
            error_msg = f"Failed to open folder: {str(e)}"
            traceback_str = traceback.format_exc()
            self._show_error(error_msg, error_obj=e, traceback_str=traceback_str)

    def _open_selected(self):
        """Open the selected file's folder in Explorer"""
        try:
            fp = self._selected_fullpath()
            if fp: 
                folder_path = os.path.dirname(fp)
                open_in_explorer(folder_path)
                self._show_status(f"📁 Opened folder: {os.path.basename(folder_path)}", is_error=False)
            else:
                self._show_error("Please select a file from the list first")
        except Exception as e:
            import traceback
            error_msg = f"Failed to open folder: {str(e)}"
            traceback_str = traceback.format_exc()
            self._show_error(error_msg, error_obj=e, traceback_str=traceback_str)

    def _copy_selected(self):
        """Copy the selected file's path to clipboard"""
        try:
            fp = self._selected_fullpath()
            if fp:
                from mono_tools.qt import QtWidgets
                QtWidgets.QApplication.clipboard().setText(fp)
                self._show_status(f"📋 Copied path: {os.path.basename(fp)}", is_error=False)
            else:
                self._show_error("Please select a file from the list first")
        except Exception as e:
            import traceback
            error_msg = f"Failed to copy path: {str(e)}"
            traceback_str = traceback.format_exc()
            self._show_error(error_msg, error_obj=e, traceback_str=traceback_str)


