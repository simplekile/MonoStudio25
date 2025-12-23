"""
Unrecognized Textures Dialog
Allows user to choose how to handle unrecognized textures
"""

from mono_tools.qt import QtCore, QtWidgets, QtGui
import os


class UnrecognizedTexturesDialog(QtWidgets.QDialog):
    """
    Dialog for handling unrecognized textures.
    
    For each unrecognized texture, user can choose:
    - Skip: Don't create node
    - Create Unconnected: Create texture node but don't connect
    - Connect to Input: Create node and connect to selected material input
    """
    
    # Color scheme (matching MonoStudio style)
    COLOR_BG = "#2a2a2a"
    COLOR_INPUT_BG = "#1e1e1e"
    COLOR_ACCENT = "#0078d4"
    COLOR_TEXT = "#e5e5e5"
    COLOR_TEXT_DIM = "#888"
    COLOR_BORDER = "#555"
    
    ACTION_SKIP = "skip"
    ACTION_UNCONNECTED = "unconnected"
    ACTION_CONNECT = "connect"
    
    def __init__(self, parent=None, unrecognized_textures=None, available_inputs=None):
        """
        Initialize dialog
        
        Args:
            parent: Parent widget
            unrecognized_textures: List of tuples (material_name, texture_type, texture_path, filename)
            available_inputs: List of available material input names
        """
        super().__init__(parent)
        self.setWindowTitle("Unrecognized Textures")
        self.setMinimumSize(800, 500)
        self.setModal(True)
        
        self.unrecognized_textures = unrecognized_textures or []
        self.available_inputs = available_inputs or []
        
        # Store user choices: {texture_key: {"action": ACTION, "input": input_name}}
        self.choices = {}
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Setup UI elements"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QtWidgets.QLabel("Unrecognized Textures")
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info label
        info = QtWidgets.QLabel(
            f"Found {len(self.unrecognized_textures)} unrecognized texture(s).\n"
            "Choose how to handle each texture:"
        )
        info.setStyleSheet(f"color: {self.COLOR_TEXT_DIM}; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Scroll area for texture list
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)
        
        # Create row for each unrecognized texture
        self.action_widgets = {}  # Store widgets for each texture
        
        for mat_name, ttype, tex_path, filename in self.unrecognized_textures:
            texture_key = f"{mat_name}::{ttype}"
            
            # Create row widget
            row = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(row)
            row_layout.setContentsMargins(8, 8, 8, 8)
            
            # Texture info (filename and type)
            info_label = QtWidgets.QLabel(f"{os.path.basename(filename)}")
            info_label.setMinimumWidth(200)
            info_label.setToolTip(tex_path)
            
            type_label = QtWidgets.QLabel(f"Type: {ttype}")
            type_label.setStyleSheet(f"color: {self.COLOR_TEXT_DIM};")
            type_label.setMinimumWidth(120)
            
            # Action selection (Radio buttons)
            action_group = QtWidgets.QButtonGroup(row)
            
            skip_radio = QtWidgets.QRadioButton("Skip")
            unconnected_radio = QtWidgets.QRadioButton("Unconnected")
            connect_radio = QtWidgets.QRadioButton("Connect")
            
            # Default: Create Unconnected
            unconnected_radio.setChecked(True)
            self.choices[texture_key] = {"action": self.ACTION_UNCONNECTED, "input": None}
            
            action_group.addButton(skip_radio, 0)
            action_group.addButton(unconnected_radio, 1)
            action_group.addButton(connect_radio, 2)
            
            # Input selection (ComboBox) - only enabled when Connect is selected
            input_combo = QtWidgets.QComboBox()
            input_combo.addItem("(Select input)", None)
            for inp in self.available_inputs:
                input_combo.addItem(inp, inp)
            input_combo.setEnabled(False)  # Disabled by default
            
            # Connect signals
            def make_handler(key, combo):
                def on_action_changed(button):
                    if button == skip_radio:
                        self.choices[key]["action"] = self.ACTION_SKIP
                        self.choices[key]["input"] = None
                        combo.setEnabled(False)
                    elif button == unconnected_radio:
                        self.choices[key]["action"] = self.ACTION_UNCONNECTED
                        self.choices[key]["input"] = None
                        combo.setEnabled(False)
                    elif button == connect_radio:
                        self.choices[key]["action"] = self.ACTION_CONNECT
                        combo.setEnabled(True)
                        # Auto-select first input if available
                        if combo.count() > 1:
                            combo.setCurrentIndex(1)
                            self.choices[key]["input"] = combo.currentData()
                return on_action_changed
            
            def make_input_handler(key):
                def on_input_changed(index):
                    self.choices[key]["input"] = input_combo.currentData()
                return on_input_changed
            
            action_group.buttonClicked.connect(make_handler(texture_key, input_combo))
            input_combo.currentIndexChanged.connect(make_input_handler(texture_key))
            
            # Layout row
            row_layout.addWidget(info_label)
            row_layout.addWidget(type_label)
            row_layout.addWidget(skip_radio)
            row_layout.addWidget(unconnected_radio)
            row_layout.addWidget(connect_radio)
            row_layout.addWidget(input_combo)
            row_layout.addStretch()
            
            scroll_layout.addWidget(row)
            
            # Store widgets for later access
            self.action_widgets[texture_key] = {
                "skip": skip_radio,
                "unconnected": unconnected_radio,
                "connect": connect_radio,
                "input": input_combo
            }
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("Apply")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _apply_style(self):
        """Apply styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.COLOR_BG};
                color: {self.COLOR_TEXT};
            }}
            QLabel {{
                color: {self.COLOR_TEXT};
            }}
            QRadioButton {{
                color: {self.COLOR_TEXT};
                spacing: 5px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            QRadioButton::indicator:unchecked {{
                border: 2px solid {self.COLOR_BORDER};
                border-radius: 8px;
                background: {self.COLOR_INPUT_BG};
            }}
            QRadioButton::indicator:checked {{
                border: 2px solid {self.COLOR_ACCENT};
                border-radius: 8px;
                background: {self.COLOR_ACCENT};
            }}
            QComboBox {{
                background: {self.COLOR_INPUT_BG};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                color: {self.COLOR_TEXT};
                min-width: 150px;
            }}
            QComboBox:disabled {{
                background: #1a1a1a;
                color: #666;
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
                background: #106ebe;
            }}
            QPushButton:pressed {{
                background: #005a9e;
            }}
            QScrollArea {{
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 4px;
                background: {self.COLOR_INPUT_BG};
            }}
        """)
    
    def get_choices(self):
        """
        Get user choices
        
        Returns:
            dict: {texture_key: {"action": ACTION, "input": input_name}}
        """
        return self.choices

