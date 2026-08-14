"""
main_window.py
===============
Ventana principal de la aplicación.

Contiene:
  - Una barra superior con un botón "split": la parte izquierda
    ("CPU Bench") abre una URL, y la parte derecha ("Opciones") abre la
    ventana de tests personalizados.
  - Un branding central estilo "logo" (CPU) con subtítulo.
  - Un botón central "Correr Benchmark" que ejecuta el benchmark general
    y muestra una ventana de progreso mientras corre.

Para modificar textos, tamaños o la URL de CPU Bench, edita config.py.
Para modificar colores y estilos, edita theme.py.
Para modificar la lógica real del benchmark, edita benchmark_logic.py.
"""

import webbrowser

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)
from PySide6.QtCore import Qt

import config
import theme
from benchmark_controller import BenchmarkController
from options_window import OptionsWindow
from circuit_background import CircuitCorner


class SplitButton(QWidget):
    """
    Botón "split": dos mitades pegadas que se comportan como botones
    independientes. Útil para casos como "CPU Bench | Opciones" donde
    cada mitad dispara una acción distinta.

    Reutilizable: solo pásale los textos y los callbacks.
    """

    def __init__(self, left_text, right_text, on_left, on_right, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.left_button = QPushButton(left_text)
        self.left_button.setObjectName("splitLeft")
        self.right_button = QPushButton(right_text)
        self.right_button.setObjectName("splitRight")

        self.left_button.clicked.connect(on_left)
        self.right_button.clicked.connect(on_right)

        self.left_button.setStyleSheet(theme.SPLIT_LEFT_QSS)
        self.right_button.setStyleSheet(theme.SPLIT_RIGHT_QSS)

        self.left_button.setCursor(Qt.PointingHandCursor)
        self.right_button.setCursor(Qt.PointingHandCursor)

        layout.addWidget(self.left_button)
        layout.addWidget(self.right_button)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_TITLE)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setStyleSheet(theme.WINDOW_BACKGROUND_QSS)

        self.controller = BenchmarkController(parent_window=self)
        self.controller.on_started = self._on_benchmark_started
        self.controller.on_finished = self._on_benchmark_finished

        self._build_ui()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # Decoración de fondo: líneas de circuito en las esquinas,
        # colocadas primero para quedar detrás del resto del contenido.
        circuit_top = CircuitCorner(central, corner="top-right", opacity=0.25)
        circuit_bottom = CircuitCorner(central, corner="bottom-left", opacity=0.18)
        self._circuit_top = circuit_top
        self._circuit_bottom = circuit_bottom
        central.resizeEvent = self._on_central_resize

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(28, 24, 28, 28)

        # --- Barra superior con el botón split ---
        top_bar = QHBoxLayout()
        self.split_button = SplitButton(
            left_text=config.CPU_BENCH_LABEL,
            right_text=config.OPTIONS_LABEL,
            on_left=self._on_cpu_bench_clicked,
            on_right=self._on_options_clicked,
        )
        top_bar.addWidget(self.split_button)
        top_bar.addStretch()

        main_layout.addLayout(top_bar)
        main_layout.addStretch()

        # --- Centro: branding + botón principal de benchmark ---
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(6)

        brand_label = QLabel(config.BRAND_TITLE)
        brand_label.setObjectName("titleLabel")
        brand_label.setStyleSheet(theme.TITLE_LABEL_QSS)
        brand_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(brand_label)

        subtitle = QLabel(config.BRAND_SUBTITLE)
        subtitle.setObjectName("subtitleLabel")
        subtitle.setStyleSheet(theme.SUBTITLE_LABEL_QSS)
        subtitle.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(subtitle)

        center_layout.addSpacing(26)

        self.run_button = QPushButton(config.RUN_BENCHMARK_LABEL)
        self.run_button.setObjectName("primaryButton")
        self.run_button.setStyleSheet(theme.PRIMARY_BUTTON_QSS)
        self.run_button.setCursor(Qt.PointingHandCursor)
        self.run_button.clicked.connect(self._on_run_benchmark_clicked)
        center_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        # Las líneas de circuito quedan detrás de todo lo demás
        circuit_top.lower()
        circuit_bottom.lower()

    def _on_central_resize(self, event):
        # Mantiene las decoraciones de circuito cubriendo toda la ventana
        # central para que se puedan dibujar en sus esquinas respectivas.
        w, h = event.size().width(), event.size().height()
        self._circuit_top.setGeometry(0, 0, w, h)
        self._circuit_bottom.setGeometry(0, 0, w, h)

    # ------------------------------------------------------------------
    # Handlers del botón split
    # ------------------------------------------------------------------
    def _on_cpu_bench_clicked(self):
        # Placeholder: abre una URL en el navegador por defecto.
        # TODO: reemplazar config.CPU_BENCH_URL por la URL real.
        webbrowser.open(config.CPU_BENCH_URL)

    def _on_options_clicked(self):
        dialog = OptionsWindow(self)
        dialog.exec()

    # ------------------------------------------------------------------
    # Handler del botón principal "Correr Benchmark"
    # ------------------------------------------------------------------
    def _on_run_benchmark_clicked(self):
        # La orden de ejecutar y el despliegue de resultados los maneja
        # BenchmarkController (ver benchmark_controller.py).
        self.controller.run_full_benchmark()

    def _on_benchmark_started(self):
        self.run_button.setEnabled(False)

    def _on_benchmark_finished(self, result: dict):
        # El controller ya se encarga de mostrar la ventana de
        # resultados; aquí solo reaccionamos a que terminó.
        self.run_button.setEnabled(True)
