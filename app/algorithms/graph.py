"""
Graph traversal & pathfinding algorithm generators — each yields ``Step`` snapshots.

Implemented:
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Dijkstra's Shortest Path
- A* Search (Manhattan heuristic)

All algorithms operate on a 2D grid graph with start and target nodes.
"""

from __future__ import annotations

import heapq
from collections import deque
from typing import Generator

from app.engine.algorithm_engine import AlgorithmInfo, Step, register


# ═══════════════════════════════════════════════════════════════════
#  Default Grid Graph Setup
# ═══════════════════════════════════════════════════════════════════

DEFAULT_GRID_ROWS = 7
DEFAULT_GRID_COLS = 12
DEFAULT_START = (0, 0)
DEFAULT_GOAL = (DEFAULT_GRID_ROWS - 1, DEFAULT_GRID_COLS - 1)

# Default obstacle walls
DEFAULT_WALLS = {
    (1, 3), (2, 3), (3, 3), (4, 3),
    (2, 7), (3, 7), (4, 7), (5, 7),
}


def create_default_grid(rows=DEFAULT_GRID_ROWS, cols=DEFAULT_GRID_COLS, walls=None) -> dict:
    if walls is None:
        walls = set(DEFAULT_WALLS)
    return {
        "rows": rows,
        "cols": cols,
        "start": DEFAULT_START,
        "goal": (rows - 1, cols - 1),
        "walls": set(walls),
    }


def _get_neighbors(r: int, c: int, rows: int, cols: int, walls: set) -> list[tuple[int, int]]:
    """4-directional orthogonal neighbors."""
    neighbors = []
    for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in walls:
            neighbors.append((nr, nc))
    return neighbors


# ═══════════════════════════════════════════════════════════════════
#  Breadth-First Search (BFS)
# ═══════════════════════════════════════════════════════════════════

BFS_PSEUDO = [
    "procedure BFS(Graph, start, goal)",
    "  Q ← Queue()",
    "  Q.push(start); visited.add(start)",
    "  while not Q.isEmpty()",
    "    current ← Q.pop()",
    "    if current == goal return reconstructPath()",
    "    for neighbor in neighbors(current)",
    "      if neighbor not in visited",
    "        visited.add(neighbor); parent[neighbor] = current",
    "        Q.push(neighbor)",
    "  return Failure",
    "end procedure",
]


def bfs_search(grid_info: dict | None = None) -> Generator[Step, None, None]:
    if grid_info is None:
        grid_info = create_default_grid()

    rows, cols = grid_info["rows"], grid_info["cols"]
    start, goal = grid_info["start"], grid_info["goal"]
    walls = set(grid_info.get("walls", []))

    visited = {start}
    frontier = deque([start])
    parent = {}
    stats = {"visited": 1, "frontier": 1, "path_length": 0, "operations": 1}

    yield Step(
        data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls)},
        highlights={start: "active", goal: "target"},
        pseudocode_line=2,
        stats=dict(stats),
        description=f"Starting BFS from {start} to {goal}.",
        visualization_type="graph",
    )

    found = False
    while frontier:
        curr = frontier.popleft()
        stats["operations"] += 1
        stats["frontier"] = len(frontier)

        if curr == goal:
            found = True
            break

        yield Step(
            data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls)},
            highlights={
                **{node: "visited" for node in visited},
                **{node: "mid" for node in frontier},
                curr: "active",
                goal: "target",
                start: "found",
            },
            pseudocode_line=4,
            stats=dict(stats),
            description=f"Visiting node {curr}. Queue size: {len(frontier)}.",
            visualization_type="graph",
        )

        for nxt in _get_neighbors(curr[0], curr[1], rows, cols, walls):
            stats["operations"] += 1
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = curr
                frontier.append(nxt)
                stats["visited"] = len(visited)
                stats["frontier"] = len(frontier)

                if nxt == goal:
                    found = True
                    break

        if found:
            break

    # Reconstruct path
    path = []
    if found:
        curr = goal
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append(start)
        path.reverse()
        stats["path_length"] = len(path)

    yield Step(
        data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls), "path": path},
        highlights={
            **{node: "visited" for node in visited},
            **{node: "found" for node in path},
            goal: "found",
            start: "found",
        },
        pseudocode_line=5 if found else 10,
        stats=dict(stats),
        description=f"BFS {'Path found! Length: ' + str(len(path)) if found else 'No path exists!'} (Visited {len(visited)} nodes).",
        visualization_type="graph",
    )


