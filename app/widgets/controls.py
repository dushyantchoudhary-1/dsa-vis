"""
Playback controls — Play/Pause, Step Forward, Step Back, Reset, Speed slider.

Emits signals consumed by the main window to drive the animation engine.
"""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QSlider,
    QLabel,
)

from app.theme import COLORS


class ControlsBar(QWidget):
    """Horizontal bar with playback buttons and a speed slider."""

    play_clicked = Signal()
    pause_clicked = Signal()
    step_forward_clicked = Signal()
    step_backward_clicked = Signal()
    reset_clicked = Signal()
    speed_changed = Signal(int)      # interval in ms

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(64)
        self._is_playing = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)

        btn_style = f"""
            QPushButton {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 15px;
                min-width: 44px;
            }}
            QPushButton:hover {{
                background: {COLORS['surface_hover']};
                border-color: {COLORS['accent_cyan']};
            }}
            QPushButton:pressed {{
                background: {COLORS['bg_tertiary']};
            }}
        """

        # Step backward
        self.btn_back = QPushButton("⏮")
        self.btn_back.setToolTip("Step Backward")
        self.btn_back.setStyleSheet(btn_style)
        self.btn_back.clicked.connect(self.step_backward_clicked.emit)
        layout.addWidget(self.btn_back)

        # Play / Pause
        self.btn_play = QPushButton("▶  Play")
        self.btn_play.setToolTip("Play / Pause")
        self.btn_play.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['accent_purple']}, stop:1 {COLORS['accent_cyan']});
                border: none;
                border-radius: 8px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['accent_purple']}, stop:1 #33ddff);
            }}
        """)
        self.btn_play.clicked.connect(self._toggle_play)
        layout.addWidget(self.btn_play)

        # Step forward
        self.btn_step = QPushButton("⏭")
        self.btn_step.setToolTip("Step Forward")
        self.btn_step.setStyleSheet(btn_style)
        self.btn_step.clicked.connect(self.step_forward_clicked.emit)
        layout.addWidget(self.btn_step)

        # Reset
        self.btn_reset = QPushButton("🔄")
        self.btn_reset.setToolTip("Reset")
        self.btn_reset.setStyleSheet(btn_style)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)
        layout.addWidget(self.btn_reset)

        layout.addSpacing(20)

        # Speed slider
        speed_layout = QVBoxLayout()
        speed_layout.setSpacing(2)

        speed_label = QLabel("⚡ Speed")
        speed_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        speed_layout.addWidget(speed_label)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(30, 2000)
        self.speed_slider.setValue(400)
        self.speed_slider.setInvertedAppearance(True)   # left = fast
        self.speed_slider.setFixedWidth(180)
        self.speed_slider.setToolTip("Adjust animation speed (left = faster)")
        self.speed_slider.valueChanged.connect(self.speed_changed.emit)
        speed_layout.addWidget(self.speed_slider)

        layout.addLayout(speed_layout)

        # Step counter label
        layout.addSpacing(12)
        self.step_label = QLabel("Step: 0 / 0")
        self.step_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        self.step_label.setFixedWidth(120)
        layout.addWidget(self.step_label)

        layout.addStretch()

    # ── Public API ───────────────────────────────────────────────

    def set_playing(self, playing: bool) -> None:
        self._is_playing = playing
        self.btn_play.setText("⏸  Pause" if playing else "▶  Play")

    def update_step_counter(self, current: int, total: int) -> None:
        self.step_label.setText(f"Step: {current + 1} / {total}")

    # ── Internal ─────────────────────────────────────────────────

    def _toggle_play(self) -> None:
        if self._is_playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()
