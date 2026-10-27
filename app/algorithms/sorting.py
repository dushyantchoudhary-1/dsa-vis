"""
Sorting algorithm generators — each yields ``Step`` snapshots.

Implemented: Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, Quick Sort.
Every generator accepts ``list[int]`` and yields ``Step`` objects with
accurate comparison / swap counters, pseudocode-line indices, and
human-readable descriptions.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Generator

from app.engine.algorithm_engine import AlgorithmInfo, Step, register


# ═══════════════════════════════════════════════════════════════════
#  Pseudocode definitions
# ═══════════════════════════════════════════════════════════════════

BUBBLE_SORT_PSEUDO = [
    "procedure bubbleSort(A, n)",
    "  for i ← 0 to n-1",
    "    for j ← 0 to n-i-2",
    "      if A[j] > A[j+1]",
    "        swap(A[j], A[j+1])",
    "      end if",
    "    end for",
    "  end for",
    "end procedure",
]

SELECTION_SORT_PSEUDO = [
    "procedure selectionSort(A, n)",
    "  for i ← 0 to n-1",
    "    minIdx ← i",
    "    for j ← i+1 to n-1",
    "      if A[j] < A[minIdx]",
    "        minIdx ← j",
    "      end if",
    "    end for",
    "    swap(A[i], A[minIdx])",
    "  end for",
    "end procedure",
]

INSERTION_SORT_PSEUDO = [
    "procedure insertionSort(A, n)",
    "  for i ← 1 to n-1",
    "    key ← A[i]",
    "    j ← i - 1",
    "    while j ≥ 0 and A[j] > key",
    "      A[j+1] ← A[j]",
    "      j ← j - 1",
    "    end while",
    "    A[j+1] ← key",
    "  end for",
    "end procedure",
]

MERGE_SORT_PSEUDO = [
    "procedure mergeSort(A, left, right)",
    "  if left < right",
    "    mid ← (left + right) / 2",
    "    mergeSort(A, left, mid)",
    "    mergeSort(A, mid+1, right)",
    "    merge(A, left, mid, right)",
    "  end if",
    "end procedure",
    "",
    "procedure merge(A, l, m, r)",
    "  copy left/right halves",
    "  compare & place smallest first",
    "  copy remaining elements",
    "end procedure",
]

QUICK_SORT_PSEUDO = [
    "procedure quickSort(A, low, high)",
    "  if low < high",
    "    pi ← partition(A, low, high)",
    "    quickSort(A, low, pi-1)",
    "    quickSort(A, pi+1, high)",
    "  end if",
    "end procedure",
    "",
    "procedure partition(A, low, high)",
    "  pivot ← A[high]",
    "  i ← low - 1",
    "  for j ← low to high-1",
    "    if A[j] ≤ pivot",
    "      i ← i + 1",
    "      swap(A[i], A[j])",
    "    end if",
    "  end for",
    "  swap(A[i+1], A[high])",
    "  return i + 1",
    "end procedure",
]


# ═══════════════════════════════════════════════════════════════════
#  Helper
# ═══════════════════════════════════════════════════════════════════

def _sorted_highlights(arr: list[int], sorted_indices: set[int]) -> dict[int, str]:
    """Return a highlight dict marking already-sorted indices."""
    return {i: "sorted" for i in sorted_indices}


# ═══════════════════════════════════════════════════════════════════
#  Bubble Sort
# ═══════════════════════════════════════════════════════════════════

def bubble_sort(data: list[int]) -> Generator[Step, None, None]:
    arr = list(data)
    n = len(arr)
    comps = swaps = 0
    sorted_set: set[int] = set()

    yield Step(
        data=list(arr),
        highlights={},
        pseudocode_line=0,
        stats={"comparisons": comps, "swaps": swaps},
        description=f"Starting Bubble Sort on {n} elements.",
    )

    for i in range(n):
        for j in range(n - i - 1):
            # Comparing
            comps += 1
            hl = {**_sorted_highlights(arr, sorted_set), j: "comparing", j + 1: "comparing"}
            yield Step(
                data=list(arr),
                highlights=hl,
                pseudocode_line=3,
                stats={"comparisons": comps, "swaps": swaps},
                description=f"Comparing A[{j}]={arr[j]} and A[{j+1}]={arr[j+1]}.",
            )

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                hl = {**_sorted_highlights(arr, sorted_set), j: "swapping", j + 1: "swapping"}
                yield Step(
                    data=list(arr),
                    highlights=hl,
                    pseudocode_line=4,
                    stats={"comparisons": comps, "swaps": swaps},
                    description=f"Swapped A[{j}] and A[{j+1}]. Array: {arr}",
                )

        sorted_set.add(n - i - 1)

    # Final state
    yield Step(
        data=list(arr),
        highlights={i: "sorted" for i in range(n)},
        pseudocode_line=8,
        stats={"comparisons": comps, "swaps": swaps},
        description=f"Bubble Sort complete! {comps} comparisons, {swaps} swaps.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Selection Sort
# ═══════════════════════════════════════════════════════════════════

def selection_sort(data: list[int]) -> Generator[Step, None, None]:
    arr = list(data)
    n = len(arr)
    comps = swaps = 0
    sorted_set: set[int] = set()

    yield Step(
        data=list(arr),
        highlights={},
        pseudocode_line=0,
        stats={"comparisons": comps, "swaps": swaps},
        description=f"Starting Selection Sort on {n} elements.",
    )

    for i in range(n):
        min_idx = i
        hl = {**_sorted_highlights(arr, sorted_set), i: "active"}
        yield Step(
            data=list(arr),
            highlights=hl,
            pseudocode_line=2,
            stats={"comparisons": comps, "swaps": swaps},
            description=f"Set minIdx = {i} (value {arr[i]}). Scanning remaining elements.",
        )

        for j in range(i + 1, n):
            comps += 1
            hl = {**_sorted_highlights(arr, sorted_set), min_idx: "active", j: "comparing"}
            yield Step(
                data=list(arr),
                highlights=hl,
                pseudocode_line=4,
                stats={"comparisons": comps, "swaps": swaps},
                description=f"Comparing A[{j}]={arr[j]} with current min A[{min_idx}]={arr[min_idx]}.",
            )
            if arr[j] < arr[min_idx]:
                min_idx = j
                hl = {**_sorted_highlights(arr, sorted_set), min_idx: "active"}
                yield Step(
                    data=list(arr),
                    highlights=hl,
                    pseudocode_line=5,
                    stats={"comparisons": comps, "swaps": swaps},
                    description=f"New minimum found: A[{min_idx}]={arr[min_idx]}.",
                )

        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
            hl = {**_sorted_highlights(arr, sorted_set), i: "swapping", min_idx: "swapping"}
            yield Step(
                data=list(arr),
                highlights=hl,
                pseudocode_line=8,
                stats={"comparisons": comps, "swaps": swaps},
                description=f"Swapped A[{i}] and A[{min_idx}].",
            )

        sorted_set.add(i)

    yield Step(
        data=list(arr),
        highlights={i: "sorted" for i in range(n)},
        pseudocode_line=10,
        stats={"comparisons": comps, "swaps": swaps},
        description=f"Selection Sort complete! {comps} comparisons, {swaps} swaps.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Insertion Sort
# ═══════════════════════════════════════════════════════════════════

def insertion_sort(data: list[int]) -> Generator[Step, None, None]:
    arr = list(data)
    n = len(arr)
    comps = swaps = 0

    yield Step(
        data=list(arr),
        highlights={0: "sorted"},
        pseudocode_line=0,
        stats={"comparisons": comps, "swaps": swaps},
        description=f"Starting Insertion Sort on {n} elements. First element is trivially sorted.",
    )

    for i in range(1, n):
        key = arr[i]
        hl = {k: "sorted" for k in range(i)}
        hl[i] = "active"
        yield Step(
            data=list(arr),
            highlights=hl,
            pseudocode_line=2,
            stats={"comparisons": comps, "swaps": swaps},
            description=f"Pick key = A[{i}] = {key}. Insert it into the sorted portion.",
        )

        j = i - 1
        while j >= 0 and arr[j] > key:
            comps += 1
            arr[j + 1] = arr[j]
            swaps += 1
            hl = {k: "sorted" for k in range(i + 1) if k != j + 1}
            hl[j] = "comparing"
            hl[j + 1] = "swapping"
            yield Step(
                data=list(arr),
                highlights=hl,
                pseudocode_line=5,
                stats={"comparisons": comps, "swaps": swaps},
                description=f"Shift A[{j}]={arr[j]} right to A[{j+1}].",
            )
            j -= 1

        if j >= 0:
            comps += 1  # the failing comparison that exits the while loop

        arr[j + 1] = key
        hl = {k: "sorted" for k in range(i + 1)}
        hl[j + 1] = "active"
        yield Step(
            data=list(arr),
            highlights=hl,
            pseudocode_line=8,
            stats={"comparisons": comps, "swaps": swaps},
            description=f"Placed key {key} at position {j + 1}.",
        )

    yield Step(
        data=list(arr),
        highlights={i: "sorted" for i in range(n)},
        pseudocode_line=10,
        stats={"comparisons": comps, "swaps": swaps},
        description=f"Insertion Sort complete! {comps} comparisons, {swaps} shifts.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Merge Sort
# ═══════════════════════════════════════════════════════════════════

def merge_sort(data: list[int]) -> Generator[Step, None, None]:
    arr = list(data)
    n = len(arr)
    stats = {"comparisons": 0, "swaps": 0}
    steps: list[Step] = []

    def _merge_sort(a: list[int], l: int, r: int) -> None:
        if l >= r:
            return

        mid = (l + r) // 2

        hl = {i: "range" for i in range(l, r + 1)}
        hl[mid] = "mid"
        steps.append(Step(
            data=list(a),
            highlights=hl,
            pseudocode_line=2,
            stats=dict(stats),
            description=f"Divide: splitting A[{l}..{r}] at mid={mid}.",
        ))

        _merge_sort(a, l, mid)
        _merge_sort(a, mid + 1, r)

        # Merge
        left_half = a[l:mid + 1]
        right_half = a[mid + 1:r + 1]
        i = j = 0
        k = l

        steps.append(Step(
            data=list(a),
            highlights={idx: "range" for idx in range(l, r + 1)},
            pseudocode_line=5,
            stats=dict(stats),
            description=f"Merging A[{l}..{mid}] and A[{mid+1}..{r}].",
        ))

        while i < len(left_half) and j < len(right_half):
            stats["comparisons"] += 1
            if left_half[i] <= right_half[j]:
                a[k] = left_half[i]
                i += 1
            else:
                a[k] = right_half[j]
                j += 1
                stats["swaps"] += 1
            hl = {idx: "sorted" if idx < k else "range" for idx in range(l, r + 1)}
            hl[k] = "active"
            steps.append(Step(
                data=list(a),
                highlights=hl,
                pseudocode_line=11,
                stats=dict(stats),
                description=f"Placed {a[k]} at position {k}.",
            ))
            k += 1

        while i < len(left_half):
            a[k] = left_half[i]
            i += 1
            hl = {idx: "sorted" if idx <= k else "range" for idx in range(l, r + 1)}
            hl[k] = "active"
            steps.append(Step(
                data=list(a),
                highlights=hl,
                pseudocode_line=12,
                stats=dict(stats),
                description=f"Copy remaining {a[k]} from left half to position {k}.",
            ))
            k += 1

        while j < len(right_half):
            a[k] = right_half[j]
            j += 1
            hl = {idx: "sorted" if idx <= k else "range" for idx in range(l, r + 1)}
            hl[k] = "active"
            steps.append(Step(
                data=list(a),
                highlights=hl,
                pseudocode_line=12,
                stats=dict(stats),
                description=f"Copy remaining {a[k]} from right half to position {k}.",
            ))
            k += 1

    # Initial step
    yield Step(
        data=list(arr),
        highlights={},
        pseudocode_line=0,
        stats={"comparisons": 0, "swaps": 0},
        description=f"Starting Merge Sort on {n} elements.",
    )

    _merge_sort(arr, 0, n - 1)

    for s in steps:
        yield s

    yield Step(
        data=list(arr),
        highlights={i: "sorted" for i in range(n)},
        pseudocode_line=7,
        stats=dict(stats),
        description=f"Merge Sort complete! {stats['comparisons']} comparisons.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Quick Sort
# ═══════════════════════════════════════════════════════════════════

def quick_sort(data: list[int]) -> Generator[Step, None, None]:
    arr = list(data)
    n = len(arr)
    stats = {"comparisons": 0, "swaps": 0}
    sorted_set: set[int] = set()
    steps: list[Step] = []

    def _partition(a: list[int], lo: int, hi: int) -> int:
        pivot = a[hi]

        hl = {i: "sorted" if i in sorted_set else "default_bar" for i in range(n)}
        for idx in range(lo, hi + 1):
            hl[idx] = "range"
        hl[hi] = "pivot"
        steps.append(Step(
            data=list(a),
            highlights=hl,
            pseudocode_line=9,
            stats=dict(stats),
            description=f"Pivot = A[{hi}] = {pivot}. Partitioning A[{lo}..{hi}].",
        ))

        i = lo - 1
        for j in range(lo, hi):
            stats["comparisons"] += 1

            hl = {idx: "sorted" if idx in sorted_set else "default_bar" for idx in range(n)}
            for idx in range(lo, hi + 1):
                hl[idx] = "range"
            hl[hi] = "pivot"
            hl[j] = "comparing"
            if i >= lo:
                hl[i] = "active"
            steps.append(Step(
                data=list(a),
                highlights=hl,
                pseudocode_line=12,
                stats=dict(stats),
                description=f"Comparing A[{j}]={a[j]} with pivot {pivot}.",
            ))

            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
                stats["swaps"] += 1

                hl2 = dict(hl)
                hl2[i] = "swapping"
                hl2[j] = "swapping"
                steps.append(Step(
                    data=list(a),
                    highlights=hl2,
                    pseudocode_line=14,
                    stats=dict(stats),
                    description=f"A[{j}]={a[j]} ≤ pivot → swap A[{i}] and A[{j}].",
                ))

        a[i + 1], a[hi] = a[hi], a[i + 1]
        stats["swaps"] += 1
        sorted_set.add(i + 1)

        hl = {idx: "sorted" if idx in sorted_set else "default_bar" for idx in range(n)}
        hl[i + 1] = "pivot"
        steps.append(Step(
            data=list(a),
            highlights=hl,
            pseudocode_line=17,
            stats=dict(stats),
            description=f"Pivot {pivot} placed at final position {i + 1}.",
        ))
        return i + 1

    def _quicksort(a: list[int], lo: int, hi: int) -> None:
        if lo < hi:
            pi = _partition(a, lo, hi)
            _quicksort(a, lo, pi - 1)
            _quicksort(a, pi + 1, hi)
        elif lo == hi:
            sorted_set.add(lo)

    yield Step(
        data=list(arr),
        highlights={},
        pseudocode_line=0,
        stats={"comparisons": 0, "swaps": 0},
        description=f"Starting Quick Sort on {n} elements.",
    )

    _quicksort(arr, 0, n - 1)

    for s in steps:
        yield s

    yield Step(
        data=list(arr),
        highlights={i: "sorted" for i in range(n)},
        pseudocode_line=6,
        stats=dict(stats),
        description=f"Quick Sort complete! {stats['comparisons']} comparisons, {stats['swaps']} swaps.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Heap Sort
# ═══════════════════════════════════════════════════════════════════

HEAP_SORT_PSEUDO = [
    "procedure heapSort(A, n)",
    "  buildMaxHeap(A, n)",
    "  for i ← n-1 down to 1",
    "    swap(A[0], A[i])",
    "    heapify(A, i, 0)",
    "  end for",
    "end procedure",
    "",
    "procedure heapify(A, n, i)",
    "  largest ← i, l ← 2i+1, r ← 2i+2",
    "  if l < n and A[l] > A[largest] largest ← l",
    "  if r < n and A[r] > A[largest] largest ← r",
    "  if largest ≠ i",
    "    swap(A[i], A[largest])",
    "    heapify(A, n, largest)",
    "  end if",
    "end procedure",
]


def heap_sort(data: list[int]) -> Generator[Step, None, None]:
    arr = list(data)
    n = len(arr)
    stats = {"comparisons": 0, "swaps": 0}
    sorted_indices = set()

    yield Step(
        data=list(arr),
        highlights={},
        pseudocode_line=0,
        stats=dict(stats),
        description=f"Starting Heap Sort on {n} elements.",
    )

    def heapify(size: int, root: int):
        largest = root
        l = 2 * root + 1
        r = 2 * root + 2

        if l < size:
            stats["comparisons"] += 1
            yield Step(
                data=list(arr),
                highlights={root: "comparing", l: "comparing", **{s: "sorted" for s in sorted_indices}},
                pseudocode_line=9,
                stats=dict(stats),
                description=f"Comparing root A[{root}]={arr[root]} with left child A[{l}]={arr[l]}.",
            )
            if arr[l] > arr[largest]:
                largest = l

        if r < size:
            stats["comparisons"] += 1
            yield Step(
                data=list(arr),
                highlights={largest: "comparing", r: "comparing", **{s: "sorted" for s in sorted_indices}},
                pseudocode_line=10,
                stats=dict(stats),
                description=f"Comparing largest candidate A[{largest}]={arr[largest]} with right child A[{r}]={arr[r]}.",
            )
            if arr[r] > arr[largest]:
                largest = r

        if largest != root:
            stats["swaps"] += 1
            arr[root], arr[largest] = arr[largest], arr[root]
            yield Step(
                data=list(arr),
                highlights={root: "swapping", largest: "swapping", **{s: "sorted" for s in sorted_indices}},
                pseudocode_line=12,
                stats=dict(stats),
                description=f"Swapped A[{root}] and A[{largest}] to satisfy max-heap property.",
            )
            yield from heapify(size, largest)

    for i in range(n // 2 - 1, -1, -1):
        yield from heapify(n, i)

    for i in range(n - 1, 0, -1):
        stats["swaps"] += 1
        arr[0], arr[i] = arr[i], arr[0]
        sorted_indices.add(i)
        yield Step(
            data=list(arr),
            highlights={0: "swapping", i: "sorted", **{s: "sorted" for s in sorted_indices}},
            pseudocode_line=3,
            stats=dict(stats),
            description=f"Moved maximum element A[0]={arr[i]} to sorted position at index {i}.",
        )
        yield from heapify(i, 0)

    sorted_indices.add(0)
    yield Step(
        data=list(arr),
        highlights={i: "sorted" for i in range(n)},
        pseudocode_line=5,
        stats=dict(stats),
        description=f"Heap Sort complete! {stats['comparisons']} comparisons, {stats['swaps']} swaps.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Registration
# ═══════════════════════════════════════════════════════════════════

def register_sorting_algorithms() -> None:
    """Register all sorting algorithms in the global registry."""
    register(AlgorithmInfo(
        key="bubble_sort",
        name="Bubble Sort",
        category="sorting",
        pseudocode=BUBBLE_SORT_PSEUDO,
        time_complexity="O(n²)",
        space_complexity="O(1)",
        description="Repeatedly swaps adjacent elements if they are in the wrong order.",
        generator_func=bubble_sort,
    ))
    register(AlgorithmInfo(
        key="selection_sort",
        name="Selection Sort",
        category="sorting",
        pseudocode=SELECTION_SORT_PSEUDO,
        time_complexity="O(n²)",
        space_complexity="O(1)",
        description="Finds the minimum element and places it at the beginning.",
        generator_func=selection_sort,
    ))
    register(AlgorithmInfo(
        key="insertion_sort",
        name="Insertion Sort",
        category="sorting",
        pseudocode=INSERTION_SORT_PSEUDO,
        time_complexity="O(n²)",
        space_complexity="O(1)",
        description="Builds sorted array one item at a time by inserting into correct position.",
        generator_func=insertion_sort,
    ))
    register(AlgorithmInfo(
        key="merge_sort",
        name="Merge Sort",
        category="sorting",
        pseudocode=MERGE_SORT_PSEUDO,
        time_complexity="O(n log n)",
        space_complexity="O(n)",
        description="Divides array in half, recursively sorts, then merges.",
        generator_func=merge_sort,
    ))
    register(AlgorithmInfo(
        key="quick_sort",
        name="Quick Sort",
        category="sorting",
        pseudocode=QUICK_SORT_PSEUDO,
        time_complexity="O(n log n) avg",
        space_complexity="O(log n)",
        description="Picks a pivot, partitions around it, recursively sorts partitions.",
        generator_func=quick_sort,
    ))
    register(AlgorithmInfo(
        key="heap_sort",
        name="Heap Sort",
        category="sorting",
        pseudocode=HEAP_SORT_PSEUDO,
        time_complexity="O(n log n)",
        space_complexity="O(1)",
        description="Builds a binary max-heap and repeatedly extracts the maximum element.",
        generator_func=heap_sort,
    ))
