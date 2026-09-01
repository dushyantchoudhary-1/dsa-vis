"""
Queue data-structure visualiser.

Maintains an internal queue and exposes enqueue / dequeue / front
operations as ``Step`` generators.
"""

from __future__ import annotations

from typing import Generator

from app.engine.algorithm_engine import AlgorithmInfo, Step, register


QUEUE_PSEUDO = {
    "enqueue": [
        "procedure enqueue(queue, value)",
        "  queue[rear + 1] ← value",
        "  rear ← rear + 1",
        "end procedure",
    ],
    "dequeue": [
        "procedure dequeue(queue)",
        "  if front > rear",
        "    error 'Queue Underflow'",
        "  end if",
        "  value ← queue[front]",
        "  front ← front + 1",
        "  return value",
        "end procedure",
    ],
    "front": [
        "procedure front(queue)",
        "  if isEmpty(queue)",
        "    error 'Queue is empty'",
        "  end if",
        "  return queue[front]",
        "end procedure",
    ],
}
QUEUE_QUESTIONS = {
    "enqueue": "Given a queue and an integer value, insert the value at the rear of the queue using the Enqueue operation.",

    "dequeue": "Given a queue, remove the element from the front of the queue using the Dequeue operation.",

    "front": "Given a queue, view the element at the front without removing it.",

    "clear": "Remove all elements from the queue and reset it to an empty state.",
}

class QueueVisualizer:
    """In-memory queue with animated operations."""

    def __init__(self) -> None:
        self.queue: list[int] = []

    def enqueue(self, value: int) -> Generator[Step, None, None]:
        yield Step(
            data=list(self.queue),
            highlights={},
            pseudocode_line=0,
            stats={"size": len(self.queue), "operation": f"enqueue({value})"},
            description=f"Enqueuing {value} at the rear.",
            visualization_type="queue",
        )

        self.queue.append(value)

        yield Step(
            data=list(self.queue),
            highlights={len(self.queue) - 1: "node_new"},
            pseudocode_line=1,
            stats={"size": len(self.queue), "operation": f"enqueue({value})"},
            description=f"{value} added to the rear. Queue size is now {len(self.queue)}.",
            visualization_type="queue",
        )

        hl = {0: "node_active", len(self.queue) - 1: "node_highlight"}
        if len(self.queue) == 1:
            hl = {0: "node_active"}
        yield Step(
            data=list(self.queue),
            highlights=hl,
            pseudocode_line=2,
            stats={"size": len(self.queue), "operation": f"enqueue({value})"},
            description=f"Enqueue complete. Front = {self.queue[0]}, Rear = {self.queue[-1]}.",
            visualization_type="queue",
        )

    def dequeue(self) -> Generator[Step, None, None]:
        if not self.queue:
            yield Step(
                data=[],
                highlights={},
                pseudocode_line=2,
                stats={"size": 0, "operation": "dequeue() — UNDERFLOW"},
                description="Cannot dequeue — the queue is empty!",
                visualization_type="queue",
            )
            return

        front_val = self.queue[0]
        yield Step(
            data=list(self.queue),
            highlights={0: "node_delete"},
            pseudocode_line=4,
            stats={"size": len(self.queue), "operation": f"dequeue() → {front_val}"},
            description=f"Removing front element {front_val}.",
            visualization_type="queue",
        )

        self.queue.pop(0)

        hl = {0: "node_active"} if self.queue else {}
        yield Step(
            data=list(self.queue),
            highlights=hl,
            pseudocode_line=5,
            stats={"size": len(self.queue), "operation": f"dequeue() → {front_val}"},
            description=f"Dequeued {front_val}. Queue size is now {len(self.queue)}.",
            visualization_type="queue",
        )

    def front_peek(self) -> Generator[Step, None, None]:
        if not self.queue:
            yield Step(
                data=[],
                highlights={},
                pseudocode_line=2,
                stats={"size": 0, "operation": "front() — EMPTY"},
                description="Cannot peek — the queue is empty!",
                visualization_type="queue",
            )
            return

        yield Step(
            data=list(self.queue),
            highlights={0: "node_highlight"},
            pseudocode_line=4,
            stats={"size": len(self.queue), "operation": f"front() → {self.queue[0]}"},
            description=f"Front element is {self.queue[0]}. Queue unchanged.",
            visualization_type="queue",
        )

    def clear(self) -> Generator[Step, None, None]:
        self.queue.clear()
        yield Step(
            data=[],
            highlights={},
            pseudocode_line=-1,
            stats={"size": 0, "operation": "clear()"},
            description="Queue cleared.",
            visualization_type="queue",
        )


def register_queue() -> None:
    register(AlgorithmInfo(
        key="queue",
        name="Queue",
        category="data_structure",
        subcategory="queue",
        pseudocode=QUEUE_PSEUDO["enqueue"],
        time_complexity="O(1) per operation",
        space_complexity="O(n)",
        description="First-In First-Out (FIFO) data structure.",
        operations=["enqueue", "dequeue", "front", "clear"],
    ))
