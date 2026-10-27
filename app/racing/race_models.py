"""
Data models and configurations for the Algorithm Racing Arena.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RaceCategory(str, Enum):
    SORTING = "sorting"
    SEARCHING = "searching"
    GRAPH = "graph"


class RaceMode(str, Enum):
    ANIMATION = "animation"       # Live step-by-step visual animation
    OPERATION = "operation"       # Ranks by total meaningful operations
    EXECUTION_TIME = "time"       # Pure computation time (high-res timer)


class RaceStatus(str, Enum):
    READY = "READY"
    RACING = "RACING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"


# Distinct color palette & icons for racers
ALGORITHM_RACER_CONFIGS: dict[str, dict[str, str]] = {
    # Sorting
    "bubble_sort": {
        "color": "#38bdf8",     # Sky Blue
        "icon": "🫧",
        "name": "Bubble Sort",
        "complexity": "O(n²)",
        "space": "O(1)",
        "desc": "Simple adjacent swapping sort.",
    },
    "selection_sort": {
        "color": "#fb923c",     # Orange
        "icon": "☝️",
        "name": "Selection Sort",
        "complexity": "O(n²)",
        "space": "O(1)",
        "desc": "Finds minimum and places at start.",
    },
    "insertion_sort": {
        "color": "#a855f7",     # Purple
        "icon": "📥",
        "name": "Insertion Sort",
        "complexity": "O(n²)",
        "space": "O(1)",
        "desc": "Inserts elements into sorted prefix.",
    },
    "merge_sort": {
        "color": "#4ade80",     # Emerald Green
        "icon": "🔀",
        "name": "Merge Sort",
        "complexity": "O(n log n)",
        "space": "O(n)",
        "desc": "Guaranteed divide-and-conquer merge.",
    },
    "quick_sort": {
        "color": "#f43f5e",     # Rose Red / Neon Crimson
        "icon": "⚡",
        "name": "Quick Sort",
        "complexity": "O(n log n) avg",
        "space": "O(log n)",
        "desc": "Fast in-place pivot partitioning.",
    },
    "heap_sort": {
        "color": "#eab308",     # Gold Yellow
        "icon": "🌲",
        "name": "Heap Sort",
        "complexity": "O(n log n)",
        "space": "O(1)",
        "desc": "Max-heap extraction sort.",
    },

    # Searching
    "linear_search": {
        "color": "#38bdf8",
        "icon": "➡️",
        "name": "Linear Search",
        "complexity": "O(n)",
        "space": "O(1)",
        "desc": "Scans elements sequentially.",
    },
    "binary_search": {
        "color": "#4ade80",
        "icon": "✂️",
        "name": "Binary Search",
        "complexity": "O(log n)",
        "space": "O(1)",
        "desc": "Halves search interval every step.",
    },

    # Graph
    "bfs_search": {
        "color": "#38bdf8",
        "icon": "🌊",
        "name": "BFS (Breadth-First)",
        "complexity": "O(V + E)",
        "space": "O(V)",
        "desc": "Layer-by-layer exploration (shortest path).",
    },
    "dfs_search": {
        "color": "#a855f7",
        "icon": "🧗",
        "name": "DFS (Depth-First)",
        "complexity": "O(V + E)",
        "space": "O(V)",
        "desc": "Deep branch exploration before backtracking.",
    },
    "dijkstra_search": {
        "color": "#fb923c",
        "icon": "🎯",
        "name": "Dijkstra's Algorithm",
        "complexity": "O((V+E) log V)",
        "space": "O(V)",
        "desc": "Weighted shortest path with priority queue.",
    },
    "astar_search": {
        "color": "#f43f5e",
        "icon": "⭐",
        "name": "A* Search",
        "complexity": "O(E) informed",
        "space": "O(V)",
        "desc": "Heuristic-guided optimal pathfinding.",
    },
}


@dataclass
class RacerState:
    """Current live state of an algorithm in the race."""
    algo_key: str
    name: str
    category: str
    color: str
    icon: str
    complexity: str
    space_complexity: str

    # Execution metrics
    status: str = "READY"          # READY, RACING, FINISHED
    current_step: int = 0
    total_steps: int = 0
    progress_percent: float = 0.0  # 0.0 to 100.0
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0
    operations: int = 0
    elapsed_time_ms: float = 0.0   # Pure computation time in ms
    rank: int = 0                  # 1 for 1st, 2 for 2nd, etc.
    finish_tick: int = 0
    current_description: str = ""
    current_data: Any = None
    highlights: dict = field(default_factory=dict)
    is_leader: bool = False


@dataclass
class RaceEvent:
    """A notable event occurring during the algorithm race."""
    timestamp_str: str
    algo_key: str
    algo_name: str
    algo_color: str
    event_type: str                # COMPARE, SWAP, PARTITION, MERGE, VISIT, FINISH, LEAD
    description: str
    is_leader: bool = False