# ═══════════════════════════════════════════════════════════════════
#  Depth-First Search (DFS)
# ═══════════════════════════════════════════════════════════════════

DFS_PSEUDO = [
    "procedure DFS(Graph, start, goal)",
    "  Stack ← Stack()",
    "  Stack.push(start)",
    "  while not Stack.isEmpty()",
    "    current ← Stack.pop()",
    "    if current == goal return reconstructPath()",
    "    if current not in visited",
    "      visited.add(current)",
    "      for neighbor in neighbors(current)",
    "        Stack.push(neighbor); parent[neighbor] = current",
    "  return Failure",
    "end procedure",
]


def dfs_search(grid_info: dict | None = None) -> Generator[Step, None, None]:
    if grid_info is None:
        grid_info = create_default_grid()

    rows, cols = grid_info["rows"], grid_info["cols"]
    start, goal = grid_info["start"], grid_info["goal"]
    walls = set(grid_info.get("walls", []))

    visited = set()
    stack = [start]
    parent = {}
    stats = {"visited": 0, "frontier": 1, "path_length": 0, "operations": 1}

    yield Step(
        data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls)},
        highlights={start: "active", goal: "target"},
        pseudocode_line=2,
        stats=dict(stats),
        description=f"Starting DFS from {start} to {goal}.",
        visualization_type="graph",
    )

    found = False
    while stack:
        curr = stack.pop()
        stats["operations"] += 1
        stats["frontier"] = len(stack)

        if curr in visited:
            continue
        visited.add(curr)
        stats["visited"] = len(visited)

        if curr == goal:
            found = True
            break

        yield Step(
            data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls)},
            highlights={
                **{node: "visited" for node in visited},
                **{node: "mid" for node in stack},
                curr: "active",
                goal: "target",
                start: "found",
            },
            pseudocode_line=4,
            stats=dict(stats),
            description=f"Visiting node {curr} deeply. Stack size: {len(stack)}.",
            visualization_type="graph",
        )

        for nxt in _get_neighbors(curr[0], curr[1], rows, cols, walls):
            stats["operations"] += 1
            if nxt not in visited:
                parent[nxt] = curr
                stack.append(nxt)
                stats["frontier"] = len(stack)
                if nxt == goal:
                    visited.add(nxt)
                    found = True
                    break
        if found:
            break

    path = []
    if found:
        curr = goal
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append(start)
        path.reverse()
        stats["path_length"] = len(path)

    yield Step(
        data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls), "path": path},
        highlights={
            **{node: "visited" for node in visited},
            **{node: "found" for node in path},
            goal: "found",
            start: "found",
        },
        pseudocode_line=5 if found else 10,
        stats=dict(stats),
        description=f"DFS {'Path found! Length: ' + str(len(path)) if found else 'No path exists!'} (Visited {len(visited)} nodes).",
        visualization_type="graph",
    )


# ═══════════════════════════════════════════════════════════════════
#  Dijkstra's Algorithm
# ═══════════════════════════════════════════════════════════════════

DIJKSTRA_PSEUDO = [
    "procedure Dijkstra(Graph, start, goal)",
    "  dist[all] ← ∞; dist[start] ← 0",
    "  PQ ← PriorityQueue(); PQ.push((0, start))",
    "  while not PQ.isEmpty()",
    "    (d, current) ← PQ.popMin()",
    "    if current == goal return reconstructPath()",
    "    for neighbor in neighbors(current)",
    "      if dist[current] + cost < dist[neighbor]",
    "        dist[neighbor] ← dist[current] + cost",
    "        PQ.push((dist[neighbor], neighbor))",
    "end procedure",
]


