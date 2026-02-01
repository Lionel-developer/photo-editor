from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QSlider, QMessageBox,
    QGroupBox, QFormLayout, QSizePolicy
)
from PIL import Image

from editor.image_editor import ImageEditor, EditParams


def pil_to_qpixmap(img: Image.Image) -> QPixmap:
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Photo Editor (Python)")
        self.resize(1100, 700)

        self.editor = ImageEditor()
        self._block_updates = False

        root = QHBoxLayout(self)

        # --- PREVIEW ---
        self.preview = QLabel("Open an image to start")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet(
            "background:#222; color:#ddd; border-radius:8px; padding:10px;"
        )

        # CRITICAL FIX: prevents infinite growth when setting pixmaps
        self.preview.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.preview.setMinimumSize(400, 400)

        root.addWidget(self.preview, 3)

        # --- CONTROLS ---
        panel = QVBoxLayout()
        root.addLayout(panel, 1)

        btn_row = QHBoxLayout()
        self.btn_open = QPushButton("Open")
        self.btn_save = QPushButton("Save As…")
        self.btn_reset = QPushButton("Reset")
        self.btn_undo = QPushButton("Undo (1-step)")
        btn_row.addWidget(self.btn_open)
        btn_row.addWidget(self.btn_save)
        panel.addLayout(btn_row)
        panel.addWidget(self.btn_reset)
        panel.addWidget(self.btn_undo)

        # --- ADJUSTMENTS ---
        adj_box = QGroupBox("Adjustments")
        adj_form = QFormLayout(adj_box)

        w_bri, self.s_brightness, _ = self._labeled_slider(0, 200, 100, "%")
        w_con, self.s_contrast, _ = self._labeled_slider(0, 200, 100, "%")
        w_sat, self.s_saturation, _ = self._labeled_slider(0, 200, 100, "%")
        w_rot, self.s_rotate, _ = self._labeled_slider(-180, 180, 0, "°")

        adj_form.addRow("Brightness", w_bri)
        adj_form.addRow("Contrast", w_con)
        adj_form.addRow("Saturation", w_sat)
        adj_form.addRow("Rotate", w_rot)

        panel.addWidget(adj_box)

        # --- CROP ---
        crop_box = QGroupBox("Crop (percent from each side)")
        crop_form = QFormLayout(crop_box)

        w_cl, self.s_crop_l, _ = self._labeled_slider(0, 40, 0, "%")
        w_ct, self.s_crop_t, _ = self._labeled_slider(0, 40, 0, "%")
        w_cr, self.s_crop_r, _ = self._labeled_slider(0, 40, 0, "%")
        w_cb, self.s_crop_b, _ = self._labeled_slider(0, 40, 0, "%")

        crop_form.addRow("Left", w_cl)
        crop_form.addRow("Top", w_ct)
        crop_form.addRow("Right", w_cr)
        crop_form.addRow("Bottom", w_cb)

        panel.addWidget(crop_box)

        panel.addStretch(1)

        # --- SIGNALS ---
        self.btn_open.clicked.connect(self.open_image)
        self.btn_save.clicked.connect(self.save_as)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_undo.clicked.connect(self.undo)

        for s in [
            self.s_brightness, self.s_contrast, self.s_saturation, self.s_rotate,
            self.s_crop_l, self.s_crop_t, self.s_crop_r, self.s_crop_b
        ]:
            s.valueChanged.connect(self.on_controls_changed)

        self._set_enabled(False)

    def _labeled_slider(self, mn: int, mx: int, val: int, suffix: str = "%"):
        """
        Returns (container_widget, slider, value_label)
        Example: 70% or -45°
        """
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(mn)
        slider.setMaximum(mx)
        slider.setValue(val)

        value_label = QLabel(f"{val}{suffix}")
        value_label.setFixedWidth(60)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        slider.valueChanged.connect(lambda v: value_label.setText(f"{v}{suffix}"))

        row.addWidget(slider, 1)
        row.addWidget(value_label, 0)
        return container, slider, value_label

    def _set_enabled(self, enabled: bool) -> None:
        self.btn_save.setEnabled(enabled)
        self.btn_reset.setEnabled(enabled)
        self.btn_undo.setEnabled(enabled)
        for s in [
            self.s_brightness, self.s_contrast, self.s_saturation, self.s_rotate,
            self.s_crop_l, self.s_crop_t, self.s_crop_r, self.s_crop_b
        ]:
            s.setEnabled(enabled)

    def open_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not path:
            return
        try:
            self.editor.load(path)
            self._set_enabled(True)
            self._reset_sliders_to_defaults()
            self.render_preview()
        except Exception as e:
            QMessageBox.critical(self, "Open failed", str(e))

    def _reset_sliders_to_defaults(self) -> None:
        self._block_updates = True
        try:
            self.s_brightness.setValue(100)
            self.s_contrast.setValue(100)
            self.s_saturation.setValue(100)
            self.s_rotate.setValue(0)
            self.s_crop_l.setValue(0)
            self.s_crop_t.setValue(0)
            self.s_crop_r.setValue(0)
            self.s_crop_b.setValue(0)
        finally:
            self._block_updates = False

    def on_controls_changed(self) -> None:
        if self._block_updates or not self.editor.has_image():
            return

        params = EditParams(
            brightness=self.s_brightness.value() / 100.0,
            contrast=self.s_contrast.value() / 100.0,
            saturation=self.s_saturation.value() / 100.0,
            rotate_deg=int(self.s_rotate.value()),
            crop_left_pct=self.s_crop_l.value() / 100.0,
            crop_top_pct=self.s_crop_t.value() / 100.0,
            crop_right_pct=self.s_crop_r.value() / 100.0,
            crop_bottom_pct=self.s_crop_b.value() / 100.0,
        )
        self.editor.set_params(params)
        self.editor.render()
        self.render_preview()

    def render_preview(self) -> None:
        img = self.editor.get_current()
        if img is None:
            return
        pix = pil_to_qpixmap(img)

        # scale to contentsRect (prevents resize feedback loop)
        target = self.preview.contentsRect().size()
        scaled = pix.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview.setPixmap(scaled)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.editor.has_image():
            self.render_preview()

    def save_as(self) -> None:
        if not self.editor.has_image():
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Image As", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;WEBP (*.webp)"
        )
        if not path:
            return
        try:
            self.editor.save_as(path)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def reset(self) -> None:
        if not self.editor.has_image():
            return
        self.editor.reset()
        self._reset_sliders_to_defaults()
        self.render_preview()

    def undo(self) -> None:
        if not self.editor.has_image():
            return
        self.editor.undo()
        self.render_preview()
