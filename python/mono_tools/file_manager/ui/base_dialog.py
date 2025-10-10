"""
Base Dialog Class
Provides consistent styling and behavior for all MonoStudio dialogs
"""

from mono_tools.qt import QtCore, QtWidgets


class MonoBaseDialog(QtWidgets.QDialog):
    """
    Base dialog with consistent MonoStudio styling
    
    All dialogs should inherit from this class to ensure:
    - Consistent dark theme
    - Standard window flags
    - Unified styling patterns
    - Common button layouts
    """
    
    # Color scheme constants
    COLOR_BG = "#2a2a2a"
    COLOR_INPUT_BG = "#1e1e1e"
    COLOR_ACCENT = "#0078d4"
    COLOR_ACCENT_HOVER = "#106ebe"
    COLOR_ACCENT_PRESSED = "#005a9e"
    COLOR_TEXT = "#e5e5e5"
    COLOR_TEXT_DIM = "#888"
    COLOR_BORDER = "#555"
    COLOR_CANCEL_BG = "#6c757d"
    COLOR_CANCEL_HOVER = "#5a6268"
    
    def __init__(self, parent=None, title="Dialog", min_width=400, min_height=300):
        """
        Initialize base dialog
        
        Args:
            parent: Parent widget
            title: Window title
            min_width: Minimum dialog width
            min_height: Minimum dialog height
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(min_width, min_height)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        
        # Apply base styling
        self._apply_base_styling()
    
    def _apply_base_styling(self):
        """Apply consistent base styling to dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.COLOR_BG};
                color: {self.COLOR_TEXT};
            }}
            
            QLabel {{
                color: {self.COLOR_TEXT};
            }}
            
            QLineEdit {{
                background: {self.COLOR_INPUT_BG};
                border: 2px solid {self.COLOR_BORDER};
                border-radius: 4px;
                padding: 8px;
                color: {self.COLOR_TEXT};
                font-size: 11pt;
            }}
            
            QLineEdit:focus {{
                border-color: {self.COLOR_ACCENT};
            }}
            
            QLineEdit:disabled {{
                background: #1a1a1a;
                color: #666;
            }}
            
            QPushButton {{
                background: {self.COLOR_ACCENT};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background: {self.COLOR_ACCENT_HOVER};
            }}
            
            QPushButton:pressed {{
                background: {self.COLOR_ACCENT_PRESSED};
            }}
            
            QPushButton:disabled {{
                background: #3a3a3a;
                color: #666;
            }}
            
            QPushButton#cancel_btn {{
                background: {self.COLOR_CANCEL_BG};
            }}
            
            QPushButton#cancel_btn:hover {{
                background: {self.COLOR_CANCEL_HOVER};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {self.COLOR_BORDER};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            
            QTextEdit {{
                background: {self.COLOR_INPUT_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
            
            QComboBox {{
                background: {self.COLOR_INPUT_BG};
                border: 2px solid {self.COLOR_BORDER};
                border-radius: 4px;
                padding: 6px;
                color: {self.COLOR_TEXT};
            }}
            
            QComboBox:focus {{
                border-color: {self.COLOR_ACCENT};
            }}
            
            QComboBox::drop-down {{
                border: none;
            }}
            
            QComboBox QAbstractItemView {{
                background: {self.COLOR_INPUT_BG};
                border: 1px solid {self.COLOR_BORDER};
                selection-background-color: {self.COLOR_ACCENT};
                color: {self.COLOR_TEXT};
            }}
        """)
    
    def create_button_layout(self, ok_text="Save", cancel_text="Cancel"):
        """
        Create standard button layout (OK + Cancel)
        
        Args:
            ok_text: Text for OK/Save button
            cancel_text: Text for Cancel button
            
        Returns:
            tuple: (layout, ok_button, cancel_button)
        """
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton(ok_text)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QtWidgets.QPushButton(cancel_text)
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        return button_layout, ok_btn, cancel_btn
    
    def create_title_label(self, text, font_size=16):
        """
        Create styled title label
        
        Args:
            text: Title text
            font_size: Font size in points
            
        Returns:
            QLabel: Styled title label
        """
        title = QtWidgets.QLabel(text)
        font = title.font()
        font.setPointSize(font_size)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(QtCore.Qt.AlignCenter)
        return title
    
    def create_hint_label(self, text):
        """
        Create styled hint/help label
        
        Args:
            text: Hint text
            
        Returns:
            QLabel: Styled hint label
        """
        hint = QtWidgets.QLabel(text)
        hint.setStyleSheet(f"""
            QLabel {{
                color: {self.COLOR_TEXT_DIM};
                font-size: 9pt;
                font-style: italic;
                margin-left: 20px;
            }}
        """)
        return hint

