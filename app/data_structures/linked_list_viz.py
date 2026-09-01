"""
Singly Linked-List data-structure visualiser.

Operations: insert_head, insert_tail, delete_value, search.
Each yields ``Step`` snapshots (visualization_type = "linked_list").
"""

from __future__ import annotations

from typing import Generator

from app.engine.algorithm_engine import AlgorithmInfo, Step, register


LL_PSEUDO = {
    "insert_head": [
        "procedure insertHead(list, value)",
        "  newNode ← Node(value)",
        "  newNode.next ← head",
        "  head ← newNode",
        "end procedure",
    ],
    "insert_tail": [
        "procedure insertTail(list, value)",
        "  newNode ← Node(value)",
        "  if head is null",
        "    head ← newNode; return",
        "  end if",
        "  current ← head",
        "  while current.next ≠ null",
        "    current ← current.next",
        "  end while",
        "  current.next ← newNode",
        "end procedure",
    ],
    "delete": [
        "procedure delete(list, value)",
        "  if head is null → error",
        "  if head.data == value",
        "    head ← head.next; return",
        "  end if",
        "  current ← head",
        "  while current.next ≠ null",
        "    if current.next.data == value",
        "      current.next ← current.next.next",
        "      return",
        "    end if",
        "    current ← current.next",
        "  end while",
        "end procedure",
    ],
    "search": [
        "procedure search(list, value)",
        "  current ← head",
        "  index ← 0",
        "  while current ≠ null",
        "    if current.data == value",
        "      return index",
        "    end if",
        "    current ← current.next",
        "    index ← index + 1",
        "  end while",
        "  return -1",
        "end procedure",
    ],
}


