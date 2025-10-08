from datetime import datetime
from mono_tools.qt import QtCore, QtGui
from .fm_helpers import human_size

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


