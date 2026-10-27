"""
Gemini AI Tutor Service for DSA Visualizer.

Provides intelligent pedagogical explanations, step-by-step reasoning,
complexity analysis, and interactive quizzing for data structures and algorithms.
Supports both online Google Gemini API (via google.genai or direct REST)
and an intelligent built-in Offline DSA Tutor fallback.
"""

from __future__ import annotations

import os
import re
import html
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from PySide6.QtCore import QObject, QThread, Signal, Slot, QSettings

# Try importing official Google GenAI SDK
try:
    from google import genai
    from google.genai import types as genai_types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

# Fallback HTTP requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class TutorMode(str, Enum):
    """Pedagogical modes for the AI Tutor."""
    TUTOR = "tutor"     # Socratic, pedagogical with intuition & analogies
    QUICK = "quick"     # Concise, high-density 2-3 sentence overview
    QUIZ = "quiz"       # Interactive DSA quiz questions & feedback
    CODE = "code"       # Deep-dive into code, invariants & edge cases


@dataclass
class VisualizerContext:
    """Current live state of the DSA visualizer."""
    algo_key: str = ""
    algo_name: str = ""
    category: str = ""
    subcategory: str = ""
    description: str = ""
    time_complexity: str = ""
    space_complexity: str = ""
    pseudocode: list[str] = field(default_factory=list)
    question: str = ""
    
    # Live execution state
    current_input: Any = None
    target: Any = None
    step_index: int = 0
    total_steps: int = 0
    current_data: Any = None
    highlights: dict = field(default_factory=dict)
    active_pseudo_line: int = -1
    step_description: str = ""
    stats: dict = field(default_factory=dict)
    output: Any = None


def md_to_html(text: str) -> str:
    """Convert Markdown to clean, elegant HTML compatible with QTextBrowser."""
    # Escape basic HTML
    text = html.escape(text)

    # Multi-line code blocks: ```lang ... ```
    def _code_block_repl(m):
        code = m.group(2).strip()
        lang = (m.group(1) or "").strip().lower()
        header = f'<div style="color: #62665F; font-size: 10px; margin-bottom: 4px; font-weight: 600; text-transform: uppercase;">{lang}</div>' if lang else ""
        return (
            f'<div style="background-color: #F8F7F2; border: 1px solid #E4E0D6; border-radius: 6px; '
            f'padding: 8px 10px; margin: 6px 0; font-family: \'Cascadia Code\', \'Consolas\', \'JetBrains Mono\', monospace; '
            f'font-size: 11px; color: #343A40; line-height: 1.4;">'
            f'{header}<pre style="margin: 0; white-space: pre-wrap; font-family: inherit;">{code}</pre></div>'
        )
    text = re.sub(r'```(\w+)?\n([\s\S]*?)```', _code_block_repl, text)

    # Inline code: `code`
    text = re.sub(
        r'`([^`]+)`',
        r'<code style="background-color: #F0EEE7; color: #343A40; border: 1px solid #E4E0D6; padding: 1px 5px; border-radius: 4px; font-family: \'Cascadia Code\', \'Consolas\', monospace; font-size: 11px;">\1</code>',
        text
    )

    # Blockquotes: > quote
    def _quote_repl(m):
        content = m.group(1).strip()
        return (
            f'<div style="background-color: #F8F7F2; border-left: 3px solid #34785B; '
            f'padding: 6px 10px; margin: 6px 0; color: #62665F; font-size: 11px; border-radius: 0 4px 4px 0; font-family: \'Segoe UI\', sans-serif;">'
            f'{content}</div>'
        )
    text = re.sub(r'^&gt;\s*(.*?)$', _quote_repl, text, flags=re.MULTILINE)

    # Bold and italics
    text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'<b style="color: #292B26;"><i>\1</i></b>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b style="color: #292B26;">\1</b>', text)
    text = re.sub(r'\*([^*]+)\*', r'<i style="color: #252822;">\1</i>', text)

    # Headings
    text = re.sub(r'^### (.*?)$', r'<h4 style="color: #292B26; margin: 8px 0 3px 0; font-size: 13px; font-weight: 600; font-family: \'Segoe UI\', sans-serif;">\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h3 style="color: #292B26; margin: 10px 0 4px 0; font-size: 14px; font-weight: 600; font-family: \'Segoe UI\', sans-serif;">\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h2 style="color: #292B26; margin: 12px 0 6px 0; font-size: 15px; font-weight: 600; font-family: \'Segoe UI\', sans-serif;">\1</h2>', text, flags=re.MULTILINE)

    # Lists
    lines = text.split('\n')
    in_list = False
    list_type = "ul"
    formatted_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('• ') or stripped.startswith('- ') or stripped.startswith('* '):
            item = stripped[2:]
            if not in_list:
                formatted_lines.append('<ul style="margin: 4px 0 4px 16px; padding-left: 4px;">')
                in_list = True
                list_type = "ul"
            formatted_lines.append(f'<li style="margin-bottom: 2px; color: #252822; font-family: \'Segoe UI\', sans-serif;">{item}</li>')
        elif re.match(r'^\d+\.\s+', stripped):
            item = re.sub(r'^\d+\.\s+', '', stripped)
            if not in_list:
                formatted_lines.append('<ol style="margin: 4px 0 4px 16px; padding-left: 4px;">')
                in_list = True
                list_type = "ol"
            formatted_lines.append(f'<li style="margin-bottom: 2px; color: #252822; font-family: \'Segoe UI\', sans-serif;">{item}</li>')
        else:
            if in_list:
                formatted_lines.append(f'</{list_type}>')
                in_list = False
            formatted_lines.append(line)
    if in_list:
        formatted_lines.append(f'</{list_type}>')
    text = '\n'.join(formatted_lines)

    # Linebreaks
    text = text.replace('\n\n', '<br/><br/>')
    text = text.replace('\n', '<br/>')
    return text