class LinkedListVisualizer:
    """Singly linked list with animated operations."""

    def __init__(self) -> None:
        self.values: list[int] = []

    def insert_head(self, value: int) -> Generator[Step, None, None]:
        yield Step(
            data=list(self.values),
            highlights={},
            pseudocode_line=0,
            stats={"size": len(self.values), "operation": f"insertHead({value})"},
            description=f"Inserting {value} at the head of the list.",
            visualization_type="linked_list",
        )

        self.values.insert(0, value)

        yield Step(
            data=list(self.values),
            highlights={0: "node_new"},
            pseudocode_line=2,
            stats={"size": len(self.values), "operation": f"insertHead({value})"},
            description=f"New node {value} points to old head. It is the new head.",
            visualization_type="linked_list",
        )

        yield Step(
            data=list(self.values),
            highlights={0: "node_active"},
            pseudocode_line=3,
            stats={"size": len(self.values), "operation": f"insertHead({value})"},
            description=f"Insert complete. List size = {len(self.values)}.",
            visualization_type="linked_list",
        )

    def insert_tail(self, value: int) -> Generator[Step, None, None]:
        yield Step(
            data=list(self.values),
            highlights={},
            pseudocode_line=0,
            stats={"size": len(self.values), "operation": f"insertTail({value})"},
            description=f"Inserting {value} at the tail of the list.",
            visualization_type="linked_list",
        )

        if not self.values:
            self.values.append(value)
            yield Step(
                data=list(self.values),
                highlights={0: "node_new"},
                pseudocode_line=3,
                stats={"size": len(self.values), "operation": f"insertTail({value})"},
                description=f"List was empty. {value} is the new head.",
                visualization_type="linked_list",
            )
            return

        # Traverse to tail
        for i in range(len(self.values)):
            yield Step(
                data=list(self.values),
                highlights={i: "node_active"},
                pseudocode_line=7,
                stats={"size": len(self.values), "operation": f"insertTail({value})"},
                description=f"Traversing — currently at node {self.values[i]} (index {i}).",
                visualization_type="linked_list",
            )

        self.values.append(value)

        yield Step(
            data=list(self.values),
            highlights={len(self.values) - 1: "node_new"},
            pseudocode_line=9,
            stats={"size": len(self.values), "operation": f"insertTail({value})"},
            description=f"Appended {value} at the tail. List size = {len(self.values)}.",
            visualization_type="linked_list",
        )

    def delete_value(self, value: int) -> Generator[Step, None, None]:
        yield Step(
            data=list(self.values),
            highlights={},
            pseudocode_line=0,
            stats={"size": len(self.values), "operation": f"delete({value})"},
            description=f"Deleting node with value {value}.",
            visualization_type="linked_list",
        )

        if not self.values:
            yield Step(
                data=[],
                highlights={},
                pseudocode_line=1,
                stats={"size": 0, "operation": f"delete({value}) — EMPTY"},
                description="List is empty — nothing to delete.",
                visualization_type="linked_list",
            )
            return

        # Check head
        if self.values[0] == value:
            yield Step(
                data=list(self.values),
                highlights={0: "node_delete"},
                pseudocode_line=3,
                stats={"size": len(self.values), "operation": f"delete({value})"},
                description=f"Head node matches {value}. Removing head.",
                visualization_type="linked_list",
            )
            self.values.pop(0)
            hl = {0: "node_active"} if self.values else {}
            yield Step(
                data=list(self.values),
                highlights=hl,
                pseudocode_line=3,
                stats={"size": len(self.values), "operation": f"delete({value})"},
                description=f"Head removed. List size = {len(self.values)}.",
                visualization_type="linked_list",
            )
            return

        # Search
        for i in range(len(self.values)):
            yield Step(
                data=list(self.values),
                highlights={i: "node_active"},
                pseudocode_line=6,
                stats={"size": len(self.values), "operation": f"delete({value})"},
                description=f"Checking node at index {i} (value {self.values[i]}).",
                visualization_type="linked_list",
            )
            if i + 1 < len(self.values) and self.values[i + 1] == value:
                yield Step(
                    data=list(self.values),
                    highlights={i: "node_active", i + 1: "node_delete"},
                    pseudocode_line=8,
                    stats={"size": len(self.values), "operation": f"delete({value})"},
                    description=f"Found {value} at index {i + 1}. Removing it.",
                    visualization_type="linked_list",
                )
                self.values.pop(i + 1)
                yield Step(
                    data=list(self.values),
                    highlights={},
                    pseudocode_line=8,
                    stats={"size": len(self.values), "operation": f"delete({value})"},
                    description=f"Deleted {value}. List size = {len(self.values)}.",
                    visualization_type="linked_list",
                )
                return

        yield Step(
            data=list(self.values),
            highlights={},
            pseudocode_line=12,
            stats={"size": len(self.values), "operation": f"delete({value}) — NOT FOUND"},
            description=f"Value {value} not found in the list.",
            visualization_type="linked_list",
        )

    def search(self, value: int) -> Generator[Step, None, None]:
        yield Step(
            data=list(self.values),
            highlights={},
            pseudocode_line=0,
            stats={"size": len(self.values), "operation": f"search({value})"},
            description=f"Searching for {value} in the linked list.",
            visualization_type="linked_list",
        )

        for i, v in enumerate(self.values):
            yield Step(
                data=list(self.values),
                highlights={i: "node_active"},
                pseudocode_line=4,
                stats={"size": len(self.values), "operation": f"search({value})"},
                description=f"Checking node at index {i}: value = {v}.",
                visualization_type="linked_list",
            )
            if v == value:
                yield Step(
                    data=list(self.values),
                    highlights={i: "found"},
                    pseudocode_line=5,
                    stats={"size": len(self.values), "operation": f"search({value}) → {i}"},
                    description=f"Found {value} at index {i}!",
                    visualization_type="linked_list",
                )
                return

        yield Step(
            data=list(self.values),
            highlights={},
            pseudocode_line=10,
            stats={"size": len(self.values), "operation": f"search({value}) → NOT FOUND"},
            description=f"Value {value} not found in the list.",
            visualization_type="linked_list",
        )

    def clear(self) -> Generator[Step, None, None]:
        self.values.clear()
        yield Step(
            data=[],
            highlights={},
            pseudocode_line=-1,
            stats={"size": 0, "operation": "clear()"},
            description="Linked list cleared.",
            visualization_type="linked_list",
        )


def register_linked_list() -> None:
    register(AlgorithmInfo(
        key="linked_list",
        name="Linked List",
        category="data_structure",
        subcategory="linked_list",
        pseudocode=LL_PSEUDO["insert_head"],
        time_complexity="O(1) head / O(n) tail",
        space_complexity="O(n)",
        description="Singly linked list with pointer-based node connections.",
        operations=["insert_head", "insert_tail", "delete", "search", "clear"],
    ))
