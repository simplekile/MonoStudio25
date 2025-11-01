"""
MonoStudio File Manager Styles
Centralized styling constants and utilities for consistent UI appearance
"""

# Color scheme (matching base_dialog.py)
COLOR_BG = "#2a2a2a"
COLOR_BG_DARK = "#1f1f1f"
COLOR_BG_DARKER = "#232323"
COLOR_INPUT_BG = "#1e1e1e"
COLOR_ACCENT = "#0078d4"
COLOR_ACCENT_HOVER = "#106ebe"
COLOR_SELECTED = "#3d5a99"
COLOR_CURRENT_FILE = "#282f44"  # Lighter than dropdown bg to highlight, but still subtle
COLOR_TEXT = "#e5e5e5"
COLOR_TEXT_DIM = "#888"
COLOR_BORDER = "#3a3a3a"
COLOR_SEPARATOR = "#3a3a3a"
COLOR_BUTTON = "#3a3a3a"
COLOR_BUTTON_HOVER = "#4a4a4a"
COLOR_TAB_BG = "#2a2a2a"
COLOR_TAB_SELECTED = "#3a3a3a"

# Note styling constants
NOTE_FONT_SIZE_RATIO = 0.85  # 85% of base font size
NOTE_COLOR = "#888"  # Dimmed text color
NOTE_FONT_WEIGHT = "normal"  # Never bold

# Department styling constants
DEPARTMENT_FONT_SIZE_RATIO = 0.9  # 90% of base font size
DEPARTMENT_COLOR = "#4a9eff"  # Light blue for department text
DEPARTMENT_FONT_WEIGHT = "normal"


def get_menu_style(include_separator=False):
    """
    Get standardized menu stylesheet
    
    Args:
        include_separator: Whether to include separator styling
        
    Returns:
        str: Complete stylesheet for QMenu
    """
    style = f"""
        QMenu {{
            background: {COLOR_BG_DARK};
            color: {COLOR_TEXT};
            border: 1px solid {COLOR_BORDER};
        }}
        QMenu::item {{
            padding: 8px 16px;
        }}
        QMenu::item:selected {{
            background: {COLOR_SELECTED};
        }}
        QMenu::item:hover {{
            background: {COLOR_SELECTED};
        }}
        QMenu::item[current="true"] {{
            background: {COLOR_CURRENT_FILE};
        }}
    """
    
    if include_separator:
        style += f"""
        QMenu::separator {{
            height: 1px;
            background: {COLOR_SEPARATOR};
        }}
        """
    
    return style


def get_dialog_style():
    """
    Get standard dialog stylesheet with common widgets
    
    Returns:
        str: Complete stylesheet for QDialog with common widgets
    """
    return f"""
        QDialog {{
            background: {COLOR_BG_DARKER};
            color: {COLOR_TEXT};
        }}
        QLabel {{
            color: {COLOR_TEXT};
        }}
        QGroupBox {{
            color: {COLOR_TEXT};
            border: 2px solid {COLOR_BORDER};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        QLineEdit, QComboBox {{
            background: {COLOR_INPUT_BG};
            color: {COLOR_TEXT};
            border: 1px solid {COLOR_BORDER};
            border-radius: 6px;
            padding: 4px 6px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {COLOR_SELECTED};
        }}
        QPushButton {{
            background: {COLOR_BUTTON};
            color: {COLOR_TEXT};
            border: 1px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 6px 10px;
            min-width: 80px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: {COLOR_BUTTON_HOVER};
        }}
        QPushButton:pressed {{
            background: {COLOR_BG};
        }}
        QPushButton:default {{
            background: {COLOR_SELECTED};
            border: 1px solid {COLOR_SELECTED};
        }}
        QPushButton:default:hover {{
            background: {COLOR_SELECTED};
        }}
        QTabWidget::pane {{
            border: 1px solid {COLOR_BORDER};
            background: {COLOR_INPUT_BG};
        }}
        QTabBar::tab {{
            background: {COLOR_TAB_BG};
            color: {COLOR_TEXT};
            padding: 8px 16px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background: {COLOR_TAB_SELECTED};
        }}
        QTableView {{
            background: {COLOR_INPUT_BG};
            alternate-background-color: {COLOR_BG};
            gridline-color: {COLOR_BORDER};
            selection-background-color: {COLOR_SELECTED};
            selection-color: white;
        }}
        QHeaderView::section {{
            background: {COLOR_TAB_BG};
            color: {COLOR_TEXT};
            border: 0;
            padding: 6px;
        }}
    """


def get_note_style():
    """
    Get CSS style string for note labels
    Used in QLabel.setStyleSheet() for note text
    
    Returns:
        str: CSS style for note labels
    """
    return f"color: {NOTE_COLOR}; font-weight: {NOTE_FONT_WEIGHT};"


def get_note_font_size(base_font_size):
    """
    Calculate note font size from base font size
    
    Args:
        base_font_size: Base font point size
        
    Returns:
        int: Note font point size (rounded)
    """
    return int(base_font_size * NOTE_FONT_SIZE_RATIO)


def get_department_style():
    """
    Get CSS style string for department labels
    Used in QLabel.setStyleSheet() for department text
    
    Returns:
        str: CSS style for department labels
    """
    return f"color: {DEPARTMENT_COLOR}; font-weight: {DEPARTMENT_FONT_WEIGHT};"


def get_department_font_size(base_font_size):
    """
    Calculate department font size from base font size
    
    Args:
        base_font_size: Base font point size
        
    Returns:
        int: Department font point size (rounded)
    """
    return int(base_font_size * DEPARTMENT_FONT_SIZE_RATIO)

