"""
benchmark_analyzer.py
=======================
Analiza un dict de resultados de benchmark — el mismo formato que
retorna benchmark_logic.get_benchmark_results() / run_full_benchmark():

    {
        "score": int,             # opcional
        "cpu_score": ..., "cpu_name": ...,
        "gpu_score": ..., "gpu_name": ...,
        "ram_score": ..., "ram_name": ...,
        "disk_score": ..., "disk_name": ...,
        "browser_score": ...,
    }

Hace dos cosas:

  1) Si el dict no trae "score" (o viene None), lo ESTIMA ponderando
     los scores por categoría según SCORE_WEIGHTS.
  2) CLASIFICA el equipo en una gama según una escala continua definida
     en GAMAS (Apto para Donación / Gama Baja / Media / Alta, o las que
     definas). La clasificación SIEMPRE devuelve una gama — no existe
     un caso "sin clasificar": un equipo por debajo de todos los
     umbrales cae en la gama más baja (por defecto, apto para
     donación).

Los pesos y los rangos son constantes editables en
benchmark_analyzer_config.py — este archivo no debería necesitar
cambios para ajustar el modelo de evaluación, solo para agregar
nuevas formas de analizar los datos.
"""

from benchmark_analyzer_config import SCORE_WEIGHTS, GAMAS


def estimate_global_score(results: dict) -> float:
    """
    Estima el score global ponderando los "<categoria>_score" del dict
    de resultados según SCORE_WEIGHTS (benchmark_analyzer_config.py).

    Si alguna categoría de SCORE_WEIGHTS no viene en `results`,
    simplemente no aporta al total (no se re-normalizan los pesos
    restantes).
    """
    total = 0.0
    for category, weight in SCORE_WEIGHTS.items():
        score = results.get(f"{category}_score")
        if score is not None:
            total += score * weight
    return round(total, 2)


def get_global_score(results: dict) -> float:
    """
    Retorna el score total a usar para clasificar: el que ya viene en
    results["score"] si existe, o el estimado con
    estimate_global_score() en caso contrario.
    """
    score = results.get("score")
    if score is not None:
        return score
    return estimate_global_score(results)


def classify_gama(score: float) -> dict:
    """
    Clasifica un score global dentro de una de las GAMAS definidas en
    benchmark_analyzer_config.py.

    GAMAS es una escala CONTINUA: cada gama solo define un score_min,
    y el techo de una gama es, implícitamente, el score_min de la
    siguiente. Esto significa que SIEMPRE hay una gama que clasifica
    (no existe una zona gris "sin clasificar"): un equipo muy por
    debajo del umbral de Gama Baja simplemente cae en la gama más baja
    definida (por defecto, "Apto para Donación").

    Se elige la gama más alta cuyo score_min sea <= score. GAMAS no
    necesita venir pre-ordenada: se ordena defensivamente aquí por
    score_min antes de evaluar.
    """
    gamas_ordenadas = sorted(GAMAS, key=lambda g: g["score_min"])

    seleccionada = gamas_ordenadas[0]
    for gama in gamas_ordenadas:
        if score >= gama["score_min"]:
            seleccionada = gama
        else:
            break

    return seleccionada


def analyze(results: dict) -> dict:
    """
    Función principal del analizador: recibe el dict de resultados del
    benchmark y retorna el análisis completo.

        {
            "score": float,              # score usado (real o estimado)
            "score_was_estimated": bool, # True si no venía en `results`
            "gama": {...},                # dict completo de la gama (ver GAMAS)
        }
    """
    had_score = results.get("score") is not None
    score = get_global_score(results)
    gama = classify_gama(score)

    return {
        "score": score,
        "score_was_estimated": not had_score,
        "gama": gama,
    }
