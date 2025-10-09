#!/usr/bin/env python3
"""
Test script to verify File Manager fixes
Tests that the File Manager can be created without attribute errors
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_file_manager_creation():
    """Test that File Manager can be created without errors"""
    print("Testing File Manager creation...")
    
    try:
        # Mock PySide6 for testing
        class MockQtCore:
            class Qt:
                WindowStaysOnTopHint = 1
                Horizontal = 1
                DisplayRole = 0
                CaseInsensitive = 1
                DescendingOrder = 1
                SelectRows = 1
                SingleSelection = 1
                CustomContextMenu = 1
                
            class QSettings:
                def __init__(self, org, app):
                    self.org = org
                    self.app = app
                    self._values = {}
                
                def value(self, key, default=None, type=None):
                    return self._values.get(key, default)
                
                def setValue(self, key, value):
                    self._values[key] = value
                
                def sync(self):
                    pass
                
            class QTimer:
                @staticmethod
                def singleShot(ms, func):
                    pass
                    
        class MockQtGui:
            class QStandardItemModel:
                def __init__(self, parent=None):
                    self._parent = parent
                    self._headers = []
                    self._rows = []
                
                def setHorizontalHeaderLabels(self, headers):
                    self._headers = headers
                
                def rowCount(self):
                    return len(self._rows)
                
                def columnCount(self):
                    return len(self._headers)
                
                def headerData(self, section, orientation, role):
                    if orientation == MockQtCore.Qt.Horizontal and role == MockQtCore.Qt.DisplayRole:
                        return self._headers[section]
                    return None
                
                def add_row(self, *args):
                    self._rows.append(args)
                
                def removeRows(self, row, count):
                    pass
                
                def appendRow(self, items):
                    self._rows.append(items)
                
                def item(self, row, col):
                    if row < len(self._rows) and col < len(self._rows[row]):
                        return self._rows[row][col]
                    return None
                
            class QSortFilterProxyModel:
                def __init__(self, parent):
                    self._parent = parent
                    self._source_model = None
                
                def setSourceModel(self, model):
                    self._source_model = model
                
                def setSortCaseSensitivity(self, sensitivity):
                    pass
                
                def sort(self, column, order):
                    pass
                
                def mapToSource(self, index):
                    return index
                
        class MockQtWidgets:
            class QDialog:
                def __init__(self, parent=None):
                    self._parent = parent
                    self._layout = None
                
                def setWindowTitle(self, title):
                    pass
                
                def setWindowFlag(self, flag, on=True):
                    pass
                
                def setMinimumWidth(self, width):
                    pass
                
                def setMinimumHeight(self, height):
                    pass
                
                def layout(self):
                    return self._layout
                
                def setLayout(self, layout):
                    self._layout = layout
                
                def move(self, x, y):
                    pass
                
                def rect(self):
                    return type('Rect', (), {'center': lambda: type('Point', (), {'x': 0, 'y': 0})()})()
                
            class QWidget:
                def __init__(self, parent=None):
                    self._parent = parent
                
                def setFixedHeight(self, height):
                    pass
                
                def setStyleSheet(self, style):
                    pass
                
                def setVisible(self, visible):
                    pass
                
                def setFocus(self):
                    pass
                
                def setPlaceholderText(self, text):
                    pass
                
                def setFixedSize(self, width, height):
                    pass
                
                def setToolTip(self, text):
                    pass
                
                def setCursor(self, cursor):
                    pass
                
                def setAlignment(self, alignment):
                    pass
                
                def setMinimumWidth(self, width):
                    pass
                
                def setMaximumWidth(self, width):
                    pass
                
                def setReadOnly(self, read_only):
                    pass
                
                def setRange(self, min_val, max_val):
                    pass
                
                def setValue(self, value):
                    pass
                
                def addItem(self, text):
                    pass
                
                def addItems(self, items):
                    pass
                
                def clear(self):
                    pass
                
                def currentText(self):
                    return ""
                
                def currentIndex(self):
                    return 0
                
                def setCurrentIndex(self, index):
                    pass
                
                def findText(self, text):
                    return -1
                
                def blockSignals(self, block):
                    pass
                
                def currentIndexChanged(self):
                    pass
                
                def currentTextChanged(self):
                    pass
                
                def textChanged(self):
                    pass
                
                def clicked(self):
                    pass
                
                def doubleClicked(self):
                    pass
                
                def tabBarDoubleClicked(self):
                    pass
                
                def tabCloseRequested(self):
                    pass
                
                def customContextMenuRequested(self):
                    pass
                
                def setMovable(self, movable):
                    pass
                
                def setTabsClosable(self, closable):
                    pass
                
                def setContextMenuPolicy(self, policy):
                    pass
                
                def addTab(self, widget, text):
                    return 0
                
                def addWidget(self, widget):
                    pass
                
                def addLayout(self, layout):
                    pass
                
                def addStretch(self, stretch=0):
                    pass
                
                def setContentsMargins(self, left, top, right, bottom):
                    pass
                
                def setSpacing(self, spacing):
                    pass
                
                def setVerticalSpacing(self, spacing):
                    pass
                
                def setHorizontalSpacing(self, spacing):
                    pass
                
                def itemAtPosition(self, row, col):
                    return None
                
                def widget(self, index):
                    return None
                
                def count(self):
                    return 0
                
                def tabText(self, index):
                    return ""
                
                def setTabText(self, index, text):
                    pass
                
                def removeTab(self, index):
                    pass
                
                def tabBar(self):
                    return self
                
                def mapToGlobal(self, pos):
                    return pos
                
                def exec_(self, pos):
                    return None
                
                def setText(self, text):
                    pass
                
                def setFont(self, font):
                    pass
                
                def font(self):
                    return type('Font', (), {'setPointSize': lambda x: None, 'setBold': lambda x: None})()
                
                def setHorizontalHeaderLabels(self, labels):
                    pass
                
                def setSortingEnabled(self, enabled):
                    pass
                
                def setSelectionBehavior(self, behavior):
                    pass
                
                def setSelectionMode(self, mode):
                    pass
                
                def setAlternatingRowColors(self, enabled):
                    pass
                
                def verticalHeader(self):
                    return type('Header', (), {'setVisible': lambda x: None})()
                
                def horizontalHeader(self):
                    return type('Header', (), {'setStretchLastSection': lambda x: None})()
                
                def resizeColumnToContents(self, column):
                    pass
                
                def selectionModel(self):
                    return type('SelectionModel', (), {'selectedRows': lambda: []})()
                
                def setModel(self, model):
                    pass
                
                def setParent(self, parent):
                    pass
                
                def isVisible(self):
                    return True
                
                def show(self):
                    pass
                
                def raise_(self):
                    pass
                
                def activateWindow(self):
                    pass
                
                def setMinimumSize(self, width, height):
                    pass
                
                def adjustSize(self):
                    pass
                
                def pos(self):
                    return type('Point', (), {'x': lambda: 0, 'y': lambda: 0})()
                
                def width(self):
                    return 100
                
                def height(self):
                    return 100
                
                def geometry(self):
                    return type('Geometry', (), {'width': lambda: 100, 'height': lambda: 100, 'x': lambda: 0, 'y': lambda: 0})()
                
                def availableGeometry(self):
                    return type('Geometry', (), {'width': lambda: 1920, 'height': lambda: 1080, 'x': lambda: 0, 'y': lambda: 0})()
                
                def center(self):
                    return type('Point', (), {'x': lambda: 960, 'y': lambda: 540})()
                
                def right(self):
                    return 1920
                
                def bottom(self):
                    return 1080
                
                def contains(self, x, y):
                    return True
                
                def primaryScreen(self):
                    return self
                
                def topLevelWidgets(self):
                    return []
                
                def findChildren(self, type, name):
                    return []
                
                def clipboard(self):
                    return type('Clipboard', (), {'setText': lambda x: None, 'text': lambda: ""})()
                
                def applicationVersion(self):
                    return "21.0"
                
                def hipFile(self):
                    return type('HipFile', (), {
                        'name': lambda: "untitled.hip",
                        'hasUnsavedChanges': lambda: False,
                        'save': lambda: None,
                        'load': lambda x: None,
                        'setName': lambda x: None
                    })()
                
                def ui(self):
                    return type('UI', (), {
                        'displayMessage': lambda msg, **kwargs: 0,
                        'setStatusMessage': lambda msg, **kwargs: None,
                        'readInput': lambda msg, **kwargs: (0, "")
                    })()
                
                def qt(self):
                    return type('Qt', (), {
                        'mainWindow': lambda: self
                    })()
                
                def exit(self, restart=False):
                    pass
                
                def menuBar(self):
                    return type('MenuBar', (), {
                        'addMenu': lambda name: type('Menu', (), {
                            'addAction': lambda text: type('Action', (), {
                                'triggered': type('Signal', (), {'connect': lambda func: None})()
                            })()
                        })()
                    })()
                
                def mainWindow(self):
                    return self
                
                def QApplication(self):
                    return self
                
                def primaryScreen(self):
                    return self
                
                def QFileDialog(self):
                    return type('FileDialog', (), {
                        'getExistingDirectory': lambda parent, title, directory: ""
                    })()
                
                def QInputDialog(self):
                    return type('InputDialog', (), {
                        'getText': lambda parent, title, label, **kwargs: ("", False)
                    })()
                
                def QMenu(self):
                    return type('Menu', (), {
                        'addAction': lambda text: type('Action', (), {
                            'setToolTip': lambda text: None,
                            'triggered': type('Signal', (), {'connect': lambda func: None})(),
                            'setData': lambda data: None,
                            'setText': lambda text: None,
                            'setFont': lambda font: None,
                            'font': lambda: type('Font', (), {'setBold': lambda x: None})()
                        })(),
                        'addSeparator': lambda: None,
                        'exec_': lambda pos: None,
                        'setStyleSheet': lambda style: None,
                        'setAttribute': lambda attr, value: None
                    })()
                
                def QTextEdit(self):
                    return type('TextEdit', (), {
                        'setPlainText': lambda text: None,
                        'setReadOnly': lambda read_only: None,
                        'setStyleSheet': lambda style: None
                    })()
                
                def QHBoxLayout(self):
                    return type('Layout', (), {
                        'addWidget': lambda widget: None,
                        'addStretch': lambda stretch: None,
                        'setContentsMargins': lambda l, t, r, b: None
                    })()
                
                def QVBoxLayout(self, parent=None):
                    return type('Layout', (), {
                        'addWidget': lambda widget: None,
                        'addLayout': lambda layout: None,
                        'setContentsMargins': lambda l, t, r, b: None,
                        'setSpacing': lambda spacing: None
                    })()
                
                def QGridLayout(self):
                    return type('Layout', (), {
                        'addWidget': lambda widget, row, col, rowspan=1, colspan=1: None,
                        'setVerticalSpacing': lambda spacing: None,
                        'setHorizontalSpacing': lambda spacing: None,
                        'itemAtPosition': lambda row, col: None
                    })()
                
                def QLabel(self, text=""):
                    return type('Label', (), {
                        'setText': lambda text: None,
                        'setStyleSheet': lambda style: None,
                        'setFont': lambda font: None,
                        'font': lambda: type('Font', (), {'setPointSize': lambda x: None, 'setBold': lambda x: None})(),
                        'setFixedHeight': lambda height: None,
                        'setFixedWidth': lambda width: None,
                        'setAlignment': lambda alignment: None,
                        'setToolTip': lambda text: None,
                        'setCursor': lambda cursor: None,
                        'setMinimumWidth': lambda width: None,
                        'setMaximumWidth': lambda width: None,
                        'setReadOnly': lambda read_only: None,
                        'setRange': lambda min_val, max_val: None,
                        'setValue': lambda value: None,
                        'addItem': lambda text: None,
                        'addItems': lambda items: None,
                        'clear': lambda: None,
                        'currentText': lambda: "",
                        'currentIndex': lambda: 0,
                        'setCurrentIndex': lambda index: None,
                        'findText': lambda text: -1,
                        'blockSignals': lambda block: None,
                        'currentIndexChanged': type('Signal', (), {'connect': lambda func: None})(),
                        'currentTextChanged': type('Signal', (), {'connect': lambda func: None})(),
                        'textChanged': type('Signal', (), {'connect': lambda func: None})(),
                        'clicked': type('Signal', (), {'connect': lambda func: None})(),
                        'doubleClicked': type('Signal', (), {'connect': lambda func: None})(),
                        'tabBarDoubleClicked': type('Signal', (), {'connect': lambda func: None})(),
                        'tabCloseRequested': type('Signal', (), {'connect': lambda func: None})(),
                        'customContextMenuRequested': type('Signal', (), {'connect': lambda func: None})(),
                        'setMovable': lambda movable: None,
                        'setTabsClosable': lambda closable: None,
                        'setContextMenuPolicy': lambda policy: None,
                        'addTab': lambda widget, text: 0,
                        'addWidget': lambda widget: None,
                        'addLayout': lambda layout: None,
                        'addStretch': lambda stretch: None,
                        'setContentsMargins': lambda l, t, r, b: None,
                        'setSpacing': lambda spacing: None,
                        'setVerticalSpacing': lambda spacing: None,
                        'setHorizontalSpacing': lambda spacing: None,
                        'itemAtPosition': lambda row, col: None,
                        'widget': lambda index: None,
                        'count': lambda: 0,
                        'tabText': lambda index: "",
                        'setTabText': lambda index, text: None,
                        'removeTab': lambda index: None,
                        'tabBar': lambda: self,
                        'mapToGlobal': lambda pos: pos,
                        'exec_': lambda pos: None,
                        'setText': lambda text: None,
                        'setFont': lambda font: None,
                        'font': lambda: type('Font', (), {'setPointSize': lambda x: None, 'setBold': lambda x: None})(),
                        'setHorizontalHeaderLabels': lambda labels: None,
                        'setSortingEnabled': lambda enabled: None,
                        'setSelectionBehavior': lambda behavior: None,
                        'setSelectionMode': lambda mode: None,
                        'setAlternatingRowColors': lambda enabled: None,
                        'verticalHeader': lambda: type('Header', (), {'setVisible': lambda x: None})(),
                        'horizontalHeader': lambda: type('Header', (), {'setStretchLastSection': lambda x: None})(),
                        'resizeColumnToContents': lambda column: None,
                        'selectionModel': lambda: type('SelectionModel', (), {'selectedRows': lambda: []})(),
                        'setModel': lambda model: None,
                        'setParent': lambda parent: None,
                        'isVisible': lambda: True,
                        'show': lambda: None,
                        'raise_': lambda: None,
                        'activateWindow': lambda: None,
                        'setMinimumSize': lambda width, height: None,
                        'adjustSize': lambda: None,
                        'pos': lambda: type('Point', (), {'x': lambda: 0, 'y': lambda: 0})(),
                        'width': lambda: 100,
                        'height': lambda: 100,
                        'geometry': lambda: type('Geometry', (), {'width': lambda: 100, 'height': lambda: 100, 'x': lambda: 0, 'y': lambda: 0})(),
                        'availableGeometry': lambda: type('Geometry', (), {'width': lambda: 1920, 'height': lambda: 1080, 'x': lambda: 0, 'y': lambda: 0})(),
                        'center': lambda: type('Point', (), {'x': lambda: 960, 'y': lambda: 540})(),
                        'right': lambda: 1920,
                        'bottom': lambda: 1080,
                        'contains': lambda x, y: True,
                        'primaryScreen': lambda: self,
                        'topLevelWidgets': lambda: [],
                        'findChildren': lambda type, name: [],
                        'clipboard': lambda: type('Clipboard', (), {'setText': lambda x: None, 'text': lambda: ""})(),
                        'applicationVersion': lambda: "21.0",
                        'hipFile': lambda: type('HipFile', (), {
                            'name': lambda: "untitled.hip",
                            'hasUnsavedChanges': lambda: False,
                            'save': lambda: None,
                            'load': lambda x: None,
                            'setName': lambda x: None
                        })(),
                        'ui': lambda: type('UI', (), {
                            'displayMessage': lambda msg, **kwargs: 0,
                            'setStatusMessage': lambda msg, **kwargs: None,
                            'readInput': lambda msg, **kwargs: (0, "")
                        })(),
                        'qt': lambda: type('Qt', (), {
                            'mainWindow': lambda: self
                        })(),
                        'exit': lambda restart=False: None,
                        'menuBar': lambda: type('MenuBar', (), {
                            'addMenu': lambda name: type('Menu', (), {
                                'addAction': lambda text: type('Action', (), {
                                    'triggered': type('Signal', (), {'connect': lambda func: None})()
                                })()
                            })()
                        })(),
                        'mainWindow': lambda: self,
                        'QApplication': lambda: self,
                        'primaryScreen': lambda: self,
                        'QFileDialog': lambda: type('FileDialog', (), {
                            'getExistingDirectory': lambda parent, title, directory: ""
                        })(),
                        'QInputDialog': lambda: type('InputDialog', (), {
                            'getText': lambda parent, title, label, **kwargs: ("", False)
                        })(),
                        'QMenu': lambda: type('Menu', (), {
                            'addAction': lambda text: type('Action', (), {
                                'setToolTip': lambda text: None,
                                'triggered': type('Signal', (), {'connect': lambda func: None})(),
                                'setData': lambda data: None,
                                'setText': lambda text: None,
                                'setFont': lambda font: None,
                                'font': lambda: type('Font', (), {'setBold': lambda x: None})()
                            })(),
                            'addSeparator': lambda: None,
                            'exec_': lambda pos: None,
                            'setStyleSheet': lambda style: None,
                            'setAttribute': lambda attr, value: None
                        })(),
                        'QTextEdit': lambda: type('TextEdit', (), {
                            'setPlainText': lambda text: None,
                            'setReadOnly': lambda read_only: None,
                            'setStyleSheet': lambda style: None
                        })(),
                        'QHBoxLayout': lambda: type('Layout', (), {
                            'addWidget': lambda widget: None,
                            'addStretch': lambda stretch: None,
                            'setContentsMargins': lambda l, t, r, b: None
                        })(),
                        'QVBoxLayout': lambda parent=None: type('Layout', (), {
                            'addWidget': lambda widget: None,
                            'addLayout': lambda layout: None,
                            'setContentsMargins': lambda l, t, r, b: None,
                            'setSpacing': lambda spacing: None
                        })(),
                        'QGridLayout': lambda: type('Layout', (), {
                            'addWidget': lambda widget, row, col, rowspan=1, colspan=1: None,
                            'setVerticalSpacing': lambda spacing: None,
                            'setHorizontalSpacing': lambda spacing: None,
                            'itemAtPosition': lambda row, col: None
                        })(),
                        'QLineEdit': lambda text="": self,
                        'QPushButton': lambda text="": self,
                        'QComboBox': lambda: self,
                        'QSpinBox': lambda: self,
                        'QTabWidget': lambda: self,
                        'QTableView': lambda: self,
                        'QToolButton': lambda: self
                    })()
                
                def QLineEdit(self, text=""):
                    return self
                
                def QPushButton(self, text=""):
                    return self
                
                def QComboBox(self):
                    return self
                
                def QSpinBox(self):
                    return self
                
                def QTabWidget(self):
                    return self
                
                def QTableView(self):
                    return self
                
                def QToolButton(self):
                    return self
        
        # Mock the modules
        sys.modules['hou'] = type('MockHou', (), {
            'ui': MockQtWidgets().ui(),
            'qt': MockQtWidgets().qt(),
            'applicationVersion': lambda: "21.0",
            'hipFile': MockQtWidgets().hipFile(),
            'exit': lambda restart=False: None,
            'menuBar': MockQtWidgets().menuBar(),
            'mainWindow': MockQtWidgets().mainWindow(),
            'QApplication': MockQtWidgets().QApplication(),
            'primaryScreen': MockQtWidgets().primaryScreen(),
            'QFileDialog': MockQtWidgets().QFileDialog(),
            'QInputDialog': MockQtWidgets().QInputDialog(),
            'QMenu': MockQtWidgets().QMenu(),
            'QTextEdit': MockQtWidgets().QTextEdit(),
            'QHBoxLayout': MockQtWidgets().QHBoxLayout(),
            'QVBoxLayout': MockQtWidgets().QVBoxLayout(),
            'QGridLayout': MockQtWidgets().QGridLayout(),
            'QLineEdit': MockQtWidgets().QLineEdit(),
            'QPushButton': MockQtWidgets().QPushButton(),
            'QComboBox': MockQtWidgets().QComboBox(),
            'QSpinBox': MockQtWidgets().QSpinBox(),
            'QTabWidget': MockQtWidgets().QTabWidget(),
            'QTableView': MockQtWidgets().QTableView(),
            'QToolButton': MockQtWidgets().QToolButton()
        })()
        
        sys.modules['mono_tools.qt'] = type('MockQt', (), {
            'QtCore': MockQtCore(),
            'QtGui': MockQtGui(),
            'QtWidgets': MockQtWidgets()
        })()
        
        # Import the file manager
        from mono_tools.file_manager.file_manager_manager import MonoFileManager
        
        # Create the file manager
        print("Creating MonoFileManager...")
        manager = MonoFileManager()
        print("File Manager created successfully!")
        
        # Test that all required attributes exist
        required_attrs = [
            'status_label', 'custom_dept_le', 'asset_type_cb', 'asset_name_cb', 
            'department_cb', 'type_tabs', 'assets_tab', 'shots_tab'
        ]
        
        for attr in required_attrs:
            if hasattr(manager, attr):
                print(f"✓ {attr} exists")
            else:
                print(f"✗ {attr} missing")
                return False
        
        print("All required attributes exist!")
        return True
        
    except Exception as e:
        print(f"Error creating File Manager: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing File Manager Fixes...")
    print("=" * 50)
    
    success = test_file_manager_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("All tests passed! File Manager fixes are working.")
    else:
        print("Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
