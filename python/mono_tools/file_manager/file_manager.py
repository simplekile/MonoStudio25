# Mono File Manager + Movable MiniBar (Houdini 21 / Python 3.11 / PySide6)
# - Scan: <ProjectRoot>/02_shots/03_lighting, depth=1, only .hip/.hiplc/.hipnc
# - Table: Shot | Ver | File Name | Ext | Folder | Modified | Size
# - MiniBar: dropdown hiển thị tên file trong popup, nhưng ô hiển thị chỉ hiện tên Shot
# - MiniBar kéo thả tự do, lưu vị trí; menu chuột phải: Lock/Reset

import os, re, platform, subprocess
from datetime import datetime
from mono_tools.qt import QtCore, QtGui, QtWidgets
import hou

ORG="Mono"; APP="FileManager"
SUBPATH=os.path.join("02_shots","03_lighting")
HOUDINI_EXTS={".hip",".hiplc",".hipnc"}
VER_RX=re.compile(r"(?:^|[_\.])v(\d{1,4})(?:[_\.]|$)", re.IGNORECASE)
SHOT_RX=re.compile(r'^(Sh\d+|SH\d+)', re.IGNORECASE)

def _human_size(b):
    try: b=float(b)
    except: return "-"
    for u in ["B","KB","MB","GB","TB"]:
        if b<1024: return f"{b:3.1f} {u}"
        b/=1024
    return f"{b:.1f} PB"

def _open_in_explorer(path):
    if not path or not os.path.exists(path):
        hou.ui.displayMessage(f"Đường dẫn không tồn tại:\n{path or '<empty>'}", 
                             severity=hou.severityType.Warning)
        return
    
    # Ensure we have a directory path
    target_path = path if os.path.isdir(path) else os.path.dirname(path)
    
    if not os.path.isdir(target_path):
        hou.ui.displayMessage(f"Thư mục không tồn tại:\n{target_path}", 
                             severity=hou.severityType.Warning)
        return
    
    sys = platform.system()
    
    try:
        if sys == "Windows":
            # Use explorer with /select to highlight the file if it's a file path
            if os.path.isfile(path):
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
            else:
                subprocess.Popen(["explorer", os.path.normpath(target_path)])
        elif sys == "Darwin":
            subprocess.Popen(["open", target_path])
        else:
            subprocess.Popen(["xdg-open", target_path])
        
    except Exception as e:
        hou.ui.displayMessage(f"Lỗi khi mở explorer:\n{str(e)}", 
                             severity=hou.severityType.Error)

def _get_render_folder_path(hip_file_path):
    """
    Lấy đường dẫn render folder từ hip file path
    Pattern: render/Final/<filename_without_ext>
    Ví dụ: D:/Project/scenes/Sh003_lighting_v002.hip 
           -> D:/Project/render/Final/Sh003_lighting_v002
    """
    if not hip_file_path or hip_file_path == "untitled.hip":
        return None
    
    try:
        # Get the project root (go up from hip file to find project root)
        hip_dir = os.path.dirname(hip_file_path)
        filename = os.path.basename(hip_file_path)
        filename_no_ext = os.path.splitext(filename)[0]
        
        # Try to find project root by looking for common project folders
        # Method 1: Look for parent folder containing "02_shots" or similar structure
        current_dir = hip_dir
        project_root = None
        
        for _ in range(5):  # Search up to 5 levels
            if os.path.exists(os.path.join(current_dir, "render")):
                project_root = current_dir
                break
            parent = os.path.dirname(current_dir)
            if parent == current_dir:  # Reached root
                break
            current_dir = parent
        
        # If not found, assume render folder is at same level as hip file directory
        if not project_root:
            # Go up one or two levels from hip file
            project_root = os.path.dirname(hip_dir)
        
        # Construct render path: <project_root>/render/Final/<filename_no_ext>
        render_folder = os.path.join(project_root, "render", "Final", filename_no_ext)
        
        return render_folder
        
    except Exception as e:
        print(f"⚠️ Error getting render folder path: {e}")
        return None

def _get_current_houdini_file():
    """Lấy thông tin file hiện tại đang mở trong Houdini"""
    try:
        current_file = hou.hipFile.name()
        if current_file and current_file != "untitled.hip":
            return os.path.normpath(current_file)
    except:
        pass
    return None

def _is_current_file(file_path):
    """Kiểm tra xem file path có phải là file hiện tại đang mở không"""
    current = _get_current_houdini_file()
    if not current or not file_path:
        return False
    return os.path.normpath(file_path) == current

def _infer_shot(full_path):
    # Method 1: Từ tên file - Extract shot từ filename pattern (ưu tiên)
    filename = os.path.basename(full_path)
    
    # Pattern: Sh001_*, Sh009_*, SH010_*, etc.
    match = SHOT_RX.match(filename)
    if match:
        shot_name = match.group(1)
        
        # Chuẩn hóa format: Sh009 (chữ S viết hoa, h viết thường)
        shot_upper = shot_name.upper()
        if shot_upper.startswith('SH'):
            result = 'Sh' + shot_upper[2:]  # SH009/sh009 -> Sh009
            return result
        return shot_name  # Giữ nguyên nếu đã đúng format
    
    # Method 2: Từ đường dẫn thư mục - Expect: <root>/02_shots/03_lighting/<SHOT>/file.hip
    parts=os.path.normpath(full_path).split(os.sep)
    try:
        i=parts.index("03_lighting")
        if len(parts)>i+1:
            folder_name = parts[i+1]
            # Kiểm tra xem folder name có phải là filename không (nếu files nằm trực tiếp)
            if '.' not in folder_name:  # Folder thật, không phải filename
                return folder_name
    except ValueError:
        pass
    
    return ""

def _parse_ver(name):
    m=VER_RX.search(name)
    return f"v{int(m.group(1)):03d}" if m else ""

