import os
from mono_tools.qt import QtCore, QtGui, QtWidgets
import hou
from .fm_helpers import ORG, APP, SUBPATH, collect_files, parse_ver, infer_shot, list_projects, DEFAULT_ROOT, load_tabs_settings, save_tabs_settings
from .fm_models import FileTableModel
from .fm_helpers import open_in_explorer

class MonoFileManager(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mono File Manager")
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setMinimumWidth(920); self.setMinimumHeight(520)
        self.s=QtCore.QSettings(ORG,APP)
        self._build_ui(); self._restore(); QtCore.QTimer.singleShot(0,self._center)
        self._minibar_ref=None

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
        
        # Tabs for subpaths within each type
        self.assets_tabs = QtWidgets.QTabWidget(); self.assets_tabs.setMovable(True); self.assets_tabs.setTabsClosable(True)
        self.assets_tabs.tabBarDoubleClicked.connect(self._rename_tab)
        self.assets_tabs.tabCloseRequested.connect(self._remove_tab)
        
        self.shots_tabs = QtWidgets.QTabWidget(); self.shots_tabs.setMovable(True); self.shots_tabs.setTabsClosable(True)
        self.shots_tabs.tabBarDoubleClicked.connect(self._rename_tab)
        self.shots_tabs.tabCloseRequested.connect(self._remove_tab)
        
        self._init_type_tabs()
        # Initialize current_tabs reference
        self.current_tabs = self.shots_tabs  # Default to shots
        # Per-tab control row
        self.depth_sb=QtWidgets.QSpinBox(); self.depth_sb.setRange(1,10); self.depth_sb.setValue(1)
        exts_lbl=QtWidgets.QLabel(".hip, .hiplc, .hipnc (fixed)")
        b_add_tab=QtWidgets.QPushButton("+ Tab"); b_add_tab.clicked.connect(self._add_tab)
        b_scan=QtWidgets.QPushButton("Scan"); b_scan.clicked.connect(self.scan)
        b_refresh=QtWidgets.QPushButton("Refresh"); b_refresh.clicked.connect(self.scan)
        b_open=QtWidgets.QPushButton("Open in Explorer"); b_open.clicked.connect(self._open_selected)
        b_copy=QtWidgets.QPushButton("Copy Path"); b_copy.clicked.connect(self._copy_selected)
        row=QtWidgets.QHBoxLayout(); row.addWidget(b_scan); row.addWidget(b_refresh); row.addStretch(1); row.addWidget(b_open); row.addWidget(b_copy)
        # Global table will be created per tab
        self.table = None
        g=QtWidgets.QGridLayout(); g.setVerticalSpacing(6); g.setHorizontalSpacing(8)
        g.addWidget(QtWidgets.QLabel("Project Root"),0,0); g.addWidget(self.root_le,0,1); g.addWidget(b_browse,0,2); g.addWidget(self.project_cb,0,3)
        g.addWidget(QtWidgets.QLabel("Type"),1,0); g.addWidget(self.type_tabs,1,1,1,3)
        g.addWidget(QtWidgets.QLabel("Depth"),2,0); g.addWidget(self.depth_sb,2,1); g.addWidget(exts_lbl,2,2); g.addWidget(b_add_tab,2,3)
        lay=QtWidgets.QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(10)
        lay.addWidget(title); lay.addLayout(g); lay.addLayout(row)
        self.setStyleSheet("""
        QDialog { background:#232323; color:#e5e5e5; }
        QLabel { color:#e5e5e5; }
        QLineEdit, QSpinBox { background:#2c2c2c; color:#e5e5e5; border:1px solid #3a3a3a; border-radius:6px; padding:4px 6px; }
        QPushButton { background:#3a3a3a; color:#fff; border:1px solid #4a4a4a; border-radius:8px; padding:6px 10px; }
        QPushButton:hover { background:#4a4a4a; }
        QTableView { background:#1e1e1e; alternate-background-color:#242424; gridline-color:#3a3a3a; selection-background-color:#3d5a99; selection-color:#fff; }
        QHeaderView::section { background:#2a2a2a; color:#dcdcdc; border:0; padding:6px; }
        """)

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
        model = self._active_model()
        if not model: return
        model.removeRows(0,model.rowCount())
        base=self._target_dir()
        if not base or not os.path.isdir(base):
            hou.ui.displayMessage(f"Không tìm thấy thư mục:\n{base or '<empty>'}", severity=hou.severityType.Warning); return
        for f in collect_files(base, depth=self.depth_sb.value()):
            try:
                st=os.stat(f)
                name=os.path.basename(f); ext=os.path.splitext(name)[1].lower()
                ver=parse_ver(name); shot=infer_shot(f); folder=os.path.dirname(f)
                model.add_row(shot,ver,name,ext,folder,st.st_mtime,st.st_size,f)
            except Exception: pass
        proxy=self._active_proxy(); proxy.sort(FileTableModel.COL_MOD, QtCore.Qt.DescendingOrder)
        if self.table:
            for c in (FileTableModel.COL_SHOT,FileTableModel.COL_VER,FileTableModel.COL_EXT,FileTableModel.COL_SIZE): 
                self.table.resizeColumnToContents(c)
        self._save()
        if hasattr(self, "_minibar_ref") and self._minibar_ref:
            self._minibar_ref.populate_from_model(model)

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
            # Auto-scan when project changes
            QtCore.QTimer.singleShot(100, self.scan)

    # ---- Type Tabs ----
    def _init_type_tabs(self):
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
            {"name": "models", "subpath": "Assets/Models", "depth": 2},
            {"name": "textures", "subpath": "Assets/Textures", "depth": 2},
            {"name": "materials", "subpath": "Assets/Materials", "depth": 2}
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

    def _on_type_changed(self, idx):
        """Handle type tab change"""
        if idx == 0:  # Assets
            self.current_tabs = self.assets_tabs
        else:  # Shots
            self.current_tabs = self.shots_tabs
        
        self.s.setValue("current_type", "Assets" if idx == 0 else "Shots")
        self.s.sync()
        
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
        
        # Create table for this tab
        model=FileTableModel(self); proxy=QtCore.QSortFilterProxyModel(self); proxy.setSourceModel(model); proxy.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        table=QtWidgets.QTableView(); table.setModel(proxy); table.setSortingEnabled(True)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows); table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        table.doubleClicked.connect(self._dbl_open); table.verticalHeader().setVisible(False); table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        
        # Store references
        w.model=model; w.proxy=proxy; w.table=table; w.subpath=subpath; w.depth=depth
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

    def _remove_tab(self, idx):
        if not hasattr(self, 'current_tabs'):
            self.current_tabs = self.shots_tabs
            
        if self.current_tabs.count()<=1: return
        name=self.current_tabs.tabText(idx)
        self.current_tabs.removeTab(idx)

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
    def _selected_fullpath(self):
        idxs = self.table.selectionModel().selectedRows()
        if not idxs: return None
        src = self.proxy.mapToSource(idxs[0])
        item = self.model.item(src.row(), FileTableModel.COL_SHOT)
        if not item: return None
        return item.data(QtCore.Qt.UserRole+1)
    def _dbl_open(self, proxy_index):
        if not proxy_index.isValid(): return
        src_index = self.proxy.mapToSource(proxy_index)
        item = self.model.item(src_index.row(), FileTableModel.COL_SHOT)
        if item:
            fp = item.data(QtCore.Qt.UserRole+1)
            if fp:
                folder_path = os.path.dirname(fp)
                open_in_explorer(folder_path)

    def _open_selected(self):
        """Open the selected file's folder in Explorer"""
        fp = self._selected_fullpath()
        if fp: 
            folder_path = os.path.dirname(fp)
            open_in_explorer(folder_path)
        else:
            hou.ui.displayMessage("Vui lòng chọn một file trong danh sách trước", 
                                severity=hou.severityType.Warning)

    def _copy_selected(self):
        """Copy the selected file's path to clipboard"""
        fp = self._selected_fullpath()
        if fp:
            from mono_tools.qt import QtWidgets
            QtWidgets.QApplication.clipboard().setText(fp)
            hou.ui.displayMessage(f"Đã copy path:\n{fp}", severity=hou.severityType.Message)
        else:
            hou.ui.displayMessage("Vui lòng chọn một file trong danh sách trước", 
                                severity=hou.severityType.Warning)


