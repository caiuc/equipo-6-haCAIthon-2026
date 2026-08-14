"""
benchmark_analyzer_config.py
=============================
Constantes editables para el analizador de benchmarks
(benchmark_analyzer.py).

Todo lo que define el modelo de evaluación vive aquí — pesos del score
global y rangos de clasificación por gama — para que puedas ajustarlo
a voluntad sin tocar la lógica en benchmark_analyzer.py.
"""

# ---------------------------------------------------------------------------
# 1) Modelo de ponderación del score global
# ---------------------------------------------------------------------------
# Se usa SOLO si el JSON de resultados no trae ya un "score" calculado.
# Las claves deben coincidir con el prefijo de "<key>_score" en el dict
# de resultados (ver benchmark_logic.py), y los pesos deberían sumar 1.0.
SCORE_WEIGHTS = {
    "cpu": 0.40,
    "gpu": 0.20,
    "disk": 0.20,   # ponderado para que un NVMe no infle la suma directa
    "ram": 0.10,
    "browser": 0.10,
}

# ---------------------------------------------------------------------------
# 2) Clasificación por gamas (escala continua, siempre clasifica)
# ---------------------------------------------------------------------------
# En vez de rangos [min, max] con huecos entre gamas (lo que dejaba
# equipos "sin clasificar" en las zonas grises), cada gama define SOLO
# un score_min: el umbral a partir del cual el equipo entra en esa
# gama. El techo de una gama es, implícitamente, el score_min de la
# siguiente. Así la escala queda continua y CUALQUIER score cae en
# alguna gama — no hace falta un caso "sin clasificar" aparte.
#
# La lista debe ir ordenada de menor a mayor score_min. El analizador
# elige la gama más alta cuyo score_min sea <= al score del equipo.
#
# La primera gama (score_min: 0) actúa como piso: cualquier equipo por
# debajo del umbral de "Gama Baja" cae aquí — se usa para marcar
# equipos obsoletos como aptos para donación/reciclaje en vez de
# dejarlos sin clasificar.
#
#   key               : identificador interno corto.
#   label             : nombre mostrado al usuario.
#   description       : texto descriptivo de la gama.
#   score_min         : score global mínimo (inclusive) para entrar en
#                        esta gama.
#   reference_metrics : valores de referencia informativos por
#                        categoría (cpu_score, disk_score, ram_score,
#                        etc.). Son solo contexto para mostrar/loguear,
#                        NO se usan para decidir la gama — la decisión
#                        se toma únicamente con score_min.
GAMAS = [
    {
        "key": "donacion",
        "label": "Apto para Donación",
        "description": (
            "Equipo obsoleto para uso normal: muy por debajo de Gama "
            "Baja. Recomendado para donación, reciclaje o, a lo sumo, "
            "tareas mínimas de texto sin multitarea."
        ),
        "score_min": 0,
        "reference_metrics": {
            "cpu_score": 600,
            "disk_score": 150,   # HDD muy lento o dañado
            "ram_score": 300,
        },
    },
    {
        "key": "baja",
        "label": "Gama Baja",
        "description": (
            "Equipos antiguos / Ofimática básica. Rendimiento "
            "equivalente a CPU de 2 núcleos antiguos."
        ),
        "score_min": 2500,
        "reference_metrics": {
            "cpu_score": 1200,
            "disk_score": 300,   # indica HDD mecánico
            "ram_score": 600,
        },
    },
    {
        "key": "media",
        "label": "Gama Media",
        "description": (
            "Equipos intermedios / Uso general fluido. Equivalente a "
            "CPU de 4 núcleos."
        ),
        "score_min": 9000,
        "reference_metrics": {
            "cpu_score": 5000,
            "disk_score": 2000,  # indica SSD SATA
            "ram_score": 1500,
        },
    },
    {
        "key": "alta",
        "label": "Gama Alta",
        "description": (
            "Equipos modernos / Alto rendimiento. Equivalente a CPUs "
            "modernos de 6+ núcleos y altas frecuencias."
        ),
        "score_min": 40000,
        "reference_metrics": {
            "cpu_score": 18000,
            "disk_score": 12000,  # indica SSD NVMe
            "ram_score": 4000,
        },
    },
]