def _increment_version_and_backup(current_filepath, note=""):
    """
    Tăng version của file hiện tại và move version cũ vào folder Vers
    Args:
        current_filepath: Path to current file
        note: Optional note to append after version number (e.g., "_note")
    Returns: (success: bool, new_filepath: str, message: str)
    """
    try:
        if not current_filepath or not os.path.exists(current_filepath):
            return False, "", "File không tồn tại"
        
        # Parse current filename
        dir_path = os.path.dirname(current_filepath)
        filename = os.path.basename(current_filepath)
        name, ext = os.path.splitext(filename)
        
        # Find current version
        ver_match = VER_RX.search(name)
        if not ver_match:
            return False, "", "Không tìm thấy version number trong tên file"
        
        # Get current version number and pattern
        current_ver_num = int(ver_match.group(1))
        new_ver_num = current_ver_num + 1
        
        # Get the full matched pattern (e.g., "_v003_" or ".v001.")
        ver_pattern = ver_match.group(0)  # Full pattern including delimiters
        
        # Extract the version string from the pattern (e.g., "v003" or "v1")
        ver_str = f"v{ver_match.group(1)}"  # e.g., "v003", "v01", "v1"
        
        # Create new version string with proper format
        new_ver_str = f"v{new_ver_num:03d}"  # Always use 3-digit format
        
        # Replace old version string with new one in the pattern
        new_ver_pattern = ver_pattern.replace(ver_str, new_ver_str)
        
        # Build new filename by replacing the entire version pattern
        new_filename = name.replace(ver_pattern, new_ver_pattern)
        
        # Add note if provided (after version, before extension)
        if note and note.strip():
            # Clean note: remove special characters, spaces -> underscore
            clean_note = re.sub(r'[^\w\s-]', '', note.strip())
            clean_note = re.sub(r'[\s]+', '_', clean_note)
            if clean_note:
                new_filename = f"{new_filename}_{clean_note}"
        
        new_filename = new_filename + ext
        new_filepath = os.path.join(dir_path, new_filename)
        
        # Create Vers folder
        vers_folder = os.path.join(dir_path, "Vers")
        if not os.path.exists(vers_folder):
            os.makedirs(vers_folder)
        
        # Move current file to Vers folder
        backup_path = os.path.join(vers_folder, filename)
        
        # If backup file already exists, add timestamp
        if os.path.exists(backup_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_only = os.path.splitext(filename)[0]
            backup_filename = f"{name_only}_{timestamp}{ext}"
            backup_path = os.path.join(vers_folder, backup_filename)
        
        # Save current file first
        hou.hipFile.save()
        
        # Copy current file to backup location
        import shutil
        shutil.copy2(current_filepath, backup_path)
        
        # Save as new version
        hou.hipFile.setName(new_filepath)
        hou.hipFile.save()
        
        # Now delete the old version file (since we've saved as new version)
        # This effectively "moves" it to Vers folder instead of just copying
        try:
            if os.path.exists(current_filepath):
                os.remove(current_filepath)
        except Exception as remove_error:
            # Don't fail the whole operation if we can't delete old file
            pass
        
        # Build success message
        message = f"✅ Saved as {os.path.basename(new_filepath)}\n📦 Old version moved to Vers/"
        if note and note.strip():
            message += f"\n📝 Note: {note}"
        
        return True, new_filepath, message
        
    except Exception as e:
        error_msg = f"Lỗi khi save version: {str(e)}"
        return False, "", error_msg

def _collect_files(base_dir, depth=1):
    if not os.path.isdir(base_dir): return []
    results=[]
    if depth<=1:
        for e in os.scandir(base_dir):
            if e.is_file() and os.path.splitext(e.name)[1].lower() in HOUDINI_EXTS:
                results.append(e.path)
        return results
    return results

# ------------------- Main Table Model -------------------
class _Model(QtGui.QStandardItemModel):
    COL_SHOT=0; COL_VER=1; COL_NAME=2; COL_EXT=3; COL_FOLDER=4; COL_MOD=5; COL_SIZE=6
    HEAD=["Shot","Ver","File Name","Ext","Folder","Modified","Size"]
    def __init__(self,parent=None):
        super().__init__(0,len(self.HEAD),parent)
        self.setHorizontalHeaderLabels(self.HEAD)
    def add_row(self, shot, ver, name, ext, folder, mtime, sz, fullpath):
        vals=[shot,ver,name,ext,folder,datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"),_human_size(sz)]
        items=[]
        for v in vals:
            it=QtGui.QStandardItem(str(v)); it.setEditable(False); items.append(it)
        items[0].setData(fullpath, QtCore.Qt.UserRole+1) # store fullpath
        self.appendRow(items)

# ------------------- Full Dialog -------------------
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

        self.root_le=QtWidgets.QLineEdit()
        b_browse=QtWidgets.QPushButton("Browse…"); b_browse.clicked.connect(self._browse)
        sub_ro=QtWidgets.QLineEdit(SUBPATH); sub_ro.setReadOnly(True)
        self.depth_sb=QtWidgets.QSpinBox(); self.depth_sb.setRange(1,10); self.depth_sb.setValue(1)
        exts_lbl=QtWidgets.QLabel(".hip, .hiplc, .hipnc (fixed)")

        g=QtWidgets.QGridLayout(); g.setVerticalSpacing(6); g.setHorizontalSpacing(8)
        g.addWidget(QtWidgets.QLabel("Project Root"),0,0); g.addWidget(self.root_le,0,1); g.addWidget(b_browse,0,2)
        g.addWidget(QtWidgets.QLabel("Subpath"),1,0); g.addWidget(sub_ro,1,1,1,2)
        g.addWidget(QtWidgets.QLabel("Depth"),2,0); g.addWidget(self.depth_sb,2,1)
        g.addWidget(QtWidgets.QLabel("Extensions"),2,2); g.addWidget(exts_lbl,2,3)

        b_scan=QtWidgets.QPushButton("Scan"); b_scan.clicked.connect(self.scan)
        b_refresh=QtWidgets.QPushButton("Refresh"); b_refresh.clicked.connect(self.scan)
        b_open=QtWidgets.QPushButton("Open in Explorer"); b_open.clicked.connect(self._open_selected)
        b_copy=QtWidgets.QPushButton("Copy Path"); b_copy.clicked.connect(self._copy_selected)
        row=QtWidgets.QHBoxLayout(); row.addWidget(b_scan); row.addWidget(b_refresh); row.addStretch(1); row.addWidget(b_open); row.addWidget(b_copy)

        self.model=_Model(self)
        self.proxy=QtCore.QSortFilterProxyModel(self); self.proxy.setSourceModel(self.model); self.proxy.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.table=QtWidgets.QTableView(); self.table.setModel(self.proxy); self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows); self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.doubleClicked.connect(self._dbl_open); self.table.verticalHeader().setVisible(False); self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)

        lay=QtWidgets.QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(10)
        lay.addWidget(title); lay.addLayout(g); lay.addLayout(row); lay.addWidget(self.table)

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
        if d: self.root_le.setText(d)

    def _save(self):
        self.s.setValue("root", self.root_le.text()); self.s.sync()

    def _restore(self):
        self.root_le.setText(self.s.value("root","",type=str))

    def _target_dir(self):
        root=self.root_le.text().strip()
        return os.path.join(root,SUBPATH) if root else ""

    def scan(self):
        self.model.removeRows(0,self.model.rowCount())
        base=self._target_dir()
        if not base or not os.path.isdir(base):
            hou.ui.displayMessage(f"Không tìm thấy thư mục:\n{base or '<empty>'}", severity=hou.severityType.Warning); return
        for f in _collect_files(base, depth=self.depth_sb.value()):
            try:
                st=os.stat(f)
                name=os.path.basename(f); ext=os.path.splitext(name)[1].lower()
                ver=_parse_ver(name); shot=_infer_shot(f); folder=os.path.dirname(f)
                self.model.add_row(shot,ver,name,ext,folder,st.st_mtime,st.st_size,f)
            except Exception: pass
        self.proxy.sort(_Model.COL_MOD, QtCore.Qt.DescendingOrder)
        for c in (_Model.COL_SHOT,_Model.COL_VER,_Model.COL_EXT,_Model.COL_SIZE):
            self.table.resizeColumnToContents(c)
        self._save()
        if hasattr(self, "_minibar_ref") and self._minibar_ref:
            self._minibar_ref.populate_from_model(self.model)

    def _selected_fullpath(self):
        idxs = self.table.selectionModel().selectedRows()
        if not idxs: 
            return None
            
        src = self.proxy.mapToSource(idxs[0])
        item = self.model.item(src.row(), _Model.COL_SHOT)
        
        if not item:
            return None
            
        fullpath = item.data(QtCore.Qt.UserRole+1)
        return fullpath

    def _dbl_open(self, proxy_index):
        # Get fullpath from the double-clicked item directly
        if not proxy_index.isValid():
            return
            
        src_index = self.proxy.mapToSource(proxy_index)
        item = self.model.item(src_index.row(), _Model.COL_SHOT)
        
        if item:
            fp = item.data(QtCore.Qt.UserRole+1)
            if fp:
                folder_path = os.path.dirname(fp)
                _open_in_explorer(folder_path)

    def _open_selected(self):
        fp=self._selected_fullpath()
        if fp: 
            folder_path = os.path.dirname(fp)
            _open_in_explorer(folder_path)
        else:
            hou.ui.displayMessage("Vui lòng chọn một file trong danh sách trước", 
                                 severity=hou.severityType.Warning)

    def _copy_selected(self):
        fp=self._selected_fullpath()
        if fp: 
            QtWidgets.QApplication.clipboard().setText(fp)
            hou.ui.displayMessage(f"Đã copy path:\n{os.path.basename(fp)}", 
                                 severity=hou.severityType.Message)
        else:
            hou.ui.displayMessage("Vui lòng chọn một file trong danh sách trước", 
                                 severity=hou.severityType.Warning)

# ------------------- Event Filter for Main Window -------------------
class MainWindowEventFilter(QtCore.QObject):
    """Event filter để monitor main window changes và update minibar position"""
    def __init__(self, minibar):
        super().__init__(minibar)
        self.minibar = minibar
        self._last_main_window_geo = None
    
    def eventFilter(self, obj, ev):
        # Skip if minibar is being dragged or recently updated
        if hasattr(self.minibar, '_is_dragging') and self.minibar._is_dragging:
            return super().eventFilter(obj, ev)
        
        if hasattr(self.minibar, '_updating_position') and self.minibar._updating_position:
            return super().eventFilter(obj, ev)
        
        # Chỉ xử lý resize và move events
        if ev.type() in (QtCore.QEvent.Resize, QtCore.QEvent.Move):
            # Use timer để debounce events
            if not hasattr(self.minibar, '_main_window_change_timer'):
                self.minibar._main_window_change_timer = QtCore.QTimer(self.minibar)
                self.minibar._main_window_change_timer.setSingleShot(True)
                self.minibar._main_window_change_timer.timeout.connect(self._on_main_window_changed)
            
            # Only start timer if not already running (prevent rapid restarts)
            if not self.minibar._main_window_change_timer.isActive():
                self.minibar._main_window_change_timer.start(150)  # Balanced: responsive but not too fast
            
        return super().eventFilter(obj, ev)
    
    def _on_main_window_changed(self):
        """Called khi main window thay đổi size/position"""
        try:
            mw = hou.qt.mainWindow()
            if mw and self.minibar and self.minibar.isVisible():
                # Get fresh geometry at time of processing (not cached)
                current_geo = mw.geometry()
                
                # More lenient change detection (allow small changes to pass through)
                significant_change = True
                if self._last_main_window_geo:
                    old_geo = self._last_main_window_geo
                    # Consider change significant if movement > 5px or resize > 10px
                    pos_diff = abs(current_geo.x() - old_geo.x()) + abs(current_geo.y() - old_geo.y())
                    size_diff = abs(current_geo.width() - old_geo.width()) + abs(current_geo.height() - old_geo.height())
                    significant_change = pos_diff > 5 or size_diff > 10
                
                # Chỉ update nếu có significant change
                if significant_change:
                    # Detect type of change
                    change_type = "unknown"
                    if self._last_main_window_geo:
                        old_geo = self._last_main_window_geo
                        size_changed = (current_geo.width() != old_geo.width() or 
                                       current_geo.height() != old_geo.height())
                        pos_changed = (current_geo.x() != old_geo.x() or 
                                      current_geo.y() != old_geo.y())
                        
                        if size_changed and pos_changed:
                            change_type = "resize+move"
                        elif size_changed:
                            change_type = "resize"
                        elif pos_changed:
                            change_type = "move"
                    
                    self._last_main_window_geo = current_geo
                    
                    if os.environ.get('MONO_DEBUG'):
                        print(f"🔄 Main window {change_type}: {current_geo.width()}x{current_geo.height()} at ({current_geo.x()}, {current_geo.y()})")
                    
                    # Update minibar position to maintain relative position
                    self.minibar._update_position_relative_to_main_window()
        except:
            pass

