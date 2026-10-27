"""
ControlsBar module — alias and adapter for the modern PlaybackBar.
Maintains backwards compatibility across imports while using the redesigned PlaybackBar.
"""

from __future__ import annotations

from app.widgets.playback_bar import PlaybackBar

# ControlsBar is aliased to PlaybackBar
ControlsBar = PlaybackBar

__all__ = ["ControlsBar", "PlaybackBar"]
