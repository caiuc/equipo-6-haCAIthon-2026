"""
benchmark_logic.py
===================
Aquí vive la lógica "real" del benchmark, separada de la interfaz gráfica.

Se asume que existe una función `get_benchmark_results()` (el motor real
de benchmark) que hace todo el trabajo pesado y retorna un dict con este
formato exacto:

    {
        "score": int,
        "cpu_score": ..., "cpu_name": ...,
        "gpu_score": ..., "gpu_name": ...,
        "ram_score": ..., "ram_name": ...,
        "disk_score": ..., "disk_name": ...,
        "browser_score": ...,
    }

Ahora mismo `get_benchmark_results()` es solo un placeholder al final de
este archivo. Cuando tengas el motor real, reemplaza SOLO esa función
(o cambia el import de abajo por el de tu módulo real) — no deberías
necesitar tocar main_window.py, workers.py ni las ventanas para que todo
siga funcionando, ya que las claves ya coinciden con lo que espera
results_window.py.

Las funciones de este archivo se ejecutan dentro de un QThread (ver
workers.py), así que pueden tardar sin bloquear la interfaz.
"""

# Si tu motor de benchmark real vive en otro módulo/paquete, puedes
# reemplazar la línea de abajo por algo como:
#   from mi_motor_de_benchmark import get_benchmark_results
# y borrar la implementación placeholder que está al final del archivo.


def run_full_benchmark(progress_callback=None):
    """
    Ejecuta el benchmark "general" (el que dispara el botón principal
    "Correr Benchmark").

    progress_callback: función opcional que se puede llamar con un string
    para reportar avances (por ejemplo progress_callback("Probando CPU...")).

    Retorna: el dict que entrega get_benchmark_results(), con el formato
    descrito arriba (y en el docstring del módulo).
    """
    if progress_callback:
        progress_callback("Ejecutando benchmark...")

    result = get_benchmark_results()

    if progress_callback:
        progress_callback("Finalizando...")

    return result


def run_custom_tests(selected_keys, progress_callback=None):
    """
    Ejecuta únicamente los tests seleccionados por el usuario en la
    ventana de Opciones.

    selected_keys: lista de strings, p.ej. ["cpu", "ram"]
    progress_callback: función opcional para reportar avance.

    Como get_benchmark_results() ya corre todo el benchmark de una vez,
    aquí simplemente lo llamamos y nos quedamos solo con las claves
    (score/name) de las categorías seleccionadas.

    Retorna: dict con las claves "<key>_score" / "<key>_name" de cada
    categoría seleccionada, p.ej.:
        {"cpu_score": 4210, "cpu_name": "AMD Ryzen 7 5800X", ...}
    """
    if progress_callback:
        progress_callback("Ejecutando tests seleccionados...")

    full_result = get_benchmark_results()

    if progress_callback:
        progress_callback("Finalizando...")

    results = {}
    for key in selected_keys:
        score_key, name_key = f"{key}_score", f"{key}_name"
        if score_key in full_result:
            results[score_key] = full_result[score_key]
        if name_key in full_result:
            results[name_key] = full_result[name_key]

    return results


def get_benchmark_results():
    """
    PLACEHOLDER — esta es la función que representa tu motor de benchmark
    real. Debe retornar un dict con exactamente este formato:

        {
            "score": int,
            "cpu_score": ..., "cpu_name": ...,
            "gpu_score": ..., "gpu_name": ...,
            "ram_score": ..., "ram_name": ...,
            "disk_score": ..., "disk_name": ...,
            "browser_score": ...,
        }

    TODO: reemplaza el cuerpo de esta función por la llamada real a tu
    motor de benchmark (o elimínala y en su lugar importa la real arriba
    del archivo, con el mismo nombre `get_benchmark_results`).
    """
    return {
        "score": 8734,
        "cpu_score": 4210,
        "cpu_name": "AMD Ryzen 7 5800X",
        "gpu_score": 6120,
        "gpu_name": "NVIDIA RTX 3070",
        "ram_score": 3890,
        "ram_name": "16 GB DDR4 3200MHz",
        "disk_score": 5310,
        "disk_name": "NVMe SSD 512GB",
        "browser_score": 2980,
    }
