"""
config.py
=========
Configuración centralizada de la aplicación.

Toda la personalización "de contenido" (textos, tamaños, URLs, lista de
tests personalizados, etc.) vive aquí para que puedas modificarla sin
tocar la lógica de la interfaz en main_window.py.
"""

# ---------------------------------------------------------------------------
# Ventana principal
# ---------------------------------------------------------------------------
APP_TITLE = "Benchmark Ligero"
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 480

# Branding mostrado en el centro de la ventana principal (estilo "logo")
BRAND_TITLE = "CPU"
BRAND_SUBTITLE = "Benchmark ligero de tu equipo"

# ---------------------------------------------------------------------------
# Botón split superior: "CPU Bench" | "Opciones"
# ---------------------------------------------------------------------------
CPU_BENCH_LABEL = "CPU Bench"
OPTIONS_LABEL = "Opciones"

# URL placeholder a la que se abre al pulsar "CPU Bench"
CPU_BENCH_URL = "https://example.com/cpu-bench-info"

# ---------------------------------------------------------------------------
# Botón principal de ejecución
# ---------------------------------------------------------------------------
RUN_BENCHMARK_LABEL = "Correr Benchmark"

# Texto / título mostrados en la ventana de progreso mientras corre
RUNNING_TITLE = "Ejecutando benchmark..."
RUNNING_MESSAGE = "El benchmark se está ejecutando, por favor espera."

# Duración simulada del benchmark placeholder (segundos)
PLACEHOLDER_BENCHMARK_DURATION_SEC = 3

# ---------------------------------------------------------------------------
# Ventana de Opciones / Tests personalizados
# ---------------------------------------------------------------------------
OPTIONS_WINDOW_TITLE = "Opciones - Tests personalizados"

# Lista de tests personalizados disponibles.
# Cada entrada es un dict con:
#   key: identificador interno (usado por la lógica del benchmark)
#   label: texto mostrado al usuario
#   description: texto de ayuda / tooltip
#
# Para agregar un nuevo test personalizado, simplemente añade otro dict aquí.
CUSTOM_TESTS = [
    {
        "key": "cpu",
        "label": "CPU",
        "description": "Prueba de rendimiento de CPU (placeholder).",
    },
    {
        "key": "ram",
        "label": "RAM",
        "description": "Prueba de rendimiento de memoria RAM (placeholder).",
    },
    {
        "key": "disk",
        "label": "Disco",
        "description": "Prueba de velocidad de lectura/escritura de disco (placeholder).",
    },
    {
        "key": "gpu",
        "label": "GPU",
        "description": "Prueba de rendimiento gráfico (placeholder).",
    },
]

RUN_CUSTOM_TESTS_LABEL = "Correr tests seleccionados"

# ---------------------------------------------------------------------------
# Ventana de Resultados
# ---------------------------------------------------------------------------
RESULTS_WINDOW_TITLE = "Resultados del Benchmark"

# Define qué categorías se muestran en la pantalla de resultados y en qué
# orden. Cada entrada mapea las claves del dict que retorna el benchmark
# (score_key / name_key) a una etiqueta visible y un ícono/emoji simple.
#
# Para agregar una nueva categoría de resultado (por ejemplo "network"),
# solo agrega otra entrada aquí y asegúrate de que benchmark_logic.py
# devuelva "network_score" / "network_name" en su resultado.
RESULT_CATEGORIES = [
    {"key": "cpu", "label": "CPU", "icon": "🧠"},
    {"key": "gpu", "label": "GPU", "icon": "🎮"},
    {"key": "ram", "label": "RAM", "icon": "💾"},
    {"key": "disk", "label": "Disco", "icon": "🗄️"},
    {"key": "browser", "label": "Navegador", "icon": "🌐"},
]

RESULTS_CLOSE_LABEL = "Cerrar"
