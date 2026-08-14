"""
running_dialog.py
==================
Ventana (diálogo) que se muestra mientras el benchmark se está
ejecutando. Muestra un indicador de progreso indeterminado y un mensaje
de estado que se puede ir actualizando.

Estilo visual definido en theme.py.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt
import config
import theme


class RunningDialog(QDialog):
    def __init__(self, parent=None, title=None, message=None):
        super().__init__(parent)
        self.setWindowTitle(title or config.RUNNING_TITLE)
        self.setModal(True)
        self.setFixedSize(380, 160)
        self.setStyleSheet(theme.WINDOW_BACKGROUND_QSS)
        # Sin botón de cerrar mientras corre, para evitar que el usuario
        # cierre la ventana mientras el benchmark está en progreso.
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        self.title_label = QLabel(title or config.RUNNING_TITLE)
        self.title_label.setObjectName("dialogTitleLabel")
        self.title_label.setStyleSheet(theme.dialog_title_qss(18))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.message_label = QLabel(message or config.RUNNING_MESSAGE)
        self.message_label.setObjectName("subtitleLabel")
        self.message_label.setStyleSheet(theme.SUBTITLE_LABEL_QSS)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # modo indeterminado ("va y viene")
        self.progress_bar.setStyleSheet(theme.PROGRESS_BAR_QSS)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

    def set_status(self, text: str):
        """Actualiza el mensaje mostrado (útil para reportar avance)."""
        self.message_label.setText(text)
