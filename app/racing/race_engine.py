"""
Race Engine for Algorithm Racing Arena.

Manages synchronized step execution, real-time metrics, leaderboard tracking,
and benchmarking for multiple competing algorithms.
"""

from __future__ import annotations

import time
from copy import deepcopy
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from app.engine.algorithm_engine import ALGORITHM_REGISTRY, Step
from app.racing.race_models import (
    ALGORITHM_RACER_CONFIGS,
    RaceCategory,
    RaceMode,
    RaceStatus,
    RacerState,
    RaceEvent,
)


class RaceEngine(QObject):
    """
    Multi-algorithm synchronized racing engine.
    
    Coordinates the live step-by-step showdown between selected algorithms
    with fair dataset distribution, real-time leaderboard sorting,
    and high-precision performance benchmarking.
    """

    # Signals
    tick_updated = Signal(dict)            # dict[algo_key, RacerState]
    event_logged = Signal(object)          # RaceEvent
    leader_changed = Signal(str, str)      # (algo_key, algo_name)
    racer_finished = Signal(str, int)      # (algo_key, rank)
    race_finished = Signal(list)           # list[RacerState] sorted by rank
    status_changed = Signal(str)           # RaceStatus value

    DEFAULT_INTERVAL = 120                 # ms per tick for animation
    MIN_INTERVAL = 10
    MAX_INTERVAL = 800

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance_tick)

        self._status = RaceStatus.READY
        self._category = RaceCategory.SORTING
        self._mode = RaceMode.ANIMATION
        self._interval = self.DEFAULT_INTERVAL

        self._shared_input: Any = None
        self._target_value: Any = None
        self._selected_keys: list[str] = []

        # Racer states: algo_key -> RacerState
        self._racers: dict[str, RacerState] = {}
        # Precomputed steps list: algo_key -> list[Step]
        self._racer_steps: dict[str, list[Step]] = {}
        # Current index in step list: algo_key -> int
        self._racer_indices: dict[str, int] = {}
        
        self._finished_racers: list[str] = []
        self._current_leader: str = ""
        self._tick_count: int = 0
        self._race_start_time: float = 0.0

    # ── Configuration & Setup ─────────────────────────────────────────
    def load_race(
        self,
        category: RaceCategory,
        algo_keys: list[str],
        shared_input: Any,
        target_value: Any = None,
    ) -> None:
        """Initialize all racers with identical copies of the shared input."""
        self.stop()
        self._category = category
        self._selected_keys = list(algo_keys)
        self._shared_input = deepcopy(shared_input)
        self._target_value = target_value

        self._racers.clear()
        self._racer_steps.clear()
        self._racer_indices.clear()
        self._finished_racers.clear()
        self._current_leader = ""
        self._tick_count = 0

        for key in self._selected_keys:
            info = ALGORITHM_REGISTRY.get(key)
            config = ALGORITHM_RACER_CONFIGS.get(key, {})
            name = config.get("name", info.name if info else key)
            color = config.get("color", "#38bdf8")
            icon = config.get("icon", "🏎️")
            complexity = config.get("complexity", info.time_complexity if info else "")
            space = config.get("space", info.space_complexity if info else "")

            # Generate steps independently using separate input copy
            input_copy = deepcopy(self._shared_input)
            steps: list[Step] = []

            # Measure pure execution time (computation benchmark)
            t0 = time.perf_counter()
            if info and info.generator_func:
                if self._category == RaceCategory.SEARCHING:
                    gen = info.generator_func(input_copy, self._target_value)
                elif self._category == RaceCategory.GRAPH:
                    gen = info.generator_func(input_copy)
                else:  # SORTING
                    gen = info.generator_func(input_copy)
                steps = list(gen)
            t1 = time.perf_counter()
            bench_time_ms = max(0.01, (t1 - t0) * 1000.0)

            self._racer_steps[key] = steps
            self._racer_indices[key] = 0

            # Initial state
            initial_data = steps[0].data if steps else input_copy
            initial_stats = steps[0].stats if steps else {}
            initial_highlights = steps[0].highlights if steps else {}

            self._racers[key] = RacerState(
                algo_key=key,
                name=name,
                category=self._category.value,
                color=color,
                icon=icon,
                complexity=complexity,
                space_complexity=space,
                status="READY",
                current_step=0,
                total_steps=len(steps),
                progress_percent=0.0,
                comparisons=initial_stats.get("comparisons", 0),
                swaps=initial_stats.get("swaps", 0),
                writes=initial_stats.get("writes", 0),
                operations=initial_stats.get("operations", 0),
                elapsed_time_ms=bench_time_ms,
                rank=0,
                current_description=f"Ready to race on {len(self._shared_input) if isinstance(self._shared_input, (list, set)) else 'grid'} items.",
                current_data=initial_data,
                highlights=initial_highlights,
                is_leader=False,
            )

        self._status = RaceStatus.READY
        self.status_changed.emit(self._status.value)
        self.tick_updated.emit(self._racers)
        self._log_event("SYSTEM", "System", "#7f8790", "INIT", f"Race loaded with {len(self._selected_keys)} racers. Ready to start!")

    # ── Race Controls ─────────────────────────────────────────────────
    def start(self) -> None:
        """Start or resume the race."""
        if not self._racers:
            return

        if self._status == RaceStatus.FINISHED:
            self.reset()

        self._status = RaceStatus.RACING
        self.status_changed.emit(self._status.value)

        for r in self._racers.values():
            if r.status != "FINISHED":
                r.status = "RACING"

        self._race_start_time = time.time()
        self._log_event("SYSTEM", "System", "#4ade80", "START", "🏁 GREEN FLAG! The race is officially underway!")
        self._timer.start(self._interval)

    def pause(self) -> None:
        """Pause the ongoing race."""
        if self._status == RaceStatus.RACING:
            self._timer.stop()
            self._status = RaceStatus.PAUSED
            self.status_changed.emit(self._status.value)
            for r in self._racers.values():
                if r.status != "FINISHED":
                    r.status = "PAUSED"
            self.tick_updated.emit(self._racers)
            self._log_event("SYSTEM", "System", "#fb923c", "PAUSE", "⏸️ Race paused by user.")

    def resume(self) -> None:
        """Resume paused race."""
        if self._status == RaceStatus.PAUSED:
            self.start()

    def step_forward(self) -> None:
        """Advance all active racers by exactly one logical step."""
        if self._status in (RaceStatus.READY, RaceStatus.PAUSED):
            self._advance_tick()

    def stop(self) -> None:
        """Stop and clear timer."""
        self._timer.stop()

    def reset(self) -> None:
        """Reset all racers to the initial starting line without modifying the dataset."""
        self.stop()
        if self._shared_input is not None and self._selected_keys:
            self.load_race(self._category, self._selected_keys, self._shared_input, self._target_value)
            self._log_event("SYSTEM", "System", "#38bdf8", "RESET", "↺ Race track reset to start line.")

    def set_speed(self, interval_ms: int) -> None:
        """Set animation interval in milliseconds."""
        self._interval = max(self.MIN_INTERVAL, min(interval_ms, self.MAX_INTERVAL))
        if self._timer.isActive():
            self._timer.setInterval(self._interval)

    def set_mode(self, mode: RaceMode) -> None:
        self._mode = mode

    # ── Live Execution Tick ───────────────────────────────────────────
    def _advance_tick(self) -> None:
        self._tick_count += 1
        all_done = True
        newly_finished: list[str] = []

        for key in self._selected_keys:
            racer = self._racers[key]
            steps = self._racer_steps.get(key, [])
            total = len(steps)

            if total == 0:
                continue

            curr_idx = self._racer_indices[key]

            if curr_idx < total - 1:
                curr_idx += 1
                self._racer_indices[key] = curr_idx
                all_done = False

                step = steps[curr_idx]
                racer.current_step = curr_idx
                racer.progress_percent = (curr_idx / (total - 1)) * 100.0 if total > 1 else 100.0
                racer.current_data = step.data
                racer.highlights = step.highlights
                racer.current_description = step.description

                # Update live counters
                stats = step.stats
                racer.comparisons = stats.get("comparisons", racer.comparisons)
                racer.swaps = stats.get("swaps", racer.swaps)
                racer.writes = stats.get("writes", racer.writes)
                racer.operations = stats.get("operations", racer.comparisons + racer.swaps + racer.writes)

                # Emit notable events (e.g., swaps or partitions)
                if "swapping" in step.highlights.values():
                    if curr_idx % 4 == 0:  # throttle event feed
                        self._log_event(key, racer.name, racer.color, "SWAP", f"Swapped elements: {step.description}")
                elif "pivot" in step.highlights.values():
                    self._log_event(key, racer.name, racer.color, "PARTITION", f"Active pivot: {step.description}")

            else:
                # Racer has reached the finish line
                if key not in self._finished_racers:
                    racer.status = "FINISHED"
                    racer.progress_percent = 100.0
                    self._finished_racers.append(key)
                    racer.rank = len(self._finished_racers)
                    racer.finish_tick = self._tick_count
                    newly_finished.append(key)

                    rank_suffix = {1: "1st (WINNER!) 🏆", 2: "2nd 🥈", 3: "3rd 🥉"}.get(racer.rank, f"{racer.rank}th")
                    self._log_event(
                        key,
                        racer.name,
                        racer.color,
                        "FINISH",
                        f"🏁 {racer.name} crossed the finish line in {rank_suffix} place ({racer.operations} ops, {racer.elapsed_time_ms:.2f} ms)!",
                        is_leader=(racer.rank == 1),
                    )
                    self.racer_finished.emit(key, racer.rank)

        # Determine current leader among racers
        self._update_leaderboard()

        self.tick_updated.emit(self._racers)

        # Check if entire race has finished
        if all_done:
            self._timer.stop()
            self._status = RaceStatus.FINISHED
            self.status_changed.emit(self._status.value)
            
            # Sort racers by final ranking
            final_ranking = sorted(self._racers.values(), key=lambda r: (r.rank if r.rank > 0 else 999, r.operations))
            winner = final_ranking[0]
            self._log_event(
                winner.algo_key,
                winner.name,
                winner.color,
                "WINNER",
                f"🎉 RACE COMPLETE! {winner.name} takes 1st Place with {winner.operations} operations!",
                is_leader=True,
            )
            self.race_finished.emit(final_ranking)

    # ── Leaderboard Calculation ───────────────────────────────────────
    def _update_leaderboard(self) -> None:
        """Calculate and update real-time ranks and current leader."""
        # Active ranking criteria:
        # 1. Finished racers ranked by finish order (1st, 2nd, 3rd...)
        # 2. In-flight racers ranked by progress percentage or operations depending on mode
        finished = [self._racers[k] for k in self._finished_racers]
        active = [r for r in self._racers.values() if r.algo_key not in self._finished_racers]

        if self._mode == RaceMode.OPERATION:
            # Lowest operations is leading
            active.sort(key=lambda r: (r.operations, -r.progress_percent))
        else:
            # Highest progress is leading
            active.sort(key=lambda r: (-r.progress_percent, r.operations))

        # Assign temp ranks to active racers
        for idx, r in enumerate(active):
            r.rank = len(finished) + idx + 1

        # Determine leader
        current_leader_racer = finished[0] if finished else (active[0] if active else None)
        new_leader_key = current_leader_racer.algo_key if current_leader_racer else ""

        for r in self._racers.values():
            r.is_leader = (r.algo_key == new_leader_key)

        if new_leader_key and new_leader_key != self._current_leader:
            self._current_leader = new_leader_key
            self.leader_changed.emit(new_leader_key, current_leader_racer.name)

    # ── Event Logging Helper ──────────────────────────────────────────
    def _log_event(
        self,
        algo_key: str,
        algo_name: str,
        algo_color: str,
        event_type: str,
        description: str,
        is_leader: bool = False,
    ) -> None:
        elapsed = time.time() - self._race_start_time if self._race_start_time > 0 else 0.0
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        time_str = f"[{minutes:02d}:{seconds:05.2f}]"

        event = RaceEvent(
            timestamp_str=time_str,
            algo_key=algo_key,
            algo_name=algo_name,
            algo_color=algo_color,
            event_type=event_type,
            description=description,
            is_leader=is_leader,
        )
        self.event_logged.emit(event)
