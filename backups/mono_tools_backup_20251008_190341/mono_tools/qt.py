"""
Qt module for Mono Studio — PySide6 only (Houdini 21).
Usage:
    from mono_tools.qt import QtCore, QtGui, QtWidgets
"""

# Keep module minimal and explicit.

from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
API = 6

__all__ = ["QtCore", "QtGui", "QtWidgets", "API"]


 