# ------------------- Mini Dropdown (movable) -------------------
class MonoFileMiniBar(QtWidgets.QWidget):
    """Frameless, movable. Dropdown shows files in popup; current display shows Shot only."""
    def __init__(self, manager_factory, parent=None):
        super().__init__(parent or hou.qt.mainWindow())
        # Use Qt.Tool without WindowStaysOnTopHint to keep it within Houdini window only
        # This prevents the minibar from appearing on top of other applications
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setObjectName("MonoMiniBar")
        self.s=QtCore.QSettings(ORG,APP)
        self.manager_factory=manager_factory
        self.manager=None
        self._drag_pos=None
        self._is_dragging=False
        self._locked=self.s.value("minibar_locked", False, type=bool)
        self._last_current_file = None
        self._position_stable_count = 0  # Track consecutive stable positions
        self._last_stable_pos = None     # Last known stable position
        
        # Timer để check file changes
        self._file_check_timer = QtCore.QTimer(self)
        self._file_check_timer.timeout.connect(self._check_file_changes)
        self._file_check_timer.start(2000)  # Check every 2 seconds
        
        # Monitor Houdini main window for changes
        self._setup_main_window_monitoring()

        # Handle area để dễ di chuyển và chuột phải
        self.handle_area = QtWidgets.QLabel("⋮⋮")  # Grip icon
        self.handle_area.setFixedWidth(20)
        self.handle_area.setAlignment(QtCore.Qt.AlignCenter)
        self.handle_area.setToolTip("Drag to move • Right-click for options")
        self.handle_area.setCursor(QtCore.Qt.OpenHandCursor)  # Show drag cursor
        
        # Shot display (clickable để mở dropdown)
        self.shot_display = QtWidgets.QLineEdit()
        self.shot_display.setReadOnly(True)
        self.shot_display.setMinimumWidth(160)
        self.shot_display.setMaximumWidth(160)
        self.shot_display.setToolTip("Click để chọn shot • Chọn shot sẽ mở file trong Houdini")
        self.shot_display.setCursor(QtCore.Qt.PointingHandCursor)  # Cursor pointer
        
        # Override mouse events for shot display
        self.shot_display.mousePressEvent = self._shot_display_clicked
        
        # Hidden combo để lưu data
        self.combo = QtWidgets.QComboBox()
        self.combo.setVisible(False)  # Ẩn combo gốc
        self.combo.currentIndexChanged.connect(self._update_shot_display)

        # 🎛️ Quick Menu button
        self.btn_quick_menu=QtWidgets.QToolButton()
        self.btn_quick_menu.setText("⚙️")
        self.btn_quick_menu.setFixedSize(28, 28)
        self.btn_quick_menu.setToolTip("Quick Menu\n• Reload Scene\n• Restart Houdini\n• Open File Location\n• Open Render Folder")
        self.btn_quick_menu.clicked.connect(self._show_quick_menu)

        # 💾 Save Version button
        self.btn_save_version=QtWidgets.QToolButton()
        self.btn_save_version.setText("💾")
        self.btn_save_version.setFixedSize(28, 28)
        self.btn_save_version.setToolTip("Save Version\n• Increment version number\n• Move old version to Vers folder")
        self.btn_save_version.clicked.connect(self._save_version)

        self.btn_expand=QtWidgets.QToolButton(); 
        self.btn_expand.setText("⚡")  # Chỉ dùng icon
        self.btn_expand.setFixedSize(32, 28)  # Fixed size cho đẹp
        self.btn_expand.setToolTip("Mở giao diện đầy đủ • Tự động scan files")
        self.btn_expand.clicked.connect(self._open_manager)

        lay=QtWidgets.QHBoxLayout(self); lay.setContentsMargins(6,6,8,6); lay.setSpacing(4)
        lay.addWidget(self.handle_area, 0)     # Handle area
        lay.addWidget(self.shot_display, 1)    # Shot display (clickable)
        lay.addWidget(self.btn_quick_menu, 0)  # Quick Menu button
        lay.addWidget(self.btn_save_version, 0)  # Save Version button
        lay.addWidget(self.btn_expand, 0)      # Expand button

        self.setStyleSheet("""
        #MonoMiniBar { background:#2a2a2a; border:1px solid #3a3a3a; border-radius:10px; }
        
        QLabel { 
            color:#888; font-weight:bold; font-size:14px;
            background:transparent;
        }
        QLabel:hover {
            color:#aaa;
            background:rgba(255,255,255,0.1);
            border-radius:4px;
        }
        
        /* QLineEdit styling will be handled dynamically for highlighting */
        
        QToolButton { 
            background:#3a3a3a; color:#fff; border:1px solid #4a4a4a; border-radius:6px; 
            font-size:12px; font-weight:bold;
        }
        QToolButton:hover { 
            background:#4a4a4a; 
        }
        QToolButton:pressed {
            background:#2a2a2a;
        }
        """)

        # Restore position relative to Houdini window
        self._restore_relative_position()
        
        # Show final position after restore (once only)
        final_pos = self.pos()
        print(f"📍 MiniBar positioned at ({final_pos.x()}, {final_pos.y()})")
        
        # Apply initial lock visual feedback
        self._update_lock_visual_feedback()
        
        # Apply initial shot display styling
        self._update_current_shot_highlighting()

        self.show()

    # ----- shot display click -----
    def _shot_display_clicked(self, event):
        """Xử lý click vào shot display để mở dropdown"""
        if event.button() == QtCore.Qt.LeftButton:
            # Dùng QTimer để tránh event conflict
            QtCore.QTimer.singleShot(0, self._show_file_menu)
        event.accept()
    
    # ----- movable -----
    def mousePressEvent(self, ev):
        # Xử lý chuột phải để hiện context menu
        if ev.button() == QtCore.Qt.RightButton:
            self._show_ctx_menu(ev.globalPos())
            return
            
        if self._locked: 
            return
        
        # Kiểm tra widget tại vị trí click
        widget_at_pos = self.childAt(ev.pos())
        
        # Cho phép drag từ:
        # 1. Handle area (grip icon)
        # 2. Empty space trong widget chính
        # 3. Bất kỳ đâu ngoại trừ shot_display và btn_expand
        can_drag = (widget_at_pos is None or 
                   widget_at_pos == self.handle_area or
                   widget_at_pos == self or
                   (hasattr(widget_at_pos, 'parent') and widget_at_pos.parent() == self and
                    widget_at_pos not in [self.shot_display, self.btn_expand, self.combo]))
        
        if can_drag and ev.button() == QtCore.Qt.LeftButton:
            self._drag_pos = ev.globalPos() - self.frameGeometry().topLeft()
            self._is_dragging = True
            
            # Visual feedback: change cursor and slight opacity
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.setWindowOpacity(0.8)
            ev.accept()
        else:
            # Pass event to child widget if we're not handling drag
            super().mousePressEvent(ev)
    
    def mouseMoveEvent(self, ev):
        if self._locked or self._drag_pos is None or not hasattr(self, '_is_dragging'):
            return
        
        if ev.buttons() & QtCore.Qt.LeftButton and self._is_dragging:
            # Smooth dragging with screen boundary checks
            new_pos = ev.globalPos() - self._drag_pos
            
            # Get screen geometry to prevent dragging off-screen
            screen = QtWidgets.QApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry()
                # Keep at least 50px of the widget visible
                min_visible = 50
                new_pos.setX(max(screen_geo.x() - self.width() + min_visible, 
                                min(new_pos.x(), screen_geo.right() - min_visible)))
                new_pos.setY(max(screen_geo.y(), 
                                min(new_pos.y(), screen_geo.bottom() - min_visible)))
            
            self.move(new_pos)
            ev.accept()
    
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self._drag_pos is not None:
            # Reset visual feedback
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.setWindowOpacity(1.0)
            
            # Clean up drag state
            self._drag_pos = None
            self._is_dragging = False
            
            # Save new position
            self._save_relative_position()
            ev.accept()
        else:
            super().mouseReleaseEvent(ev)
    
    def enterEvent(self, ev):
        """Provide visual feedback when hovering over the minibar"""
        if not self._locked and not self._is_dragging:
            # Subtle highlight effect when hovering
            self.setStyleSheet(self.styleSheet().replace(
                "#MonoMiniBar { background:#2a2a2a;",
                "#MonoMiniBar { background:#303030;"
            ))
        super().enterEvent(ev)
    
    def leaveEvent(self, ev):
        """Reset visual feedback when leaving the minibar"""
        if not self._is_dragging:
            # Reset to original background
            self.setStyleSheet(self.styleSheet().replace(
                "#MonoMiniBar { background:#303030;",
                "#MonoMiniBar { background:#2a2a2a;"
            ))
        super().leaveEvent(ev)
    
    def moveEvent(self, ev):
        """Save position when widget is moved by any means"""
        super().moveEvent(ev)
        # Only save if move is not part of dragging (to avoid excessive saves during drag)
        if not self._is_dragging and not self._locked:
            # Use QTimer to debounce rapid move events
            if not hasattr(self, '_move_save_timer'):
                self._move_save_timer = QtCore.QTimer(self)
                self._move_save_timer.setSingleShot(True)
                self._move_save_timer.timeout.connect(self._save_relative_position)
            
            # Delay save to avoid excessive writes during window management operations
            self._move_save_timer.start(500)  # Save after 500ms of no movement
    
    def resizeEvent(self, ev):
        """Save position when widget is resized (future-proofing)"""
        super().resizeEvent(ev)
        # Save position after resize to account for size changes
        if not hasattr(self, '_resize_save_timer'):
            self._resize_save_timer = QtCore.QTimer(self)
            self._resize_save_timer.setSingleShot(True)  
            self._resize_save_timer.timeout.connect(self._save_relative_position)
        
        self._resize_save_timer.start(300)  # Save after resize completes
    
    def closeEvent(self, ev):
        """Save position when widget is closed by any means"""
        self._save_relative_position()
        
        # Clean up timers
        if hasattr(self, '_file_check_timer'):
            self._file_check_timer.stop()
        if hasattr(self, '_move_save_timer'):
            self._move_save_timer.stop()
        if hasattr(self, '_resize_save_timer'):
            self._resize_save_timer.stop()
        if hasattr(self, '_main_window_change_timer'):
            self._main_window_change_timer.stop()
        
        # Clean up event filter
        if hasattr(self, '_main_window_filter'):
            try:
                mw = hou.qt.mainWindow()
                if mw:
                    mw.removeEventFilter(self._main_window_filter)
            except:
                pass
            
        super().closeEvent(ev)

    def _show_ctx_menu(self, global_pos):
        m=QtWidgets.QMenu(self)
        m.setStyleSheet("""
            QMenu { background:#1f1f1f; color:#e5e5e5; border:1px solid #3a3a3a; }
            QMenu::item { padding:6px 12px; }
            QMenu::item:selected { background:#3d5a99; }
        """)
        
        act_lock=m.addAction("Lock position ✓" if self._locked else "Lock position")
        act_reset=m.addAction("Reset to default position")
        m.addSeparator()
        act_close=m.addAction("Close MiniBar")
        
        a=m.exec_(global_pos)
        if a==act_lock:
            self._locked=not self._locked
            self.s.setValue("minibar_locked", self._locked); self.s.sync()
            # Update visual feedback based on lock state
            self._update_lock_visual_feedback()
        elif a==act_reset:
            self._snap_top_right()
        elif a==act_close:
            self._close_minibar()

    def _snap_top_right(self):
        mw=hou.qt.mainWindow()
        if not mw: return
        geo=mw.geometry()
        self.adjustSize()
        # New default position: rel(0.915, 0.000) = 91.5% width, 0% height (top edge)
        new_x = geo.x() + int(0.915 * geo.width()) - self.width()
        new_y = geo.y() + int(0.000 * geo.height())
        self.move(new_x, new_y)
        
        # Print final position after move
        final_pos = self.pos()
        final_rel_x = (final_pos.x() + self.width() - geo.x()) / geo.width()
        final_rel_y = (final_pos.y() - geo.y()) / geo.height()
        print(f"🎯 Snap to default: rel({final_rel_x:.3f}, {final_rel_y:.3f}) | pos({final_pos.x()}, {final_pos.y()})")
        
        # Save the new position
        self._save_relative_position()
    
    def _update_lock_visual_feedback(self):
        """Update visual feedback based on lock state"""
        if self._locked:
            # Locked state - more muted colors and lock icon in handle
            self.handle_area.setText("🔒")
            self.handle_area.setToolTip("Position locked • Right-click to unlock")
            self.handle_area.setCursor(QtCore.Qt.ForbiddenCursor)
            # Add slight red tint to indicate locked state
            self.setStyleSheet(self.styleSheet().replace(
                "border:1px solid #3a3a3a;",
                "border:1px solid #5a3a3a;"
            ))
        else:
            # Unlocked state - normal appearance
            self.handle_area.setText("⋮⋮")
            self.handle_area.setToolTip("Drag to move • Right-click for options")
            self.handle_area.setCursor(QtCore.Qt.OpenHandCursor)
            # Reset to normal border color
            self.setStyleSheet(self.styleSheet().replace(
                "border:1px solid #5a3a3a;",
                "border:1px solid #3a3a3a;"
            ))
        
    def _close_minibar(self):
        """Đóng minibar và clear global reference"""
        global _active_minibar
        
        # Save position before closing
        self._save_relative_position()
        
        # Clean up timers
        if hasattr(self, '_file_check_timer'):
            self._file_check_timer.stop()
        if hasattr(self, '_move_save_timer'):
            self._move_save_timer.stop()
        if hasattr(self, '_resize_save_timer'):
            self._resize_save_timer.stop()
        if hasattr(self, '_main_window_change_timer'):
            self._main_window_change_timer.stop()
        
        # Clean up event filter
        if hasattr(self, '_main_window_filter'):
            try:
                mw = hou.qt.mainWindow()
                if mw:
                    mw.removeEventFilter(self._main_window_filter)
            except:
                pass
        
        self.hide()
        self.deleteLater()
        _active_minibar = None
        
    def _save_relative_position(self):
        """Lưu vị trí tương đối so với Houdini window với validation tốt hơn"""
        try:
            # Prevent cascading updates during automatic positioning
            if hasattr(self, '_updating_position') and self._updating_position:
                return
                
            mw = hou.qt.mainWindow()
            if not mw or not mw.isVisible():
                return
                
            hou_geo = mw.geometry()
            my_pos = self.pos()
            
            # Validate geometries
            if hou_geo.width() <= 0 or hou_geo.height() <= 0:
                return
            
            # Lưu offset từ góc phải-trên của Houdini window (pixel-based)
            # Điều này sẽ chính xác hơn khi resize vì không phụ thuộc vào tỷ lệ
            hou_right = hou_geo.x() + hou_geo.width()
            hou_top = hou_geo.y()
            
            minibar_right = my_pos.x() + self.width()
            minibar_top = my_pos.y()
            
            # Offset từ góc phải-trên của Houdini (âm = bên trong, dương = bên ngoài)
            offset_x = minibar_right - hou_right  # Khoảng cách từ mép phải
            offset_y = minibar_top - hou_top      # Khoảng cách từ mép trên
            
            # Tính relative position để backup (fallback cho old logic)
            rel_x = (minibar_right - hou_geo.x()) / hou_geo.width()
            rel_y = (minibar_top - hou_geo.y()) / hou_geo.height()
            
            # Clamp values trong khoảng hợp lý để tránh vị trí không hợp lệ
            rel_x = max(-0.5, min(1.5, rel_x))  # Allow some off-screen positioning
            rel_y = max(-0.2, min(1.2, rel_y))
            
            # Chỉ save nếu vị trí thay đổi đáng kể (tránh spam)
            old_offset_x = self.s.value("minibar_offset_x", -85, type=int)
            old_offset_y = self.s.value("minibar_offset_y", 0, type=int)
            
            threshold = 5  # Minimum pixel change to trigger save
            if abs(offset_x - old_offset_x) > threshold or abs(offset_y - old_offset_y) > threshold:
                # Save offset-based position (primary method)
                self.s.setValue("minibar_offset_x", offset_x)
                self.s.setValue("minibar_offset_y", offset_y)
                
                # Save relative position (backup method)
                self.s.setValue("minibar_rel_x", rel_x)
                self.s.setValue("minibar_rel_y", rel_y)
                
                # Also save absolute position as backup
                self.s.setValue("minibar_abs_x", my_pos.x())
                self.s.setValue("minibar_abs_y", my_pos.y())
                
                self.s.sync()
                
                # Debug info - always print relative position
                print(f"📍 MiniBar rel position: ({rel_x:.3f}, {rel_y:.3f}) | pos({my_pos.x()}, {my_pos.y()}) | offset({offset_x}, {offset_y})")
                if os.environ.get('MONO_DEBUG'):
                    print(f"💾 MiniBar saved: pos({my_pos.x()}, {my_pos.y()}) -> offset({offset_x}, {offset_y}) rel({rel_x:.3f}, {rel_y:.3f}) | Houdini: {hou_geo.width()}x{hou_geo.height()}")
                    
        except Exception as e:
            # Fail silently but log if debug mode
            if os.environ.get('MONO_DEBUG'):
                print(f"⚠️ Failed to save minibar position: {e}")
    
    def _update_position_relative_to_main_window(self):
        """Cập nhật vị trí minibar theo main window mà vẫn giữ vị trí tương đối"""
        try:
            # Set flag to prevent save cascade
            self._updating_position = True
            
            mw = hou.qt.mainWindow()
            if not mw or not mw.isVisible():
                return
                
            hou_geo = mw.geometry()
            if hou_geo.width() <= 0 or hou_geo.height() <= 0:
                return
                
            # Method 1: Use offset-based positioning (more accurate for resize)
            offset_x = self.s.value("minibar_offset_x", -85, type=int)  # Default: corresponds to rel_x=0.915
            offset_y = self.s.value("minibar_offset_y", 0, type=int)    # Default: corresponds to rel_y=0.000
            
            # Store current minibar position before calculation
            current_minibar_pos = self.pos()
            
            # Tính vị trí từ góc phải-trên của Houdini window
            hou_right = hou_geo.x() + hou_geo.width()
            hou_top = hou_geo.y()
            
            # Vị trí góc phải-trên của minibar
            minibar_right = hou_right + offset_x
            minibar_top = hou_top + offset_y
            
            # Tính vị trí góc trái-trên của minibar (pos() của widget)
            new_x = minibar_right - self.width()
            new_y = minibar_top
            
            # Debug info for offset calculation
            if os.environ.get('MONO_DEBUG'):
                print(f"🔧 Position calculation:")
                print(f"   Houdini: {hou_geo.width()}x{hou_geo.height()} at ({hou_geo.x()}, {hou_geo.y()})")
                print(f"   Offset: ({offset_x}, {offset_y})")
                print(f"   Current minibar: ({current_minibar_pos.x()}, {current_minibar_pos.y()})")
                print(f"   Calculated: ({new_x}, {new_y})")
            
            # Validate position is on screen
            screen = QtWidgets.QApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry()
                
                # Clamp to screen bounds
                min_visible = 50
                new_x = max(screen_geo.x() - self.width() + min_visible, 
                           min(new_x, screen_geo.right() - min_visible))
                new_y = max(screen_geo.y(), 
                           min(new_y, screen_geo.bottom() - min_visible))
            
            # Validate calculated position before move
            current_pos = self.pos()
            distance_moved = abs(new_x - current_pos.x()) + abs(new_y - current_pos.y())
            
            # Only move if position change is significant (avoid micro-adjustments)
            if distance_moved > 3:  # Balanced threshold: responsive but prevents micro-drift
                # Additional validation: prevent extreme positions
                rel_x_check = (new_x + self.width() - hou_geo.x()) / hou_geo.width()
                rel_y_check = (new_y - hou_geo.y()) / hou_geo.height()
                
                # Validate relative position is reasonable (tighter bounds to prevent drift)
                if 0.85 <= rel_x_check <= 1.05 and -0.1 <= rel_y_check <= 0.1:
                    # Check if position is stable (similar to last known good position)
                    if hasattr(self, '_last_stable_pos') and self._last_stable_pos:
                        stable_distance = abs(new_x - self._last_stable_pos.x()) + abs(new_y - self._last_stable_pos.y())
                        if stable_distance < 5:  # Very close to last stable position
                            self._position_stable_count += 1
                        else:
                            self._position_stable_count = 0
                            self._last_stable_pos = QtCore.QPoint(new_x, new_y)
                    else:
                        self._last_stable_pos = QtCore.QPoint(new_x, new_y)
                        self._position_stable_count = 0
                    
                    # Skip update if position has been stable for too long (prevent micro-drift)
                    if self._position_stable_count < 3:  # Allow max 3 consecutive stable updates
                        # Move to new position
                        self.move(new_x, new_y)
                        
                        # Debug info
                        if os.environ.get('MONO_DEBUG'):
                            print(f"📍 MiniBar updated: offset({offset_x}, {offset_y}) -> pos({new_x}, {new_y}) | stable_count: {self._position_stable_count}")
                    else:
                        if os.environ.get('MONO_DEBUG'):
                            print(f"🔒 Position locked (stable count: {self._position_stable_count})")
                else:
                    if os.environ.get('MONO_DEBUG'):
                        print(f"⚠️ Position validation failed: rel({rel_x_check:.3f}, {rel_y_check:.3f}) out of bounds")
            else:
                if os.environ.get('MONO_DEBUG'):
                    print(f"📍 Position unchanged (distance: {distance_moved}px)")
                
        except Exception as e:
            if os.environ.get('MONO_DEBUG'):
                print(f"⚠️ Error updating minibar position: {e}")
        finally:
            # Clear update flag
            self._updating_position = False
    
    def _migrate_old_default_position(self):
        """Migration để cập nhật từ vị trí mặc định cũ sang mới"""
        try:
            # Check if migration has already been done
            migration_done = self.s.value("minibar_position_migrated_v2", False, type=bool)
            if migration_done:
                return
                
            # Kiểm tra xem có phải đang sử dụng vị trí mặc định cũ không
            current_rel_x = self.s.value("minibar_rel_x", None)
            current_rel_y = self.s.value("minibar_rel_y", None)
            
            # Nếu chưa có settings nào hoặc đang sử dụng vị trí gần mặc định cũ (0.85, 0.05)
            should_migrate = False
            
            if current_rel_x is None or current_rel_y is None:
                # Chưa có settings -> sử dụng default mới
                should_migrate = True
                print("🔄 First time setup - using new default position...")
            elif (abs(float(current_rel_x) - 0.85) < 0.05 and 
                  abs(float(current_rel_y) - 0.05) < 0.05):
                # Đang ở gần vị trí mặc định cũ -> migrate
                should_migrate = True
                print("🔄 Migrating minibar from old default position to new position...")
            
            if should_migrate:
                # Xóa settings cũ để force sử dụng default mới
                self.s.remove("minibar_rel_x")
                self.s.remove("minibar_rel_y")
                self.s.remove("minibar_offset_x") 
                self.s.remove("minibar_offset_y")
                self.s.remove("minibar_abs_x")
                self.s.remove("minibar_abs_y")
                
                # Mark migration as done
                self.s.setValue("minibar_position_migrated_v2", True)
                self.s.sync()
                
                # Snap to new default position
                self._snap_top_right()
                print("✅ Migration completed - using new default position rel(0.915, 0.000)")
                
        except Exception as e:
            print(f"⚠️ Error during position migration: {e}")
    

    def _restore_relative_position(self):
        """Khôi phục vị trí với fallback cho nhiều trường hợp"""
        try:
            mw = hou.qt.mainWindow()
            if not mw or not mw.isVisible():
                self._snap_top_right()
                return
            
            self.adjustSize()  # Ensure proper size first
            
            # Check if we need to migrate from old position defaults
            # self._migrate_old_default_position()  # Disabled - keep new position only
            
            # Method 1: Try offset-based position (preferred - more accurate)
            hou_geo = mw.geometry()
            if hou_geo.width() > 0 and hou_geo.height() > 0:
                offset_x = self.s.value("minibar_offset_x", None, type=int)
                offset_y = self.s.value("minibar_offset_y", None, type=int)
                
                if offset_x is not None and offset_y is not None:
                    # Use offset-based positioning
                    hou_right = hou_geo.x() + hou_geo.width()
                    hou_top = hou_geo.y()
                    
                    minibar_right = hou_right + offset_x
                    minibar_top = hou_top + offset_y
                    
                    new_x = minibar_right - self.width()
                    new_y = minibar_top
                else:
                    # Fallback to relative position method
                    rel_x = self.s.value("minibar_rel_x", 0.915, type=float)
                    rel_y = self.s.value("minibar_rel_y", 0.000, type=float)
                    
                    # Tính vị trí absolute từ vị trí tương đối
                    new_x = hou_geo.x() + int(rel_x * hou_geo.width()) - self.width()
                    new_y = hou_geo.y() + int(rel_y * hou_geo.height())
                
                # Validate calculated position
                screen = QtWidgets.QApplication.primaryScreen()
                if screen:
                    screen_geo = screen.availableGeometry()
                    
                    # Check if position is reasonable
                    is_valid_pos = (screen_geo.x() - 100 <= new_x <= screen_geo.right() + 100 and
                                   screen_geo.y() - 50 <= new_y <= screen_geo.bottom() + 50)
                    
                    if is_valid_pos:
                        # Clamp to screen bounds but allow some off-screen
                        min_visible = 50
                        original_x, original_y = new_x, new_y
                        new_x = max(screen_geo.x() - self.width() + min_visible, 
                                   min(new_x, screen_geo.right() - min_visible))
                        new_y = max(screen_geo.y(), 
                                   min(new_y, screen_geo.bottom() - min_visible))
                        
                        # Debug clamping if position changed
                        if os.environ.get('MONO_DEBUG') and (original_x != new_x or original_y != new_y):
                            print(f"🔧 Position clamped: ({original_x}, {original_y}) -> ({new_x}, {new_y})")
                            print(f"   Screen bounds: {screen_geo.width()}x{screen_geo.height()} at ({screen_geo.x()}, {screen_geo.y()})")
                        
                        self.move(new_x, new_y)
                        
                        # Verify actual position after move
                        actual_pos = self.pos()
                        if os.environ.get('MONO_DEBUG') and (actual_pos.x() != new_x or actual_pos.y() != new_y):
                            print(f"⚠️ Position mismatch after move: expected({new_x}, {new_y}) vs actual({actual_pos.x()}, {actual_pos.y()})")
                        
                        # Show which method was used and calculate final relative position
                        final_pos = self.pos()
                        final_rel_x = (final_pos.x() + self.width() - hou_geo.x()) / hou_geo.width()
                        final_rel_y = (final_pos.y() - hou_geo.y()) / hou_geo.height()
                        
                        if offset_x is not None and offset_y is not None:
                            print(f"📍 Restored using offset method: offset({offset_x}, {offset_y}) -> pos({new_x}, {new_y}) -> rel({final_rel_x:.3f}, {final_rel_y:.3f})")
                        else:
                            print(f"📍 Restored using relative method: rel({rel_x:.3f}, {rel_y:.3f}) -> pos({new_x}, {new_y}) -> final_rel({final_rel_x:.3f}, {final_rel_y:.3f})")
                            
                        # Show final position only in debug mode to avoid spam
                        if os.environ.get('MONO_DEBUG'):
                            final_pos = self.pos()
                            print(f"📍 MiniBar positioned at ({final_pos.x()}, {final_pos.y()})")
                        return
            
            # Method 2: Fallback to absolute position if available
            abs_x = self.s.value("minibar_abs_x", None, type=int)
            abs_y = self.s.value("minibar_abs_y", None, type=int)
            
            if abs_x is not None and abs_y is not None:
                screen = QtWidgets.QApplication.primaryScreen()
                if screen:
                    screen_geo = screen.availableGeometry()
                    # Validate absolute position is on screen
                    if (screen_geo.contains(abs_x + 25, abs_y + 25)):  # At least 25px visible
                        self.move(abs_x, abs_y)
                        if os.environ.get('MONO_DEBUG'):
                            print(f"📍 Restored absolute position: ({abs_x}, {abs_y})")
                        return
            
            # Method 3: Fallback to default position
            self._snap_top_right()
            if os.environ.get('MONO_DEBUG'):
                print("📍 Used default top-right position")
                
        except Exception as e:
            if os.environ.get('MONO_DEBUG'):
                print(f"⚠️ Error restoring position: {e}")
            self._snap_top_right()

    # ----- Quick Menu -----
    def _show_quick_menu(self):
        """Hiển thị Quick Menu với các tùy chọn nhanh"""
        menu = QtWidgets.QMenu(self)
        
        # Reload Scene action
        reload_action = menu.addAction("🔄 Reload Scene")
        reload_action.setToolTip("Reload current Houdini scene file")
        reload_action.triggered.connect(self._reload_scene)
        
        # Restart Houdini action
        restart_action = menu.addAction("🔃 Restart Houdini")
        restart_action.setToolTip("Restart Houdini application")
        restart_action.triggered.connect(self._restart_houdini)
        
        menu.addSeparator()
        
        # Open File Location action
        location_action = menu.addAction("📁 Open File Location")
        location_action.setToolTip("Open current scene file location in Explorer")
        location_action.triggered.connect(self._open_current_file_location)
        
        # Open Render Folder action
        render_action = menu.addAction("🎬 Open Render Folder")
        render_action.setToolTip("Open render output folder for current scene")
        render_action.triggered.connect(self._open_render_folder)
        
        # Show menu at button position
        button_rect = self.btn_quick_menu.geometry()
        menu_pos = self.mapToGlobal(button_rect.bottomLeft())
        menu.exec_(menu_pos)

    def _reload_scene(self):
        """Reload current Houdini scene"""
        try:
            current_file = hou.hipFile.name()
            if current_file and current_file != "untitled.hip":
                # Save current file first if modified
                if hou.hipFile.hasUnsavedChanges():
                    result = hou.ui.displayMessage(
                        "Scene has unsaved changes. Save before reloading?",
                        buttons=("Save & Reload", "Reload Without Saving", "Cancel"),
                        severity=hou.severityType.ImportantMessage
                    )
                    if result == 0:  # Save & Reload
                        hou.hipFile.save()
                        hou.hipFile.load(current_file)
                        print(f"✅ Scene saved and reloaded: {os.path.basename(current_file)}")
                    elif result == 1:  # Reload Without Saving
                        hou.hipFile.load(current_file)
                        print(f"✅ Scene reloaded: {os.path.basename(current_file)}")
                    # else: Cancel - do nothing
                else:
                    hou.hipFile.load(current_file)
                    print(f"✅ Scene reloaded: {os.path.basename(current_file)}")
            else:
                hou.ui.displayMessage("No scene file to reload (untitled scene)", 
                                     severity=hou.severityType.Warning)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to reload scene:\n{str(e)}", 
                                 severity=hou.severityType.Error)

    def _restart_houdini(self):
        """Restart Houdini application"""
        try:
            result = hou.ui.displayMessage(
                "This will restart Houdini. Any unsaved changes will be lost.\n\nContinue?",
                buttons=("Restart", "Cancel"),
                severity=hou.severityType.ImportantMessage
            )
            if result == 0:  # Restart
                print("🔃 Restarting Houdini...")
                # Save current session if possible
                try:
                    current_file = hou.hipFile.name()
                    if current_file and current_file != "untitled.hip" and hou.hipFile.hasUnsavedChanges():
                        save_result = hou.ui.displayMessage(
                            "Save current scene before restart?",
                            buttons=("Save", "Don't Save"),
                            severity=hou.severityType.Message
                        )
                        if save_result == 0:
                            hou.hipFile.save()
                except Exception as save_error:
                    print(f"⚠️ Error during save: {save_error}")
                
                # Try different restart methods
                try:
                    # Method 1: Try hou.exit with restart parameter (preferred)
                    print("🔄 Method 1: Trying hou.exit(restart=True)...")
                    hou.exit(restart=True)
                except Exception as exit_error:
                    print(f"⚠️ hou.exit(restart=True) failed: {exit_error}")
                    try:
                        # Method 2: Alternative restart method using subprocess
                        print("🔄 Method 2: Using subprocess to restart...")
                        import subprocess
                        import sys
                        import os
                        
                        # Get Houdini executable path
                        houdini_exe = sys.executable
                        print(f"📍 Current executable: {houdini_exe}")
                        
                        if "houdini" not in houdini_exe.lower():
                            # Try to find houdini executable
                            hfs_path = os.environ.get("HFS", "")
                            print(f"📍 HFS environment: {hfs_path}")
                            houdini_bin = os.path.join(hfs_path, "bin", "houdini.exe")
                            print(f"📍 Checking Houdini path: {houdini_bin}")
                            if os.path.exists(houdini_bin):
                                houdini_exe = houdini_bin
                                print(f"✅ Found Houdini executable: {houdini_exe}")
                            else:
                                print(f"❌ Houdini executable not found at: {houdini_bin}")
                        
                        print(f"🔃 Attempting restart via subprocess: {houdini_exe}")
                        
                        if os.path.exists(houdini_exe):
                            # Get current scene file to restore after restart
                            current_scene = None
                            try:
                                current_scene = hou.hipFile.name()
                                if current_scene == "untitled.hip":
                                    current_scene = None
                            except:
                                pass
                            
                            # Build command with scene file if available
                            cmd = [houdini_exe]
                            if current_scene and os.path.exists(current_scene):
                                cmd.append(current_scene)
                                print(f"📁 Will reopen scene: {os.path.basename(current_scene)}")
                            
                            # Start new instance
                            try:
                                print(f"🚀 Starting command: {' '.join(cmd)}")
                                process = subprocess.Popen(cmd, shell=False, cwd=os.path.dirname(houdini_exe))
                                print(f"✅ New Houdini instance started with PID: {process.pid}")
                                
                                # Use QTimer to delay exit (better than time.sleep in GUI)
                                from mono_tools.qt import QtCore
                                def delayed_exit():
                                    print("👋 Closing current instance...")
                                    hou.exit()
                                
                                QtCore.QTimer.singleShot(1500, delayed_exit)  # 1.5 second delay
                                
                                # Show user feedback
                                hou.ui.displayMessage(
                                    "🔃 Houdini restart initiated!\n\n✅ New instance starting...\n👋 Current instance will close in 1.5 seconds",
                                    severity=hou.severityType.Message,
                                    default_choice=0,
                                    close_choice=0
                                )
                                
                            except Exception as popen_error:
                                print(f"❌ Failed to start subprocess: {popen_error}")
                                raise popen_error
                            
                        else:
                            raise Exception(f"Houdini executable not found: {houdini_exe}")
                        
                    except Exception as subprocess_error:
                        print(f"⚠️ Subprocess restart failed: {subprocess_error}")
                        # Method 3: Simple exit (user needs to manually restart)
                        result = hou.ui.displayMessage(
                            "Automatic restart failed. Houdini will close.\n\nPlease restart Houdini manually.",
                            buttons=("Close Houdini", "Cancel"),
                            severity=hou.severityType.Warning
                        )
                        if result == 0:
                            hou.exit()
                        
        except Exception as e:
            hou.ui.displayMessage(f"Failed to restart Houdini:\n{str(e)}", 
                                 severity=hou.severityType.Error)

    def _open_current_file_location(self):
        """Open current scene file location in Explorer"""
        try:
            current_file = hou.hipFile.name()
            if current_file and current_file != "untitled.hip":
                if os.path.exists(current_file):
                    _open_in_explorer(current_file)
                    print(f"📁 Opened location: {os.path.dirname(current_file)}")
                else:
                    hou.ui.displayMessage(f"File not found:\n{current_file}", 
                                         severity=hou.severityType.Warning)
            else:
                hou.ui.displayMessage("No scene file to open (untitled scene)", 
                                     severity=hou.severityType.Warning)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to open file location:\n{str(e)}", 
                                 severity=hou.severityType.Error)

    def _open_render_folder(self):
        """Open render output folder for current scene"""
        try:
            current_file = hou.hipFile.name()
            
            if not current_file or current_file == "untitled.hip":
                hou.ui.displayMessage(
                    "No scene file to find render folder (untitled scene)", 
                    severity=hou.severityType.Warning
                )
                return
            
            # Get render folder path
            render_folder = _get_render_folder_path(current_file)
            
            if not render_folder:
                hou.ui.displayMessage(
                    "Could not determine render folder path", 
                    severity=hou.severityType.Warning
                )
                return
            
            # Check if folder exists
            if os.path.exists(render_folder):
                _open_in_explorer(render_folder)
                print(f"🎬 Opened render folder: {render_folder}")
            else:
                # Folder doesn't exist, ask if user wants to create it
                result = hou.ui.displayMessage(
                    f"Render folder does not exist:\n{render_folder}\n\n"
                    "Would you like to create it?",
                    buttons=("Create & Open", "Cancel"),
                    severity=hou.severityType.Message,
                    default_choice=0,
                    close_choice=1,
                    title="Render Folder Not Found"
                )
                
                if result == 0:  # Create & Open
                    try:
                        os.makedirs(render_folder, exist_ok=True)
                        _open_in_explorer(render_folder)
                        print(f"🎬 Created and opened render folder: {render_folder}")
                    except Exception as create_error:
                        hou.ui.displayMessage(
                            f"Failed to create render folder:\n{str(create_error)}", 
                            severity=hou.severityType.Error
                        )
                        
        except Exception as e:
            hou.ui.displayMessage(
                f"Failed to open render folder:\n{str(e)}", 
                severity=hou.severityType.Error
            )

    def _save_version(self):
        """Save incremented version and move old file to Vers folder"""
        try:
            current_file = hou.hipFile.name()
            
            # Check if file is saved
            if not current_file or current_file == "untitled.hip":
                hou.ui.displayMessage(
                    "Please save the scene file first before creating a version.",
                    severity=hou.severityType.Warning
                )
                return
            
            # Check if file exists
            if not os.path.exists(current_file):
                hou.ui.displayMessage(
                    f"Current file not found:\n{current_file}",
                    severity=hou.severityType.Warning
                )
                return
            
            # Parse current filename to show example
            current_basename = os.path.basename(current_file)
            current_name, current_ext = os.path.splitext(current_basename)
            
            # Get current version and create example preview
            ver_match = VER_RX.search(current_name)
            if ver_match:
                current_ver_num = int(ver_match.group(1))
                next_ver_num = current_ver_num + 1
                
                # Use same logic as _increment_version_and_backup
                ver_pattern = ver_match.group(0)  # Full pattern e.g., "_v003_"
                ver_str = f"v{ver_match.group(1)}"  # Version string e.g., "v003"
                new_ver_str = f"v{next_ver_num:03d}"  # New version e.g., "v004"
                new_ver_pattern = ver_pattern.replace(ver_str, new_ver_str)
                
                # Create example filename without note
                example_name_no_note = current_name.replace(ver_pattern, new_ver_pattern)
                example_no_note = f"{example_name_no_note}{current_ext}"
                
                # Create example filename with note
                example_with_note = f"{example_name_no_note}_note{current_ext}"
            else:
                example_no_note = f"{current_name}{current_ext}"
                example_with_note = f"{current_name}_note{current_ext}"
            
            # Ask user if they want to add a note
            note = ""
            note_input = hou.ui.readInput(
                "Add a note to this version? (optional)\n\n"
                f"Current: {current_basename}\n"
                f"New (no note): {example_no_note}\n"
                f"New (with note): {example_with_note}\n\n"
                "Enter note below (leave empty to skip):",
                buttons=("Save", "Cancel"),
                severity=hou.severityType.Message,
                default_choice=0,
                close_choice=1,
                title="Save Version"
            )
            
            # note_input returns (button_index, text_value)
            # Button 0 = Save, Button 1 = Cancel
            if note_input[0] != 0:
                # User cancelled
                return
            
            # User clicked Save - check if they entered a note
            if note_input[1].strip():
                note = note_input[1].strip()
            
            # Call the increment version function
            success, new_filepath, message = _increment_version_and_backup(current_file, note)
            
            if success:
                # Update shot display to reflect new file
                self._check_file_changes()
                
                # Show success message
                hou.ui.displayMessage(
                    message,
                    severity=hou.severityType.Message,
                    title="Save Version Success"
                )
            else:
                # Show error message
                hou.ui.displayMessage(
                    message,
                    severity=hou.severityType.Error,
                    title="Save Version Failed"
                )
                
        except Exception as e:
            error_msg = f"Unexpected error during save version:\n{str(e)}"
            print(f"❌ {error_msg}")
            hou.ui.displayMessage(
                error_msg,
                severity=hou.severityType.Error,
                title="Save Version Error"
            )

    # ----- manager -----
    def _open_manager(self):
        if not self.manager:
            self.manager=self.manager_factory()
            self.manager._minibar_ref=self
        
        # Tự động scan khi mở giao diện chính
        if self.manager.root_le.text().strip():  # Nếu đã có project root
            QtCore.QTimer.singleShot(100, self.manager.scan)  # Delay nhỏ để UI load xong
            
        self.manager.show(); self.manager.raise_(); self.manager.activateWindow()

    def _show_file_menu(self):
        """Hiển thị menu dropdown với danh sách shot (chọn version mới nhất)"""
        
        # Auto-update file list before showing menu if manager exists
        if self.manager:
            # Scan if project root is set
            if self.manager.root_le.text().strip():
                self.manager.scan()
        
        if self.combo.count() == 0:
            hou.ui.displayMessage(
                "No files found.\n\nPlease click ⚡ button to open File Manager and scan for files.",
                severity=hou.severityType.Warning
            )
            return
        
        # Tạo menu với parent là None để tránh event conflicts
        menu = QtWidgets.QMenu()
        menu.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # Auto cleanup
        menu.setStyleSheet("""
            QMenu { background:#1f1f1f; color:#e5e5e5; border:1px solid #3a3a3a; }
            QMenu::item { padding:8px 16px; }
            QMenu::item:selected { background:#3d5a99; }
        """)
        
        # Group files by shot và tìm version cao nhất
        shot_files = {}
        for i in range(self.combo.count()):
            fp = self.combo.itemData(i, role=QtCore.Qt.UserRole)
            if not fp:
                continue
            
            # Ưu tiên lấy shot name từ model
            model_shot = self.combo.itemData(i, role=QtCore.Qt.UserRole+2)
            shot = model_shot if model_shot else (_infer_shot(fp) or "Unknown")
            
            filename = os.path.basename(fp)
            ver_str = _parse_ver(filename)
            
            # Parse version number để so sánh
            try:
                ver_num = int(ver_str.replace('v', '')) if ver_str else 0
            except:
                ver_num = 0
            
            if shot not in shot_files or ver_num > shot_files[shot]['version']:
                shot_files[shot] = {'index': i, 'version': ver_num, 'ver_str': ver_str}
        
        # Tạo menu với shot names (sorted) và highlight current file
        current_file = _get_current_houdini_file()
        for shot in sorted(shot_files.keys()):
            file_info = shot_files[shot]
            idx = file_info['index']
            fp = self.combo.itemData(idx, role=QtCore.Qt.UserRole)
            is_current = _is_current_file(fp) if current_file else False
            
            display_text = f"{shot} ({file_info['ver_str']})" if file_info['ver_str'] else shot
            
            # Add indicator for current file
            if is_current:
                display_text = f"🎯 {display_text} (Current)"
            
            action = menu.addAction(display_text)
            action.setData(file_info['index'])
            
            # Style current file differently
            if is_current:
                action.setText(f"🎯 {shot} ({file_info['ver_str']}) (Current)" if file_info['ver_str'] else f"🎯 {shot} (Current)")
                # Bold font for current file (if supported by menu)
                font = action.font()
                font.setBold(True)
                action.setFont(font)
            
        # Show menu below shot display
        pos = self.shot_display.mapToGlobal(self.shot_display.rect().bottomLeft())
        
        # Exec menu và xử lý kết quả
        selected_action = menu.exec_(pos)
        if selected_action:
            idx = selected_action.data()
            self.combo.setCurrentIndex(idx)
            self._activate_current(idx)
            
        # Menu tự động cleanup sau exec_, không cần deleteLater()

    def _activate_current(self, idx):
        fp=self.combo.itemData(idx, role=QtCore.Qt.UserRole)
        if fp:
            self.s.setValue("last_selected_path", fp); self.s.sync()
            self._open_houdini_file(fp)
    
    def _open_houdini_file(self, filepath):
        """Mở file trong Houdini"""
        try:
            if not os.path.exists(filepath):
                hou.ui.displayMessage(f"File không tồn tại:\n{filepath}", 
                                     severity=hou.severityType.Warning)
                return
            
            # Hỏi user có muốn save scene hiện tại không
            if hou.hipFile.hasUnsavedChanges():
                choice = hou.ui.displayMessage(
                    "Scene hiện tại có thay đổi chưa save.\nBạn có muốn save trước khi mở file mới?",
                    buttons=("Save & Open", "Open Without Saving", "Cancel"),
                    severity=hou.severityType.ImportantMessage,
                    default_choice=0,
                    close_choice=2
                )
                if choice == 0:  # Save & Open
                    try:
                        hou.hipFile.save()
                    except hou.OperationFailed as e:
                        hou.ui.displayMessage(f"Không thể save file:\n{str(e)}", 
                                             severity=hou.severityType.Error)
                        return
                elif choice == 2:  # Cancel
                    return
                # choice == 1: Open Without Saving - tiếp tục
            
            # Mở file
            hou.hipFile.load(filepath, suppress_save_prompt=True)
            
            # Thông báo thành công
            filename = os.path.basename(filepath)
            hou.ui.setStatusMessage(f"Đã mở: {filename}", severity=hou.severityType.Message)
            
        except Exception as e:
            hou.ui.displayMessage(f"Lỗi khi mở file:\n{str(e)}", 
                                 severity=hou.severityType.Error)

    def _update_shot_display(self, idx):
        """Cập nhật shot display khi thay đổi selection"""
        # Ưu tiên lấy shot name từ model trước
        model_shot = self.combo.itemData(idx, role=QtCore.Qt.UserRole+2)
        if model_shot:
            shot_text = model_shot
        else:
            # Fallback: infer từ filepath
            fp = self.combo.itemData(idx, role=QtCore.Qt.UserRole)
            shot_text = _infer_shot(fp) if fp else (os.path.basename(fp) if fp else "")
        
        self.shot_display.setText(shot_text)
        
        # Update highlighting based on current file
        self._update_current_shot_highlighting()
    
    def _update_current_shot_highlighting(self):
        """Cập nhật highlighting cho shot hiện tại đang mở"""
        current_file = _get_current_houdini_file()
        is_current = False
        
        if current_file:
            # Kiểm tra xem shot hiện tại có match với file đang mở không
            current_idx = self.combo.currentIndex()
            if current_idx >= 0:
                fp = self.combo.itemData(current_idx, role=QtCore.Qt.UserRole)
                is_current = _is_current_file(fp)
        
        # Apply styling based on whether this is the current file
        if is_current:
            # Highlight style for current shot
            self.shot_display.setStyleSheet("""
                QLineEdit { 
                    background:#2a4a2a; color:#90ff90; border:2px solid #4a8a4a; 
                    padding:4px 8px; border-radius:6px; font-weight:bold;
                }
                QLineEdit:read-only {
                    background:#2a4a2a; color:#90ff90;
                }
                QLineEdit:read-only:hover {
                    background:#2f5a2f; border:2px solid #5a9a5a;
                }
            """)
            self.shot_display.setToolTip("🎯 Shot hiện tại đang mở • Click để chọn shot khác")
        else:
            # Normal style for non-current shots
            self.shot_display.setStyleSheet("""
                QLineEdit { 
                    background:#1e1e1e; color:#e5e5e5; border:1px solid #3a3a3a; 
                    padding:4px 8px; border-radius:6px; 
                }
                QLineEdit:read-only {
                    background:#1a1a1a; color:#d0d0d0;
                }
                QLineEdit:read-only:hover {
                    background:#252525; border:1px solid #4a4a4a;
                }
            """)
            self.shot_display.setToolTip("Click để chọn shot • Chọn shot sẽ mở file trong Houdini")
    
    def _check_file_changes(self):
        """Kiểm tra thay đổi file và cập nhật highlighting"""
        current_file = _get_current_houdini_file()
        
        # Nếu file thay đổi, update highlighting
        if current_file != self._last_current_file:
            self._last_current_file = current_file
            self._update_current_shot_highlighting()
            
            # Tự động select shot tương ứng nếu có trong danh sách
            if current_file and self.combo.count() > 0:
                self._auto_select_current_file(current_file)
    
    def _auto_select_current_file(self, current_file):
        """Tự động select file hiện tại trong combo nếu có"""
        for i in range(self.combo.count()):
            fp = self.combo.itemData(i, role=QtCore.Qt.UserRole)
            if _is_current_file(fp):
                # Chỉ update nếu không phải là selection hiện tại
                if self.combo.currentIndex() != i:
                    # Block signals để tránh trigger _activate_current
                    self.combo.blockSignals(True)
                    self.combo.setCurrentIndex(i)
                    self.combo.blockSignals(False)
                    # Manually update display
                    self._update_shot_display(i)
                break
    
    def _setup_main_window_monitoring(self):
        """Setup monitoring của Houdini main window để update position khi cần"""
        try:
            mw = hou.qt.mainWindow()
            if mw:
                # Install event filter để catch main window move/resize events
                if not hasattr(self, '_main_window_filter'):
                    self._main_window_filter = MainWindowEventFilter(self)
                    mw.installEventFilter(self._main_window_filter)
        except:
            pass  # Fail silently if can't setup monitoring

    def populate(self, paths, shot_names=None):
        self.combo.clear()
        if shot_names is None:
            shot_names = {}
            
        for p in sorted(paths):
            name=os.path.basename(p)
            ver=_parse_ver(name)
            label=f"{name} ({ver or '—'})"     # label trong popup
            idx=self.combo.count()
            self.combo.addItem(label)
            self.combo.setItemData(idx, p, QtCore.Qt.UserRole)   # lưu fullpath
            self.combo.setItemData(idx, label, QtCore.Qt.DisplayRole)
            self.combo.setItemData(idx, name, QtCore.Qt.ToolTipRole)
            # Lưu shot name từ model (nếu có)
            if p in shot_names:
                self.combo.setItemData(idx, shot_names[p], QtCore.Qt.UserRole+2)
                
        # Ưu tiên chọn file hiện tại nếu có trong danh sách
        current_file = _get_current_houdini_file()
        current_selected = False
        
        if current_file:
            for i in range(self.combo.count()):
                fp = self.combo.itemData(i, role=QtCore.Qt.UserRole)
                if _is_current_file(fp):
                    self.combo.setCurrentIndex(i)
                    current_selected = True
                    break
        
        # Nếu không có file hiện tại hoặc không tìm thấy, chọn last selected
        if not current_selected:
            last = self.s.value("last_selected_path", "", type=str)
            if last:
                i = self.combo.findData(last, role=QtCore.Qt.UserRole)
                if i >= 0: 
                    self.combo.setCurrentIndex(i)
        
        # Update display và highlighting
        self._update_shot_display(self.combo.currentIndex())
        self._last_current_file = current_file

    def populate_from_model(self, model):
        paths=[]
        shot_names={}  # Map fullpath -> shot name từ model
        for r in range(model.rowCount()):
            p=model.item(r, _Model.COL_SHOT).data(QtCore.Qt.UserRole+1)  # fullpath
            shot_name = model.item(r, _Model.COL_SHOT).text()  # shot name từ model
            if p: 
                paths.append(p)
                shot_names[p] = shot_name
        self.populate(paths, shot_names)
        
        # Đảm bảo highlighting được update sau khi populate
        QtCore.QTimer.singleShot(100, self._update_current_shot_highlighting)

