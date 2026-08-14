"""
results_window.py
===================
Ventana que muestra los resultados de un benchmark ya finalizado: el
score total y el detalle por categoría (CPU, GPU, RAM, disco, navegador).

Espera un dict con este formato (ver benchmark_logic.run_full_benchmark):
    {
        "score": int,
        "cpu_score": ..., "cpu_name": ...,
        "gpu_score": ..., "gpu_name": ...,
        "ram_score": ..., "ram_name": ...,
        "disk_score": ..., "disk_name": ...,
        "browser_score": ...,   # sin "_name" — es normal, no todas las
                                  categorías necesitan nombre de hardware
    }

Las categorías mostradas (y su orden/ícono/etiqueta) se definen en
config.RESULT_CATEGORIES, así que agregar una nueva categoría no
requiere tocar este archivo — solo config.py y que benchmark_logic.py
devuelva las claves correspondientes.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
import config
import theme
import benchmark_analyzer


class ResultRow(QFrame):
    """
    Una fila/tarjeta individual de resultado: ícono, nombre de la
    categoría, nombre del hardware (opcional) y el score.
    """

    def __init__(self, icon: str, label: str, hardware_name: str, score, parent=None):
        super().__init__(parent)
        self.setObjectName("resultCard")
        self.setStyleSheet(theme.RESULT_CARD_QSS)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setObjectName("resultIcon")
        icon_label.setStyleSheet(theme.RESULT_ICON_QSS)
        layout.addWidget(icon_label)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        name_label = QLabel(label)
        name_label.setObjectName("resultName")
        name_label.setStyleSheet(theme.RESULT_NAME_QSS)
        text_col.addWidget(name_label)

        if hardware_name:
            sub_label = QLabel(hardware_name)
            sub_label.setObjectName("resultSubname")
            sub_label.setStyleSheet(theme.RESULT_SUBNAME_QSS)
            sub_label.setWordWrap(True)
            text_col.addWidget(sub_label)

        layout.addLayout(text_col, stretch=1)

        score_label = QLabel(str(score))
        score_label.setObjectName("resultScore")
        score_label.setStyleSheet(theme.RESULT_SCORE_QSS)
        score_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(score_label)


class ResultsWindow(QDialog):
    def __init__(self, results: dict, parent=None):
        super().__init__(parent)
        self.results = results

        self.setWindowTitle(config.RESULTS_WINDOW_TITLE)
        self.resize(440, 560)
        self.setStyleSheet(theme.WINDOW_BACKGROUND_QSS)

        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(28, 28, 28, 24)
        outer_layout.setSpacing(4)

        # --- Score total, destacado arriba ---
        caption = QLabel("SCORE TOTAL")
        caption.setObjectName("scoreTotalCaption")
        caption.setStyleSheet(theme.SCORE_TOTAL_CAPTION_QSS)
        caption.setAlignment(Qt.AlignCenter)
        outer_layout.addWidget(caption)

        total_score = self.results.get("score", "—")
        score_label = QLabel(str(total_score))
        score_label.setObjectName("scoreTotalLabel")
        score_label.setStyleSheet(theme.SCORE_TOTAL_LABEL_QSS)
        score_label.setAlignment(Qt.AlignCenter)
        outer_layout.addWidget(score_label)

        # --- Gama del equipo, según benchmark_analyzer.py ---
        # (pesos y rangos configurables en benchmark_analyzer_config.py)
        analysis = benchmark_analyzer.analyze(self.results)
        gama_text = analysis["gama"]["label"]
        if analysis["score_was_estimated"]:
            gama_text += "  ·  score estimado"

        gama_label = QLabel(gama_text)
        gama_label.setObjectName("gamaLabel")
        gama_label.setStyleSheet(theme.SUBTITLE_LABEL_QSS)
        gama_label.setAlignment(Qt.AlignCenter)
        outer_layout.addWidget(gama_label)

        outer_layout.addSpacing(18)

        # --- Lista de categorías, dentro de un scroll por si crecen ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        for category in config.RESULT_CATEGORIES:
            key = category["key"]
            score = self.results.get(f"{key}_score")
            if score is None:
                # Si el resultado no trae esta categoría, se omite en
                # lugar de mostrar una fila vacía.
                continue
            hardware_name = self.results.get(f"{key}_name", "")

            row = ResultRow(
                icon=category.get("icon", "•"),
                label=category["label"],
                hardware_name=hardware_name,
                score=score,
            )
            scroll_layout.addWidget(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        outer_layout.addWidget(scroll, stretch=1)

        # --- Botón de cerrar ---
        button_row = QHBoxLayout()
        button_row.addStretch()
        close_button = QPushButton(config.RESULTS_CLOSE_LABEL)
        close_button.setObjectName("secondaryButton")
        close_button.setStyleSheet(theme.SECONDARY_BUTTON_QSS)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.accept)
        button_row.addWidget(close_button)

        outer_layout.addLayout(button_row)
