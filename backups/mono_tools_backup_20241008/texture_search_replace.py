"""
Texture Search and Replace Tool
Công cụ tìm kiếm và thay thế đường dẫn texture trong Houdini
"""

import os
import re
import hou
import shutil
from datetime import datetime
from PySide6 import QtWidgets, QtCore, QtGui


class TextureSearchReplace(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Texture Search & Replace")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        # Backup settings
        self.backup_enabled = True
        self.backup_folder = None
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Search pattern section
        search_group = QtWidgets.QGroupBox("Tìm kiếm Pattern")
        search_layout = QtWidgets.QFormLayout(search_group)
        
        self.search_pattern_edit = QtWidgets.QLineEdit()
        self.search_pattern_edit.setPlaceholderText("Ví dụ: D:/Textures/OldProject/")
        search_layout.addRow("Pattern cần tìm:", self.search_pattern_edit)
        
        self.replace_pattern_edit = QtWidgets.QLineEdit()
        self.replace_pattern_edit.setPlaceholderText("Ví dụ: E:/NewProject/Assets/")
        search_layout.addRow("Thay thế bằng:", self.replace_pattern_edit)
        
        # Options
        options_group = QtWidgets.QGroupBox("Tùy chọn")
        options_layout = QtWidgets.QVBoxLayout(options_group)
        
        self.case_sensitive_cb = QtWidgets.QCheckBox("Phân biệt hoa thường")
        self.use_regex_cb = QtWidgets.QCheckBox("Sử dụng Regular Expression")
        self.backup_cb = QtWidgets.QCheckBox("Tạo backup trước khi thay đổi")
        self.backup_cb.setChecked(True)
        
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.use_regex_cb)
        options_layout.addWidget(self.backup_cb)
        
        # Scope selection
        scope_group = QtWidgets.QGroupBox("Phạm vi tìm kiếm")
        scope_layout = QtWidgets.QVBoxLayout(scope_group)
        
        self.scope_current_network = QtWidgets.QRadioButton("Network hiện tại")
        self.scope_selected_nodes = QtWidgets.QRadioButton("Nodes được chọn")
        self.scope_entire_scene = QtWidgets.QRadioButton("Toàn bộ scene")
        self.scope_current_network.setChecked(True)
        
        scope_layout.addWidget(self.scope_current_network)
        scope_layout.addWidget(self.scope_selected_nodes)
        scope_layout.addWidget(self.scope_entire_scene)
        
        # Results display
        results_group = QtWidgets.QGroupBox("Kết quả")
        results_layout = QtWidgets.QVBoxLayout(results_group)
        
        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.preview_btn = QtWidgets.QPushButton("Preview")
        self.preview_btn.clicked.connect(self.preview_changes)
        
        self.apply_btn = QtWidgets.QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_changes)
        self.apply_btn.setEnabled(False)
        
        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        # Add all groups to main layout
        layout.addWidget(search_group)
        layout.addWidget(options_group)
        layout.addWidget(scope_group)
        layout.addWidget(results_group)
        layout.addLayout(button_layout)
        
    def load_settings(self):
        """Load settings from Houdini preferences"""
        try:
            settings = hou.preferences().get("mono_texture_search_replace", {})
            self.search_pattern_edit.setText(settings.get("search_pattern", ""))
            self.replace_pattern_edit.setText(settings.get("replace_pattern", ""))
            self.case_sensitive_cb.setChecked(settings.get("case_sensitive", False))
            self.use_regex_cb.setChecked(settings.get("use_regex", False))
            self.backup_cb.setChecked(settings.get("backup_enabled", True))
        except:
            pass
            
    def save_settings(self):
        """Save settings to Houdini preferences"""
        try:
            settings = {
                "search_pattern": self.search_pattern_edit.text(),
                "replace_pattern": self.replace_pattern_edit.text(),
                "case_sensitive": self.case_sensitive_cb.isChecked(),
                "use_regex": self.use_regex_cb.isChecked(),
                "backup_enabled": self.backup_cb.isChecked()
            }
            hou.preferences().set("mono_texture_search_replace", settings)
        except:
            pass
    
    def get_search_scope(self):
        """Lấy danh sách nodes để tìm kiếm dựa trên phạm vi được chọn"""
        if self.scope_selected_nodes.isChecked():
            return hou.selectedNodes()
        elif self.scope_current_network.isChecked():
            current_network = hou.pwd()
            return [current_network] if current_network else []
        else:  # entire scene
            return hou.node("/").allSubChildren()
    
    def find_texture_parameters(self, node):
        """Tìm tất cả parameters chứa texture paths trong một node"""
        texture_params = []
        
        for parm in node.parms():
            if not parm:
                continue
                
            # Check if parameter contains file path
            parm_value = parm.evalAsString()
            if not parm_value:
                continue
                
            # Common texture parameter names
            texture_keywords = [
                'tex', 'texture', 'map', 'file', 'filename', 'path', 
                'image', 'diffuse', 'normal', 'bump', 'displacement',
                'roughness', 'metallic', 'emission', 'opacity'
            ]
            
            parm_name_lower = parm.name().lower()
            is_texture_param = any(keyword in parm_name_lower for keyword in texture_keywords)
            
            # Check if value looks like a file path
            is_file_path = (
                ('/' in parm_value or '\\' in parm_value) and
                any(ext in parm_value.lower() for ext in ['.exr', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.hdr', '.tga'])
            )
            
            if is_texture_param or is_file_path:
                texture_params.append(parm)
        
        return texture_params
    
    def create_backup(self):
        """Tạo backup file hiện tại"""
        if not self.backup_cb.isChecked():
            return None
            
        try:
            current_file = hou.hipFile.name()
            if not current_file or current_file == "untitled.hip":
                hou.ui.displayMessage("Không thể tạo backup cho file chưa được lưu!", 
                                    severity=hou.severityType.Warning)
                return None
            
            # Create backup folder
            backup_dir = os.path.join(os.path.dirname(current_file), "backups")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(current_file)
            name, ext = os.path.splitext(filename)
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Save current file
            hou.hipFile.save()
            
            # Copy to backup
            shutil.copy2(current_file, backup_path)
            
            self.backup_folder = backup_dir
            return backup_path
            
        except Exception as e:
            hou.ui.displayMessage(f"Lỗi khi tạo backup: {str(e)}", 
                                severity=hou.severityType.Error)
            return None
    
    def preview_changes(self):
        """Preview các thay đổi sẽ được thực hiện"""
        search_pattern = self.search_pattern_edit.text().strip()
        replace_pattern = self.replace_pattern_edit.text().strip()
        
        if not search_pattern:
            hou.ui.displayMessage("Vui lòng nhập pattern cần tìm!", 
                                severity=hou.severityType.Warning)
            return
        
        self.results_text.clear()
        self.changes_found = []
        
        # Prepare search pattern
        if self.use_regex_cb.isChecked():
            try:
                flags = 0 if self.case_sensitive_cb.isChecked() else re.IGNORECASE
                search_regex = re.compile(search_pattern, flags)
            except re.error as e:
                hou.ui.displayMessage(f"Lỗi Regular Expression: {str(e)}", 
                                    severity=hou.severityType.Error)
                return
        else:
            search_regex = None
        
        # Get search scope
        search_nodes = self.get_search_scope()
        if not search_nodes:
            hou.ui.displayMessage("Không tìm thấy nodes để tìm kiếm!", 
                                severity=hou.severityType.Warning)
            return
        
        # Search through nodes
        total_found = 0
        for node in search_nodes:
            texture_params = self.find_texture_parameters(node)
            
            for parm in texture_params:
                old_value = parm.evalAsString()
                if not old_value:
                    continue
                
                # Check if pattern matches
                if search_regex:
                    if not search_regex.search(old_value):
                        continue
                    new_value = search_regex.sub(replace_pattern, old_value)
                else:
                    if self.case_sensitive_cb.isChecked():
                        if search_pattern not in old_value:
                            continue
                        new_value = old_value.replace(search_pattern, replace_pattern)
                    else:
                        if search_pattern.lower() not in old_value.lower():
                            continue
                        # Case-insensitive replacement
                        pattern_lower = search_pattern.lower()
                        old_lower = old_value.lower()
                        start_idx = old_lower.find(pattern_lower)
                        if start_idx != -1:
                            new_value = (old_value[:start_idx] + 
                                       replace_pattern + 
                                       old_value[start_idx + len(search_pattern):])
                        else:
                            continue
                
                if new_value != old_value:
                    change_info = {
                        'node': node,
                        'parm': parm,
                        'old_value': old_value,
                        'new_value': new_value
                    }
                    self.changes_found.append(change_info)
                    total_found += 1
        
        # Display results
        if total_found == 0:
            self.results_text.append("Không tìm thấy pattern nào phù hợp.")
        else:
            self.results_text.append(f"Tìm thấy {total_found} thay đổi:\n")
            
            for i, change in enumerate(self.changes_found[:50]):  # Limit to 50 results
                node_path = change['node'].path()
                parm_name = change['parm'].name()
                old_val = change['old_value']
                new_val = change['new_value']
                
                self.results_text.append(f"{i+1}. {node_path}.{parm_name}")
                self.results_text.append(f"   Cũ: {old_val}")
                self.results_text.append(f"   Mới: {new_val}\n")
            
            if total_found > 50:
                self.results_text.append(f"... và {total_found - 50} thay đổi khác")
        
        self.apply_btn.setEnabled(total_found > 0)
        self.save_settings()
    
    def apply_changes(self):
        """Áp dụng các thay đổi đã preview"""
        if not hasattr(self, 'changes_found') or not self.changes_found:
            hou.ui.displayMessage("Không có thay đổi nào để áp dụng!", 
                                severity=hou.severityType.Warning)
            return
        
        # Create backup
        backup_path = self.create_backup()
        if self.backup_cb.isChecked() and not backup_path:
            return
        
        # Apply changes
        try:
            hou.hipFile.save()
            
            applied_count = 0
            for change in self.changes_found:
                try:
                    change['parm'].set(change['new_value'])
                    applied_count += 1
                except Exception as e:
                    print(f"Lỗi khi thay đổi {change['node'].path()}.{change['parm'].name()}: {e}")
            
            # Save file after changes
            hou.hipFile.save()
            
            # Show results
            message = f"Đã áp dụng {applied_count}/{len(self.changes_found)} thay đổi thành công!"
            if backup_path:
                message += f"\nBackup được lưu tại: {backup_path}"
            
            hou.ui.displayMessage(message, severity=hou.severityType.Message)
            
            # Clear results
            self.results_text.clear()
            self.apply_btn.setEnabled(False)
            self.changes_found = []
            
        except Exception as e:
            hou.ui.displayMessage(f"Lỗi khi áp dụng thay đổi: {str(e)}", 
                                severity=hou.severityType.Error)


def show_texture_search_replace():
    """Hiển thị dialog Texture Search & Replace"""
    try:
        dialog = TextureSearchReplace()
        dialog.show()
        return dialog
    except Exception as e:
        hou.ui.displayMessage(f"Lỗi khi mở Texture Search & Replace: {str(e)}", 
                            severity=hou.severityType.Error)
        return None


# Test function
if __name__ == "__main__":
    show_texture_search_replace()