def dijkstra_search(grid_info: dict | None = None) -> Generator[Step, None, None]:
    if grid_info is None:
        grid_info = create_default_grid()

    rows, cols = grid_info["rows"], grid_info["cols"]
    start, goal = grid_info["start"], grid_info["goal"]
    walls = set(grid_info.get("walls", []))

    dist = {start: 0}
    pq = [(0, 0, start)]  # (cost, counter, node)
    counter = 0
    visited = set()
    parent = {}
    stats = {"visited": 0, "frontier": 1, "path_length": 0, "operations": 1}

    yield Step(
        data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls)},
        highlights={start: "active", goal: "target"},
        pseudocode_line=2,
        stats=dict(stats),
        description=f"Starting Dijkstra's shortest path algorithm.",
        visualization_type="graph",
    )

    found = False
    while pq:
        d, _, curr = heapq.heappop(pq)
        stats["operations"] += 1
        stats["frontier"] = len(pq)

        if curr in visited:
            continue
        visited.add(curr)
        stats["visited"] = len(visited)

        if curr == goal:
            found = True
            break

        yield Step(
            data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls)},
            highlights={
                **{node: "visited" for node in visited},
                curr: "active",
                goal: "target",
                start: "found",
            },
            pseudocode_line=4,
            stats=dict(stats),
            description=f"Relaxing edges from {curr} (min distance = {d}).",
            visualization_type="graph",
        )

        for nxt in _get_neighbors(curr[0], curr[1], rows, cols, walls):
            stats["operations"] += 1
            new_cost = d + 1
            if new_cost < dist.get(nxt, float("inf")):
                dist[nxt] = new_cost
                parent[nxt] = curr
                counter += 1
                heapq.heappush(pq, (new_cost, counter, nxt))
                stats["frontier"] = len(pq)

    path = []
    if found:
        curr = goal
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append(start)
        path.reverse()
        stats["path_length"] = len(path)

    yield Step(
        data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls), "path": path},
        highlights={
            **{node: "visited" for node in visited},
            **{node: "found" for node in path},
            goal: "found",
            start: "found",
        },
        pseudocode_line=5 if found else 10,
        stats=dict(stats),
        description=f"Dijkstra {'Optimal path found! Cost: ' + str(len(path) - 1) if found else 'No path exists!'} (Visited {len(visited)} nodes).",
        visualization_type="graph",
    )


# ═══════════════════════════════════════════════════════════════════
#  A* Search Algorithm (A-Star)
# ═══════════════════════════════════════════════════════════════════

ASTAR_PSEUDO = [
    "procedure AStar(Graph, start, goal)",
    "  gScore[start] ← 0; fScore[start] ← h(start, goal)",
    "  openSet ← PriorityQueue(); openSet.push((fScore[start], start))",
    "  while not openSet.isEmpty()",
    "    current ← openSet.popMin()",
    "    if current == goal return reconstructPath()",
    "    for neighbor in neighbors(current)",
    "      tentative_g ← gScore[current] + cost",
    "      if tentative_g < gScore[neighbor]",
    "        gScore[neighbor] ← tentative_g",
    "        fScore[neighbor] ← tentative_g + h(neighbor, goal)",
    "        openSet.push((fScore[neighbor], neighbor))",
    "end procedure",
]


