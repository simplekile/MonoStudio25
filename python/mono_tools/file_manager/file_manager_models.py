from datetime import datetime
from mono_tools.qt import QtCore, QtGui, QtWidgets
try:
    from .file_manager_helpers import human_size
except ImportError:
    from file_manager_helpers import human_size

class FileTableModel(QtGui.QStandardItemModel):
    COL_SHOT=0; COL_VER=1; COL_NAME=2; COL_EXT=3; COL_FOLDER=4; COL_MOD=5; COL_SIZE=6
    HEAD=["Shot","Ver","File Name","Ext","Folder","Modified","Size"]
    def __init__(self,parent=None):
        super().__init__(0,len(self.HEAD),parent)
        self.setHorizontalHeaderLabels(self.HEAD)
    def add_row(self, shot, ver, name, ext, folder, mtime, sz, fullpath):
        vals=[shot,ver,name,ext,folder,datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"),human_size(sz)]
        items=[]
        for v in vals:
            it=QtGui.QStandardItem(str(v)); it.setEditable(False); items.append(it)
        items[0].setData(fullpath, QtCore.Qt.UserRole+1)
        self.appendRow(items)

class AssetTableModel(QtGui.QStandardItemModel):
    COL_ASSET=0; COL_DEPT=1; COL_VER=2; COL_NAME=3; COL_EXT=4; COL_FOLDER=5; COL_MOD=6; COL_SIZE=7
    HEAD=["Asset Name","Department","Ver","File Name","Ext","Folder","Modified","Size"]
    def __init__(self,parent=None):
        super().__init__(0,len(self.HEAD),parent)
        self.setHorizontalHeaderLabels(self.HEAD)
        self._asset_groups = {}  # Store grouped data by (asset, dept)
    
    def add_asset_group(self, asset, dept, versions_data):
        """
        Add a grouped asset row with version dropdown
        versions_data: list of (ver, name, ext, folder, mtime, sz, fullpath) tuples
        """
        # Sort versions by version number (descending)
        versions_data.sort(key=lambda x: self._parse_version(x[0]), reverse=True)
        
        # Use the latest version for display
        latest = versions_data[0]
        ver, name, ext, folder, mtime, sz, fullpath = latest
        
        # Create row items
        vals = [asset, dept, ver, name, ext, folder, 
                datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"), 
                human_size(sz)]
        
        items = []
        for i, v in enumerate(vals):
            it = QtGui.QStandardItem(str(v))
            it.setEditable(False)
            items.append(it)
        
        # Store full path in first item
        items[0].setData(fullpath, QtCore.Qt.UserRole+1)
        
        # Store all versions data in the version item
        items[2].setData(versions_data, QtCore.Qt.UserRole+2)
        
        # Store group key for easy lookup
        group_key = f"{asset}_{dept}"
        items[0].setData(group_key, QtCore.Qt.UserRole+3)
        
        self.appendRow(items)
        self._asset_groups[group_key] = versions_data
    
    def _parse_version(self, ver_str):
        """Parse version string to integer for sorting"""
        try:
            if ver_str and ver_str.startswith('v'):
                return int(ver_str[1:])
            return 0
        except:
            return 0
    
    def get_versions_for_group(self, group_key):
        """Get all versions for a specific asset group"""
        return self._asset_groups.get(group_key, [])
    
    def update_row_for_version(self, row, version_data):
        """Update row data when version changes"""
        ver, name, ext, folder, mtime, sz, fullpath = version_data
        
        # Update version column
        self.setItem(row, self.COL_VER, QtGui.QStandardItem(ver))
        
        # Update file name
        self.setItem(row, self.COL_NAME, QtGui.QStandardItem(name))
        
        # Update extension
        self.setItem(row, self.COL_EXT, QtGui.QStandardItem(ext))
        
        # Update folder
        self.setItem(row, self.COL_FOLDER, QtGui.QStandardItem(folder))
        
        # Update modified time
        self.setItem(row, self.COL_MOD, QtGui.QStandardItem(
            datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")))
        
        # Update size
        self.setItem(row, self.COL_SIZE, QtGui.QStandardItem(human_size(sz)))
        
        # Update full path in first item
        self.item(row, 0).setData(fullpath, QtCore.Qt.UserRole+1)


class VersionComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    """Custom delegate for version dropdown in asset table"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_table = parent
    
    def createEditor(self, parent, option, index):
        """Create combobox editor for version column"""
        if index.column() != AssetTableModel.COL_VER:
            return super().createEditor(parent, option, index)
        
        combo = QtWidgets.QComboBox(parent)
        combo.setMinimumWidth(80)
        
        # Get versions data from the model
        versions_data = index.data(QtCore.Qt.UserRole+2)
        if versions_data:
            for ver, name, ext, folder, mtime, sz, fullpath in versions_data:
                combo.addItem(ver, (ver, name, ext, folder, mtime, sz, fullpath))
        
        return combo
    
    def setEditorData(self, editor, index):
        """Set current value in editor"""
        if isinstance(editor, QtWidgets.QComboBox):
            current_ver = index.data(QtCore.Qt.DisplayRole)
            idx = editor.findText(current_ver)
            if idx >= 0:
                editor.setCurrentIndex(idx)
    
    def setModelData(self, editor, model, index):
        """Update model when editor value changes"""
        if isinstance(editor, QtWidgets.QComboBox):
            current_idx = editor.currentIndex()
            if current_idx >= 0:
                version_data = editor.itemData(current_idx)
                if version_data and isinstance(model, AssetTableModel):
                    # Update the row with new version data
                    model.update_row_for_version(index.row(), version_data)
    
    def updateEditorGeometry(self, editor, option, index):
        """Set editor geometry"""
        editor.setGeometry(option.rect)


