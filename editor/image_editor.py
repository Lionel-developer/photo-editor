from __future__ import annotations
from dataclasses import dataclass
from PIL import Image

from editor.operations import (
    ImageOperation, BrightnessOp, ContrastOp, SaturationOp, RotateOp, CropPercentOp
)
from editor.undo_stack import UndoStack


@dataclass
class EditParams:
    brightness: float = 1.0
    contrast: float = 1.0
    saturation: float = 1.0
    rotate_deg: int = 0
    crop_left_pct: float = 0.0
    crop_top_pct: float = 0.0
    crop_right_pct: float = 0.0
    crop_bottom_pct: float = 0.0


class ImageEditor:
    """
    Encapsulates editing state + operations.
    UI calls set_params() and render().
    """
    def __init__(self) -> None:
        self._original: Image.Image | None = None
        self._current: Image.Image | None = None
        self._params = EditParams()
        self._undo = UndoStack()

    def has_image(self) -> bool:
        return self._original is not None

    def load(self, path: str) -> None:
        img = Image.open(path).convert("RGBA")
        self._original = img
        self._current = img.copy()
        self._params = EditParams()
        self._undo.clear()

    def get_current(self) -> Image.Image | None:
        return self._current

    def set_params(self, params: EditParams) -> None:
        self._params = params

    def reset(self) -> None:
        if self._original is None:
            return
        self._undo.push(self._current or self._original)
        self._current = self._original.copy()
        self._params = EditParams()

    def undo(self) -> None:
        prev = self._undo.pop()
        if prev is not None:
            self._current = prev

    def render(self) -> None:

        if self._original is None:
            return

        self._undo.push(self._current or self._original)

        ops: list[ImageOperation] = [
            CropPercentOp(
                self._params.crop_left_pct,
                self._params.crop_top_pct,
                self._params.crop_right_pct,
                self._params.crop_bottom_pct,
            ),
            BrightnessOp(self._params.brightness),
            ContrastOp(self._params.contrast),
            SaturationOp(self._params.saturation),
            RotateOp(self._params.rotate_deg),
        ]

        img = self._original.copy()
        for op in ops:
            img = op.apply(img)

        self._current = img

    def save_as(self, path: str) -> None:
        if self._current is None:
            raise ValueError("No image to save")

        if path.lower().endswith((".jpg", ".jpeg")):
            self._current.convert("RGB").save(path, quality=95)
        else:
            self._current.save(path)
