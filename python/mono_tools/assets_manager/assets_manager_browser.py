"""
Assets Manager Browser - Grid and List view widgets

Grid view with thumbnails and List view with table.

Phase 3: Grid view implementation
"""

import os
from typing import List, Dict, Optional

# Import Qt
try:
    from ..qt import QtCore, QtGui, QtWidgets
except (ImportError, ValueError):
    try:
        from mono_tools.qt import QtCore, QtGui, QtWidgets
    except ImportError:
        from PySide6 import QtCore, QtGui, QtWidgets

# Debug flag
DEBUG = os.environ.get('MONO_DEBUG', '0').lower() in ('1', 'true', 'yes')

def debug_print(*args, **kwargs):
    """Print only if DEBUG mode is enabled"""
    if DEBUG:
        print(*args, **kwargs)


class FlowLayout(QtWidgets.QLayout):
    """
    Custom flow layout that wraps items like a grid
    
    Based on Qt's Flow Layout example
    """
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self.setSpacing(spacing)
        self.item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QtCore.QSize()
        
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size
    
    def _do_layout(self, rect, test_only):
        """Perform layout calculation"""
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            widget = item.widget()
            space_x = spacing + widget.style().layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Horizontal
            )
            space_y = spacing + widget.style().layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Vertical
            )
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()


class AssetCard(QtWidgets.QWidget):
    """
    Asset card widget for grid view
    
    Shows:
    - Thumbnail (256x256)
    - Asset name
    - Version
    """
    
    clicked = QtCore.Signal(dict)  # Emits asset data on click
    double_clicked = QtCore.Signal(dict)  # Emits asset data on double-click
    
    def __init__(self, asset_data: Dict, pixmap: QtGui.QPixmap, parent=None):
        """
        Initialize asset card
        
        Args:
            asset_data: Dictionary with asset information
            pixmap: Thumbnail pixmap
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.asset_data = asset_data
        self.is_selected = False
        
        # Setup UI
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Thumbnail
        self.thumb_label = QtWidgets.QLabel()
        self.thumb_label.setPixmap(pixmap)
        self.thumb_label.setFixedSize(256, 256)
        self.thumb_label.setScaledContents(False)
        self.thumb_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.thumb_label)
        
        # Asset name
        filename = asset_data.get('filename', 'Unknown')
        self.name_label = QtWidgets.QLabel(filename)
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setMaximumWidth(256)
        layout.addWidget(self.name_label)
        
        # Version badge
        version = asset_data.get('version', '')
        if version:
            version_label = QtWidgets.QLabel(version)
            version_label.setAlignment(QtCore.Qt.AlignCenter)
            version_label.setStyleSheet("""
                background: #5a9fd4;
                color: white;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            """)
            layout.addWidget(version_label, 0, QtCore.Qt.AlignCenter)
        
        # Set fixed size
        self.setFixedSize(264, 320)
        
        # Style
        self.update_style()
        
        # Mouse tracking
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.asset_data)
        event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click"""
        if event.button() == QtCore.Qt.LeftButton:
            self.double_clicked.emit(self.asset_data)
        event.accept()
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        self.update_style()
    
    def update_style(self):
        """Update visual style based on state"""
        if self.is_selected:
            self.setStyleSheet("""
                AssetCard {
                    background: #3d5a80;
                    border: 2px solid #5a9fd4;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                AssetCard {
                    background: #2a2a2a;
                    border: 1px solid #444;
                    border-radius: 4px;
                }
                AssetCard:hover {
                    background: #333;
                    border: 1px solid #555;
                }
            """)


class AssetBrowserGrid(QtWidgets.QWidget):
    """
    Grid view browser with thumbnails
    
    Phase 3: Grid layout with asset cards
    """
    
    asset_selected = QtCore.Signal(dict)  # Emits selected asset
    asset_double_clicked = QtCore.Signal(dict)  # Emits double-clicked asset
    
    def __init__(self, thumbnail_generator=None, parent=None):
        """
        Initialize grid browser
        
        Args:
            thumbnail_generator: ThumbnailGenerator instance (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Thumbnail generator
        from .assets_manager_thumbnails import ThumbnailGenerator
        self.thumbnail_generator = thumbnail_generator or ThumbnailGenerator(size=256)
        
        # Setup UI
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # Container for cards
        self.container = QtWidgets.QWidget()
        self.flow_layout = FlowLayout(self.container, margin=10, spacing=10)
        self.container.setLayout(self.flow_layout)
        
        self.scroll_area.setWidget(self.container)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)
        
        # Cards list
        self.cards = []
        self.selected_card = None
        
        debug_print("🎨 Grid browser initialized")
    
    def populate(self, assets: List[Dict]):
        """
        Populate grid with assets
        
        Args:
            assets: List of asset dictionaries
        """
        try:
            # Clear existing cards
            self.clear()
            
            debug_print(f"🎨 Populating grid with {len(assets)} assets")
            
            # Create cards
            for asset in assets:
                # Get thumbnail
                filepath = asset.get('filepath', '')
                asset_format = asset.get('file_format', '')
                
                pixmap = self.thumbnail_generator.get_thumbnail(filepath, asset_format)
                
                # Create card
                card = AssetCard(asset, pixmap)
                card.clicked.connect(self._on_card_clicked)
                card.double_clicked.connect(self._on_card_double_clicked)
                
                # Add to layout
                self.flow_layout.addWidget(card)
                self.cards.append(card)
            
            debug_print(f"✅ Grid populated with {len(self.cards)} cards")
            
        except Exception as e:
            debug_print(f"❌ Error populating grid: {e}")
            import traceback
            traceback.print_exc()
    
    def clear(self):
        """Clear all cards"""
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()
        self.selected_card = None
        
        # Clear layout
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _on_card_clicked(self, asset_data):
        """Handle card click"""
        # Update selection
        for card in self.cards:
            if card.asset_data == asset_data:
                card.set_selected(True)
                self.selected_card = card
            else:
                card.set_selected(False)
        
        # Emit signal
        self.asset_selected.emit(asset_data)
    
    def _on_card_double_clicked(self, asset_data):
        """Handle card double-click"""
        self.asset_double_clicked.emit(asset_data)
    
    def get_selected_asset(self) -> Optional[Dict]:
        """Get currently selected asset"""
        if self.selected_card:
            return self.selected_card.asset_data
        return None


# Export
__all__ = ['AssetBrowserGrid', 'AssetCard', 'FlowLayout']
