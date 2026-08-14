"""
circuit_background.py
======================
Widget decorativo que dibuja líneas tipo "circuito" (como en la imagen de
referencia) en una esquina de la ventana. Es puramente estético y no
afecta la lógica de la app.

Se coloca detrás de los demás widgets (como fondo) usando
`widget.lower()` o simplemente agregándolo primero en un layout con
posición absoluta.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF
import random


class CircuitCorner(QWidget):
    """
    Dibuja un patrón de líneas ortogonales con pequeños nodos circulares,
    simulando circuitería, ubicado típicamente en una esquina.

    corner: "top-right" | "bottom-right" | "top-left" | "bottom-left"
    """

    def __init__(self, parent=None, corner="top-right", opacity=0.35, seed=42):
        super().__init__(parent)
        self.corner = corner
        self.opacity = opacity
        self._rng = random.Random(seed)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color = QColor(255, 255, 255)
        color.setAlphaF(self.opacity)
        pen = QPen(color, 2)
        painter.setPen(pen)

        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        # Genera un pequeño árbol de líneas ortogonales tipo "circuito"
        # a partir de una esquina, con nodos (puntos) en las uniones.
        origin = self._corner_origin(w, h)
        self._draw_branch(painter, origin, w, h, depth=0, max_depth=4)

    def _corner_origin(self, w, h):
        if self.corner == "top-right":
            return QPointF(w, 0)
        if self.corner == "bottom-right":
            return QPointF(w, h)
        if self.corner == "top-left":
            return QPointF(0, 0)
        return QPointF(0, h)  # bottom-left

    def _draw_branch(self, painter, point, w, h, depth, max_depth):
        if depth >= max_depth:
            return

        # Dibuja un pequeño nodo circular en cada unión
        radius = 3.5
        painter.drawEllipse(point, radius, radius)

        # 1-2 segmentos ortogonales (horizontal/vertical) desde el punto
        num_segments = self._rng.choice([1, 1, 2])
        for _ in range(num_segments):
            horizontal = self._rng.choice([True, False])
            length = self._rng.uniform(min(w, h) * 0.08, min(w, h) * 0.18)
            dx_sign = -1 if self.corner.endswith("right") else 1
            dy_sign = -1 if self.corner.startswith("bottom") else 1

            if horizontal:
                new_point = QPointF(point.x() + dx_sign * length, point.y())
            else:
                new_point = QPointF(point.x(), point.y() + dy_sign * length)

            painter.drawLine(point, new_point)
            self._draw_branch(painter, new_point, w, h, depth + 1, max_depth)
