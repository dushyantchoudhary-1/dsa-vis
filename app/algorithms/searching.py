"""
Searching algorithm generators — each yields ``Step`` snapshots.

Implemented: Linear Search, Binary Search.
"""

from __future__ import annotations

from typing import Generator

from app.engine.algorithm_engine import AlgorithmInfo, Step, register


# ═══════════════════════════════════════════════════════════════════
#  Pseudocode
# ═══════════════════════════════════════════════════════════════════

LINEAR_SEARCH_PSEUDO = [
    "procedure linearSearch(A, n, target)",
    "  for i ← 0 to n-1",
    "    if A[i] == target",
    "      return i   // found",
    "    end if",
    "  end for",
    "  return -1      // not found",
    "end procedure",
]

BINARY_SEARCH_PSEUDO = [
    "procedure binarySearch(A, n, target)",
    "  low ← 0, high ← n-1",
    "  while low ≤ high",
    "    mid ← (low + high) / 2",
    "    if A[mid] == target",
    "      return mid",
    "    else if A[mid] < target",
    "      low ← mid + 1",
    "    else",
    "      high ← mid - 1",
    "    end if",
    "  end while",
    "  return -1",
    "end procedure",
]


# ═══════════════════════════════════════════════════════════════════
#  Linear Search
# ═══════════════════════════════════════════════════════════════════

def linear_search(data: list[int], target: int) -> Generator[Step, None, None]:
    arr = list(data)
    n = len(arr)
    comps = 0

    yield Step(
        data=list(arr),
        highlights={},
        pseudocode_line=0,
        stats={"comparisons": comps, "target": target},
        description=f"Starting Linear Search for target {target} in {n} elements.",
    )

    for i in range(n):
        comps += 1
        yield Step(
            data=list(arr),
            highlights={i: "comparing"},
            pseudocode_line=2,
            stats={"comparisons": comps, "target": target},
            description=f"Checking A[{i}] = {arr[i]}. Is it equal to {target}?",
        )

        if arr[i] == target:
            yield Step(
                data=list(arr),
                highlights={i: "found"},
                pseudocode_line=3,
                stats={"comparisons": comps, "target": target, "result": i},
                description=f"Found target {target} at index {i}! Search complete.",
            )
            return

    yield Step(
        data=list(arr),
        highlights={i: "not_found" for i in range(n)},
        pseudocode_line=6,
        stats={"comparisons": comps, "target": target, "result": -1},
        description=f"Target {target} not found after {comps} comparisons.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Binary Search
# ═══════════════════════════════════════════════════════════════════

def binary_search(data: list[int], target: int) -> Generator[Step, None, None]:
    arr = sorted(data)  # binary search requires sorted input
    n = len(arr)
    comps = 0
    low = 0
    high = n - 1

    yield Step(
        data=list(arr),
        highlights={},
        pseudocode_line=0,
        stats={"comparisons": comps, "target": target},
        description=f"Starting Binary Search for target {target}. Array is sorted.",
    )

    while low <= high:
        mid = (low + high) // 2
        comps += 1

        hl: dict[int, str] = {}
        for i in range(n):
            if i < low or i > high:
                hl[i] = "text_muted"
            elif i == low:
                hl[i] = "low"
            elif i == high:
                hl[i] = "high"
            elif i == mid:
                hl[i] = "mid"
            else:
                hl[i] = "range"
        hl[mid] = "mid"  # ensure mid is always highlighted

        yield Step(
            data=list(arr),
            highlights=hl,
            pseudocode_line=3,
            stats={"comparisons": comps, "target": target, "low": low, "high": high, "mid": mid},
            description=f"low={low}, high={high}, mid={mid}. A[mid]={arr[mid]}.",
        )

        if arr[mid] == target:
            yield Step(
                data=list(arr),
                highlights={mid: "found"},
                pseudocode_line=5,
                stats={"comparisons": comps, "target": target, "result": mid},
                description=f"Found target {target} at index {mid}!",
            )
            return
        elif arr[mid] < target:
            yield Step(
                data=list(arr),
                highlights={mid: "comparing"},
                pseudocode_line=7,
                stats={"comparisons": comps, "target": target, "low": mid + 1, "high": high},
                description=f"A[mid]={arr[mid]} < {target}. Search right half: low ← {mid + 1}.",
            )
            low = mid + 1
        else:
            yield Step(
                data=list(arr),
                highlights={mid: "comparing"},
                pseudocode_line=9,
                stats={"comparisons": comps, "target": target, "low": low, "high": mid - 1},
                description=f"A[mid]={arr[mid]} > {target}. Search left half: high ← {mid - 1}.",
            )
            high = mid - 1

    yield Step(
        data=list(arr),
        highlights={},
        pseudocode_line=12,
        stats={"comparisons": comps, "target": target, "result": -1},
        description=f"Target {target} not found after {comps} comparisons.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Registration
# ═══════════════════════════════════════════════════════════════════

def register_searching_algorithms() -> None:
    register(AlgorithmInfo(
        key="linear_search",
        name="Linear Search",
        category="searching",
        pseudocode=LINEAR_SEARCH_PSEUDO,
        time_complexity="O(n)",
        space_complexity="O(1)",
        description="Sequentially checks each element until the target is found.",
        generator_func=linear_search,
    ))
    register(AlgorithmInfo(
        key="binary_search",
        name="Binary Search",
        category="searching",
        pseudocode=BINARY_SEARCH_PSEUDO,
        time_complexity="O(log n)",
        space_complexity="O(1)",
        description="Halves the search space each step on a sorted array.",
        generator_func=binary_search,
    ))
