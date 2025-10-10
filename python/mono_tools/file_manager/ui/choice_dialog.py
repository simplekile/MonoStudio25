"""
Choice Dialog
Custom choice dialog with MonoStudio styling
"""

from mono_tools.qt import QtCore, QtWidgets
from .base_dialog import MonoBaseDialog


class ChoiceDialog(MonoBaseDialog):
    """
    Custom choice dialog matching MonoStudio styling
    
    Replaces hou.ui.displayMessage for consistent UI
    """
    
    def __init__(self, parent=None, title="Choose", message="Select an option:", 
                 choices=None, icons=None):
        """
        Initialize choice dialog
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display
            choices: List of choice labels
            icons: Optional list of icons (same length as choices)
        """
        super().__init__(parent, title=title, min_width=400, min_height=250)
        
        self.choices = choices or []
        self.icons = icons or []
        self.selected_index = -1
        
        self._build_ui(message)
    
    def _build_ui(self, message):
        """Build choice dialog UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = self.create_title_label(self.windowTitle(), font_size=16)
        layout.addWidget(title)
        
        # Message
        msg_label = QtWidgets.QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(QtCore.Qt.AlignCenter)
        msg_label.setStyleSheet(f"QLabel {{ color: {self.COLOR_TEXT_DIM}; padding: 10px; }}")
        layout.addWidget(msg_label)
        
        # Choice buttons
        button_group = QtWidgets.QWidget()
        button_layout = QtWidgets.QVBoxLayout(button_group)
        button_layout.setSpacing(10)
        
        for i, choice in enumerate(self.choices):
            icon = self.icons[i] if i < len(self.icons) else ""
            btn_text = f"{icon} {choice}" if icon else choice
            
            btn = QtWidgets.QPushButton(btn_text)
            btn.setMinimumHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #3a3a3a;
                    color: {self.COLOR_TEXT};
                    border: 2px solid {self.COLOR_BORDER};
                    border-radius: 6px;
                    padding: 12px;
                    font-size: 12pt;
                    font-weight: bold;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background: #4a4a4a;
                    border-color: {self.COLOR_ACCENT};
                }}
                QPushButton:pressed {{
                    background: {self.COLOR_ACCENT};
                }}
            """)
            btn.clicked.connect(lambda idx=i: self._on_choice_selected(idx))
            button_layout.addWidget(btn)
        
        layout.addWidget(button_group)
        
        # Cancel button
        cancel_layout = QtWidgets.QHBoxLayout()
        cancel_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("❌ Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        cancel_layout.addWidget(cancel_btn)
        
        layout.addLayout(cancel_layout)
    
    def _on_choice_selected(self, index):
        """Handle choice selection"""
        self.selected_index = index
        self.accept()
    
    def get_selected_index(self):
        """Get selected choice index"""
        return self.selected_index


class InputDialog(MonoBaseDialog):
    """
    Custom input dialog matching MonoStudio styling
    
    Replaces hou.ui.readInput for consistent UI
    """
    
    def __init__(self, parent=None, title="Input", message="Enter value:", 
                 initial_value="", placeholder=""):
        """
        Initialize input dialog
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message/prompt to display
            initial_value: Initial input value
            placeholder: Placeholder text
        """
        super().__init__(parent, title=title, min_width=450, min_height=200)
        
        self.message = message
        self.initial_value = initial_value
        self.placeholder = placeholder
        
        self._build_ui()
    
    def _build_ui(self):
        """Build input dialog UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = self.create_title_label(self.windowTitle(), font_size=16)
        layout.addWidget(title)
        
        # Message
        msg_label = QtWidgets.QLabel(self.message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"QLabel {{ color: {self.COLOR_TEXT}; padding: 10px; }}")
        layout.addWidget(msg_label)
        
        # Input field
        self.input_field = QtWidgets.QLineEdit()
        self.input_field.setText(self.initial_value)
        self.input_field.setPlaceholderText(self.placeholder)
        self.input_field.setMinimumHeight(40)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                font-size: 12pt;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.input_field)
        
        # Focus on input
        self.input_field.setFocus()
        self.input_field.selectAll()
        
        # Buttons
        button_layout, ok_btn, cancel_btn = self.create_button_layout(
            ok_text="✅ OK",
            cancel_text="❌ Cancel"
        )
        layout.addLayout(button_layout)
        
        # Enter key submits
        ok_btn.setDefault(True)
    
    def get_value(self):
        """Get input value"""
        return self.input_field.text().strip()

