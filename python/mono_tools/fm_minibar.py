import os
import subprocess
from mono_tools.qt import QtCore, QtGui, QtWidgets
import hou
from .fm_helpers import ORG, APP, collect_files, get_current_houdini_file, is_current_file, infer_shot, parse_ver, open_in_explorer, get_render_folder_path, increment_version_and_backup

class MainWindowEventFilter(QtCore.QObject):
    def __init__(self, minibar):
        super().__init__(minibar); self.minibar = minibar; self._last_main_window_geo=None
    def eventFilter(self, obj, ev):
        if hasattr(self.minibar, '_is_dragging') and self.minibar._is_dragging: return super().eventFilter(obj, ev)
        if hasattr(self.minibar, '_updating_position') and self.minibar._updating_position: return super().eventFilter(obj, ev)
        if ev.type() in (QtCore.QEvent.Resize, QtCore.QEvent.Move):
            if not hasattr(self.minibar, '_main_window_change_timer'):
                self.minibar._main_window_change_timer = QtCore.QTimer(self.minibar)
                self.minibar._main_window_change_timer.setSingleShot(True)
                self.minibar._main_window_change_timer.timeout.connect(self._on_main_window_changed)
            if not self.minibar._main_window_change_timer.isActive():
                self.minibar._main_window_change_timer.start(150)
        return super().eventFilter(obj, ev)
    def _on_main_window_changed(self):
        try:
            mw = hou.qt.mainWindow()
            if mw and self.minibar and self.minibar.isVisible():
                current_geo = mw.geometry()
                significant_change = True
                if self._last_main_window_geo:
                    old_geo = self._last_main_window_geo
                    pos_diff = abs(current_geo.x() - old_geo.x()) + abs(current_geo.y() - old_geo.y())
                    size_diff = abs(current_geo.width() - old_geo.width()) + abs(current_geo.height() - old_geo.height())
                    significant_change = pos_diff > 5 or size_diff > 10
                if significant_change:
                    self._last_main_window_geo = current_geo
                    self.minibar._update_position_relative_to_main_window()
        except: pass

