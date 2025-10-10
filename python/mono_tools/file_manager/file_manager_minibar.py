import os
import subprocess
from mono_tools.qt import QtCore, QtGui, QtWidgets
import hou
from .file_manager_helpers import (
    ORG, APP, collect_files, get_current_houdini_file, is_current_file, 
    infer_shot, parse_ver, open_in_explorer, get_render_folder_path, 
    increment_version_and_backup, debug_print, DEBUG,
    generate_new_filename, create_asset_folder_structure, get_standard_departments,
    load_asset_types_config
)

class MainWindowEventFilter(QtCore.QObject):
    """Monitor Houdini main window for resize/move events"""
    def __init__(self, minibar):
        super().__init__(minibar)
        self.minibar = minibar
        
    def eventFilter(self, obj, ev):
        # Skip if minibar is being dragged
        if hasattr(self.minibar, '_is_dragging') and self.minibar._is_dragging:
            return super().eventFilter(obj, ev)
        
        # Debounce window changes with 150ms timer
        if ev.type() in (QtCore.QEvent.Resize, QtCore.QEvent.Move):
            if not hasattr(self.minibar, '_main_window_change_timer'):
                self.minibar._main_window_change_timer = QtCore.QTimer(self.minibar)
                self.minibar._main_window_change_timer.setSingleShot(True)
                self.minibar._main_window_change_timer.timeout.connect(self._on_main_window_changed)
            if not self.minibar._main_window_change_timer.isActive():
                self.minibar._main_window_change_timer.start(150)
        
        return super().eventFilter(obj, ev)
    
    def _on_main_window_changed(self):
        """Update minibar position when Houdini window changes"""
        try:
            if self.minibar and self.minibar.isVisible():
                self.minibar._update_position_relative_to_main_window()
        except:
            pass

