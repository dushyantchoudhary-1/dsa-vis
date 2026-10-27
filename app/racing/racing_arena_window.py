"""
Algorithm Racing Arena — Real-Time DSA Showdown Window.

Dedicated gaming-themed window where multiple algorithms race on identical datasets,
with real-time progress lanes, live leaderboard, execution event feed, and victory celebrations.
"""

from __future__ import annotations

import random
from typing import Any

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QComboBox,
    QSlider,
    QCheckBox,
    QScrollArea,
    QSplitter,
    QLineEdit,
    QInputDialog,
    QButtonGroup,
)

from app.theme import COLORS
from app.racing.race_models import (
    ALGORITHM_RACER_CONFIGS,
    RaceCategory,
    RaceMode,
    RaceStatus,
    RacerState,
    RaceEvent,
)
from app.racing.race_engine import RaceEngine
from app.racing.racing_lane_widget import RacingLaneWidget
from app.racing.leaderboard_widget import RaceLeaderboardWidget
from app.racing.event_log_widget import RaceEventLogWidget
from app.racing.winner_dialog import WinnerCelebrationDialog
from app.algorithms.graph import create_default_grid


class RacingArenaWindow(QMainWindow):
    """
    Dedicated Algorithm Racing Arena Window.
    
    Provides an interactive multi-algorithm racing experience with
    customizable datasets, synchronized step execution, and live leaderboards.
    """

    open_in_visualizer = Signal(str)  # emitted when user requests to view algorithm in main visualizer

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("🏁 Algorithm Racing Arena — Real-Time DSA Showdown")
        self.resize(1220, 820)
        self.setMinimumSize(960, 650)

        self._engine = RaceEngine(self)
        self._current_category = RaceCategory.SORTING
        self._current_mode = RaceMode.ANIMATION

        self._lane_widgets: dict[str, RacingLaneWidget] = {}
        self._selected_algo_keys: list[str] = [
            "bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort", "heap_sort"
        ]

        # Shared input dataset
        self._array_size = 25
        self._current_dataset: Any = []
        self._target_value: Any = None

        self._build_ui()
        self._connect_signals()
        self._generate_new_dataset("random")
        self._load_current_race()

    # ── UI Construction ───────────────────────────────────────────────
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        # ── 1. Top Futuristic Arena Header ────────────────────────────
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 4px;
            }}
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(14, 8, 14, 8)
        h_lay.setSpacing(12)

        # Title & Logo
        title_box = QHBoxLayout()
        title_box.setSpacing(8)

        logo = QLabel("🏁")
        logo.setFont(QFont("Segoe UI Emoji", 20))
        title_box.addWidget(logo)

        v_title = QVBoxLayout()
        v_title.setSpacing(1)
        title_lbl = QLabel("ALGORITHM RACING ARENA")
        title_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #D95F42; letter-spacing: 1px;")
        v_title.addWidget(title_lbl)

        sub_lbl = QLabel("Real-Time DSA Showdown & Benchmark")
        sub_lbl.setFont(QFont("Segoe UI", 10))
        sub_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        v_title.addWidget(sub_lbl)
        title_box.addLayout(v_title)
        h_lay.addLayout(title_box)

        # Status badge
        self._status_badge = QLabel("READY")
        self._status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        h_lay.addWidget(self._status_badge)

        h_lay.addStretch()

        # Race Mode Tabs
        mode_box = QWidget()
        mode_box.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        m_lay = QHBoxLayout(mode_box)
        m_lay.setContentsMargins(3, 3, 3, 3)
        m_lay.setSpacing(2)

        self._mode_btn_group = QButtonGroup(self)
        mode_options = [
            ("🎮 Animation Race", RaceMode.ANIMATION),
            ("⚡ Operation Race", RaceMode.OPERATION),
            ("⏱️ Benchmark Time", RaceMode.EXECUTION_TIME),
        ]

        for idx, (label, mode) in enumerate(mode_options):
            btn = QPushButton(label)
            btn.setCheckable(True)
            if mode == RaceMode.ANIMATION:
                btn.setChecked(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    color: {COLORS['text_secondary']};
                    font-size: 11px;
                    font-weight: 600;
                    padding: 6px 12px;
                }}
                QPushButton:checked {{
                    background-color: #D95F42;
                    color: #ffffff;
                }}
                QPushButton:hover:!checked {{
                    background-color: {COLORS['surface_hover']};
                }}
            """)
            self._mode_btn_group.addButton(btn, idx)
            m_lay.addWidget(btn)
            btn.clicked.connect(lambda checked, m=mode: self._on_mode_changed(m))

        h_lay.addWidget(mode_box)
        root.addWidget(header)

        # ── 2. Category & Algorithm Selection Bar ────────────────────
        sel_bar = QFrame()
        sel_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 4px;
            }}
        """)
        s_lay = QHBoxLayout(sel_bar)
        s_lay.setContentsMargins(12, 6, 12, 6)
        s_lay.setSpacing(10)

        # Category Dropdown
        cat_lbl = QLabel("Category:")
        cat_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: bold; font-size: 11px;")
        s_lay.addWidget(cat_lbl)

        self._cat_combo = QComboBox()
        self._cat_combo.addItems(["📊 Sorting Algorithms", "🔍 Searching Algorithms", "🕸️ Graph Traversal"])
        self._cat_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px 10px;
                color: {COLORS['text_primary']};
                font-size: 11px;
                font-weight: bold;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                selection-background-color: #D95F42;
            }}
        """)
        self._cat_combo.currentIndexChanged.connect(self._on_category_changed)
        s_lay.addWidget(self._cat_combo)

        # Algorithms checkboxes container
        self._algo_cb_container = QWidget()
        self._algo_cb_layout = QHBoxLayout(self._algo_cb_container)
        self._algo_cb_layout.setContentsMargins(8, 0, 8, 0)
        self._algo_cb_layout.setSpacing(8)
        s_lay.addWidget(self._algo_cb_container, 1)

        root.addWidget(sel_bar)

        # ── 3. Dataset & Controls Toolbar ────────────────────────────
        ctrl_bar = QFrame()
        ctrl_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 4px;
            }}
        """)
        c_lay = QHBoxLayout(ctrl_bar)
        c_lay.setContentsMargins(12, 6, 12, 6)
        c_lay.setSpacing(10)

        # Start / Pause / Resume Button (Forest Green)
        self._play_btn = QPushButton("▶  START RACE")
        self._play_btn.setFixedHeight(34)
        self._play_btn.setStyleSheet("""
            QPushButton {
                background-color: #34785B;
                border: 1px solid #34785B;
                border-radius: 8px;
                padding: 6px 18px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2D694F;
            }
        """)
        self._play_btn.clicked.connect(self._on_play_toggle)
        c_lay.addWidget(self._play_btn)

        # Step Forward Button
        self._step_btn = QPushButton("⏭  Step")
        self._step_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 14px;
                color: {COLORS['text_primary']};
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        self._step_btn.clicked.connect(self._engine.step_forward)
        c_lay.addWidget(self._step_btn)

        # Reset Track Button
        self._reset_btn = QPushButton("↺  Reset")
        self._reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 14px;
                color: {COLORS['text_secondary']};
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['text_primary']};
            }}
        """)
        self._reset_btn.clicked.connect(self._on_reset_clicked)
        c_lay.addWidget(self._reset_btn)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet(f"color: {COLORS['border']};")
        c_lay.addWidget(sep1)

        # Dataset Preset Selector
        preset_lbl = QLabel("Preset:")
        preset_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        c_lay.addWidget(preset_lbl)

        self._preset_combo = QComboBox()
        self._preset_combo.addItems(["🎲 Random", "📉 Reverse", "📈 Nearly Sorted", "👯 Duplicates", "✏️ Custom..."])
        self._preset_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px 8px;
                color: {COLORS['text_primary']};
                font-size: 11px;
            }}
        """)
        self._preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        c_lay.addWidget(self._preset_combo)

        # Array Size Slider
        self._size_lbl = QLabel(f"Size: {self._array_size}")
        self._size_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        c_lay.addWidget(self._size_lbl)

        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(10, 60)
        self._size_slider.setValue(self._array_size)
        self._size_slider.setFixedWidth(90)
        self._size_slider.valueChanged.connect(self._on_size_slider_changed)
        c_lay.addWidget(self._size_slider)

        # Randomize Button
        rand_btn = QPushButton("🎲 New Input")
        rand_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px 10px;
                color: {COLORS['accent_cyan']};
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        rand_btn.clicked.connect(lambda: self._generate_new_dataset("random"))
        c_lay.addWidget(rand_btn)

        # Speed Slider
        c_lay.addStretch()
        speed_lbl = QLabel("⚡ Speed:")
        speed_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        c_lay.addWidget(speed_lbl)

        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(20, 600)
        self._speed_slider.setValue(120)
        self._speed_slider.setFixedWidth(80)
        self._speed_slider.valueChanged.connect(self._on_speed_changed)
        c_lay.addWidget(self._speed_slider)

        root.addWidget(ctrl_bar)

        # ── 4. Main Body: Lanes Track & Right Panels ─────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left area: Scrollable Racing Lanes
        lanes_area = QScrollArea()
        lanes_area.setWidgetResizable(True)
        lanes_area.setStyleSheet("background: transparent; border: none;")

        self._lanes_container = QWidget()
        self._lanes_layout = QVBoxLayout(self._lanes_container)
        self._lanes_layout.setContentsMargins(0, 0, 6, 0)
        self._lanes_layout.setSpacing(8)
        lanes_area.setWidget(self._lanes_container)
        splitter.addWidget(lanes_area)

        # Right area: Leaderboard & Event Log
        right_panel = QWidget()
        r_lay = QVBoxLayout(right_panel)
        r_lay.setContentsMargins(0, 0, 0, 0)
        r_lay.setSpacing(8)

        self._leaderboard = RaceLeaderboardWidget()
        r_lay.addWidget(self._leaderboard, 1)

        self._event_log = RaceEventLogWidget()
        r_lay.addWidget(self._event_log)

        splitter.addWidget(right_panel)
        splitter.setSizes([850, 330])
        root.addWidget(splitter, 1)

    # ── Signal Connections ────────────────────────────────────────────
    def _connect_signals(self) -> None:
        self._engine.tick_updated.connect(self._on_tick_updated)
        self._engine.event_logged.connect(self._event_log.log_event)
        self._engine.status_changed.connect(self._on_status_changed)
        self._engine.race_finished.connect(self._on_race_finished)

    # ── Category & Checkbox Management ────────────────────────────────
    def _build_algo_checkboxes(self) -> None:
        """Populate algorithm selection checkboxes based on active category."""
        while self._algo_cb_layout.count():
            item = self._algo_cb_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cat_algos = {
            RaceCategory.SORTING: [
                "bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort", "heap_sort"
            ],
            RaceCategory.SEARCHING: [
                "linear_search", "binary_search"
            ],
            RaceCategory.GRAPH: [
                "bfs_search", "dfs_search", "dijkstra_search", "astar_search"
            ],
        }

        available = cat_algos.get(self._current_category, [])
        self._selected_algo_keys = list(available)

        for key in available:
            config = ALGORITHM_RACER_CONFIGS.get(key, {})
            name = config.get("name", key)
            icon = config.get("icon", "🏎️")
            color = config.get("color", "#38bdf8")

            cb = QCheckBox(f"{icon} {name}")
            cb.setChecked(True)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {color};
                    font-size: 11px;
                    font-weight: 600;
                }}
                QCheckBox::indicator {{
                    width: 13px;
                    height: 13px;
                    border: 1px solid {COLORS['border']};
                    border-radius: 3px;
                    background: {COLORS['bg_secondary']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {color};
                    border-color: {color};
                }}
            """)
            cb.toggled.connect(lambda checked, k=key: self._on_algo_toggled(k, checked))
            self._algo_cb_layout.addWidget(cb)

        self._algo_cb_layout.addStretch()

    def _on_category_changed(self, index: int) -> None:
        cats = [RaceCategory.SORTING, RaceCategory.SEARCHING, RaceCategory.GRAPH]
        self._current_category = cats[index]
        self._build_algo_checkboxes()
        self._generate_new_dataset("random")
        self._load_current_race()

    def _on_algo_toggled(self, key: str, checked: bool) -> None:
        if checked and key not in self._selected_algo_keys:
            self._selected_algo_keys.append(key)
        elif not checked and key in self._selected_algo_keys:
            if len(self._selected_algo_keys) <= 1:
                return  # keep at least one racer
            self._selected_algo_keys.remove(key)
        self._load_current_race()

    # ── Dataset Generation ────────────────────────────────────────────
    def _generate_new_dataset(self, preset_type: str) -> None:
        """Create shared input dataset for all racers."""
        n = self._array_size

        if self._current_category == RaceCategory.GRAPH:
            self._current_dataset = create_default_grid()
            self._target_value = None
            return

        if preset_type == "random":
            self._current_dataset = [random.randint(10, 100) for _ in range(n)]
        elif preset_type == "reversed":
            self._current_dataset = list(range(n * 4, 0, -4))
        elif preset_type == "nearly_sorted":
            arr = sorted([random.randint(10, 100) for _ in range(n)])
            # Swap 2 random pairs
            if n > 4:
                arr[2], arr[4] = arr[4], arr[2]
            self._current_dataset = arr
        elif preset_type == "duplicates":
            choices = [15, 30, 45, 60, 75]
            self._current_dataset = [random.choice(choices) for _ in range(n)]

        if self._current_category == RaceCategory.SEARCHING:
            # Pick a target value (usually in middle or near end)
            if self._current_dataset:
                self._target_value = self._current_dataset[len(self._current_dataset) // 2]
            else:
                self._target_value = 42

    def _on_preset_changed(self, index: int) -> None:
        presets = ["random", "reversed", "nearly_sorted", "duplicates", "custom"]
        choice = presets[index]
        if choice == "custom":
            text, ok = QInputDialog.getText(
                self,
                "Custom Dataset",
                "Enter comma-separated integers (e.g. 45, 12, 89, 23, 7):",
                QLineEdit.EchoMode.Normal,
                ", ".join(str(x) for x in self._current_dataset[:12]),
            )
            if ok and text:
                try:
                    vals = [int(x.strip()) for x in text.split(",") if x.strip()]
                    if vals:
                        self._current_dataset = vals
                        self._array_size = len(vals)
                        self._size_lbl.setText(f"Size: {self._array_size}")
                except Exception:
                    pass
        else:
            self._generate_new_dataset(choice)
        self._load_current_race()

    def _on_size_slider_changed(self, val: int) -> None:
        self._array_size = val
        self._size_lbl.setText(f"Size: {val}")
        self._generate_new_dataset("random")
        self._load_current_race()

    def _on_speed_changed(self, val: int) -> None:
        self._engine.set_speed(val)

    def _on_mode_changed(self, mode: RaceMode) -> None:
        self._current_mode = mode
        self._engine.set_mode(mode)
        if mode == RaceMode.EXECUTION_TIME:
            self._event_log.log_event(RaceEvent(
                timestamp_str="[00:00.00]",
                algo_key="SYSTEM",
                algo_name="Mode",
                algo_color="#fb923c",
                event_type="MODE",
                description="Switched to Benchmark Time Mode (measuring pure computation throughput in ms).",
            ))

    # ── Race Loading & Lane Rebuilding ────────────────────────────────
    def _load_current_race(self) -> None:
        """Rebuild lanes and load racers into the engine."""
        self._engine.stop()

        # Clear existing lane widgets
        while self._lanes_layout.count():
            item = self._lanes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._lane_widgets.clear()

        # Load race engine
        self._engine.load_race(
            category=self._current_category,
            algo_keys=self._selected_algo_keys,
            shared_input=self._current_dataset,
            target_value=self._target_value,
        )

        # Create a RacingLaneWidget for every racer
        for key in self._selected_algo_keys:
            racer_state = self._engine._racers[key]
            lane = RacingLaneWidget(racer_state, self)
            self._lanes_layout.addWidget(lane)
            self._lane_widgets[key] = lane

        self._lanes_layout.addStretch()
        self._leaderboard.update_leaderboard(self._engine._racers)
        self._play_btn.setText("▶  START RACE")
        self._play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #15803d;
                border: 1px solid #22c55e;
                border-radius: 8px;
                padding: 6px 18px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #16a34a;
            }}
        """)

    # ── Playback Slots ────────────────────────────────────────────────
    def _on_play_toggle(self) -> None:
        status = self._engine._status
        if status == RaceStatus.RACING:
            self._engine.pause()
        elif status == RaceStatus.PAUSED:
            self._engine.resume()
        else:
            self._engine.start()

    def _on_reset_clicked(self) -> None:
        self._engine.reset()
        self._load_current_race()

    @Slot(dict)
    def _on_tick_updated(self, racers_dict: dict[str, RacerState]) -> None:
        for key, racer in racers_dict.items():
            if key in self._lane_widgets:
                self._lane_widgets[key].update_state(racer)
        self._leaderboard.update_leaderboard(racers_dict)

    @Slot(str)
    def _on_status_changed(self, status: str) -> None:
        self._status_badge.setText(status)
        if status == RaceStatus.RACING.value:
            self._status_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: #14532d;
                    color: #86efac;
                    border: 1px solid #22c55e;
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                }}
            """)
            self._play_btn.setText("⏸  PAUSE")
            self._play_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #854d0e;
                    border: 1px solid #eab308;
                    border-radius: 8px;
                    padding: 6px 18px;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #a16207;
                }}
            """)
        elif status == RaceStatus.PAUSED.value:
            self._status_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: #713f12;
                    color: #fde047;
                    border: 1px solid #eab308;
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                }}
            """)
            self._play_btn.setText("▶  RESUME")
            self._play_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #15803d;
                    border: 1px solid #22c55e;
                    border-radius: 8px;
                    padding: 6px 18px;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: bold;
                }}
            """)
        elif status == RaceStatus.FINISHED.value:
            self._status_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: #701a75;
                    color: #f5d0fe;
                    border: 1px solid #d946ef;
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                }}
            """)
            self._play_btn.setText("🔄  RESTART")
        else:
            self._status_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['bg_tertiary']};
                    color: {COLORS['text_muted']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                }}
            """)
            self._play_btn.setText("▶  START RACE")

    @Slot(list)
    def _on_race_finished(self, rankings: list[RacerState]) -> None:
        dialog = WinnerCelebrationDialog(rankings, self)
        dialog.inspect_requested.connect(self._on_inspect_winner)
        dialog.exec()

    def _on_inspect_winner(self, algo_key: str) -> None:
        self.open_in_visualizer.emit(algo_key)
        self.hide()
