#!/usr/bin/env python3
"""
Simple test to verify File Manager can be imported without errors
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_import():
    """Test that File Manager can be imported without errors"""
    print("Testing File Manager import...")
    
    try:
        # Mock hou module
        class MockHou:
            class ui:
                @staticmethod
                def displayMessage(msg, severity=None):
                    print(f"Mock Houdini Message: {msg}")
            
            class qt:
                @staticmethod
                def mainWindow():
                    return None
            
            @staticmethod
            def applicationVersion():
                return "21.0"
            
            @staticmethod
            def hipFile():
                return type('HipFile', (), {
                    'name': lambda: "untitled.hip",
                    'hasUnsavedChanges': lambda: False,
                    'save': lambda: None,
                    'load': lambda x: None,
                    'setName': lambda x: None
                })()
            
            @staticmethod
            def exit(restart=False):
                pass
        
        sys.modules['hou'] = MockHou()
        
        # Mock PySide6
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
                    pass
                
                def setHorizontalHeaderLabels(self, headers):
                    pass
                
                def rowCount(self):
                    return 0
                
                def columnCount(self):
                    return 0
                
                def headerData(self, section, orientation, role):
                    return ""
                
                def add_row(self, *args):
                    pass
                
                def removeRows(self, row, count):
                    pass
                
                def appendRow(self, items):
                    pass
                
                def item(self, row, col):
                    return None
        
        class MockQtWidgets:
            class QDialog:
                def __init__(self, parent=None):
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
                    pass
                
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
                
                def QApplication(self):
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
                
                def QLabel(self, text=""):
                    return self
        
        # Mock the modules
        sys.modules['mono_tools.qt'] = type('MockQt', (), {
            'QtCore': MockQtCore(),
            'QtGui': MockQtGui(),
            'QtWidgets': MockQtWidgets()
        })()
        
        # Import the file manager
        print("Importing MonoFileManager...")
        from mono_tools.file_manager.file_manager_manager import MonoFileManager
        print("Import successful!")
        
        # Test that the class can be instantiated
        print("Creating MonoFileManager instance...")
        manager = MonoFileManager()
        print("Instance created successfully!")
        
        # Test that all required attributes exist
        required_attrs = [
            'status_label', 'custom_dept_le', 'asset_type_cb', 'asset_name_cb', 
            'department_cb', 'type_tabs', 'assets_tab', 'shots_tab'
        ]
        
        missing_attrs = []
        for attr in required_attrs:
            if hasattr(manager, attr):
                print(f"✓ {attr} exists")
            else:
                print(f"✗ {attr} missing")
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"Missing attributes: {missing_attrs}")
            return False
        
        print("All required attributes exist!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing File Manager Import and Creation...")
    print("=" * 50)
    
    success = test_import()
    
    print("\n" + "=" * 50)
    if success:
        print("All tests passed! File Manager fixes are working.")
        print("The Asset Finder should now work without attribute errors.")
    else:
        print("Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
