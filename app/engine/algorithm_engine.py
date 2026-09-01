"""
Core data models shared across the entire application.

* ``Step``  — a single snapshot of algorithm/data-structure state.
* ``AlgorithmInfo`` — metadata for one algorithm (pseudocode, complexity, …).
* ``ALGORITHM_REGISTRY`` — global dict of all registered algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generator


# ── Step ────────────────────────────────────────────────────────────
@dataclass
class Step:
    """One snapshot emitted by an algorithm generator.

    The animation engine pops these one-by-one and forwards them to
    the canvas, pseudocode panel, and statistics panel.
    """

    data: Any
    """Current state of the data.
    • Sorting / Searching → ``list[int]``
    • Stack / Queue / Linked-list → ``list[int]``
    • BST → nested ``dict`` (``{value, left, right}``)
    """

    highlights: dict = field(default_factory=dict)
    """Which elements to highlight and how.
    • Array-based → ``{index: colour_key, …}``
    • BST → ``{node_value: colour_key, …}``
    """

    pseudocode_line: int = -1
    """0-based index of the pseudocode line to highlight (-1 = none)."""

    stats: dict = field(default_factory=dict)
    """Live statistics: ``{comparisons, swaps, …}``."""

    description: str = ""
    """Human-readable explanation of what happened in this step.
    Future AI module will consume this to generate richer text."""

    visualization_type: str = "bars"
    """Render mode for the canvas.
    One of: ``bars``, ``stack``, ``queue``, ``linked_list``, ``bst``."""


# ── AlgorithmInfo ───────────────────────────────────────────────────
@dataclass
class AlgorithmInfo:
    """Metadata that describes one algorithm / data-structure."""

    key: str
    """Unique identifier, e.g. ``'bubble_sort'``."""

    name: str
    """Human-readable display name."""

    category: str
    """One of: ``sorting``, ``searching``, ``data_structure``."""

    subcategory: str = ""
    """e.g. ``stack``, ``queue``, ``linked_list``, ``bst``."""

    pseudocode: list[str] = field(default_factory=list)
    """Lines of pseudocode displayed in the panel."""

    time_complexity: str = ""
    space_complexity: str = ""
    description: str = ""

    generator_func: Callable[..., Generator[Step, None, None]] | None = None
    """Function that accepts input data and returns a Step generator."""

    operations: list[str] = field(default_factory=list)
    question: str = ""
    """For data-structures: list of available operation names
    (e.g. ``['push', 'pop', 'peek']``)."""


# ── Global Registry ─────────────────────────────────────────────────
ALGORITHM_REGISTRY: dict[str, AlgorithmInfo] = {}


def register(info: AlgorithmInfo) -> None:
    """Add an algorithm / data-structure to the global registry."""
    ALGORITHM_REGISTRY[info.key] = info
