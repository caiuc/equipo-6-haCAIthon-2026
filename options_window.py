"""
options_window.py
==================
Ventana de "Opciones": permite al usuario elegir qué tests personalizados
correr (CPU, RAM, Disco, GPU, etc.).

La lista de tests disponibles se define en config.py (CUSTOM_TESTS), así
que para agregar/quitar tests personalizados no hace falta tocar este
archivo, solo config.py. El estilo visual vive en theme.py.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
import config
import theme
from benchmark_controller import BenchmarkController


class OptionsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(config.OPTIONS_WINDOW_TITLE)
        self.resize(400, 420)
        self.setStyleSheet(theme.WINDOW_BACKGROUND_QSS)

        self._checkboxes = {}  # key -> QCheckBox

        self.controller = BenchmarkController(parent_window=self)
        self.controller.on_started = self._on_tests_started
        self.controller.on_finished = self._on_tests_finished

        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel(config.OPTIONS_WINDOW_TITLE)
        title_label.setObjectName("dialogTitleLabel")
        title_label.setStyleSheet(theme.dialog_title_qss(20))
        title_label.setWordWrap(True)
        outer_layout.addWidget(title_label)

        subtitle_label = QLabel("Selecciona los tests que quieres correr:")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setStyleSheet(theme.SUBTITLE_LABEL_QSS)
        outer_layout.addWidget(subtitle_label)

        outer_layout.addSpacing(14)

        # Tarjeta translúcida que agrupa los checkboxes
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(theme.CARD_QSS)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(4)

        # Genera dinámicamente un checkbox por cada test en config.CUSTOM_TESTS
        for test in config.CUSTOM_TESTS:
            checkbox = QCheckBox(test["label"])
            checkbox.setStyleSheet(theme.CHECKBOX_QSS)
            checkbox.setToolTip(test.get("description", ""))
            checkbox.setCursor(Qt.PointingHandCursor)
            self._checkboxes[test["key"]] = checkbox
            card_layout.addWidget(checkbox)

        outer_layout.addWidget(card)
        outer_layout.addStretch()

        button_row = QHBoxLayout()
        self.run_button = QPushButton(config.RUN_CUSTOM_TESTS_LABEL)
        self.run_button.setObjectName("secondaryButton")
        self.run_button.setStyleSheet(theme.SECONDARY_BUTTON_QSS)
        self.run_button.setCursor(Qt.PointingHandCursor)
        self.run_button.clicked.connect(self._on_run_clicked)
        button_row.addStretch()
        button_row.addWidget(self.run_button)

        outer_layout.addLayout(button_row)

    def _selected_keys(self):
        return [key for key, cb in self._checkboxes.items() if cb.isChecked()]

    def _on_run_clicked(self):
        selected = self._selected_keys()
        if not selected:
            QMessageBox.information(
                self, "Nada seleccionado",
                "Selecciona al menos un test antes de correr."
            )
            return

        # La orden de ejecutar y el despliegue de resultados los maneja
        # BenchmarkController (ver benchmark_controller.py).
        self.controller.run_custom_tests(selected)

    def _on_tests_started(self):
        self.run_button.setEnabled(False)

    def _on_tests_finished(self, results: dict):
        # El controller ya se encarga de mostrar la ventana de
        # resultados (ResultsWindow); aquí solo reaccionamos a que
        # terminó.
        self.run_button.setEnabled(True)
