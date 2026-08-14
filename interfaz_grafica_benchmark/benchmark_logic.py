"""
benchmark_logic.py
===================
Lógica "real" del benchmark, separada de la interfaz gráfica.

Por defecto usa native_benchmark.py: un motor 100% real que mide
CPU/RAM/disco de TU equipo en el momento (hashes/seg, MB/s de memoria,
MB/s de disco), sin depender de instalar nada aparte de
requirements.txt. "Llegar y ejecutar" de verdad: no hay datos
simulados/inventados en el flujo por defecto.

Si activas config.USE_PTS (ver config.py), además intenta correr los
test-profiles reales de Phoronix Test Suite para las categorías que
PTS sepa medir; si PTS no está instalado o un test falla, cae de
vuelta al motor nativo (nunca inventa números si puede medir algo
real).

El dict de resultados tiene siempre este formato (así results_window.py
y benchmark_analyzer.py no necesitan cambios):

    {
        "score": int,
        "cpu_score": ..., "cpu_name": ...,
        "gpu_score": ..., "gpu_name": ...,   # solo si USE_PTS y PTS lo midió
        "ram_score": ..., "ram_name": ...,
        "disk_score": ..., "disk_name": ...,
        "browser_score": ...,   # opcional
    }

Las funciones de este archivo se ejecutan dentro de un QThread (ver
workers.py), así que pueden tardar sin bloquear la interfaz.
"""

import config
import native_benchmark


def run_full_benchmark(progress_callback=None):
    """
    Ejecuta el benchmark "general" (el que dispara el botón principal
    "Correr Benchmark"): todas las categorías que el motor activo sepa
    medir de verdad.
    """
    if config.USE_PTS:
        categories = [key for key, profile in config.PTS_TEST_PROFILES.items() if profile]
    else:
        categories = list(native_benchmark.AVAILABLE_CATEGORIES)
    return get_benchmark_results(categories=categories, progress_callback=progress_callback)


def run_custom_tests(selected_keys, progress_callback=None):
    """
    Ejecuta únicamente los tests seleccionados por el usuario en la
    ventana de Opciones.

    selected_keys: lista de strings, p.ej. ["cpu", "ram"]

    Retorna: dict con las claves "<key>_score" / "<key>_name" de cada
    categoría seleccionada, p.ej.:
        {"cpu_score": 4210, "cpu_name": "AMD Ryzen 7 5800X", ...}
    """
    full_result = get_benchmark_results(categories=selected_keys, progress_callback=progress_callback)

    results = {}
    for key in selected_keys:
        for suffix in ("score", "name"):
            result_key = f"{key}_{suffix}"
            if result_key in full_result:
                results[result_key] = full_result[result_key]

    return results


def get_benchmark_results(categories=None, progress_callback=None):
    """
    Motor de benchmark. Corre las categorías pedidas y retorna el dict
    de resultados con el formato descrito arriba.

    categories: lista de keys ("cpu", "ram", "disk", y "gpu"/"browser"
        si USE_PTS está activo) o None para usar todas las disponibles.
    progress_callback: función opcional que se llama con un string para
        reportar avance en tiempo real (ver running_dialog.py).
    """
    if categories is None:
        categories = list(native_benchmark.AVAILABLE_CATEGORIES)

    if config.USE_PTS:
        pts_result = _try_pts(categories, progress_callback)
        if pts_result is not None:
            return pts_result
        # PTS activado pero no disponible / falló por completo: seguimos
        # abajo con el motor nativo para las categorías que sí sabe medir.

    native_categories = [key for key in categories if key in native_benchmark.AVAILABLE_CATEGORIES]
    skipped = [key for key in categories if key not in native_benchmark.AVAILABLE_CATEGORIES]

    if skipped and progress_callback:
        progress_callback(
            f"{', '.join(k.upper() for k in skipped)}: sin test real disponible "
            f"en el motor nativo (activa config.USE_PTS para medirlas con "
            f"Phoronix Test Suite). Se omiten, no se inventan datos."
        )

    return native_benchmark.run_benchmark(native_categories, progress_callback=progress_callback)


# ---------------------------------------------------------------------------
# Integración opcional con Phoronix Test Suite (solo si config.USE_PTS)
# ---------------------------------------------------------------------------

def _try_pts(categories, progress_callback):
    """
    Intenta correr las categorías pedidas vía Phoronix Test Suite.
    Retorna el dict de resultados si PTS está disponible, o None si no
    lo está (para que get_benchmark_results() siga con el motor nativo).
    """
    import pts_integration  # import perezoso: solo si USE_PTS está activo

    if not pts_integration.is_available():
        if progress_callback:
            progress_callback(
                "USE_PTS está activo pero no se encontró Phoronix Test Suite "
                "instalado — usando el motor nativo (real) en su lugar."
            )
        return None

    if progress_callback:
        progress_callback("Detectando hardware (phodevi, vía phoronix-test-suite system-info)...")
    hw_info = pts_integration.get_system_info()

    results = {}
    category_scores = {}

    for key in categories:
        profile = config.PTS_TEST_PROFILES.get(key)
        if not profile:
            continue

        if progress_callback:
            progress_callback(f"Ejecutando test de {key.upper()} ({profile})...")

        try:
            score, hw_name = pts_integration.run_category_benchmark(
                key, profile, hw_info, progress_callback=progress_callback,
            )
        except pts_integration.PTSBenchmarkError as exc:
            if not config.PTS_FALLBACK_TO_SIMULATION:
                raise
            if progress_callback:
                progress_callback(
                    f"Test de {key} vía PTS falló ({exc}); usando el motor "
                    f"nativo para esta categoría si es posible."
                )
            if key in native_benchmark.AVAILABLE_CATEGORIES:
                score, hw_name = native_benchmark._BENCH_FUNCS[key](progress_callback=progress_callback)
            else:
                continue

        results[f"{key}_score"] = score
        if hw_name:
            results[f"{key}_name"] = hw_name
        category_scores[key] = score

    if progress_callback:
        progress_callback("Calculando score total...")

    if category_scores:
        results["score"] = sum(category_scores.values())

    return results if results else None
