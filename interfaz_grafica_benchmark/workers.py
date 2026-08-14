"""
workers.py
==========
QThread workers que ejecutan las funciones de benchmark_logic.py en un
hilo separado, para que la interfaz no se congele mientras corre el
benchmark.

Si agregas una nueva función de benchmark en benchmark_logic.py, puedes
reutilizar estos workers o crear uno nuevo siguiendo el mismo patrón.
"""

from PySide6.QtCore import QThread, Signal
import benchmark_logic


class BenchmarkWorker(QThread):
    """Corre el benchmark general (botón principal)."""

    progress = Signal(str)   # emite mensajes de avance
    finished_ok = Signal(dict)  # emite el resultado final

    def run(self):
        result = benchmark_logic.run_full_benchmark(
            progress_callback=self.progress.emit
        )
        self.finished_ok.emit(result)


class CustomTestsWorker(QThread):
    """Corre solo los tests personalizados seleccionados en Opciones."""

    progress = Signal(str)
    finished_ok = Signal(dict)

    def __init__(self, selected_keys, parent=None):
        super().__init__(parent)
        self.selected_keys = selected_keys

    def run(self):
        result = benchmark_logic.run_custom_tests(
            self.selected_keys, progress_callback=self.progress.emit
        )
        self.finished_ok.emit(result)
