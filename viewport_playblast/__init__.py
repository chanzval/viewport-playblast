"""
Viewport Playblast is a playblast and encoder tool for Autodesk Maya.

This package provides a comprehensive playblast solution with FFmpeg encoding,
visibility presets, camera switching, and more.
"""

from .core.playblast import ViewportPlayblast
from .ui.main_window import ViewportPlayblastUi

__version__ = "1.0.0"
__all__ = ['ViewportPlayblast', 'ViewportPlayblastUi']

def show_dialog():
    """Show the main Viewport Playblast UI dialog."""
    ViewportPlayblastUi.show_dialog()