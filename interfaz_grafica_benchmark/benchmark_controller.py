"""
benchmark_controller.py
=========================
Punto único de control entre la interfaz y la lógica de benchmark.

Este archivo se encarga de dos cosas:

  1) DAR LA ORDEN de ejecutar el benchmark (completo o personalizado),
     lanzando el worker (QThread) correspondiente y mostrando la
     ventana de "Ejecutando...".

  2) RECIBIR los resultados (el dict que entrega benchmark_logic.py) y
     DESPLEGARLOS en pantalla.

La idea es que main_window.py y options_window.py NO necesiten saber
nada sobre workers, threads ni benchmark_logic — solo llaman a las
funciones de este archivo. Así, si el día de mañana cambias cómo se
ejecuta el benchmark o cómo se muestran los resultados, este es el
único archivo que necesitas tocar.

Uso típico:

    from benchmark_controller import BenchmarkController

    self.controller = BenchmarkController(parent_window=self)
    self.controller.run_full_benchmark()
    self.controller.run_custom_tests(["cpu", "ram"])
"""

from workers import BenchmarkWorker, CustomTestsWorker
from running_dialog import RunningDialog
from results_window import ResultsWindow


class BenchmarkController:
    """
    Orquesta la ejecución del benchmark y el despliegue de resultados.

    parent_window: la ventana (QWidget) que actúa como padre de los
    diálogos que se abren (ventana "Ejecutando..." y ventana de
    resultados). Normalmente es MainWindow o OptionsWindow.
    """

    def __init__(self, parent_window=None):
        self.parent_window = parent_window
        self._worker = None
        self._running_dialog = None

        # Callbacks opcionales que la ventana que use el controller
        # puede setear si necesita hacer algo extra (por ejemplo,
        # deshabilitar un botón mientras corre el benchmark).
        self.on_started = None          # func() -> None
        self.on_progress = None         # func(str) -> None
        self.on_finished = None         # func(dict) -> None

    # ------------------------------------------------------------------
    # 1) DAR LA ORDEN DE EJECUTAR
    # ------------------------------------------------------------------
    def run_full_benchmark(self):
        """
        Da la orden de correr el benchmark completo (botón principal
        "Correr Benchmark").
        """
        self._start_worker(BenchmarkWorker())

    def run_custom_tests(self, selected_keys):
        """
        Da la orden de correr solo los tests seleccionados.

        selected_keys: lista de strings, p.ej. ["cpu", "ram"]
        """
        self._start_worker(CustomTestsWorker(selected_keys))

    def _start_worker(self, worker):
        if self.on_started:
            self.on_started()

        self._running_dialog = RunningDialog(self.parent_window)
        self._worker = worker
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_ok.connect(self._on_finished)

        self._worker.start()
        self._running_dialog.exec()  # se cierra desde _on_finished

    # ------------------------------------------------------------------
    # 2) RECIBIR resultados
    # ------------------------------------------------------------------
    def _on_progress(self, status_text: str):
        if self._running_dialog:
            self._running_dialog.set_status(status_text)
        if self.on_progress:
            self.on_progress(status_text)

    def _on_finished(self, result: dict):
        if self._running_dialog:
            self._running_dialog.accept()
            self._running_dialog = None

        if self.on_finished:
            self.on_finished(result)

        self.display_results(result)

    # ------------------------------------------------------------------
    # 3) DESPLEGAR resultados
    # ------------------------------------------------------------------
    def display_results(self, result: dict):
        """
        Recibe un dict de resultados (formato de benchmark_logic.py) y
        lo despliega en la ventana de resultados.

        Se puede llamar también "a mano" si en algún momento quieres
        mostrar resultados que no vinieron de run_full_benchmark /
        run_custom_tests (por ejemplo, resultados guardados de una
        corrida anterior).
        """
        dialog = ResultsWindow(result, parent=self.parent_window)
        dialog.exec()