class MonoFileMiniBar(QtWidgets.QWidget):
    def __init__(self, manager_factory, parent=None):
        super().__init__(parent or hou.qt.mainWindow())
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setObjectName("MonoMiniBar")
        self.s=QtCore.QSettings(ORG,APP)
        self.manager_factory=manager_factory; self.manager=None
        self._drag_pos=None; self._is_dragging=False
        self._locked=self.s.value("minibar_locked", False, type=bool)
        self._last_current_file = None
        self._file_check_timer = QtCore.QTimer(self); self._file_check_timer.timeout.connect(self._check_file_changes); self._file_check_timer.start(2000)
        self._setup_main_window_monitoring()
        self.handle_area = QtWidgets.QLabel("⋮⋮"); self.handle_area.setFixedWidth(20); self.handle_area.setAlignment(QtCore.Qt.AlignCenter); self.handle_area.setToolTip("Drag to move • Right-click for options"); self.handle_area.setCursor(QtCore.Qt.OpenHandCursor)
        self.handle_area.mousePressEvent = self._handle_mouse_press
        self.handle_area.mouseMoveEvent = self._handle_mouse_move
        self.handle_area.mouseReleaseEvent = self._handle_mouse_release
        self.handle_area.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.handle_area.customContextMenuRequested.connect(self._show_handle_context_menu)
        self._dragging = False
        self._drag_start_pos = None
        
        # Type menu button (dynamic from scan)
        self.type_btn = QtWidgets.QToolButton()
        self.type_btn.setText("🏷️ Type")
        self.type_btn.setFixedSize(70, 24)
        self.type_btn.setToolTip("Select type (auto-scanned from project)")
        self.type_btn.clicked.connect(self._show_type_menu)
        self.current_type = None
        self.current_type_is_assets = True

        # Department menu button (departments for selected type)
        self.dept_btn = QtWidgets.QToolButton()
        self.dept_btn.setText("📁 Dept")
        self.dept_btn.setFixedSize(70, 24)
        self.dept_btn.setToolTip("Select department")
        self.dept_btn.clicked.connect(self._show_dept_menu)
        self.current_dept = None
        
        self.shot_display = QtWidgets.QLineEdit(); self.shot_display.setReadOnly(True); self.shot_display.setMinimumWidth(160); self.shot_display.setMaximumWidth(160); self.shot_display.setToolTip("Click để chọn shot • Chọn shot sẽ mở file trong Houdini"); self.shot_display.setCursor(QtCore.Qt.PointingHandCursor)
        self.shot_display.mousePressEvent = self._shot_display_clicked
        self.combo = QtWidgets.QComboBox(); self.combo.setVisible(False); self.combo.currentIndexChanged.connect(self._update_shot_display)
        self.btn_quick_menu=QtWidgets.QToolButton(); self.btn_quick_menu.setText("⚡"); self.btn_quick_menu.setFixedSize(24, 24); self.btn_quick_menu.setToolTip("Quick Menu\n• New File\n• New Folder\n• Save Version\n• Reload/Restart\n• Open Folders"); self.btn_quick_menu.clicked.connect(self._show_quick_menu)
        self.btn_settings=QtWidgets.QToolButton(); self.btn_settings.setText("⚙️"); self.btn_settings.setFixedSize(32, 24); self.btn_settings.setToolTip("Settings Dialog • Configure project and scan files"); self.btn_settings.clicked.connect(self._open_settings)
        lay=QtWidgets.QHBoxLayout(self); lay.setContentsMargins(4,3,6,3); lay.setSpacing(3)
        lay.addWidget(self.handle_area, 0)
        lay.addWidget(self.type_btn, 0)
        lay.addWidget(self.dept_btn, 0)
        lay.addWidget(self.shot_display, 1)
        lay.addWidget(self.btn_quick_menu, 0)
        lay.addWidget(self.btn_settings, 0)
        self.setStyleSheet("""
        #MonoMiniBar { 
            background:#2a2a2a; 
            border:1px solid #3a3a3a; 
            border-radius:8px; 
        }
        QLabel { 
            color:#888; 
            font-weight:bold; 
            font-size:12px; 
            background:transparent; 
        }
        QLabel:hover { 
            color:#aaa; 
            background:rgba(255,255,255,0.1); 
            border-radius:3px; 
        }
        QToolButton { 
            background:#3a3a3a; 
            color:#fff; 
            border:1px solid #4a4a4a; 
            border-radius:4px; 
            font-size:11px; 
            font-weight:bold; 
        }
        QToolButton:hover { 
            background:#4a4a4a; 
        }
        QToolButton:pressed { 
            background:#2a2a2a; 
        }
        QLineEdit { 
            background:#1a1a1a; 
            color:#fff; 
            border:1px solid #3a3a3a; 
            border-radius:4px; 
            padding:2px 6px; 
            font-size:11px; 
        }
        """)
        # Initialize with empty state
        self.shot_display.setText("No files")
        self.shot_display.setToolTip("Click ⚡ to configure project")
        
        # Load saved settings
        self._load_minibar_settings()
        
        # Apply UI scale
        self._apply_ui_scale()
        
        # Trigger initial file refresh after UI is ready
        QtCore.QTimer.singleShot(100, self._refresh_files_for_current_tab)
        
        # Delay position restore to let Houdini window stabilize
        # This prevents incorrect position calculation on startup
        QtCore.QTimer.singleShot(200, self._restore_relative_position)
        
        self._update_lock_visual_feedback()
        self._update_current_shot_highlighting()
        
        # Auto-start MiniBar (always enabled)
        self.show()
        self.raise_()
        self.activateWindow()
        debug_print("🚀 MiniBar auto-started with Houdini")

    # --- a subset of methods ported from original for brevity ---
    def _shot_display_clicked(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            QtCore.QTimer.singleShot(0, self._show_file_menu)
        event.accept()
    
    def _handle_mouse_press(self, event):
        """Handle mouse press on drag handle"""
        if event.button() == QtCore.Qt.LeftButton and not self._locked:
            self._dragging = True
            self._drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.handle_area.setCursor(QtCore.Qt.ClosedHandCursor)
        event.accept()
    
    def _handle_mouse_move(self, event):
        """Handle mouse move for dragging"""
        if self._dragging and not self._locked:
            self.move(event.globalPos() - self._drag_start_pos)
        event.accept()
    
    def _handle_mouse_release(self, event):
        """Handle mouse release after dragging"""
        if event.button() == QtCore.Qt.LeftButton:
            self._dragging = False
            self.handle_area.setCursor(QtCore.Qt.OpenHandCursor)
            
            # Save new position as offset
            self._save_relative_position()
        event.accept()
    
    def _show_handle_context_menu(self, pos):
        """Show context menu for handle"""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu { background:#1f1f1f; color:#e5e5e5; border:1px solid #3a3a3a; }
            QMenu::item { padding:8px 16px; }
            QMenu::item:selected { background:#3d5a99; }
        """)
        
        # Lock/Unlock toggle
        if self._locked:
            lock_action = menu.addAction("🔓 Unlock Position")
            lock_action.triggered.connect(self._toggle_lock)
        else:
            lock_action = menu.addAction("🔒 Lock Position")
            lock_action.triggered.connect(self._toggle_lock)
        
        menu.addSeparator()
        
        # Reset position
        reset_action = menu.addAction("📍 Reset to Default Position")
        reset_action.triggered.connect(self._reset_position)
        
        menu.addSeparator()
        
        # Close MiniBar
        close_action = menu.addAction("❌ Close MiniBar")
        close_action.triggered.connect(self._close_minibar)
        
        menu.addSeparator()
        
        # Remove startup toggle - always auto-start
        
        # Version info (use cached version to avoid git calls)
        try:
            from mono_tools import __version__
            version_action = menu.addAction(f"ℹ️ v{__version__}")
            version_action.setToolTip(f"Mono Studio v{__version__}")
            version_action.setEnabled(False)  # Disabled, just for display
        except Exception as e:
            debug_print(f"⚠️ Error loading version: {e}")
            version_action = menu.addAction("ℹ️ v2.2.0")
            version_action.setEnabled(False)
        
        # Show menu
        global_pos = self.handle_area.mapToGlobal(pos)
        menu.exec_(global_pos)
    
    def _toggle_lock(self):
        """Toggle lock state"""
        self._locked = not self._locked
        self.s.setValue("minibar_locked", self._locked)
        self.s.sync()
        self._update_lock_visual_feedback()
    
    def _reset_position(self):
        """Reset to default position (top-right of Houdini window)"""
        # Set default offsets (top-right position)
        self.s.setValue("minibar_offset_x", -85)  # ~20px from right edge
        self.s.setValue("minibar_offset_y", 0)     # At top edge
        self.s.sync()
        
        # Apply position
        self._update_position_relative_to_main_window()
    
    def _close_minibar(self):
        """Close MiniBar"""
        try:
            # Save current position before closing
            self._save_relative_position()
            
            # Hide MiniBar
            self.hide()
            debug_print("❌ MiniBar closed")
            
        except Exception as e:
            debug_print(f"⚠️ Error closing MiniBar: {e}")
            self.hide()
    
    # Removed _toggle_startup - always auto-start
    
    def show_minibar(self):
        """Show MiniBar manually"""
        self.show()
        self.raise_()
        self.activateWindow()
        debug_print("🚀 MiniBar shown manually")

    def _show_type_menu(self):
        """Show type selection menu"""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu { background:#1f1f1f; color:#e5e5e5; border:1px solid #3a3a3a; }
            QMenu::item { padding:8px 16px; }
            QMenu::item:selected { background:#3d5a99; }
        """)
        
        # Get available types from settings
        root = self.s.value("project_root", "", type=str)
        project = self.s.value("current_project", "", type=str)
        
        if not root or not project:
            menu.addAction("No project configured").setEnabled(False)
        else:
            project_path = os.path.join(root, project)
            if os.path.isdir(project_path):
                from .file_manager_helpers import scan_project_types
                types = scan_project_types(project_path)
                
                if not types:
                    menu.addAction("No types found").setEnabled(False)
                else:
                    for type_name, type_path, is_assets in types:
                        # Count total files for this type
                        from .file_manager_helpers import collect_files_with_filters
                        files = collect_files_with_filters(project_path, type_name)
                        file_count = len(files)
                        
                        action = menu.addAction(f"{type_name} ({file_count})")
                        action.setData((type_name, type_path, is_assets))
                        
                        # Bold current type
                        if type_name == self.current_type:
                            font = action.font()
                            font.setBold(True)
                            action.setFont(font)
        
        # Show menu
        menu_pos = self.mapToGlobal(self.type_btn.geometry().bottomLeft())
        selected = menu.exec_(menu_pos)
        
        if selected and selected.data():
            type_name, type_path, is_assets = selected.data()
            self._select_type(type_name, type_path, is_assets)
    
    def _show_dept_menu(self):
        """Show department selection menu"""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu { background:#1f1f1f; color:#e5e5e5; border:1px solid #3a3a3a; }
            QMenu::item { padding:8px 16px; }
            QMenu::item:selected { background:#3d5a99; }
        """)
        
        if not self.current_type:
            menu.addAction("Select type first").setEnabled(False)
        else:
            root = self.s.value("project_root", "", type=str)
            project = self.s.value("current_project", "", type=str)
            
            if root and project:
                project_path = os.path.join(root, project)
                from .file_manager_helpers import scan_departments_for_type, collect_files_with_filters
                
                departments = scan_departments_for_type(project_path, self.current_type, self.current_type_is_assets)
                
                if not departments:
                    menu.addAction("No departments found").setEnabled(False)
                else:
                    for dept in departments:
                        # Count files in this department
                        files = collect_files_with_filters(project_path, self.current_type, dept)
                        file_count = len(files)
                        
                        action = menu.addAction(f"{dept} ({file_count})")
                        action.setData(dept)
                        
                        # Bold current department
                        if dept == self.current_dept:
                            font = action.font()
                            font.setBold(True)
                            action.setFont(font)
        
        # Show menu
        menu_pos = self.mapToGlobal(self.dept_btn.geometry().bottomLeft())
        selected = menu.exec_(menu_pos)
        
        if selected and selected.data():
            dept_name = selected.data()
            self._select_department(dept_name)
    
    def _select_type(self, type_name, type_path, is_assets):
        """Handle type selection"""
        self.current_type = type_name
        self.current_type_is_assets = is_assets
        
        # Update button text (shorten if needed)
        short_name = type_name.replace('_', '').replace('Shots', 'Shots')[:8]
        self.type_btn.setText(f"🏷️ {short_name}")
        self.type_btn.setToolTip(f"Type: {type_name}")
        
        # Save selection
        self.s.setValue("minibar_type", type_name)
        self.s.sync()
        
        # Reset department selection
        self.current_dept = None
        self.dept_btn.setText("📁 Dept")
        self.dept_btn.setToolTip("Select department")
        
        # Clear files
        self.combo.clear()
        self.shot_display.setText("Select department")
    
    def _select_department(self, dept_name):
        """Handle department selection"""
        self.current_dept = dept_name
        
        # Update button text (shorten if needed)
        short_dept = dept_name.split('_')[-1][:8] if '_' in dept_name else dept_name[:8]
        self.dept_btn.setText(f"📁 {short_dept}")
        self.dept_btn.setToolTip(f"Department: {dept_name}")
        
        # Save selection
        if self.current_type:
            saved_dept_key = f"minibar_dept_{self.current_type}"
            self.s.setValue(saved_dept_key, dept_name)
            self.s.sync()
        
        # Refresh files
        self._refresh_files_for_current_tab()
    
    def _show_quick_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu { background:#1f1f1f; color:#e5e5e5; border:1px solid #3a3a3a; }
            QMenu::item { padding:8px 16px; }
            QMenu::item:selected { background:#3d5a99; }
        """)
        # File operations
        new_action = menu.addAction("📄 New File..."); new_action.triggered.connect(self._new_file)
        new_folder_action = menu.addAction("📁 New Folder..."); new_folder_action.triggered.connect(self._new_folder)
        save_ver_action = menu.addAction("💾 Save Version..."); save_ver_action.triggered.connect(self._save_version)
        menu.addSeparator()
        # Folder operations
        location_action = menu.addAction("📂 Open File Location"); location_action.triggered.connect(self._open_current_file_location)
        render_action = menu.addAction("🎬 Open Render Folder"); render_action.triggered.connect(self._open_render_folder)
        menu.addSeparator()
        # System operations (at bottom)
        reload_action = menu.addAction("🔄 Reload Scene"); reload_action.triggered.connect(self._reload_scene)
        restart_action = menu.addAction("🔃 Restart Houdini"); restart_action.triggered.connect(self._restart_houdini)
        menu_pos = self.mapToGlobal(self.btn_quick_menu.geometry().bottomLeft()); menu.exec_(menu_pos)

    # ---- File change monitoring ----
    def _check_file_changes(self):
        current_file = get_current_houdini_file()
        if current_file != self._last_current_file:
            self._last_current_file = current_file
            self._update_current_shot_highlighting()
            if current_file and self.combo.count() > 0:
                self._auto_select_current_file(current_file)

    def _update_current_shot_highlighting(self):
        current_file = get_current_houdini_file(); is_current=False
        if current_file and self.combo.currentIndex() >= 0:
            fp = self.combo.itemData(self.combo.currentIndex(), role=QtCore.Qt.UserRole)
            is_current = is_current_file(fp)
        if is_current:
            self.shot_display.setStyleSheet("""
                QLineEdit { background:#2a4a2a; color:#90ff90; border:2px solid #4a8a4a; padding:4px 8px; border-radius:6px; font-weight:bold; }
                QLineEdit:read-only { background:#2a4a2a; color:#90ff90; }
                QLineEdit:read-only:hover { background:#2f5a2f; border:2px solid #5a9a5a; }
            """)
            self.shot_display.setToolTip("🎯 Shot hiện tại đang mở • Click để chọn shot khác")
        else:
            self.shot_display.setStyleSheet("""
                QLineEdit { background:#1e1e1e; color:#e5e5e5; border:1px solid #3a3a3a; padding:4px 8px; border-radius:6px; }
                QLineEdit:read-only { background:#1a1a1a; color:#d0d0d0; }
                QLineEdit:read-only:hover { background:#252525; border:1px solid #4a4a4a; }
            """)
            self.shot_display.setToolTip("Click để chọn shot • Chọn shot sẽ mở file trong Houdini")

    def _auto_select_current_file(self, current_file):
        for i in range(self.combo.count()):
            fp = self.combo.itemData(i, role=QtCore.Qt.UserRole)
            if is_current_file(fp):
                if self.combo.currentIndex() != i:
                    self.combo.blockSignals(True); self.combo.setCurrentIndex(i); self.combo.blockSignals(False); self._update_shot_display(i)
                break

    def _update_shot_display(self, idx):
        if idx >= 0 and idx < self.combo.count():
            fp = self.combo.itemData(idx, role=QtCore.Qt.UserRole)
            if fp:
                shot = self.combo.itemData(idx, role=QtCore.Qt.UserRole+2) or infer_shot(fp) or "Unknown"
                self.shot_display.setText(shot)
                self.shot_display.setToolTip(f"Current: {shot}\nClick to change")
            else:
                self.shot_display.setText("No files")
                self.shot_display.setToolTip("No files available")
        else:
            self.shot_display.setText("No files")
            self.shot_display.setToolTip("No files available")

    # ---- Positioning relative to main window ----
    def _save_relative_position(self):
        """Save MiniBar position as offset from Houdini window"""
        try:
            if hasattr(self, '_updating_position') and self._updating_position:
                return
            
            mw = hou.qt.mainWindow()
            if not mw or not mw.isVisible():
                return
            
            hou_geo = mw.geometry()
            my_pos = self.pos()
            
            # Calculate offset from Houdini right/top edges
            hou_right = hou_geo.x() + hou_geo.width()
            hou_top = hou_geo.y()
            minibar_right = my_pos.x() + self.width()
            minibar_top = my_pos.y()
            
            offset_x = minibar_right - hou_right
            offset_y = minibar_top - hou_top
            
            # Save offsets (no threshold - always save)
            self.s.setValue("minibar_offset_x", offset_x)
            self.s.setValue("minibar_offset_y", offset_y)
            self.s.sync()
            
        except Exception as e:
            if DEBUG:
                debug_print(f"⚠️ Failed to save position: {e}")

    def _update_position_relative_to_main_window(self):
        """Update MiniBar position when Houdini window resizes/moves"""
        try:
            self._updating_position = True
            
            mw = hou.qt.mainWindow()
            if not mw or not mw.isVisible():
                return
            
            hou_geo = mw.geometry()
            if hou_geo.width() <= 0 or hou_geo.height() <= 0:
                return
            
            # Load saved offset (default: top-right position)
            offset_x = self.s.value("minibar_offset_x", -85, type=int)
            offset_y = self.s.value("minibar_offset_y", 0, type=int)
            
            # Calculate position from Houdini geometry + offset
            hou_right = hou_geo.x() + hou_geo.width()
            hou_top = hou_geo.y()
            minibar_right = hou_right + offset_x
            minibar_top = hou_top + offset_y
            new_x = minibar_right - self.width()
            new_y = minibar_top
            
            # NO SCREEN CONSTRAINT - Allow MiniBar at any position
            # User is responsible for positioning (can use reset if needed)
            
            # Move to new position
            self.move(new_x, new_y)
            
        except Exception as e:
            if DEBUG:
                debug_print(f"⚠️ Error updating position: {e}")
        finally:
            self._updating_position = False

    def _get_default_position(self):
        """Get default position (used for both initial load and reset)"""
        try:
            # Use primary screen for positioning (more reliable)
            screen = QtWidgets.QApplication.primaryScreen()
            if not screen:
                return (20, 80)
            
            screen_geo = screen.availableGeometry()
            
            # Position in top-right area of primary screen
            # 20px from right edge, 20px from top
            minibar_width = 400  # Approximate MiniBar width
            new_x = screen_geo.x() + screen_geo.width() - minibar_width - 20
            new_y = screen_geo.y() + 20
            
            # Ensure within screen bounds
            minibar_width = 400  # Approximate MiniBar width
            minibar_height = 40  # Approximate MiniBar height
            
            new_x = max(screen_geo.x() + 10, min(new_x, screen_geo.x() + screen_geo.width() - minibar_width - 10))
            new_y = max(screen_geo.y() + 10, min(new_y, screen_geo.y() + screen_geo.height() - minibar_height - 10))
            
            return (new_x, new_y)
            
        except Exception as e:
            return (20, 80)

    def _restore_relative_position(self):
        """Restore MiniBar position using offset-based calculation"""
        try:
            # Always use offset-based positioning for consistency
            self._update_position_relative_to_main_window()
        except Exception as e:
            # Fallback to default position
            default_x, default_y = self._get_default_position()
            self.move(default_x, default_y)


    def _update_lock_visual_feedback(self):
        if self._locked:
            self.handle_area.setText("🔒"); self.handle_area.setToolTip("Position locked • Right-click to unlock"); self.handle_area.setCursor(QtCore.Qt.ForbiddenCursor)
            self.setStyleSheet(self.styleSheet().replace("border:1px solid #3a3a3a;","border:1px solid #5a3a3a;"))
        else:
            self.handle_area.setText("⋮⋮"); self.handle_area.setToolTip("Drag to move • Right-click for options"); self.handle_area.setCursor(QtCore.Qt.OpenHandCursor)
            self.setStyleSheet(self.styleSheet().replace("border:1px solid #5a3a3a;","border:1px solid #3a3a3a;"))

    # ---- File menu (dropdown) ----
    def _show_file_menu(self):
        """Show file dropdown menu"""
        if self.combo.count() == 0:
            # Show better message based on context
            type_name = self.current_type
            dept_name = self.current_dept
            
            if not type_name:
                msg = "No project configured.\n\nClick ⚡ button to set up project."
            elif not dept_name:
                msg = f"No department selected.\n\nClick 📁 button to select department."
            else:
                msg = f"No files found in:\n{type_name} / {dept_name}\n\nTry a different department or type."
            
            hou.ui.displayMessage(msg, severity=hou.severityType.Warning)
            return
        menu = QtWidgets.QMenu(); menu.setAttribute(QtCore.Qt.WA_DeleteOnClose); menu.setStyleSheet("""
            QMenu { background:#1f1f1f; color:#e5e5e5; border:1px solid #3a3a3a; }
            QMenu::item { padding:8px 16px; }
            QMenu::item:selected { background:#3d5a99; }
        """)
        shot_files = {}
        for i in range(self.combo.count()):
            fp = self.combo.itemData(i, role=QtCore.Qt.UserRole)
            if not fp: continue
            model_shot = self.combo.itemData(i, role=QtCore.Qt.UserRole+2)
            shot = model_shot if model_shot else (infer_shot(fp) or "Unknown")
            filename = os.path.basename(fp); ver_str = parse_ver(filename)
            try: ver_num = int(ver_str.replace('v', '')) if ver_str else 0
            except: ver_num = 0
            if shot not in shot_files or ver_num > shot_files[shot]['version']:
                shot_files[shot] = {'index': i, 'version': ver_num, 'ver_str': ver_str}
        current_file = get_current_houdini_file()
        for shot in sorted(shot_files.keys()):
            file_info = shot_files[shot]; idx = file_info['index']
            fp = self.combo.itemData(idx, role=QtCore.Qt.UserRole); is_cur = is_current_file(fp) if current_file else False
            display_text = f"{shot} ({file_info['ver_str']})" if file_info['ver_str'] else shot
            if is_cur: display_text = f"🎯 {display_text} (Current)"
            action = menu.addAction(display_text); action.setData(idx)
            if is_cur:
                font = action.font(); font.setBold(True); action.setFont(font)
        pos = self.shot_display.mapToGlobal(self.shot_display.rect().bottomLeft())
        selected_action = menu.exec_(pos)
        if selected_action:
            idx = selected_action.data(); self.combo.setCurrentIndex(idx); self._activate_current(idx)

    def _activate_current(self, idx):
        fp=self.combo.itemData(idx, role=QtCore.Qt.UserRole)
        if fp:
            self.s.setValue("last_selected_path", fp); self.s.sync(); self._open_houdini_file(fp)

    def _open_houdini_file(self, filepath):
        try:
            if not os.path.exists(filepath):
                hou.ui.displayMessage(f"File không tồn tại:\n{filepath}", severity=hou.severityType.Warning); return
            
            # Open Houdini file (only .hip files supported)
            if hou.hipFile.hasUnsavedChanges():
                choice = hou.ui.displayMessage(
                    "Scene hiện tại có thay đổi chưa save.\nBạn có muốn save trước khi mở file mới?",
                    buttons=("Save & Open", "Open Without Saving", "Cancel"),
                    severity=hou.severityType.ImportantMessage,
                    default_choice=0,
                    close_choice=2
                )
                if choice == 0:
                    try: hou.hipFile.save()
                    except hou.OperationFailed as e:
                        hou.ui.displayMessage(f"Không thể save file:\n{str(e)}", severity=hou.severityType.Error); return
                elif choice == 2: return
            hou.hipFile.load(filepath, suppress_save_prompt=True)
            hou.ui.setStatusMessage(f"Đã mở: {os.path.basename(filepath)}", severity=hou.severityType.Message)
                
        except Exception as e:
            hou.ui.displayMessage(f"Lỗi khi mở file:\n{str(e)}", severity=hou.severityType.Error)
    
    # ---- Quick menu actions ----
    def _open_current_file_location(self):
        try:
            current_file = hou.hipFile.name()
            if current_file and current_file != "untitled.hip":
                if os.path.exists(current_file):
                    open_in_explorer(current_file); debug_print(f"📁 Opened location: {os.path.dirname(current_file)}")
                else:
                    hou.ui.displayMessage(f"File not found:\n{current_file}", severity=hou.severityType.Warning)
            else:
                hou.ui.displayMessage("No scene file to open (untitled scene)", severity=hou.severityType.Warning)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to open file location:\n{str(e)}", severity=hou.severityType.Error)

    def _open_render_folder(self):
        try:
            current_file = hou.hipFile.name()
            if not current_file or current_file == "untitled.hip":
                hou.ui.displayMessage("No scene file to find render folder (untitled scene)", severity=hou.severityType.Warning); return
            render_folder = get_render_folder_path(current_file)
            if not render_folder:
                hou.ui.displayMessage("Could not determine render folder path", severity=hou.severityType.Warning); return
            if os.path.exists(render_folder):
                open_in_explorer(render_folder); debug_print(f"🎬 Opened render folder: {render_folder}")
            else:
                result = hou.ui.displayMessage(
                    f"Render folder does not exist:\n{render_folder}\n\nWould you like to create it?",
                    buttons=("Create & Open", "Cancel"), severity=hou.severityType.Message, default_choice=0, close_choice=1, title="Render Folder Not Found"
                )
                if result == 0:
                    try: os.makedirs(render_folder, exist_ok=True); open_in_explorer(render_folder); debug_print(f"🎬 Created and opened render folder: {render_folder}")
                    except Exception as create_error:
                        hou.ui.displayMessage(f"Failed to create render folder:\n{str(create_error)}", severity=hou.severityType.Error)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to open render folder:\n{str(e)}", severity=hou.severityType.Error)

    def _reload_scene(self):
        try:
            current_file = hou.hipFile.name()
            if current_file and current_file != "untitled.hip":
                if hou.hipFile.hasUnsavedChanges():
                    result = hou.ui.displayMessage("Scene has unsaved changes. Save before reloading?", buttons=("Save & Reload", "Reload Without Saving", "Cancel"), severity=hou.severityType.ImportantMessage)
                    if result == 0: hou.hipFile.save(); hou.hipFile.load(current_file)
                    elif result == 1: hou.hipFile.load(current_file)
                else:
                    hou.hipFile.load(current_file)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to reload scene:\n{str(e)}", severity=hou.severityType.Error)

    def _restart_houdini(self):
        try:
            result = hou.ui.displayMessage("This will restart Houdini. Any unsaved changes will be lost.\n\nContinue?", buttons=("Restart", "Cancel"), severity=hou.severityType.ImportantMessage)
            if result != 0: return
            try:
                debug_print("🔄 Method 1: Trying hou.exit(restart=True)..."); hou.exit(restart=True)
            except Exception as exit_error:
                debug_print(f"⚠️ hou.exit(restart=True) failed: {exit_error}")
                try:
                    import sys
                    houdini_exe = sys.executable
                    if "houdini" not in houdini_exe.lower():
                        hfs_path = os.environ.get("HFS", ""); houdini_bin = os.path.join(hfs_path, "bin", "houdini.exe")
                        if os.path.exists(houdini_bin): houdini_exe = houdini_bin
                    if os.path.exists(houdini_exe):
                        cmd = [houdini_exe]; current_scene = None
                        try:
                            current_scene = hou.hipFile.name();
                            if current_scene == "untitled.hip": current_scene=None
                        except: pass
                        if current_scene and os.path.exists(current_scene): cmd.append(current_scene)
                        process = subprocess.Popen(cmd, shell=False, cwd=os.path.dirname(houdini_exe))
                        from mono_tools.qt import QtCore as _QtCore
                        def delayed_exit(): debug_print("👋 Closing current instance..."); hou.exit()
                        _QtCore.QTimer.singleShot(1500, delayed_exit)
                        hou.ui.displayMessage("🔃 Houdini restart initiated!\n\n✅ New instance starting...\n👋 Current instance will close in 1.5 seconds", severity=hou.severityType.Message, default_choice=0, close_choice=0)
                except Exception as popen_error:
                    debug_print(f"❌ Failed to start subprocess: {popen_error}")
        except Exception as e:
            hou.ui.displayMessage(f"Failed to restart Houdini:\n{str(e)}", severity=hou.severityType.Error)

    def _new_file(self):
        """Create new file with auto-naming based on type/department"""
        try:
            # Get current selections
            type_name = self.current_type
            department = self.current_dept
            
            if not type_name:
                hou.ui.displayMessage(
                    "Please select a type first.\n\nClick 🏷️ Type button to select.",
                    severity=hou.severityType.Warning,
                    title="New File"
                )
                return
            
            if not department:
                hou.ui.displayMessage(
                    "Please select a department first.\n\nClick 📁 Dept button to select.",
                    severity=hou.severityType.Warning,
                    title="New File"
                )
                return
            
            # Get project settings
            root = self.s.value("project_root", "", type=str)
            project = self.s.value("current_project", "", type=str)
            
            if not root or not project:
                hou.ui.displayMessage(
                    "No project configured.\n\nClick ⚙️ Settings to configure project.",
                    severity=hou.severityType.Warning,
                    title="New File"
                )
                return
            
            # Ask for asset/shot name
            is_assets = self.current_type_is_assets
            
            if is_assets:
                prompt = f"Create new asset file:\n\nType: {type_name}\nDepartment: {department}\n\nEnter asset name (e.g., Cyborg, Chair, Tree):"
            else:
                prompt = f"Create new shot file:\n\nType: {type_name}\nDepartment: {department}\n\nEnter shot name (e.g., Sh010, Sh020):"
            
            result = hou.ui.readInput(
                prompt,
                buttons=("Create", "Cancel"),
                severity=hou.severityType.Message,
                default_choice=0,
                close_choice=1,
                title="New File"
            )
            
            if result[0] != 0:  # Cancelled
                return
            
            asset_name = result[1].strip()
            if not asset_name:
                hou.ui.displayMessage(
                    "Asset name cannot be empty.",
                    severity=hou.severityType.Warning,
                    title="New File"
                )
                return
            
            # Generate filename
            filename = generate_new_filename(type_name, asset_name, department, "v001", ".hip")
            
            # Determine target directory
            if is_assets:
                # Assets: 01_assets/_characters/char_AssetName/01_modeling/
                # Add prefix if not present
                if not any(asset_name.lower().startswith(p) for p in ['char_', 'prop_', 'env_', 'veh_']):
                    # Guess prefix from type
                    if 'character' in type_name.lower():
                        asset_name = f"char_{asset_name}"
                    elif 'prop' in type_name.lower():
                        asset_name = f"prop_{asset_name}"
                    elif 'environment' in type_name.lower():
                        asset_name = f"env_{asset_name}"
                
                target_dir = os.path.join(root, project, "01_assets", type_name, asset_name, department)
            else:
                # Shots: 02_shots/03_lighting/
                # Extract subpath from department
                subpath = os.path.join("02_shots", department)
                target_dir = os.path.join(root, project, subpath)
            
            # Create directory if not exists
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                debug_print(f"📁 Created directory: {target_dir}")
            
            # Full file path
            filepath = os.path.join(target_dir, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                choice = hou.ui.displayMessage(
                    f"File already exists:\n{filename}\n\nDo you want to open it instead?",
                    buttons=("Open", "Cancel"),
                    severity=hou.severityType.Warning,
                    default_choice=0,
                    close_choice=1,
                    title="File Exists"
                )
                
                if choice == 0:
                    # Open existing file
                    hou.hipFile.load(filepath, suppress_save_prompt=True)
                    hou.ui.setStatusMessage(f"Opened: {filename}", severity=hou.severityType.Message)
                return
            
            # Save current scene if has unsaved changes
            if hou.hipFile.hasUnsavedChanges():
                save_choice = hou.ui.displayMessage(
                    "Current scene has unsaved changes.\n\nSave before creating new file?",
                    buttons=("Save & Create", "Create Without Saving", "Cancel"),
                    severity=hou.severityType.ImportantMessage,
                    default_choice=0,
                    close_choice=2,
                    title="Unsaved Changes"
                )
                
                if save_choice == 0:
                    try:
                        hou.hipFile.save()
                    except hou.OperationFailed as e:
                        hou.ui.displayMessage(f"Failed to save:\n{str(e)}", severity=hou.severityType.Error)
                        return
                elif save_choice == 2:
                    return
            
            # Create new file
            hou.hipFile.clear()
            hou.hipFile.save(filepath)
            
            # Refresh file list
            self._refresh_files_for_current_tab()
            
            # Show success message
            hou.ui.setStatusMessage(f"Created: {filename}", severity=hou.severityType.Message)
            hou.ui.displayMessage(
                f"New file created successfully!\n\n{filename}\n\nLocation:\n{target_dir}",
                severity=hou.severityType.Message,
                title="New File Created"
            )
            
        except Exception as e:
            hou.ui.displayMessage(
                f"Failed to create new file:\n{str(e)}",
                severity=hou.severityType.Error,
                title="New File Error"
            )
            import traceback
            traceback.print_exc()
    
    def _new_folder(self):
        """Create new asset or shot folder structure"""
        try:
            # Get project settings
            root = self.s.value("project_root", "", type=str)
            project = self.s.value("current_project", "", type=str)
            
            if not root or not project:
                hou.ui.displayMessage(
                    "No project configured.\n\nClick ⚙️ Settings to configure project.",
                    severity=hou.severityType.Warning,
                    title="New Folder"
                )
                return
            
            # Ask user: Asset or Shot? (using custom styled dialog)
            from .ui import ChoiceDialog
            
            choice_dialog = ChoiceDialog(
                parent=self,
                title="New Folder",
                message="What would you like to create?",
                choices=["Asset Folder", "Shot Folder"],
                icons=["🎨", "🎬"]
            )
            
            if choice_dialog.exec_():
                selected = choice_dialog.get_selected_index()
                
                if selected == 0:  # Asset
                    self._new_asset_folder(root, project)
                elif selected == 1:  # Shot
                    self._new_shot_folder(root, project)
                
        except Exception as e:
            hou.ui.displayMessage(
                f"Error creating folder:\n{str(e)}",
                severity=hou.severityType.Error,
                title="New Folder Error"
            )
            import traceback
            traceback.print_exc()
    
    def _new_asset_folder(self, root, project):
        """Create new asset folder structure"""
        try:
            # Load asset types from config (not scan - so user can create even if folder doesn't exist)
            asset_types = load_asset_types_config()
            
            if not asset_types:
                hou.ui.displayMessage(
                    "No asset types configured.\n\nPlease configure in Settings.",
                    severity=hou.severityType.Warning,
                    title="New Folder"
                )
                return
            
            # Build type selection for dropdown
            project_path = os.path.join(root, project)
            type_choices = []
            type_ids = []
            
            for atype in asset_types:
                type_id = atype['id']
                type_name = atype.get('name', type_id)
                icon = atype.get('icon', '📁')
                
                # Count existing assets (if type folder exists)
                type_path = os.path.join(project_path, "01_assets", type_id)
                if os.path.exists(type_path):
                    count = len([d for d in os.listdir(type_path) if os.path.isdir(os.path.join(type_path, d))])
                    type_choices.append(f"{icon} {type_name} ({count} existing)")
                else:
                    type_choices.append(f"{icon} {type_name} (new type folder)")
                
                type_ids.append(type_id)
            
            # Show native Houdini selection dialog
            selected = hou.ui.selectFromList(
                type_choices,
                message="Select asset type for new folder:",
                title="New Folder - Select Type",
                column_header="Type",
                num_visible_rows=len(type_choices)
            )
            
            if not selected:  # Cancelled
                return
            
            selected_type = type_ids[selected[0]]
            
            # Ask for asset name (using custom styled dialog)
            from .ui import InputDialog
            
            input_dialog = InputDialog(
                parent=self,
                title="New Asset",
                message=f"Type: {selected_type}\n\nEnter asset name:",
                initial_value="",
                placeholder="e.g., Phoenix, Table, Tree"
            )
            
            if not input_dialog.exec_():
                return
            
            asset_name = input_dialog.get_value()
            if not asset_name:
                hou.ui.displayMessage("Asset name cannot be empty.", severity=hou.severityType.Warning)
                return
            
            # Get standard departments
            departments = get_standard_departments()
            
            # Load department config for preview
            from .file_manager_helpers import load_department_config
            config = load_department_config()
            dept_map = {}
            if config and 'standard_departments' in config:
                dept_map = {d['id']: d for d in config['standard_departments']}
            
            # Build preview with software subfolders
            # Get prefix for asset name
            prefix = ''
            for atype in asset_types:
                if atype['id'] == selected_type:
                    prefix = atype.get('prefix', '')
                    break
            
            preview = f"Creating folder structure:\n\n"
            preview += f"01_assets/{selected_type}/{prefix}{asset_name}/\n"
            
            # Show each department with software subfolders if configured
            for i, dept_id in enumerate(departments):
                dept_config = dept_map.get(dept_id, {})
                software_folders = dept_config.get('software_folders', [])
                
                is_last = (i == len(departments) - 1)
                branch = "└─" if is_last else "├─"
                
                if software_folders:
                    preview += f"  {branch} {dept_id}/\n"
                    for j, software in enumerate(software_folders):
                        is_last_sw = (j == len(software_folders) - 1)
                        sw_branch = "└─" if is_last_sw else "├─"
                        indent = "     " if is_last else "  │  "
                        preview += f"{indent}{sw_branch} {software}/\n"
                else:
                    preview += f"  {branch} {dept_id}/\n"
            
            # Count total folders that will be created
            total_folders = 0
            for dept_id in departments:
                dept_config = dept_map.get(dept_id, {})
                software_folders = dept_config.get('software_folders', [])
                subdepartments = dept_config.get('subdepartments', [])
                create_publish = dept_config.get('create_publish', False)
                
                # Main department folder
                total_folders += 1
                
                # Software folders
                total_folders += len(software_folders)
                
                # Subdepartments
                for subdept in subdepartments:
                    total_folders += 1  # Subdepartment folder
                    if subdept.get('create_publish', False):
                        total_folders += 1  # Subdepartment publish
                
                # Department publish
                if create_publish:
                    total_folders += 1
            preview += f"\nTotal: {len(departments)} departments, {total_folders} folders\n\nProceed?"
            
            confirm = hou.ui.displayMessage(
                preview,
                buttons=("Create", "Cancel"),
                severity=hou.severityType.Message,
                default_choice=0,
                close_choice=1,
                title="Confirm Folder Structure"
            )
            
            if confirm != 0:  # Cancelled
                return
            
            # Create folder structure
            success, asset_folder, message = create_asset_folder_structure(
                project_path, 
                selected_type, 
                asset_name, 
                departments
            )
            
            if success:
                # Show success message
                hou.ui.displayMessage(
                    message,
                    severity=hou.severityType.Message,
                    title="Folder Created"
                )
                
                # Refresh file list if type matches current selection
                if self.current_type == selected_type:
                    self._refresh_files_for_current_tab()
                
                # Ask if user wants to create a file in the new folder
                create_file = hou.ui.displayMessage(
                    "Folder structure created!\n\nWould you like to create a new file in this asset?",
                    buttons=("Yes", "No"),
                    severity=hou.severityType.Message,
                    default_choice=0,
                    close_choice=1,
                    title="Create File?"
                )
                
                if create_file == 0:
                    # Set type and open new file dialog
                    # asset_types here is from config, need to convert format for _select_type
                    type_path = os.path.join(project_path, "01_assets", selected_type)
                    is_assets = True
                    self._select_type(selected_type, type_path, is_assets)
                    
                    # Open new file dialog (will use current type)
                    self._new_file()
            else:
                hou.ui.displayMessage(
                    message,
                    severity=hou.severityType.Error,
                    title="Folder Creation Failed"
                )
            
        except Exception as e:
            hou.ui.displayMessage(
                f"Failed to create folder structure:\n{str(e)}",
                severity=hou.severityType.Error,
                title="New Folder Error"
            )
            import traceback
            traceback.print_exc()
    
    def _new_shot_folder(self, root, project):
        """Create new shot folder structure"""
        try:
            from .ui import ConfigManager
            
            project_path = os.path.join(root, project)
            
            # Ask for shot name (using custom styled dialog)
            from .ui import InputDialog
            
            input_dialog = InputDialog(
                parent=self,
                title="New Shot",
                message="Enter shot name:\n\nFormat: sq010_sh0010 (Sequence + Shot number)",
                initial_value="sq010_sh0010",
                placeholder="sq010_sh0010"
            )
            
            if not input_dialog.exec_():
                return
            
            shot_name = input_dialog.get_value()
            if not shot_name:
                hou.ui.displayMessage("Shot name cannot be empty.", severity=hou.severityType.Warning)
                return
            
            # Validate shot name format (optional but recommended)
            if '_' not in shot_name:
                hou.ui.displayMessage(
                    "Shot name should follow format: sq###_sh####\n\nExample: sq010_sh0010",
                    severity=hou.severityType.Warning
                )
                return
            
            # Load shot departments using ConfigManager
            shot_departments = ConfigManager.load_shot_departments()
            
            if not shot_departments:
                hou.ui.displayMessage(
                    "No shot departments configured.\n\nUsing default: Layout/Anim/FX/Light/Comp",
                    severity=hou.severityType.Warning,
                    title="New Shot"
                )
            
            # Build preview
            preview = f"Creating shot structure:\n\n"
            preview += f"02_shots/{shot_name}/\n"
            
            for i, dept in enumerate(shot_departments):
                dept_id = dept['id']
                dept_name = dept.get('name', dept_id)
                icon = dept.get('icon', '📁')
                software_folders = dept.get('software_folders', [])
                create_publish = dept.get('create_publish', False)
                
                is_last = (i == len(shot_departments) - 1)
                branch = "└─" if is_last else "├─"
                
                preview += f"  {branch} {icon} {dept_id}/ ({dept_name})\n"
                
                # Software subfolders
                if software_folders:
                    for j, sw in enumerate(software_folders):
                        is_last_sw = (j == len(software_folders) - 1) and not create_publish
                        sw_branch = "└─" if is_last_sw else "├─"
                        indent = "     " if is_last else "  │  "
                        preview += f"{indent}{sw_branch} {sw}/\n"
                
                # Publish folder
                if create_publish:
                    indent = "     " if is_last else "  │  "
                    preview += f"{indent}└─ _publish/\n"
            
            total_folders = len(shot_departments)
            for dept in shot_departments:
                total_folders += len(dept.get('software_folders', []))
                if dept.get('create_publish', False):
                    total_folders += 1
            
            preview += f"\nTotal: {len(shot_departments)} departments, {total_folders} folders\n\nProceed?"
            
            confirm = hou.ui.displayMessage(
                preview,
                buttons=("Create", "Cancel"),
                severity=hou.severityType.Message,
                default_choice=0,
                close_choice=1,
                title="Confirm Shot Structure"
            )
            
            if confirm != 0:  # Cancelled
                return
            
            # Create shot folder structure
            shot_base = os.path.join(project_path, "02_shots")
            os.makedirs(shot_base, exist_ok=True)
            
            shot_folder = os.path.join(shot_base, shot_name)
            
            if os.path.exists(shot_folder):
                hou.ui.displayMessage(
                    f"Shot already exists:\n{shot_name}",
                    severity=hou.severityType.Warning
                )
                return
            
            # Create shot folder
            os.makedirs(shot_folder, exist_ok=True)
            
            # Create all department folders
            for dept in shot_departments:
                dept_id = dept['id']
                dept_folder = os.path.join(shot_folder, dept_id)
                os.makedirs(dept_folder, exist_ok=True)
                
                # Software subfolders
                for sw in dept.get('software_folders', []):
                    sw_folder = os.path.join(dept_folder, sw)
                    os.makedirs(sw_folder, exist_ok=True)
                
                # Publish folder
                if dept.get('create_publish', False):
                    publish_folder = os.path.join(dept_folder, '_publish')
                    os.makedirs(publish_folder, exist_ok=True)
            
            # Success message
            hou.ui.displayMessage(
                f"Shot created successfully!\n\n{shot_name}\n\nCreate a new file in this shot?",
                buttons=("Create File", "Done"),
                severity=hou.severityType.Message,
                title="Shot Created"
            )
            
            # TODO: Open new file dialog for shot
            
        except Exception as e:
            hou.ui.displayMessage(
                f"Failed to create shot:\n{str(e)}",
                severity=hou.severityType.Error,
                title="New Shot Error"
            )
            import traceback
            traceback.print_exc()
    
    def _save_version(self):
        try:
            current_file = hou.hipFile.name()
            if not current_file or current_file == "untitled.hip":
                hou.ui.displayMessage("Please save the scene file first before creating a version.", severity=hou.severityType.Warning); return
            if not os.path.exists(current_file):
                hou.ui.displayMessage(f"Current file not found:\n{current_file}", severity=hou.severityType.Warning); return
            current_basename = os.path.basename(current_file); current_name, current_ext = os.path.splitext(current_basename)
            ver_match = parse_ver(current_name)
            example_no_note = f"{current_name}{current_ext}"; example_with_note = f"{current_name}_note{current_ext}"
            note = ""; note_input = hou.ui.readInput(
                "Add a note to this version? (optional)\n\n"
                f"Current: {current_basename}\n"
                f"New (no note): {example_no_note}\n"
                f"New (with note): {example_with_note}\n\n"
                "Enter note below (leave empty to skip):",
                buttons=("Save", "Cancel"), severity=hou.severityType.Message, default_choice=0, close_choice=1, title="Save Version")
            if note_input[0] != 0: return
            if note_input[1].strip(): note = note_input[1].strip()
            success, new_filepath, message = increment_version_and_backup(current_file, note)
            if success:
                self._check_file_changes(); hou.ui.displayMessage(message, severity=hou.severityType.Message, title="Save Version Success")
            else:
                hou.ui.displayMessage(message, severity=hou.severityType.Error, title="Save Version Failed")
        except Exception as e:
            hou.ui.displayMessage(f"Unexpected error during save version:\n{str(e)}", severity=hou.severityType.Error, title="Save Version Error")

    # ---- Manager integration ----
    def _open_manager(self):
        if not self.manager:
            self.manager=self.manager_factory(); self.manager._minibar_ref=self
        
        # Sync type and tab selection
        type_idx = self.type_cb.currentIndex()
        self.manager.type_tabs.setCurrentIndex(type_idx)
        
        tab_name = self.tab_cb.currentText()
        if type_idx == 0:  # Assets
            for i in range(self.manager.assets_tabs.count()):
                if self.manager.assets_tabs.tabText(i) == tab_name:
                    self.manager.assets_tabs.setCurrentIndex(i)
                    break
        else:  # Shots
            for i in range(self.manager.shots_tabs.count()):
                if self.manager.shots_tabs.tabText(i) == tab_name:
                    self.manager.shots_tabs.setCurrentIndex(i)
                    break
        
        # Save current settings for standalone mode
        if hasattr(self.manager, 'root_le') and self.manager.root_le.text().strip():
            root = self.manager.root_le.text().strip()
            self.s.setValue("project_root", root)
            debug_print(f"💾 Saved project root: {root}")
        
        if hasattr(self.manager, 'project_cb') and self.manager.project_cb.currentText().strip():
            project = self.manager.project_cb.currentText().strip()
            self.s.setValue("current_project", project)
            debug_print(f"💾 Saved current project: {project}")
        
        if self.manager.root_le.text().strip():
            QtCore.QTimer.singleShot(100, self.manager.scan)
        self.manager.show(); self.manager.raise_(); self.manager.activateWindow()

    # ---- Populate helpers ----
    def populate(self, paths, shot_names=None):
        debug_print(f"📁 Populating MiniBar with {len(paths)} files")
        
        # Always clear combo first to prevent showing stale data
        self.combo.clear()
        shot_names = shot_names or {}
        
        # Handle empty state
        if not paths:
            debug_print("No files found")
            self.shot_display.setText("No files")
            self.shot_display.setToolTip("No files found for current selection")
            return
        
        # Log found files
        debug_print("Files found:")
        sorted_paths = sorted(paths)
        for i, p in enumerate(sorted_paths[:10]):  # Show first 10 files
            name = os.path.basename(p)
            ver = parse_ver(name)
            debug_print(f"  {i+1}. {name} (v{ver or '—'})")
        if len(sorted_paths) > 10:
            debug_print(f"  ... and {len(sorted_paths) - 10} more files")
            
        added_count = 0
        for p in sorted(paths):
            # Use asset name if available, otherwise use filename
            if p in shot_names:
                display_name = shot_names[p]  # This is actually asset_name now
                name = os.path.basename(p)
                ver = parse_ver(name)
                label = f"{display_name} - {name} ({ver or '—'})"
            else:
                name = os.path.basename(p)
                ver = parse_ver(name)
                label = f"{name} ({ver or '—'})"
            
            idx = self.combo.count()
            self.combo.addItem(label)
            self.combo.setItemData(idx, p, QtCore.Qt.UserRole)
            self.combo.setItemData(idx, label, QtCore.Qt.DisplayRole)
            self.combo.setItemData(idx, name, QtCore.Qt.ToolTipRole)
            if p in shot_names: 
                self.combo.setItemData(idx, shot_names[p], QtCore.Qt.UserRole+2)
            added_count += 1
        
        # Clear shot display if no files found
        if self.combo.count() == 0:
            self.shot_display.setText("No files")
            self.shot_display.setToolTip("No files available")
            return
        
        current_file = get_current_houdini_file(); current_selected=False
        if current_file:
            for i in range(self.combo.count()):
                fp = self.combo.itemData(i, role=QtCore.Qt.UserRole)
                if is_current_file(fp): self.combo.setCurrentIndex(i); current_selected=True; break
        if not current_selected:
            last = self.s.value("last_selected_path", "", type=str)
            if last:
                i = self.combo.findData(last, role=QtCore.Qt.UserRole)
                if i >= 0: self.combo.setCurrentIndex(i)
        self._update_shot_display(self.combo.currentIndex()); self._last_current_file = current_file

    def populate_from_model(self, model):
        paths=[]; shot_names={}
        for r in range(model.rowCount()):
            p=model.item(r, 0).data(QtCore.Qt.UserRole+1)
            shot_name = model.item(r, 0).text()
            if p: paths.append(p); shot_names[p]=shot_name
        self.populate(paths, shot_names)

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


    def _load_tabs_for_type(self, type_index):
        """Load available tabs based on type (0=Assets, 1=Shots)"""
        try:
            debug_print(f"🔄 Loading tabs for type {type_index} ({'Assets' if type_index == 0 else 'Shots'})")
            self.tab_cb.blockSignals(True)
            self.tab_cb.clear()
            
            if type_index == 0:  # Assets
                # Load asset tabs from hardcoded config
                assets_configs = [
                    {"name": "models", "is_asset_tab": True, "asset_type": "_characters", "department": "01_modeling"},
                    {"name": "rigging", "is_asset_tab": True, "asset_type": "_characters", "department": "02_rigging"},
                    {"name": "surfacing", "is_asset_tab": True, "asset_type": "_characters", "department": "03_surfacing"},
                    {"name": "lookdev", "is_asset_tab": True, "asset_type": "_characters", "department": "04_lookdev"},
                    {"name": "groom", "is_asset_tab": True, "asset_type": "_characters", "department": "05_groom"}
                ]
                for conf in assets_configs:
                    name = conf.get('name', 'Unknown')
                    self.tab_cb.addItem(name, conf)
                debug_print(f"✅ Loaded {len(assets_configs)} asset tabs: {[c['name'] for c in assets_configs]}")
            else:  # Shots
                # Load shot tabs from hardcoded config
                shots_configs = [
                    {"name": "lighting", "subpath": "02_shots/03_lighting", "depth": 1},
                    {"name": "animation", "subpath": "02_shots/02_animation", "depth": 1},
                    {"name": "comp", "subpath": "02_shots/04_comp", "depth": 1}
                ]
                for conf in shots_configs:
                    name = conf.get('name', 'lighting')
                    self.tab_cb.addItem(name, conf)
                debug_print(f"✅ Loaded {len(shots_configs)} shot tabs: {[c['name'] for c in shots_configs]}")
            
            # Restore last selected tab for this type
            saved_tab_key = f"minibar_tab_{type_index}"
            saved_tab = self.s.value(saved_tab_key, "", type=str)
            if saved_tab:
                idx = self.tab_cb.findText(saved_tab)
                if idx >= 0:
                    self.tab_cb.setCurrentIndex(idx)
                    debug_print(f"✅ Restored tab: {saved_tab}")
                else:
                    self.tab_cb.setCurrentIndex(0)
                    debug_print(f"⚠️ Saved tab '{saved_tab}' not found, using default")
            else:
                # Set default selection
                self.tab_cb.setCurrentIndex(0)
                debug_print(f"✅ Using default tab selection")
            
            self.tab_cb.blockSignals(False)
            
            # Don't trigger refresh here - let the caller handle it
            debug_print(f"✅ Tab dropdown now has {self.tab_cb.count()} items")
            
            # Don't trigger initial load here - let user interaction trigger it
                
        except Exception as e:
            debug_print(f"⚠️ Error loading tabs for type: {e}")


    def _refresh_files_for_current_tab(self):
        """Refresh files based on current type and tab selection"""
        try:
            if not self.manager:
                debug_print("⚠️ No manager available for file refresh")
                # Try to refresh without manager using saved settings
                self._refresh_files_standalone()
                return
            
            type_idx = self.type_cb.currentIndex()
            tab_config = self.tab_cb.itemData(self.tab_cb.currentIndex())
            
            if not tab_config:
                debug_print("⚠️ No tab config available")
                return
            
            root = self.manager.root_le.text().strip()
            project = self.manager.project_cb.currentText().strip()
            
            if not root or not project:
                debug_print(f"⚠️ Missing root or project: root='{root}', project='{project}'")
                return
            
            debug_print(f"🔄 Refreshing files for type {type_idx} ({'Assets' if type_idx == 0 else 'Shots'})")
            debug_print(f"📍 Root: {root}")
            debug_print(f"📍 Project: {project}")
            debug_print(f"📍 Tab: {tab_config.get('name', 'Unknown')}")
            
            if type_idx == 0:  # Assets mode
                # Get asset filtering from File Manager
                base_dir = os.path.join(root, project)
                debug_print(f"📍 Asset base dir: {base_dir}")
                
                from .file_manager_helpers import collect_asset_files_hybrid
                
                # Get current filters from manager if available
                asset_type = None
                department = None
                asset_name = None
                
                if hasattr(self.manager, 'asset_type_cb'):
                    asset_type_text = self.manager.asset_type_cb.currentText()
                    if asset_type_text and asset_type_text != "All Types":
                        asset_type = asset_type_text
                
                if hasattr(self.manager, 'department_cb'):
                    dept_text = self.manager.department_cb.currentText()
                    if dept_text and dept_text != "All Departments":
                        department = dept_text
                
                if hasattr(self.manager, 'asset_name_cb'):
                    asset_name_text = self.manager.asset_name_cb.currentText()
                    if asset_name_text and asset_name_text != "All Assets":
                        asset_name = asset_name_text
                
                debug_print(f"📍 Asset filters: type='{asset_type}', department='{department}', asset_name='{asset_name}'")
                
                # Collect asset files using hybrid approach
                asset_files = collect_asset_files_hybrid(base_dir, asset_type, department, asset_name)
                paths = [f[0] for f in asset_files]  # Extract file paths
                
                debug_print(f"📍 Found {len(asset_files)} asset files")
                if asset_files:
                    debug_print("Asset files details:")
                    for i, (filepath, asset_name, dept_name) in enumerate(asset_files[:5]):
                        debug_print(f"  {i+1}. {os.path.basename(filepath)} (asset: {asset_name}, dept: {dept_name})")
                    if len(asset_files) > 5:
                        debug_print(f"  ... and {len(asset_files) - 5} more asset files")
                
                # Create asset names from file paths for proper display
                asset_names = {}
                for filepath, asset_name, dept_name in asset_files:
                    asset_names[filepath] = asset_name
                
                self.populate(paths, asset_names)
                
            else:  # Shots mode
                subpath = tab_config.get('subpath', '02_shots/03_lighting')
                target_dir = os.path.join(root, project, subpath)
                debug_print(f"📍 Shot target dir: {target_dir}")
                
                if not os.path.isdir(target_dir):
                    debug_print(f"⚠️ Target directory does not exist: {target_dir}")
                    return
                
                from .file_manager_helpers import collect_files
                depth = tab_config.get('depth', 1)
                debug_print(f"📍 Scan depth: {depth}")
                files = collect_files(target_dir, depth=depth)
                debug_print(f"📍 Found {len(files)} shot files")
                if files:
                    debug_print("Shot files details:")
                    for i, filepath in enumerate(files[:5]):
                        debug_print(f"  {i+1}. {os.path.basename(filepath)}")
                    if len(files) > 5:
                        debug_print(f"  ... and {len(files) - 5} more shot files")
                self.populate(files)
            
        except Exception as e:
            debug_print(f"⚠️ Error refreshing files: {e}")

    def _refresh_files_standalone(self):
        """Refresh files without File Manager using saved settings"""
        try:
            
            # Get saved settings
            root = self.s.value("project_root", "", type=str)
            project = self.s.value("current_project", "", type=str)
            
            if not root or not project:
                debug_print(f"⚠️ Missing saved settings: root='{root}', project='{project}'")
                self.shot_display.setText("No project configured")
                self.shot_display.setToolTip("Click ⚡ to configure project")
                return
            
            project_path = os.path.join(root, project)
            if not os.path.isdir(project_path):
                debug_print(f"⚠️ Project directory not found: {project_path}")
                self.shot_display.setText("Project not found")
                self.shot_display.setToolTip("Click ⚡ to configure project")
                return
            
            # Get current selections from buttons
            type_name = self.current_type
            department = self.current_dept
            
            if not type_name:
                debug_print("⚠️ No type selected")
                self.shot_display.setText("Select type")
                self.shot_display.setToolTip("Click 🏷️ button to select type")
                return
            
            if not department:
                debug_print("⚠️ No department selected")
                self.shot_display.setText("Select department")
                self.shot_display.setToolTip("Click 📁 button to select department")
                return
            
            debug_print(f"🔄 Standalone refresh: type='{type_name}', dept='{department}'")
            
            # Collect files using new scan functions (always .hip files only)
            from .file_manager_helpers import collect_files_with_filters
            files_data = collect_files_with_filters(project_path, type_name, department)
            
            if not files_data:
                debug_print("⚠️ No files found")
                self.shot_display.setText("No files found")
                self.shot_display.setToolTip("No files found for current selection")
                return
            
            # Convert to old format for compatibility
            paths = [f[0] for f in files_data]
            asset_names = {f[0]: f[1] for f in files_data}  # filepath -> asset_name
            
            debug_print(f"📍 Found {len(files_data)} files")
            self.populate(paths, asset_names)
            
        except Exception as e:
            if DEBUG:
                debug_print(f"⚠️ Error in standalone refresh: {e}")
            self.shot_display.setText("Error loading files")
            self.shot_display.setToolTip("Error loading files - check settings")

    # ================ NEW METHODS FOR SETTINGS DIALOG ================
    
    def _load_minibar_settings(self):
        """Load saved minibar settings"""
        try:
            # Load project settings
            root = self.s.value("project_root", "", type=str)
            project = self.s.value("current_project", "", type=str)
            
            if root and project:
                project_path = os.path.join(root, project)
                if os.path.isdir(project_path):
                    # Load last selected type
                    saved_type = self.s.value("minibar_type", "", type=str)
                    
                    if saved_type:
                        # Try to load and select the saved type
                        from .file_manager_helpers import scan_project_types
                        types = scan_project_types(project_path)
                        
                        for type_name, type_path, is_assets in types:
                            if type_name == saved_type:
                                self._select_type(type_name, type_path, is_assets)
                                
                                # Load saved department
                                saved_dept_key = f"minibar_dept_{type_name}"
                                saved_dept = self.s.value(saved_dept_key, "", type=str)
                                if saved_dept:
                                    self._select_department(saved_dept)
                                break
                    return
            
            # No valid project, show empty state
            self.type_btn.setText("🏷️ Type")
            self.type_btn.setToolTip("No project configured • Click ⚡ to set up")
            self.dept_btn.setText("📁 Dept")
            self.dept_btn.setToolTip("No project configured")
            
        except Exception as e:
            debug_print(f"⚠️ Error loading minibar settings: {e}")
    
    def _apply_ui_scale(self):
        """Apply UI scale to MiniBar"""
        try:
            scale = self.s.value("minibar_ui_scale", 100, type=int)
            debug_print(f"🔍 Loading UI scale setting: {scale}%")
            
            if scale != 100:
                # Apply scale factor
                scale_factor = scale / 100.0
                debug_print(f"🔍 Applying scale factor: {scale_factor}")
                
                # Scale font sizes
                font = self.font()
                base_size = 11
                new_font_size = int(base_size * scale_factor)
                font.setPointSize(new_font_size)
                self.setFont(font)
                debug_print(f"🔍 Font size: {base_size} → {new_font_size}")
                
                # Scale button sizes
                base_size = 24
                scaled_size = int(base_size * scale_factor)
                debug_print(f"🔍 Button size: {base_size} → {scaled_size}")
                
                self.btn_quick_menu.setFixedSize(scaled_size, scaled_size)
                self.btn_settings.setFixedSize(int(32 * scale_factor), scaled_size)
                
                # Scale type and dept buttons
                type_width = int(70 * scale_factor)
                self.type_btn.setFixedSize(type_width, scaled_size)
                self.dept_btn.setFixedSize(type_width, scaled_size)
                debug_print(f"🔍 Type/Dept button size: 70 → {type_width}")
                
                # Scale handle
                handle_width = int(20 * scale_factor)
                self.handle_area.setFixedWidth(handle_width)
                debug_print(f"🔍 Handle width: 20 → {handle_width}")
                
                # Scale file display
                display_width = int(160 * scale_factor)
                self.shot_display.setMinimumWidth(display_width)
                self.shot_display.setMaximumWidth(display_width)
                debug_print(f"🔍 File display width: 160 → {display_width}")
                
                # Update margins and spacing
                layout = self.layout()
                margin_left = int(4 * scale_factor)
                margin_top = int(3 * scale_factor)
                margin_right = int(6 * scale_factor)
                margin_bottom = int(3 * scale_factor)
                spacing = int(3 * scale_factor)
                
                layout.setContentsMargins(margin_left, margin_top, margin_right, margin_bottom)
                layout.setSpacing(spacing)
                debug_print(f"🔍 Layout margins: (4,3,6,3) → ({margin_left},{margin_top},{margin_right},{margin_bottom})")
                debug_print(f"🔍 Layout spacing: 3 → {spacing}")
                
                debug_print(f"✅ UI scale applied successfully: {scale}%")
            else:
                debug_print(f"🔍 No scaling needed: {scale}%")
                
        except Exception as e:
            debug_print(f"⚠️ Error applying UI scale: {e}")
            import traceback
            traceback.print_exc()
    
    
    
    def _open_settings(self):
        """Open settings dialog"""
        try:
            from .file_manager_settings import MonoFileManagerSettings
            
            if not hasattr(self, 'settings_dialog') or not self.settings_dialog:
                self.settings_dialog = MonoFileManagerSettings(parent=self)
            
            self.settings_dialog.show()
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            
            # Connect to settings changed signal if available
            if hasattr(self.settings_dialog, 'settings_changed'):
                self.settings_dialog.settings_changed.connect(self._on_settings_changed)
                
        except Exception as e:
            debug_print(f"⚠️ Error opening settings dialog: {e}")
            hou.ui.displayMessage(f"Error opening settings:\n{str(e)}", 
                                 severity=hou.severityType.Error)
    
    def _on_settings_changed(self):
        """Handle settings changed signal from dialog"""
        try:
            # Reload settings
            self._load_minibar_settings()
            
            # Refresh files
            self._refresh_files_for_current_tab()
            
        except Exception as e:
            debug_print(f"⚠️ Error handling settings change: {e}")


