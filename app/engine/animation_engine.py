"""
QTimer-based animation controller.

Consumes a list of ``Step`` objects (pre-computed from a generator)
and emits one step at a time at an adjustable speed.
Supports play / pause / step-forward / step-backward / reset.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal

from app.engine.algorithm_engine import Step


class AnimationEngine(QObject):
    """Drives the visualisation by emitting steps on a timer."""

    # ── Signals ──────────────────────────────────────────────────
    step_updated = Signal(object)       # emits the current Step
    animation_finished = Signal()       # emitted when the last step plays
    animation_reset = Signal()          # emitted on reset

    # ── Speed limits (ms) ────────────────────────────────────────
    MIN_INTERVAL = 30
    MAX_INTERVAL = 2000
    DEFAULT_INTERVAL = 400

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)

        self._steps: list[Step] = []
        self._index: int = 0
        self._interval: int = self.DEFAULT_INTERVAL
        self._playing: bool = False

    # ── Public API ───────────────────────────────────────────────
    def load(self, generator) -> None:
        """Pre-compute all steps from *generator* and reset to the first."""
        self.stop()
        self._steps = list(generator)
        self._index = 0
        if self._steps:
            self.step_updated.emit(self._steps[0])

    @property
    def total_steps(self) -> int:
        return len(self._steps)

    @property
    def current_index(self) -> int:
        return self._index

    @property
    def is_playing(self) -> bool:
        return self._playing

    def play(self) -> None:
        if not self._steps:
            return
        self._playing = True
        self._timer.start(self._interval)

    def pause(self) -> None:
        self._playing = False
        self._timer.stop()

    def toggle_play(self) -> None:
        if self._playing:
            self.pause()
        else:
            self.play()

    def step_forward(self) -> None:
        """Advance exactly one step (even while paused)."""
        self.pause()
        self._advance()

    def step_backward(self) -> None:
        """Go back one step (even while paused)."""
        self.pause()
        if self._index > 0:
            self._index -= 1
            self.step_updated.emit(self._steps[self._index])

    def seek(self, index: int) -> None:
        """Jump directly to the step at index (pauses playback if running)."""
        if not self._steps:
            return
        self.pause()
        self._index = max(0, min(index, len(self._steps) - 1))
        self.step_updated.emit(self._steps[self._index])

    def stop(self) -> None:
        self.pause()
        self._index = 0

    def reset(self) -> None:
        """Stop and jump to the first step."""
        self.stop()
        if self._steps:
            self.step_updated.emit(self._steps[0])
        self.animation_reset.emit()

    def set_speed(self, ms: int) -> None:
        """Set the interval between steps in milliseconds."""
        self._interval = max(self.MIN_INTERVAL, min(ms, self.MAX_INTERVAL))
        if self._playing:
            self._timer.setInterval(self._interval)

    def clear(self) -> None:
        """Remove all loaded steps."""
        self.stop()
        self._steps = []
        self._index = 0

    # ── Private ──────────────────────────────────────────────────
    def _advance(self) -> None:
        if self._index < len(self._steps) - 1:
            self._index += 1
            self.step_updated.emit(self._steps[self._index])
        else:
            self.pause()
            self.animation_finished.emit()