class _Worker(QObject):
    """Background worker for non-blocking Gemini API calls."""
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, task_func: Callable[[], str]):
        super().__init__()
        self._task_func = task_func

    @Slot()
    def run(self):
        try:
            result = self._task_func()
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))


class GeminiTutor(QObject):
    """
    Core AI Tutor Service.
    
    Manages API key, visualizer context, chat history, and prompt synthesis.
    Dispatches generation requests asynchronously so the visualizer never stutters.
    """

    response_ready = Signal(str)            # Emitted when tutor response is ready
    error_occurred = Signal(str)            # Emitted on error
    status_changed = Signal(str, bool)      # (status_message, is_online)
    step_insight_ready = Signal(str)        # Emitted for automatic step insights

    DEFAULT_MODEL = "gemini-3-flash-preview"
    FALLBACK_MODELS = [
        "gemini-flash-latest",
        "gemini-3.1-pro-preview",
        "gemini-pro-latest",
        "gemini-2.5-flash",
    ]

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings = QSettings("DSAVisualizer", "Gemini")
        self._api_key = self._load_api_key()
        self._mode: TutorMode = TutorMode.TUTOR
        self._context = VisualizerContext()
        self._history: list[dict[str, str]] = []  # list of {"role": "user"|"model", "text": "..."}
        self._thread: QThread | None = None
        self._worker: _Worker | None = None
        self._client: Any = None
        self._active_model: str = self.DEFAULT_MODEL
        self._init_client()

    # ── Key Management ────────────────────────────────────────────────
    def _load_api_key(self) -> str:
        """Load API key from QSettings, environment variable, or .env file."""
        # 1. QSettings
        key = self._settings.value("api_key", "")
        if key:
            return str(key).strip()
        
        # 2. Environment variable
        key = os.environ.get("GEMINI_API_KEY", "")
        if key:
            return key.strip()

        # 3. Local .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass

        return ""

    def get_api_key(self) -> str:
        return self._api_key

    def set_api_key(self, key: str, persist: bool = True) -> None:
        """Set a new Gemini API key and reinitialize the client."""
        self._api_key = key.strip()
        if persist:
            self._settings.setValue("api_key", self._api_key)
        self._init_client()

    def clear_api_key(self) -> None:
        """Clear the stored Gemini API key."""
        self._api_key = ""
        self._settings.remove("api_key")
        self._client = None
        self.status_changed.emit("Offline Tutor Mode", False)

    def is_online(self) -> bool:
        """Return True if a Gemini API key is configured."""
        return bool(self._api_key)

    def _init_client(self) -> None:
        """Initialize Google GenAI client if key is available."""
        if not self._api_key:
            self._client = None
            self.status_changed.emit("Offline Tutor Mode", False)
            return

        if HAS_GENAI_SDK:
            try:
                self._client = genai.Client(api_key=self._api_key)
                self.status_changed.emit(f"Connected ({self.DEFAULT_MODEL})", True)
                return
            except Exception:
                pass
        
        # Fallback to direct REST mode if SDK init failed or not present
        if HAS_REQUESTS:
            self._client = "REST"
            self.status_changed.emit(f"Connected (REST)", True)
        else:
            self._client = None
            self.status_changed.emit("Offline Tutor Mode", False)

    # ── Mode & Context ────────────────────────────────────────────────
    @property
    def mode(self) -> TutorMode:
        return self._mode

    def set_mode(self, mode: TutorMode) -> None:
        self._mode = mode

    def update_context(self, **kwargs) -> None:
        """Update the visualizer context with new values."""
        for k, v in kwargs.items():
            if hasattr(self._context, k):
                setattr(self._context, k, v)

    def clear_history(self) -> None:
        self._history.clear()

    # ── Test Connection ───────────────────────────────────────────────
    def test_key_connection(self, key: str) -> tuple[bool, str]:
        """Synchronously test if an API key is valid."""
        if not key:
            return False, "API key cannot be empty."

        models_to_test = [self.DEFAULT_MODEL] + self.FALLBACK_MODELS

        # Test using SDK
        if HAS_GENAI_SDK:
            try:
                test_client = genai.Client(api_key=key)
                for mod in models_to_test:
                    try:
                        resp = test_client.models.generate_content(
                            model=mod,
                            contents="Say 'OK' in 1 word.",
                        )
                        if resp and resp.text:
                            self._active_model = mod
                            return True, f"Successfully connected to {mod}!"
                    except Exception:
                        continue
            except Exception as e:
                pass

        # Test using REST
        if HAS_REQUESTS:
            for mod in models_to_test:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": "Say OK in one word."}]}]}
                    resp = requests.post(url, json=payload, timeout=8)
                    if resp.status_code == 200:
                        self._active_model = mod
                        return True, f"Successfully connected to Gemini API ({mod})!"
                except Exception:
                    continue

        return False, "Could not connect to Gemini API with this key. Check internet connection and key permissions."

    # ── Prompt Synthesis ──────────────────────────────────────────────
    def _build_system_instruction(self) -> str:
        """Build the tailored system instruction encouraging concise, natural explanations."""
        return (
            "You are a helpful, clear, and student-friendly Computer Science DSA AI Tutor "
            "embedded in an interactive algorithm visualizer.\n\n"
            "Response Guidelines:\n"
            "- Answer the student's question directly without repetitive introductions, generic conclusions, or boilerplate summaries.\n"
            "- Use simple, natural language.\n"
            "- Prefer 2 to 5 short sentences by default. Keep answers concise, focused, and immediately useful.\n"
            "- Use bullet points only when they genuinely improve clarity.\n"
            "- Include code or pseudocode snippets only when directly needed.\n"
            "- When explaining a step or operation, ground your answer in the actual visualization state (elements, comparisons, swaps, partition boundaries, or active line).\n"
            "- Expand with deeper analysis only when the user asks for more detail."
        )

    def _build_context_prompt(self, user_question: str) -> str:
        """Assemble current visualizer state into a structured context for Gemini."""
        ctx = self._context
        lines = [f"[DSA VISUALIZER LIVE STATE]"]
        if ctx.algo_name:
            lines.append(f"Algorithm: {ctx.algo_name} ({ctx.category}" + (f" / {ctx.subcategory}" if ctx.subcategory else "") + ")")
        if ctx.time_complexity:
            lines.append(f"Time Complexity: {ctx.time_complexity}")
        if ctx.space_complexity:
            lines.append(f"Space Complexity: {ctx.space_complexity}")
        if ctx.question:
            lines.append(f"Problem: {ctx.question}")
        if ctx.current_input is not None:
            lines.append(f"Initial Input: {ctx.current_input}")
        if ctx.target is not None:
            lines.append(f"Target Search Value: {ctx.target}")
        if ctx.total_steps > 0:
            lines.append(f"Execution Progress: Step {ctx.step_index + 1} of {ctx.total_steps}")
        if ctx.current_data is not None:
            lines.append(f"Current State Data: {ctx.current_data}")
        if ctx.highlights:
            lines.append(f"Current Element Highlights: {ctx.highlights}")
        if ctx.step_description:
            lines.append(f"Current Step Action: {ctx.step_description}")
        if ctx.stats:
            lines.append(f"Live Statistics: {ctx.stats}")
        if ctx.pseudocode:
            lines.append("Pseudocode:")
            for idx, pline in enumerate(ctx.pseudocode):
                prefix = "  👉 [ACTIVE] " if idx == ctx.active_pseudo_line else "     "
                lines.append(f"{prefix}{idx + 1}: {pline}")

        lines.append("\n[USER QUESTION / REQUEST]")
        lines.append(user_question)
        return "\n".join(lines)

    # ── Asynchronous Request Dispatcher ───────────────────────────────
    def ask(self, user_question: str) -> None:
        """Submit a question to the AI Tutor asynchronously."""
        # Record user message in history
        self._history.append({"role": "user", "text": user_question})

        if not self.is_online():
            # Use offline intelligent tutor fallback
            offline_answer = self._generate_offline_response(user_question)
            self._history.append({"role": "model", "text": offline_answer})
            self.response_ready.emit(offline_answer)
            return

        # Prepare context and system instruction
        system_instruction = self._build_system_instruction()
        full_prompt = self._build_context_prompt(user_question)

        def _call_gemini() -> str:
            models_to_try = [self._active_model] + [
                m for m in [self.DEFAULT_MODEL] + self.FALLBACK_MODELS if m != self._active_model
            ]
            last_err = None

            # 1. Try google.genai SDK
            if HAS_GENAI_SDK and isinstance(self._client, genai.Client):
                chat_contents = []
                recent_history = self._history[-6:-1]
                for msg in recent_history:
                    chat_contents.append(f"{msg['role'].upper()}: {msg['text']}")

                full_turn_prompt = full_prompt
                if chat_contents:
                    full_turn_prompt = "Previous conversation:\n" + "\n".join(chat_contents) + "\n\n" + full_prompt

                config = genai_types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )

                for mod in models_to_try:
                    try:
                        response = self._client.models.generate_content(
                            model=mod,
                            contents=full_turn_prompt,
                            config=config,
                        )
                        if response and response.text:
                            self._active_model = mod
                            return response.text
                    except Exception as sdk_err:
                        last_err = sdk_err
                        continue

            # 2. Try REST API with requests or urllib
            for mod in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={self._api_key}"
                payload = {
                    "system_instruction": {"parts": [{"text": system_instruction}]},
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"temperature": 0.7}
                }
                if HAS_REQUESTS:
                    try:
                        resp = requests.post(url, json=payload, timeout=20)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                if parts and "text" in parts[0]:
                                    self._active_model = mod
                                    return parts[0]["text"]
                        elif resp.status_code == 429:
                            raise RuntimeError("Gemini API rate limit reached. Please wait a few seconds.")
                    except Exception as req_err:
                        last_err = req_err
                        continue

            if last_err:
                raise RuntimeError(str(last_err))
            raise RuntimeError("Gemini connection is not configured.")

        # Execute in background thread so GUI never hangs
        self._thread = QThread()
        self._worker = _Worker(_call_gemini)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_worker_success)
        self._worker.error.connect(self._on_worker_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    @Slot(str)
    def _on_worker_success(self, text: str) -> None:
        self._history.append({"role": "model", "text": text})
        self.response_ready.emit(text)

    @Slot(str)
    def _on_worker_error(self, err_msg: str) -> None:
        # Fallback to offline tutor if online failed
        fallback = self._generate_offline_response(self._history[-1]["text"] if self._history else "")
        notice = f"> *Connection issue. Displaying offline answer:*\n\n" + fallback
        self._history.append({"role": "model", "text": notice})
        self.response_ready.emit(notice)

    # ── Live Step Insight ─────────────────────────────────────────────
    def generate_step_insight(self) -> None:
        """Generate a brief pedagogical commentary for the current step."""
        ctx = self._context
        if not ctx.algo_name or ctx.total_steps <= 0:
            return

        insight = self._generate_offline_step_insight()
        self.step_insight_ready.emit(insight)

    # ── Comprehensive Offline DSA Tutor Engine ────────────────────────
    def _generate_offline_step_insight(self) -> str:
        """Synthesize a live step insight using current step highlights and metadata."""
        ctx = self._context
        step_num = ctx.step_index + 1
        desc = ctx.step_description or "Executing algorithm step."

        # Check highlight semantics
        h_types = {}
        for idx, col in ctx.highlights.items():
            h_types.setdefault(col, []).append(str(idx))

        details = []
        if "comparing" in h_types:
            details.append(f"comparing index {', '.join(h_types['comparing'])}")
        if "swapping" in h_types:
            details.append(f"swapping index {', '.join(h_types['swapping'])}")
        if "sorted" in h_types:
            details.append(f"sorted at index {', '.join(h_types['sorted'])}")
        if "mid" in h_types:
            details.append(f"midpoint index {', '.join(h_types['mid'])}")

        meta = f" ({'; '.join(details)})" if details else ""
        return f"**Step {step_num}/{ctx.total_steps}:** {desc}{meta}"

    def _generate_offline_response(self, question: str) -> str:
        """
        Intelligent offline DSA tutor rule-engine.
        Provides concise, natural 2-4 sentence student-friendly explanations.
        """
        q = question.lower().strip()
        ctx = self._context
        name = ctx.algo_name or "Algorithm"

        # 1. Step explanation request ("Explain this step")
        if any(w in q for w in ["step", "why did it swap", "what is happening", "current step", "explain this step"]):
            step_text = self._generate_offline_step_insight()
            if ctx.total_steps > 0:
                return (
                    f"{step_text}\n\n"
                    f"{name} examines elements to verify their relative ordering. "
                    f"If an inversion is found, items are swapped or shifted so that the target partition progresses."
                )
            return f"Run or step forward through **{name}** on the canvas, and I will explain each operation as it executes."

        # 2. Complexity inquiry ("Why is this O(n²)?", "complexity", "big-o")
        if any(w in q for w in ["complexity", "time complexity", "space complexity", "big o", "big-o", "o(n", "o(log", "why is this"]):
            tc = ctx.time_complexity or "O(n²)"
            sc = ctx.space_complexity or "O(1)"
            if "bubble" in name.lower() or "selection" in name.lower() or "insertion" in name.lower():
                return (
                    f"**{name}** has a time complexity of **{tc}** and auxiliary space of **{sc}**.\n\n"
                    f"The nested loops compare pairs of elements across the dataset, requiring roughly n(n - 1) / 2 comparisons in the worst case. "
                    f"Space is {sc} because elements are reordered in place without additional arrays."
                )
            elif "binary" in name.lower():
                return (
                    f"**{name}** runs in **{tc}** time with **{sc}** space.\n\n"
                    f"Each comparison halves the remaining search range, requiring at most log₂(n) steps to find the target or determine it is absent."
                )
            elif "merge" in name.lower():
                return (
                    f"**{name}** guarantees **{tc}** time across all cases with **{sc}** auxiliary space.\n\n"
                    f"The array is split log(n) times and merged in linear time O(n) per level, trading extra memory for optimal guaranteed speed."
                )
            elif "quick" in name.lower():
                return (
                    f"**{name}** runs in **{tc}** average time with **{sc}** space.\n\n"
                    f"Partitioning around a pivot takes linear time per level, achieving logarithmic recursion depth with well-distributed pivots."
                )
            return (
                f"**{name}** runs in **{tc}** time with **{sc}** auxiliary space. "
                f"Operations scale proportionally to input size according to its partitioning and traversal strategy."
            )

        # 3. Compare algorithms ("Compare algorithms")
        if any(w in q for w in ["compare", "alternative", "vs", "difference"]):
            if "sort" in name.lower():
                tc = ctx.time_complexity or "O(n²)"
                return (
                    f"**{name}** ({tc}) is simple to conceptualize and requires O(1) extra space, making it great for teaching and small lists.\n\n"
                    f"For large production datasets, **Merge Sort** and **Quick Sort** are preferred because their O(n log n) efficiency scales much better."
                )
            elif "search" in name.lower():
                return (
                    f"**Linear Search** checks every element in O(n) time on any list, whereas **Binary Search** requires a sorted array but finds targets in fast O(log n) time."
                )
            return f"**{name}** trades time and memory characteristics against alternative data structures to optimize operations for specific access patterns."

        # 4. Code / implementation request
        if any(w in q for w in ["code", "python", "implementation", "pseudocode"]):
            pseudo = "\n".join(ctx.pseudocode) if ctx.pseudocode else f"# {name} implementation"
            return f"Here is the standard implementation for **{name}**:\n\n```python\n{pseudo}\n```"

        # 5. Quiz request
        if any(w in q for w in ["quiz", "test me", "question"]):
            if "bubble" in name.lower():
                return (
                    f"**Quick Check: Bubble Sort**\n\n"
                    f"After the first complete pass of Bubble Sort, which element is guaranteed to be in its final sorted position?"
                )
            elif "binary" in name.lower():
                return (
                    f"**Quick Check: Binary Search**\n\n"
                    f"What essential property must the array satisfy before Binary Search can be applied?"
                )
            return f"**Quick Check: {name}**\n\nWhat is the worst-case time complexity of {name}, and when does it occur?"

        # 6. Concise algorithm overview
        algo_overviews = {
            "bubble_sort": (
                "**Bubble Sort** repeatedly compares adjacent items and swaps them if out of order. "
                "With each pass, the largest remaining unsorted value bubbles up to its final position at the end. "
                "It runs in **O(n²)** average time and uses **O(1)** auxiliary memory."
            ),
            "selection_sort": (
                "**Selection Sort** scans the unsorted portion of the array to find the minimum element, "
                "then swaps it into place at the start of the unsorted segment. "
                "It performs at most n-1 swaps and runs in **O(n²)** time with **O(1)** memory."
            ),
            "insertion_sort": (
                "**Insertion Sort** constructs a sorted array one element at a time by inserting each item "
                "into its correct location among earlier sorted items. "
                "It runs in adaptive **O(n)** time on sorted input and **O(n²)** in the worst case."
            ),
            "merge_sort": (
                "**Merge Sort** divides the array into halves recursively, then merges the sorted halves back together in linear time. "
                "It guarantees **O(n log n)** performance in all cases while using **O(n)** auxiliary space."
            ),
            "quick_sort": (
                "**Quick Sort** partitions the array around a chosen pivot, placing smaller elements to the left and larger ones to the right. "
                "It sorts partitions recursively, achieving **O(n log n)** average time with in-place operations."
            ),
            "binary_search": (
                "**Binary Search** finds target values in a sorted array by repeatedly dividing the search interval in half. "
                "Each comparison eliminates half the remaining items, achieving fast **O(log n)** lookup time."
            ),
        }

        return algo_overviews.get(ctx.algo_key, (
            f"**{name}** is active in the visualizer. "
            f"It runs in **{ctx.time_complexity or 'O(n²)'}** time with **{ctx.space_complexity or 'O(1)'}** space. "
            f"Ask a question or step through the animation to explore its behavior."
        ))