# ------------------- Bootstrap -------------------
_active_dialog=None
_active_minibar=None

def _make_manager():
    global _active_dialog
    # Check existing dialog first
    if _active_dialog and _active_dialog.isVisible():
        return _active_dialog
        
    # Search for existing MonoFileManager windows
    for w in QtWidgets.QApplication.topLevelWidgets():
        if w.__class__.__name__ == 'MonoFileManager':
            _active_dialog=w; return w
            
    # Create new one if not found
    d=MonoFileManager(hou.qt.mainWindow()); _active_dialog=d; return d

def show_mono_file_manager():
    d=_make_manager(); d.show(); d.raise_(); d.activateWindow(); return d

def show_mono_minibar():
    global _active_minibar
    
    # Kiểm tra và đóng tất cả minibar cũ (tránh duplicate)
    try:
        for widget in hou.qt.mainWindow().findChildren(QtCore.QObject, "MonoMiniBar"):
            if hasattr(widget, 'close') and widget.isVisible():
                print(f"🗑️ Closing existing minibar at {widget.pos()}")
                widget.close()
                widget.deleteLater()
    except:
        pass
    
    # Reset global reference
    _active_minibar = None
    
    # Tạo minibar mới
    print("🔄 Creating new minibar...")
    mb=MonoFileMiniBar(manager_factory=_make_manager, parent=hou.qt.mainWindow())
    _active_minibar=mb

    # auto-populate nhanh nếu đã có Root
    d=_make_manager()
    base=os.path.join(d.root_le.text().strip(), SUBPATH) if d.root_le.text().strip() else ""
    if base and os.path.isdir(base):
        mb.populate(_collect_files(base, depth=1))  # Không có shot_names, sẽ dùng infer
    return mb

