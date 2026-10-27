"""
Modern Playback Bar — Primary Task-Focused Execution Controller.

Features:
- Primary Play / Pause button with distinct electric styling
- Step Backward (⏮), Step Forward (⏭), Reset (🔄)
- Interactive scrubbable progress timeline slider
- Step counter with percentage progress
- Speed presets (0.5x, 1x, 2x, 5x) + fine slider
- Keyboard shortcut annotations
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
    QFrame,
    QButtonGroup,
)

from app.theme import COLORS


class PlaybackBar(QWidget):
    """Unified execution deck with playback controls and scrubbable timeline."""

    play_clicked = Signal()
    pause_clicked = Signal()
    step_forward_clicked = Signal()
    step_backward_clicked = Signal()
    reset_clicked = Signal()
    speed_changed = Signal(int)       # interval in ms
    seek_requested = Signal(int)      # jump to specific step index

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(68)
        self._is_playing = False
        self._total_steps = 0
        self._current_step = 0
        self._user_scrubbing = False
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(18, 10, 18, 10)
        root.setSpacing(14)

        # ── 1. Left Control Button Group ─────────────────────────
        btn_box = QHBoxLayout()
        btn_box.setSpacing(6)

        self.setStyleSheet(f"""
            PlaybackBar {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)

        sub_btn_style = f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                color: {COLORS['text_primary']};
                min-width: 36px;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                border-color: {COLORS['text_muted']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['surface_active']};
            }}
            QPushButton:disabled {{
                color: {COLORS['text_muted']};
                border-color: {COLORS['border']};
            }}
        """

        # Step Back
        self.btn_back = QPushButton("⏮")
        self.btn_back.setToolTip("Step Backward (Left Arrow)")
        self.btn_back.setStyleSheet(sub_btn_style)
        self.btn_back.clicked.connect(self.step_backward_clicked.emit)
        btn_box.addWidget(self.btn_back)

        # Primary Play / Pause — Forest Green
        self.btn_play = QPushButton("▶  Play")
        self.btn_play.setToolTip("Play / Pause Animation (Space)")
        self.btn_play.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_primary']};
                border: 1px solid #2B644B;
                border-radius: 6px;
                padding: 6px 20px;
                font-size: 13px;
                font-weight: bold;
                color: #FFFFFF;
                min-width: 90px;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
                border-color: #23523D;
            }}
            QPushButton:pressed {{
                background-color: {COLORS['button_pressed']};
            }}
        """)
        self.btn_play.clicked.connect(self._toggle_play)
        btn_box.addWidget(self.btn_play)

        # Step Forward
        self.btn_step = QPushButton("⏭")
        self.btn_step.setToolTip("Step Forward (Right Arrow)")
        self.btn_step.setStyleSheet(sub_btn_style)
        self.btn_step.clicked.connect(self.step_forward_clicked.emit)
        btn_box.addWidget(self.btn_step)

        # Reset
        self.btn_reset = QPushButton("🔄")
        self.btn_reset.setToolTip("Reset Animation (R)")
        self.btn_reset.setStyleSheet(sub_btn_style)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)
        btn_box.addWidget(self.btn_reset)

        root.addLayout(btn_box)

        # Vertical Divider
        div1 = QFrame()
        div1.setFrameShape(QFrame.Shape.VLine)
        div1.setStyleSheet(f"color: {COLORS['border']};")
        root.addWidget(div1)

        # ── 2. Center Scrubbable Progress Timeline ───────────────
        timeline_box = QVBoxLayout()
        timeline_box.setSpacing(3)

        label_row = QHBoxLayout()
        label_row.setContentsMargins(0, 0, 0, 0)

        t_title = QLabel("Execution Timeline")
        t_title.setFont(QFont("Segoe UI", 9))
        t_title.setStyleSheet(f"color: {COLORS['text_muted']};")
        label_row.addWidget(t_title)

        label_row.addStretch()

        self.step_label = QLabel("Step: 0 / 0 (0%)")
        self.step_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.step_label.setStyleSheet(f"color: {COLORS['button_primary']};")
        label_row.addWidget(self.step_label)
        timeline_box.addLayout(label_row)

        self.timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.setValue(0)
        self.timeline_slider.setToolTip("Scrub through algorithm execution steps")
        self.timeline_slider.sliderPressed.connect(self._on_slider_pressed)
        self.timeline_slider.sliderReleased.connect(self._on_slider_released)
        self.timeline_slider.valueChanged.connect(self._on_slider_moved)
        timeline_box.addWidget(self.timeline_slider)

        root.addLayout(timeline_box, 1)

        # Vertical Divider
        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.VLine)
        div2.setStyleSheet(f"color: {COLORS['border']};")
        root.addWidget(div2)

        # ── 3. Right Speed Selector ──────────────────────────────
        speed_box = QVBoxLayout()
        speed_box.setSpacing(2)

        s_header = QHBoxLayout()
        s_title = QLabel("⚡ Speed")
        s_title.setFont(QFont("Segoe UI", 9))
        s_title.setStyleSheet(f"color: {COLORS['text_muted']};")
        s_header.addWidget(s_title)

        s_header.addStretch()

        self._speed_val_lbl = QLabel("1.0x")
        self._speed_val_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._speed_val_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        s_header.addWidget(self._speed_val_lbl)
        speed_box.addLayout(s_header)

        # Speed Slider (left = fast, right = slow interval)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(30, 1200)
        self.speed_slider.setValue(350)
        self.speed_slider.setInvertedAppearance(True)  # left = faster (smaller interval)
        self.speed_slider.setFixedWidth(130)
        self.speed_slider.setToolTip("Adjust animation speed (Left: Fast, Right: Slow)")
        self.speed_slider.valueChanged.connect(self._on_speed_slider_changed)
        speed_box.addWidget(self.speed_slider)

        root.addLayout(speed_box)

    # ── Public API ───────────────────────────────────────────────

    def set_playing(self, playing: bool) -> None:
        self._is_playing = playing
        self.btn_play.setText("⏸  Pause" if playing else "▶  Play")

    def update_step_counter(self, current: int, total: int) -> None:
        self._current_step = current
        self._total_steps = total

        if total > 0:
            pct = int((current + 1) / total * 100)
            self.step_label.setText(f"Step: {current + 1} / {total} ({pct}%)")
            if not self._user_scrubbing:
                self.timeline_slider.blockSignals(True)
                self.timeline_slider.setRange(0, total - 1)
                self.timeline_slider.setValue(current)
                self.timeline_slider.blockSignals(False)
        else:
            self.step_label.setText("Step: 0 / 0 (0%)")
            self.timeline_slider.setValue(0)

    # ── Internal Callbacks ───────────────────────────────────────

    def _toggle_play(self) -> None:
        if self._is_playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()

    def _on_slider_pressed(self) -> None:
        self._user_scrubbing = True
        self.pause_clicked.emit()

    def _on_slider_released(self) -> None:
        self._user_scrubbing = False
        target_step = self.timeline_slider.value()
        self.seek_requested.emit(target_step)

    def _on_slider_moved(self, val: int) -> None:
        if self._user_scrubbing and self._total_steps > 0:
            pct = int((val + 1) / self._total_steps * 100)
            self.step_label.setText(f"Step: {val + 1} / {self._total_steps} ({pct}%)")
            self.seek_requested.emit(val)

    def _on_speed_slider_changed(self, interval_ms: int) -> None:
        # Calculate human-readable multiplier relative to default (350ms)
        multiplier = round(350.0 / max(interval_ms, 30), 1)
        self._speed_val_lbl.setText(f"{multiplier}x")
        self.speed_changed.emit(interval_ms)
