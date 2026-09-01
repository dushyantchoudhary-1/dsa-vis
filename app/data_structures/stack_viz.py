"""
Stack data-structure visualiser.

Maintains an internal stack and exposes push / pop / peek operations
that return generators of ``Step`` objects for animation.
"""

from __future__ import annotations

from typing import Generator

from app.engine.algorithm_engine import AlgorithmInfo, Step, register


STACK_PSEUDO = {
    "push": [
        "procedure push(stack, value)",
        "  stack[top + 1] ← value",
        "  top ← top + 1",
        "end procedure",
    ],
    "pop": [
        "procedure pop(stack)",
        "  if top < 0",
        "    error 'Stack Underflow'",
        "  end if",
        "  value ← stack[top]",
        "  top ← top - 1",
        "  return value",
        "end procedure",
    ],
    "peek": [
        "procedure peek(stack)",
        "  if top < 0",
        "    error 'Stack is empty'",
        "  end if",
        "  return stack[top]",
        "end procedure",
    ],
}


class StackVisualizer:
    """In-memory stack with animated operations."""

    def __init__(self) -> None:
        self.stack: list[int] = []

    def push(self, value: int) -> Generator[Step, None, None]:
        yield Step(
            data=list(self.stack),
            highlights={},
            pseudocode_line=0,
            stats={"size": len(self.stack), "operation": f"push({value})"},
            description=f"Pushing {value} onto the stack.",
            visualization_type="stack",
        )

        self.stack.append(value)

        yield Step(
            data=list(self.stack),
            highlights={len(self.stack) - 1: "node_new"},
            pseudocode_line=1,
            stats={"size": len(self.stack), "operation": f"push({value})"},
            description=f"{value} added as the new top. Stack size is now {len(self.stack)}.",
            visualization_type="stack",
        )

        yield Step(
            data=list(self.stack),
            highlights={len(self.stack) - 1: "node_active"},
            pseudocode_line=2,
            stats={"size": len(self.stack), "operation": f"push({value})"},
            description=f"Push complete. Top = {self.stack[-1]}.",
            visualization_type="stack",
        )

    def pop(self) -> Generator[Step, None, None]:
        if not self.stack:
            yield Step(
                data=[],
                highlights={},
                pseudocode_line=2,
                stats={"size": 0, "operation": "pop() — UNDERFLOW"},
                description="Cannot pop — the stack is empty! Stack underflow.",
                visualization_type="stack",
            )
            return

        top_val = self.stack[-1]
        yield Step(
            data=list(self.stack),
            highlights={len(self.stack) - 1: "node_delete"},
            pseudocode_line=4,
            stats={"size": len(self.stack), "operation": f"pop() → {top_val}"},
            description=f"Removing top element {top_val} from the stack.",
            visualization_type="stack",
        )

        self.stack.pop()

        hl = {len(self.stack) - 1: "node_active"} if self.stack else {}
        yield Step(
            data=list(self.stack),
            highlights=hl,
            pseudocode_line=5,
            stats={"size": len(self.stack), "operation": f"pop() → {top_val}"},
            description=f"Popped {top_val}. Stack size is now {len(self.stack)}.",
            visualization_type="stack",
        )

    def peek(self) -> Generator[Step, None, None]:
        if not self.stack:
            yield Step(
                data=[],
                highlights={},
                pseudocode_line=2,
                stats={"size": 0, "operation": "peek() — EMPTY"},
                description="Cannot peek — the stack is empty!",
                visualization_type="stack",
            )
            return

        yield Step(
            data=list(self.stack),
            highlights={len(self.stack) - 1: "node_highlight"},
            pseudocode_line=4,
            stats={"size": len(self.stack), "operation": f"peek() → {self.stack[-1]}"},
            description=f"Top element is {self.stack[-1]}. Stack unchanged.",
            visualization_type="stack",
        )

    def clear(self) -> Generator[Step, None, None]:
        self.stack.clear()
        yield Step(
            data=[],
            highlights={},
            pseudocode_line=-1,
            stats={"size": 0, "operation": "clear()"},
            description="Stack cleared.",
            visualization_type="stack",
        )


def register_stack() -> None:
    register(AlgorithmInfo(
        key="stack",
        name="Stack",
        category="data_structure",
        subcategory="stack",
        pseudocode=STACK_PSEUDO["push"],
        time_complexity="O(1) per operation",
        space_complexity="O(n)",
        description="Last-In First-Out (LIFO) data structure.",
        operations=["push", "pop", "peek", "clear"],
    ))