# Compatibility wrapper classes for the package system
class FileManagerWrapper:
    """Wrapper for compatibility with the package system"""
    
    def __init__(self):
        self.minibar = None
    
    def show_minibar(self):
        """Show the minibar"""
        try:
            self.minibar = show_mono_minibar()
            return True
        except Exception as e:
            print(f"❌ Could not show minibar: {e}")
            return False

# Factory function for backward compatibility  
def create_mono_file_manager():
    """Factory function to create file manager - now returns the full dialog"""
    return show_mono_file_manager()

# Run MiniBar (có nút Expand để mở UI đầy đủ)
# show_mono_minibar()

# ------------------- Debug Functions -------------------
def test_explorer_functions():
    """Test function để kiểm tra Open Explorer và Copy Path"""
    print("🧪 Testing File Manager Functions...")
    
    # Test open in explorer with a known path
    test_path = r"C:\Windows"  # Should exist on all Windows systems
    if os.path.exists(test_path):
        print(f"Testing _open_in_explorer with: {test_path}")
        _open_in_explorer(test_path)
    else:
        print("⚠️ Test path C:\\Windows not found")
    
    # Test clipboard functionality
    try:
        import hou
        from mono_tools.qt import QtWidgets
        
        test_text = "Test clipboard text from Mono File Manager"
        QtWidgets.QApplication.clipboard().setText(test_text)
        clipboard_content = QtWidgets.QApplication.clipboard().text()
        
        if clipboard_content == test_text:
            print("✅ Clipboard functionality working")
            hou.ui.displayMessage("Clipboard test successful!", severity=hou.severityType.Message)
        else:
            print("❌ Clipboard test failed")
            
    except Exception as e:
        print(f"❌ Error testing clipboard: {e}")

