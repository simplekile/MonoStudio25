"""
SmartLineEdit - Autocomplete Input Widget
Chrome-style inline autocomplete with Tab to accept
"""

from mono_tools.qt import QtCore, QtGui, QtWidgets


class SmartLineEdit(QtWidgets.QLineEdit):
    """
    LineEdit with Chrome-style inline autocomplete suggestions
    
    Features:
    - Real-time inline suggestions (gray text)
    - Tab key to accept suggestion
    - Dictionary-based matching
    - Arrow display format: "typed → suggestion"
    
    Usage:
        suggestions = {'char': '_characters', 'prop': '_props'}
        input_field = SmartLineEdit(suggestions, parent)
        # User types "char" → sees "char → _characters" (gray)
        # User presses Tab → accepts "_characters"
    """
    
    def __init__(self, suggestions_dict=None, parent=None):
        """
        Initialize SmartLineEdit
        
        Args:
            suggestions_dict: Dictionary mapping input → suggestion
                             Example: {'char': '_characters', 'prop': '_props'}
            parent: Parent widget
        """
        super().__init__(parent)
        self.suggestions_dict = suggestions_dict or {}
        self.current_suggestion = ""
        
        # CRITICAL: Disable default Tab focus behavior
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
    
    def set_suggestions(self, suggestions_dict):
        """
        Update suggestions dictionary
        
        Args:
            suggestions_dict: New suggestions dictionary
        """
        self.suggestions_dict = suggestions_dict or {}
        self.current_suggestion = ""
        self.update()
    
    def event(self, event):
        """Override event to catch Tab before Qt processes it"""
        if event.type() == QtCore.QEvent.KeyPress:
            key_event = event
            if key_event.key() == QtCore.Qt.Key_Tab and self.current_suggestion:
                # Accept suggestion and block Tab propagation
                self.setText(self.current_suggestion)
                self.current_suggestion = ""
                self.setCursorPosition(len(self.text()))
                self.update()
                return True  # Event handled, stop propagation
        
        return super().event(event)
        
    def keyPressEvent(self, event):
        """Handle Tab key to accept suggestion (backup if event() doesn't catch it)"""
        if event.key() == QtCore.Qt.Key_Tab:
            if self.current_suggestion:
                # Accept suggestion
                self.setText(self.current_suggestion)
                self.current_suggestion = ""
                self.setCursorPosition(len(self.text()))
                self.update()
                event.ignore()
                return
            else:
                # Allow normal Tab (move to next field)
                super().keyPressEvent(event)
                return
        
        # For all other keys
        super().keyPressEvent(event)
        
        # Update suggestion after key is processed
        self._update_suggestion()
    
    def _update_suggestion(self):
        """Find matching suggestion based on typed text"""
        text = self.text().lower().strip()
        
        if not text:
            self.current_suggestion = ""
            self.update()
            return
        
        # Find best match from suggestions
        for key, value in self.suggestions_dict.items():
            if key.startswith(text):
                self.current_suggestion = value
                self.update()
                return
        
        # No match found
        self.current_suggestion = ""
        self.update()
    
    def paintEvent(self, event):
        """Custom paint to show gray suggestion text"""
        super().paintEvent(event)
        
        # Draw suggestion in gray after typed text
        if self.current_suggestion and self.text():
            typed = self.text().strip()
            suggestion = self.current_suggestion
            
            # IMPORTANT: Show the FULL suggestion, not check if it starts with typed text
            # Because typed="char" but suggestion="_characters" (with underscore)
            # We want to show the full suggestion as gray text
            
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            # Calculate position
            fm = self.fontMetrics()
            typed_width = fm.horizontalAdvance(typed)
            
            # Style options to get exact text position
            option = QtWidgets.QStyleOptionFrame()
            self.initStyleOption(option)
            text_rect = self.style().subElementRect(QtWidgets.QStyle.SE_LineEditContents, option, self)
            
            # Draw gray text - show FULL suggestion
            painter.setPen(QtGui.QColor(120, 120, 120))  # Gray
            painter.setFont(self.font())
            
            # Position: after typed text
            x = text_rect.left() + typed_width + 4
            y = text_rect.center().y() + fm.ascent() // 2 - 1
            
            painter.drawText(x, y, f" → {suggestion}")
            painter.end()

