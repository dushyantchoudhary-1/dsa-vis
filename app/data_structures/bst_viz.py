"""
Binary Search Tree (BST) data-structure visualiser.

The tree is represented as nested dicts for easy serialisation:
    {"value": 10, "left": {...} | None, "right": {...} | None}

Operations: insert, search, inorder, preorder, postorder.
"""

from __future__ import annotations

from typing import Generator

from app.engine.algorithm_engine import AlgorithmInfo, Step, register


BST_PSEUDO = {
    "insert": [
        "procedure insert(root, value)",
        "  if root is null",
        "    return Node(value)",
        "  end if",
        "  if value < root.value",
        "    root.left ← insert(root.left, value)",
        "  else if value > root.value",
        "    root.right ← insert(root.right, value)",
        "  end if",
        "  return root",
        "end procedure",
    ],
    "search": [
        "procedure search(root, value)",
        "  if root is null",
        "    return null",
        "  end if",
        "  if value == root.value",
        "    return root",
        "  else if value < root.value",
        "    return search(root.left, value)",
        "  else",
        "    return search(root.right, value)",
        "  end if",
        "end procedure",
    ],
    "inorder": [
        "procedure inorder(root)",
        "  if root is null → return",
        "  inorder(root.left)",
        "  visit(root)",
        "  inorder(root.right)",
        "end procedure",
    ],
    "preorder": [
        "procedure preorder(root)",
        "  if root is null → return",
        "  visit(root)",
        "  preorder(root.left)",
        "  preorder(root.right)",
        "end procedure",
    ],
    "postorder": [
        "procedure postorder(root)",
        "  if root is null → return",
        "  postorder(root.left)",
        "  postorder(root.right)",
        "  visit(root)",
        "end procedure",
    ],
}


# ── Tree helpers ─────────────────────────────────────────────────

def _make_node(value: int) -> dict:
    return {"value": value, "left": None, "right": None}


def _deep_copy(node: dict | None) -> dict | None:
    if node is None:
        return None
    return {
        "value": node["value"],
        "left": _deep_copy(node["left"]),
        "right": _deep_copy(node["right"]),
    }


def _tree_size(node: dict | None) -> int:
    if node is None:
        return 0
    return 1 + _tree_size(node["left"]) + _tree_size(node["right"])


def _tree_height(node: dict | None) -> int:
    if node is None:
        return 0
    return 1 + max(_tree_height(node["left"]), _tree_height(node["right"]))