def debug_file_manager_selection():
    """Debug function để kiểm tra selection trong file manager"""
    try:
        # Find active file manager dialog
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(widget, MonoFileManager) and widget.isVisible():
                print(f"🔍 Found active File Manager")
                
                # Check if table has data
                row_count = widget.model.rowCount()
                print(f"📊 Table has {row_count} rows")
                
                # Check selection
                selected_rows = widget.table.selectionModel().selectedRows()
                print(f"📋 Selected rows: {len(selected_rows)}")
                
                if selected_rows:
                    # Test _selected_fullpath
                    fp = widget._selected_fullpath()
                    print(f"📄 Selected fullpath: {fp}")
                    
                    if fp:
                        print("✅ Selection working correctly")
                        return widget
                else:
                    print("⚠️ No rows selected - try selecting a file first")
                    
                return widget
                
        print("❌ No active File Manager found")
        
    except Exception as e:
        print(f"❌ Error debugging selection: {e}")
        import traceback
        traceback.print_exc()
        
    return None

# ================ Helper Functions for Migration ================

def test_restart_houdini():
    """Test function để kiểm tra restart functionality"""
    try:
        import subprocess
        import sys
        import os
        
        print("🧪 Testing Houdini restart functionality...")
        
        # Get Houdini executable path
        houdini_exe = sys.executable
        print(f"📍 Current executable: {houdini_exe}")
        
        if "houdini" not in houdini_exe.lower():
            # Try to find houdini executable
            hfs_path = os.environ.get("HFS", "")
            print(f"📍 HFS environment: {hfs_path}")
            houdini_bin = os.path.join(hfs_path, "bin", "houdini.exe")
            print(f"📍 Checking Houdini path: {houdini_bin}")
            if os.path.exists(houdini_bin):
                houdini_exe = houdini_bin
                print(f"✅ Found Houdini executable: {houdini_exe}")
            else:
                print(f"❌ Houdini executable not found at: {houdini_bin}")
                return False
        
        # Test if executable exists
        if os.path.exists(houdini_exe):
            print(f"✅ Executable exists: {houdini_exe}")
            
            # Test command building
            cmd = [houdini_exe]
            print(f"🚀 Test command: {' '.join(cmd)}")
            
            # Don't actually start - just test the path
            print("💡 Restart should work with this executable")
            return True
        else:
            print(f"❌ Executable not found: {houdini_exe}")
            return False
            
    except Exception as e:
        print(f"❌ Error during restart test: {e}")
        return False

