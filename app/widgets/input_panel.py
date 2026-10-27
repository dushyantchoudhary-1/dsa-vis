"""
InputPanel module — adapter and alias for the modern InputToolbar.
Maintains backwards compatibility across imports while using the upgraded InputToolbar.
"""

from __future__ import annotations

from app.widgets.input_toolbar import InputToolbar

# InputPanel is aliased to InputToolbar
InputPanel = InputToolbar

__all__ = ["InputPanel", "InputToolbar"]