def astar_search(grid_info: dict | None = None) -> Generator[Step, None, None]:
    if grid_info is None:
        grid_info = create_default_grid()

    rows, cols = grid_info["rows"], grid_info["cols"]
    start, goal = grid_info["start"], grid_info["goal"]
    walls = set(grid_info.get("walls", []))

    def h(pos: tuple[int, int]) -> int:
        """Manhattan distance heuristic."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    g_score = {start: 0}
    f_score = {start: h(start)}
    pq = [(f_score[start], 0, start)]
    counter = 0
    visited = set()
    parent = {}
    stats = {"visited": 0, "frontier": 1, "path_length": 0, "operations": 1}

    yield Step(
        data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls)},
        highlights={start: "active", goal: "target"},
        pseudocode_line=2,
        stats=dict(stats),
        description=f"Starting A* Search with Manhattan heuristic h={h(start)}.",
        visualization_type="graph",
    )

    found = False
    while pq:
        f, _, curr = heapq.heappop(pq)
        stats["operations"] += 1
        stats["frontier"] = len(pq)

        if curr in visited:
            continue
        visited.add(curr)
        stats["visited"] = len(visited)

        if curr == goal:
            found = True
            break

        yield Step(
            data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls)},
            highlights={
                **{node: "visited" for node in visited},
                curr: "active",
                goal: "target",
                start: "found",
            },
            pseudocode_line=4,
            stats=dict(stats),
            description=f"Expanding node {curr} with f(n) = g({g_score[curr]}) + h({h(curr)}) = {f}.",
            visualization_type="graph",
        )

        for nxt in _get_neighbors(curr[0], curr[1], rows, cols, walls):
            stats["operations"] += 1
            tentative_g = g_score[curr] + 1
            if tentative_g < g_score.get(nxt, float("inf")):
                parent[nxt] = curr
                g_score[nxt] = tentative_g
                fn = tentative_g + h(nxt)
                f_score[nxt] = fn
                counter += 1
                heapq.heappush(pq, (fn, counter, nxt))
                stats["frontier"] = len(pq)

    path = []
    if found:
        curr = goal
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append(start)
        path.reverse()
        stats["path_length"] = len(path)

    yield Step(
        data={"rows": rows, "cols": cols, "start": start, "goal": goal, "walls": list(walls), "path": path},
        highlights={
            **{node: "visited" for node in visited},
            **{node: "found" for node in path},
            goal: "found",
            start: "found",
        },
        pseudocode_line=5 if found else 12,
        stats=dict(stats),
        description=f"A* {'Optimal path found! Cost: ' + str(len(path) - 1) if found else 'No path exists!'} (Visited only {len(visited)} nodes).",
        visualization_type="graph",
    )


# ═══════════════════════════════════════════════════════════════════
#  Registration
# ═══════════════════════════════════════════════════════════════════

def register_graph_algorithms() -> None:
    """Register all graph traversal/search algorithms."""
    register(AlgorithmInfo(
        key="bfs_search",
        name="Breadth-First Search (BFS)",
        category="graph",
        pseudocode=BFS_PSEUDO,
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        description="Explores graph layer by layer, guaranteed to find shortest path in unweighted graphs.",
        generator_func=bfs_search,
    ))
    register(AlgorithmInfo(
        key="dfs_search",
        name="Depth-First Search (DFS)",
        category="graph",
        pseudocode=DFS_PSEUDO,
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        description="Explores as deep as possible along each branch before backtracking.",
        generator_func=dfs_search,
    ))
    register(AlgorithmInfo(
        key="dijkstra_search",
        name="Dijkstra's Algorithm",
        category="graph",
        pseudocode=DIJKSTRA_PSEUDO,
        time_complexity="O((V + E) log V)",
        space_complexity="O(V)",
        description="Finds shortest paths from start node to all nodes using a priority queue.",
        generator_func=dijkstra_search,
    ))
    register(AlgorithmInfo(
        key="astar_search",
        name="A* Search",
        category="graph",
        pseudocode=ASTAR_PSEUDO,
        time_complexity="O(E) with heuristic",
        space_complexity="O(V)",
        description="Informed search algorithm using heuristic function f(n) = g(n) + h(n).",
        generator_func=astar_search,
    ))