def force_migrate_minibar_position():
    """Force migration của minibar position sang default mới rel(0.915, 0.000)"""
    try:
        from mono_tools.qt import QtCore
        
        s = QtCore.QSettings("Mono", "FileManager")
        
        print("🔄 Force migrating minibar position...")
        
        # Show current position 
        old_rel_x = s.value("minibar_rel_x", "None")
        old_rel_y = s.value("minibar_rel_y", "None")
        print(f"📍 Current position: rel_x={old_rel_x}, rel_y={old_rel_y}")
        
        # Clear all position settings
        s.remove("minibar_rel_x")
        s.remove("minibar_rel_y")
        s.remove("minibar_offset_x") 
        s.remove("minibar_offset_y")
        s.remove("minibar_abs_x")
        s.remove("minibar_abs_y")
        s.setValue("minibar_position_migrated_v2", True)
        s.sync()
        
        print("✅ Migration completed!")
        print("📍 New default position: rel(0.915, 0.000)")
        print("💡 Restart minibar to see changes:")
        print("   import mono_tools; mono_tools.open_minibar()")
        
    except Exception as e:
        print(f"❌ Error during force migration: {e}")

def reset_minibar_settings():
    """Xóa tất cả settings của minibar"""
    try:
        from mono_tools.qt import QtCore
        
        s = QtCore.QSettings("Mono", "FileManager")
        
        # Remove all minibar related settings
        keys_to_remove = [
            "minibar_rel_x", "minibar_rel_y",
            "minibar_offset_x", "minibar_offset_y", 
            "minibar_abs_x", "minibar_abs_y",
            "minibar_locked", "minibar_position_migrated_v2"
        ]
        
        for key in keys_to_remove:
            s.remove(key)
        s.sync()
        
        print("✅ All minibar settings cleared!")
        print("💡 Restart minibar to use fresh defaults:")
        print("   import mono_tools; mono_tools.open_minibar()")
        
    except Exception as e:
        print(f"❌ Error resetting settings: {e}")