class BSTVisualizer:
    """Binary Search Tree with animated operations."""

    def __init__(self) -> None:
        self.root: dict | None = None

    def insert(self, value: int) -> Generator[Step, None, None]:
        stats = {"size": _tree_size(self.root), "height": _tree_height(self.root)}

        yield Step(
            data=_deep_copy(self.root),
            highlights={},
            pseudocode_line=0,
            stats={**stats, "operation": f"insert({value})"},
            description=f"Inserting {value} into the BST.",
            visualization_type="bst",
        )

        if self.root is None:
            self.root = _make_node(value)
            yield Step(
                data=_deep_copy(self.root),
                highlights={value: "node_new"},
                pseudocode_line=2,
                stats={"size": 1, "height": 1, "operation": f"insert({value})"},
                description=f"Tree was empty. {value} is the new root.",
                visualization_type="bst",
            )
            return

        # Walk the tree
        current = self.root
        path: list[int] = []

        while True:
            path.append(current["value"])
            path_hl = {v: "node_active" for v in path}
            yield Step(
                data=_deep_copy(self.root),
                highlights=path_hl,
                pseudocode_line=4 if value < current["value"] else 6,
                stats={**stats, "operation": f"insert({value})"},
                description=(
                    f"At node {current['value']}. "
                    f"{value} {'<' if value < current['value'] else '>'} "
                    f"{current['value']} → go {'left' if value < current['value'] else 'right'}."
                ),
                visualization_type="bst",
            )

            if value < current["value"]:
                if current["left"] is None:
                    current["left"] = _make_node(value)
                    break
                current = current["left"]
            elif value > current["value"]:
                if current["right"] is None:
                    current["right"] = _make_node(value)
                    break
                current = current["right"]
            else:
                # Duplicate — skip
                yield Step(
                    data=_deep_copy(self.root),
                    highlights={value: "node_highlight"},
                    pseudocode_line=8,
                    stats={**stats, "operation": f"insert({value}) — DUPLICATE"},
                    description=f"Value {value} already exists. Skipping.",
                    visualization_type="bst",
                )
                return

        yield Step(
            data=_deep_copy(self.root),
            highlights={**{v: "node_active" for v in path}, value: "node_new"},
            pseudocode_line=9,
            stats={
                "size": _tree_size(self.root),
                "height": _tree_height(self.root),
                "operation": f"insert({value})",
            },
            description=f"Inserted {value}. Tree size = {_tree_size(self.root)}, height = {_tree_height(self.root)}.",
            visualization_type="bst",
        )

    def search(self, value: int) -> Generator[Step, None, None]:
        stats = {"size": _tree_size(self.root), "height": _tree_height(self.root)}

        yield Step(
            data=_deep_copy(self.root),
            highlights={},
            pseudocode_line=0,
            stats={**stats, "operation": f"search({value})"},
            description=f"Searching for {value} in the BST.",
            visualization_type="bst",
        )

        current = self.root
        comps = 0

        while current is not None:
            comps += 1
            yield Step(
                data=_deep_copy(self.root),
                highlights={current["value"]: "node_active"},
                pseudocode_line=4,
                stats={**stats, "comparisons": comps, "operation": f"search({value})"},
                description=f"Comparing with node {current['value']}.",
                visualization_type="bst",
            )

            if value == current["value"]:
                yield Step(
                    data=_deep_copy(self.root),
                    highlights={current["value"]: "found"},
                    pseudocode_line=5,
                    stats={**stats, "comparisons": comps, "operation": f"search({value}) → FOUND"},
                    description=f"Found {value} after {comps} comparisons!",
                    visualization_type="bst",
                )
                return
            elif value < current["value"]:
                yield Step(
                    data=_deep_copy(self.root),
                    highlights={current["value"]: "node_highlight"},
                    pseudocode_line=7,
                    stats={**stats, "comparisons": comps, "operation": f"search({value})"},
                    description=f"{value} < {current['value']} → go left.",
                    visualization_type="bst",
                )
                current = current["left"]
            else:
                yield Step(
                    data=_deep_copy(self.root),
                    highlights={current["value"]: "node_highlight"},
                    pseudocode_line=9,
                    stats={**stats, "comparisons": comps, "operation": f"search({value})"},
                    description=f"{value} > {current['value']} → go right.",
                    visualization_type="bst",
                )
                current = current["right"]

        yield Step(
            data=_deep_copy(self.root),
            highlights={},
            pseudocode_line=2,
            stats={**stats, "comparisons": comps, "operation": f"search({value}) → NOT FOUND"},
            description=f"Value {value} not found after {comps} comparisons.",
            visualization_type="bst",
        )

    # ── Traversals ───────────────────────────────────────────────

    def _inorder(self, node: dict | None, visited: list[int], steps: list[Step]) -> None:
        if node is None:
            return
        self._inorder(node["left"], visited, steps)
        visited.append(node["value"])
        steps.append(Step(
            data=_deep_copy(self.root),
            highlights={**{v: "sorted" for v in visited[:-1]}, node["value"]: "node_active"},
            pseudocode_line=3,
            stats={"visited": list(visited), "operation": "inorder"},
            description=f"Visit node {node['value']}. Order so far: {visited}",
            visualization_type="bst",
        ))
        self._inorder(node["right"], visited, steps)

    def inorder(self) -> Generator[Step, None, None]:
        yield Step(
            data=_deep_copy(self.root),
            highlights={},
            pseudocode_line=0,
            stats={"operation": "inorder"},
            description="Starting In-order traversal (Left → Root → Right).",
            visualization_type="bst",
        )
        visited: list[int] = []
        steps: list[Step] = []
        self._inorder(self.root, visited, steps)
        yield from steps
        yield Step(
            data=_deep_copy(self.root),
            highlights={v: "sorted" for v in visited},
            pseudocode_line=5,
            stats={"visited": list(visited), "operation": "inorder"},
            description=f"In-order traversal complete: {visited}",
            visualization_type="bst",
        )

    def _preorder(self, node: dict | None, visited: list[int], steps: list[Step]) -> None:
        if node is None:
            return
        visited.append(node["value"])
        steps.append(Step(
            data=_deep_copy(self.root),
            highlights={**{v: "sorted" for v in visited[:-1]}, node["value"]: "node_active"},
            pseudocode_line=2,
            stats={"visited": list(visited), "operation": "preorder"},
            description=f"Visit node {node['value']}. Order so far: {visited}",
            visualization_type="bst",
        ))
        self._preorder(node["left"], visited, steps)
        self._preorder(node["right"], visited, steps)

    def preorder(self) -> Generator[Step, None, None]:
        yield Step(
            data=_deep_copy(self.root),
            highlights={},
            pseudocode_line=0,
            stats={"operation": "preorder"},
            description="Starting Pre-order traversal (Root → Left → Right).",
            visualization_type="bst",
        )
        visited: list[int] = []
        steps: list[Step] = []
        self._preorder(self.root, visited, steps)
        yield from steps
        yield Step(
            data=_deep_copy(self.root),
            highlights={v: "sorted" for v in visited},
            pseudocode_line=5,
            stats={"visited": list(visited), "operation": "preorder"},
            description=f"Pre-order traversal complete: {visited}",
            visualization_type="bst",
        )

    def _postorder(self, node: dict | None, visited: list[int], steps: list[Step]) -> None:
        if node is None:
            return
        self._postorder(node["left"], visited, steps)
        self._postorder(node["right"], visited, steps)
        visited.append(node["value"])
        steps.append(Step(
            data=_deep_copy(self.root),
            highlights={**{v: "sorted" for v in visited[:-1]}, node["value"]: "node_active"},
            pseudocode_line=4,
            stats={"visited": list(visited), "operation": "postorder"},
            description=f"Visit node {node['value']}. Order so far: {visited}",
            visualization_type="bst",
        ))

    def postorder(self) -> Generator[Step, None, None]:
        yield Step(
            data=_deep_copy(self.root),
            highlights={},
            pseudocode_line=0,
            stats={"operation": "postorder"},
            description="Starting Post-order traversal (Left → Right → Root).",
            visualization_type="bst",
        )
        visited: list[int] = []
        steps: list[Step] = []
        self._postorder(self.root, visited, steps)
        yield from steps
        yield Step(
            data=_deep_copy(self.root),
            highlights={v: "sorted" for v in visited},
            pseudocode_line=5,
            stats={"visited": list(visited), "operation": "postorder"},
            description=f"Post-order traversal complete: {visited}",
            visualization_type="bst",
        )

    def clear(self) -> Generator[Step, None, None]:
        self.root = None
        yield Step(
            data=None,
            highlights={},
            pseudocode_line=-1,
            stats={"size": 0, "height": 0, "operation": "clear()"},
            description="BST cleared.",
            visualization_type="bst",
        )


def register_bst() -> None:
    register(AlgorithmInfo(
        key="bst",
        name="Binary Search Tree",
        category="data_structure",
        subcategory="bst",
        pseudocode=BST_PSEUDO["insert"],
        time_complexity="O(h) per operation",
        space_complexity="O(n)",
        description="Binary tree where left < root < right.",
        operations=["insert", "search", "inorder", "preorder", "postorder", "clear"],
    ))