class MonoFileMiniBar(QtWidgets.QWidget):
    def __init__(self, manager_factory, parent=None):
        super().__init__(parent or hou.qt.mainWindow())
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setObjectName("MonoMiniBar")
        self.s=QtCore.QSettings(ORG,APP)
        self.manager_factory=manager_factory; self.manager=None
        self._drag_pos=None; self._is_dragging=False
        self._locked=self.s.value("minibar_locked", False, type=bool)
        self._last_current_file = None; self._position_stable_count = 0; self._last_stable_pos = None
        self._file_check_timer = QtCore.QTimer(self); self._file_check_timer.timeout.connect(self._check_file_changes); self._file_check_timer.start(2000)
        self._setup_main_window_monitoring()
        self.handle_area = QtWidgets.QLabel("⋮⋮"); self.handle_area.setFixedWidth(20); self.handle_area.setAlignment(QtCore.Qt.AlignCenter); self.handle_area.setToolTip("Drag to move • Right-click for options"); self.handle_area.setCursor(QtCore.Qt.OpenHandCursor)
        self.shot_display = QtWidgets.QLineEdit(); self.shot_display.setReadOnly(True); self.shot_display.setMinimumWidth(160); self.shot_display.setMaximumWidth(160); self.shot_display.setToolTip("Click để chọn shot • Chọn shot sẽ mở file trong Houdini"); self.shot_display.setCursor(QtCore.Qt.PointingHandCursor)
        self.shot_display.mousePressEvent = self._shot_display_clicked
        self.combo = QtWidgets.QComboBox(); self.combo.setVisible(False); self.combo.currentIndexChanged.connect(self._update_shot_display)
        self.btn_quick_menu=QtWidgets.QToolButton(); self.btn_quick_menu.setText("⚙️"); self.btn_quick_menu.setFixedSize(28, 28); self.btn_quick_menu.setToolTip("Quick Menu\n• Reload Scene\n• Restart Houdini\n• Open File Location\n• Open Render Folder"); self.btn_quick_menu.clicked.connect(self._show_quick_menu)
        self.btn_save_version=QtWidgets.QToolButton(); self.btn_save_version.setText("💾"); self.btn_save_version.setFixedSize(28, 28); self.btn_save_version.setToolTip("Save Version\n• Increment version number\n• Move old version to Vers folder"); self.btn_save_version.clicked.connect(self._save_version)
        self.btn_expand=QtWidgets.QToolButton(); self.btn_expand.setText("⚡"); self.btn_expand.setFixedSize(32, 28); self.btn_expand.setToolTip("Mở giao diện đầy đủ • Tự động scan files"); self.btn_expand.clicked.connect(self._open_manager)
        lay=QtWidgets.QHBoxLayout(self); lay.setContentsMargins(6,6,8,6); lay.setSpacing(4)
        lay.addWidget(self.handle_area, 0); lay.addWidget(self.shot_display, 1); lay.addWidget(self.btn_quick_menu, 0); lay.addWidget(self.btn_save_version, 0); lay.addWidget(self.btn_expand, 0)
        self.setStyleSheet("""
        #MonoMiniBar { background:#2a2a2a; border:1px solid #3a3a3a; border-radius:10px; }
        QLabel { color:#888; font-weight:bold; font-size:14px; background:transparent; }
        QLabel:hover { color:#aaa; background:rgba(255,255,255,0.1); border-radius:4px; }
        QToolButton { background:#3a3a3a; color:#fff; border:1px solid #4a4a4a; border-radius:6px; font-size:12px; font-weight:bold; }
        QToolButton:hover { background:#4a4a4a; }
        QToolButton:pressed { background:#2a2a2a; }
        """)
        self._restore_relative_position(); final_pos = self.pos(); print(f"📍 MiniBar positioned at ({final_pos.x()}, {final_pos.y()})")
        self._update_lock_visual_feedback(); self._update_current_shot_highlighting(); self.show()

    # --- a subset of methods ported from original for brevity ---
    def _shot_display_clicked(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            QtCore.QTimer.singleShot(0, self._show_file_menu)
        event.accept()

    def _show_quick_menu(self):
        menu = QtWidgets.QMenu(self)
        reload_action = menu.addAction("🔄 Reload Scene"); reload_action.triggered.connect(self._reload_scene)
        restart_action = menu.addAction("🔃 Restart Houdini"); restart_action.triggered.connect(self._restart_houdini)
        menu.addSeparator()
        location_action = menu.addAction("📁 Open File Location"); location_action.triggered.connect(self._open_current_file_location)
        render_action = menu.addAction("🎬 Open Render Folder"); render_action.triggered.connect(self._open_render_folder)
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
        try:
            if hasattr(self, '_updating_position') and self._updating_position: return
            mw = hou.qt.mainWindow()
            if not mw or not mw.isVisible():
                return
            hou_geo = mw.geometry()
            my_pos = self.pos()
            if hou_geo.width() <= 0 or hou_geo.height() <= 0: return
            hou_right = hou_geo.x() + hou_geo.width(); hou_top = hou_geo.y()
            minibar_right = my_pos.x() + self.width(); minibar_top = my_pos.y()
            offset_x = minibar_right - hou_right; offset_y = minibar_top - hou_top
            rel_x = (minibar_right - hou_geo.x()) / hou_geo.width(); rel_y = (minibar_top - hou_geo.y()) / hou_geo.height()
            rel_x = max(-0.5, min(1.5, rel_x)); rel_y = max(-0.2, min(1.2, rel_y))
            old_offset_x = self.s.value("minibar_offset_x", -85, type=int); old_offset_y = self.s.value("minibar_offset_y", 0, type=int)
            if abs(offset_x - old_offset_x) > 5 or abs(offset_y - old_offset_y) > 5:
                self.s.setValue("minibar_offset_x", offset_x); self.s.setValue("minibar_offset_y", offset_y)
                self.s.setValue("minibar_rel_x", rel_x); self.s.setValue("minibar_rel_y", rel_y)
                self.s.setValue("minibar_abs_x", my_pos.x()); self.s.setValue("minibar_abs_y", my_pos.y()); self.s.sync()
                print(f"📍 MiniBar rel position: ({rel_x:.3f}, {rel_y:.3f}) | pos({my_pos.x()}, {my_pos.y()}) | offset({offset_x}, {offset_y})")
        except Exception as e:
            if os.environ.get('MONO_DEBUG'): print(f"⚠️ Failed to save minibar position: {e}")

    def _update_position_relative_to_main_window(self):
        try:
            self._updating_position = True
            mw = hou.qt.mainWindow()
            if not mw or not mw.isVisible():
                return
            hou_geo = mw.geometry()
            if hou_geo.width() <= 0 or hou_geo.height() <= 0:
                return
            offset_x = self.s.value("minibar_offset_x", -85, type=int); offset_y = self.s.value("minibar_offset_y", 0, type=int)
            hou_right = hou_geo.x() + hou_geo.width(); hou_top = hou_geo.y()
            minibar_right = hou_right + offset_x; minibar_top = hou_top + offset_y
            new_x = minibar_right - self.width(); new_y = minibar_top
            screen = QtWidgets.QApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry(); min_visible=50
                new_x = max(screen_geo.x() - self.width() + min_visible, min(new_x, screen_geo.right() - min_visible))
                new_y = max(screen_geo.y(), min(new_y, screen_geo.bottom() - min_visible))
            current_pos = self.pos(); distance_moved = abs(new_x - current_pos.x()) + abs(new_y - current_pos.y())
            if distance_moved > 3:
                rel_x_check = (new_x + self.width() - hou_geo.x()) / hou_geo.width(); rel_y_check = (new_y - hou_geo.y()) / hou_geo.height()
                if 0.85 <= rel_x_check <= 1.05 and -0.1 <= rel_y_check <= 0.1:
                    if hasattr(self, '_last_stable_pos') and self._last_stable_pos:
                        stable_distance = abs(new_x - self._last_stable_pos.x()) + abs(new_y - self._last_stable_pos.y())
                        if stable_distance < 5: self._position_stable_count += 1
                        else: self._position_stable_count = 0; self._last_stable_pos = QtCore.QPoint(new_x, new_y)
                    else:
                        self._last_stable_pos = QtCore.QPoint(new_x, new_y); self._position_stable_count = 0
                    if self._position_stable_count < 3: self.move(new_x, new_y)
        except Exception as e:
            if os.environ.get('MONO_DEBUG'): print(f"⚠️ Error updating minibar position: {e}")
        finally:
            self._updating_position = False

    def _restore_relative_position(self):
        try:
            mw = hou.qt.mainWindow()
            if not mw or not mw.isVisible():
                self._snap_top_right()
                return
            self.adjustSize()
            hou_geo = mw.geometry()
            if hou_geo.width() > 0 and hou_geo.height() > 0:
                offset_x = self.s.value("minibar_offset_x", None, type=int); offset_y = self.s.value("minibar_offset_y", None, type=int)
                if offset_x is not None and offset_y is not None:
                    hou_right = hou_geo.x() + hou_geo.width(); hou_top = hou_geo.y(); minibar_right = hou_right + offset_x; minibar_top = hou_top + offset_y
                    new_x = minibar_right - self.width(); new_y = minibar_top
                else:
                    rel_x = self.s.value("minibar_rel_x", 0.915, type=float); rel_y = self.s.value("minibar_rel_y", 0.000, type=float)
                    new_x = hou_geo.x() + int(rel_x * hou_geo.width()) - self.width(); new_y = hou_geo.y() + int(rel_y * hou_geo.height())
                screen = QtWidgets.QApplication.primaryScreen()
                if screen:
                    screen_geo = screen.availableGeometry(); min_visible=50
                    new_x = max(screen_geo.x() - self.width() + min_visible, min(new_x, screen_geo.right() - min_visible))
                    new_y = max(screen_geo.y(), min(new_y, screen_geo.bottom() - min_visible))
                self.move(new_x, new_y)
        except Exception as e:
            if os.environ.get('MONO_DEBUG'): print(f"⚠️ Error restoring position: {e}"); self._snap_top_right()

    def _snap_top_right(self):
        mw=hou.qt.mainWindow();
        if not mw: return
        geo=mw.geometry(); self.adjustSize()
        new_x = geo.x() + int(0.915 * geo.width()) - self.width(); new_y = geo.y() + int(0.000 * geo.height())
        self.move(new_x, new_y); final_pos = self.pos()
        final_rel_x = (final_pos.x() + self.width() - geo.x()) / geo.width(); final_rel_y = (final_pos.y() - geo.y()) / geo.height()
        print(f"🎯 Snap to default: rel({final_rel_x:.3f}, {final_rel_y:.3f}) | pos({final_pos.x()}, {final_pos.y()})")
        self._save_relative_position()

    def _update_lock_visual_feedback(self):
        if self._locked:
            self.handle_area.setText("🔒"); self.handle_area.setToolTip("Position locked • Right-click to unlock"); self.handle_area.setCursor(QtCore.Qt.ForbiddenCursor)
            self.setStyleSheet(self.styleSheet().replace("border:1px solid #3a3a3a;","border:1px solid #5a3a3a;"))
        else:
            self.handle_area.setText("⋮⋮"); self.handle_area.setToolTip("Drag to move • Right-click for options"); self.handle_area.setCursor(QtCore.Qt.OpenHandCursor)
            self.setStyleSheet(self.styleSheet().replace("border:1px solid #5a3a3a;","border:1px solid #3a3a3a;"))

    # ---- File menu (dropdown) ----
    def _show_file_menu(self):
        if self.combo.count() == 0:
            hou.ui.displayMessage("No files found.\n\nPlease click ⚡ button to open File Manager and scan for files.", severity=hou.severityType.Warning); return
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
                    open_in_explorer(current_file); print(f"📁 Opened location: {os.path.dirname(current_file)}")
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
                open_in_explorer(render_folder); print(f"🎬 Opened render folder: {render_folder}")
            else:
                result = hou.ui.displayMessage(
                    f"Render folder does not exist:\n{render_folder}\n\nWould you like to create it?",
                    buttons=("Create & Open", "Cancel"), severity=hou.severityType.Message, default_choice=0, close_choice=1, title="Render Folder Not Found"
                )
                if result == 0:
                    try: os.makedirs(render_folder, exist_ok=True); open_in_explorer(render_folder); print(f"🎬 Created and opened render folder: {render_folder}")
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
                print("🔄 Method 1: Trying hou.exit(restart=True)..."); hou.exit(restart=True)
            except Exception as exit_error:
                print(f"⚠️ hou.exit(restart=True) failed: {exit_error}")
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
                        def delayed_exit(): print("👋 Closing current instance..."); hou.exit()
                        _QtCore.QTimer.singleShot(1500, delayed_exit)
                        hou.ui.displayMessage("🔃 Houdini restart initiated!\n\n✅ New instance starting...\n👋 Current instance will close in 1.5 seconds", severity=hou.severityType.Message, default_choice=0, close_choice=0)
                except Exception as popen_error:
                    print(f"❌ Failed to start subprocess: {popen_error}")
        except Exception as e:
            hou.ui.displayMessage(f"Failed to restart Houdini:\n{str(e)}", severity=hou.severityType.Error)

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
        if self.manager.root_le.text().strip():
            QtCore.QTimer.singleShot(100, self.manager.scan)
        self.manager.show(); self.manager.raise_(); self.manager.activateWindow()

    # ---- Populate helpers ----
    def populate(self, paths, shot_names=None):
        self.combo.clear(); shot_names = shot_names or {}
        for p in sorted(paths):
            name=os.path.basename(p); ver=parse_ver(name); label=f"{name} ({ver or '—'})"
            idx=self.combo.count(); self.combo.addItem(label)
            self.combo.setItemData(idx, p, QtCore.Qt.UserRole)
            self.combo.setItemData(idx, label, QtCore.Qt.DisplayRole)
            self.combo.setItemData(idx, name, QtCore.Qt.ToolTipRole)
            if p in shot_names: self.combo.setItemData(idx, shot_names[p], QtCore.Qt.UserRole+2)
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