def test_restart_methods():
    """Test different restart methods to see which works"""
    try:
        import hou
        print("🔍 Testing Houdini restart methods...")
        
        # Check if hou.exit supports restart parameter
        import inspect
        sig = inspect.signature(hou.exit)
        print(f"📋 hou.exit signature: {sig}")
        
        # Check Houdini version
        print(f"🏠 Houdini version: {hou.applicationVersion()}")
        
        # Check environment
        import os
        print(f"💻 HFS: {os.environ.get('HFS', 'Not set')}")
        print(f"🐍 Python executable: {__import__('sys').executable}")
        
        # Test if we can find Houdini executable
        hfs = os.environ.get("HFS", "")
        if hfs:
            houdini_exe = os.path.join(hfs, "bin", "houdini.exe")
            print(f"🎯 Houdini executable: {houdini_exe}")
            print(f"📁 Exists: {os.path.exists(houdini_exe)}")
        
        print("✅ Restart method analysis complete")
        
    except Exception as e:
        print(f"❌ Error testing restart methods: {e}")

def simple_restart_houdini():
    """Simple restart function for testing"""
    try:
        import hou
        result = hou.ui.displayMessage(
            "Test restart Houdini?\n\nThis will close current session.",
            buttons=("Restart", "Cancel"),
            severity=hou.severityType.ImportantMessage
        )
        if result == 0:
            print("🔃 Testing simple restart...")
            hou.exit()  # Simple exit - user manually restarts
    except Exception as e:
        print(f"❌ Simple restart failed: {e}")