from __future__ import annotations
from PIL import Image


class UndoStack:
    """Very simple 1-step undo (enough for requirements)."""
    def __init__(self) -> None:
        self._prev: Image.Image | None = None

    def push(self, img: Image.Image) -> None:
        self._prev = img.copy()

    def pop(self) -> Image.Image | None:
        if self._prev is None:
            return None
        out = self._prev
        self._prev = None
        return out

    def clear(self) -> None:
        self._prev = None
