from __future__ import annotations
from dataclasses import dataclass
from PIL import Image, ImageEnhance


class ImageOperation:
    """Base class (Inheritance). All operations implement apply() (Polymorphism)."""
    def apply(self, img: Image.Image) -> Image.Image:
        raise NotImplementedError


@dataclass(frozen=True)
class BrightnessOp(ImageOperation):
    factor: float  # 1.0 = no change
    def apply(self, img: Image.Image) -> Image.Image:
        return ImageEnhance.Brightness(img).enhance(self.factor)


@dataclass(frozen=True)
class ContrastOp(ImageOperation):
    factor: float
    def apply(self, img: Image.Image) -> Image.Image:
        return ImageEnhance.Contrast(img).enhance(self.factor)


@dataclass(frozen=True)
class SaturationOp(ImageOperation):
    factor: float
    def apply(self, img: Image.Image) -> Image.Image:
        return ImageEnhance.Color(img).enhance(self.factor)


@dataclass(frozen=True)
class RotateOp(ImageOperation):
    degrees: int
    def apply(self, img: Image.Image) -> Image.Image:
        if self.degrees == 0:
            return img
        return img.rotate(self.degrees, expand=True)


@dataclass(frozen=True)
class CropPercentOp(ImageOperation):
    left_pct: float
    top_pct: float
    right_pct: float
    bottom_pct: float

    def apply(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        left = int(w * self.left_pct)
        top = int(h * self.top_pct)
        right = w - int(w * self.right_pct)
        bottom = h - int(h * self.bottom_pct)

        # keep it safe: don't allow tiny/invalid crops
        if right - left < 20 or bottom - top < 20:
            return img
        return img.crop((left, top, right, bottom))
