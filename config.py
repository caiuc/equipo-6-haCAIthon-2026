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
        "description": "Hashes SHA-256/seg reales, en paralelo entre núcleos.",
    },
    {
        "key": "ram",
        "label": "RAM",
        "description": "Ancho de banda real de memoria (MB/s), medido en el momento.",
    },
    {
        "key": "disk",
        "label": "Disco",
        "description": "Velocidad real de lectura/escritura (MB/s), con archivo temporal.",
    },
    {
        "key": "gpu",
        "label": "GPU",
        "description": (
            "Sin test nativo real todavía (se omite en el motor por defecto; "
            "activa config.USE_PTS para medirla con Phoronix Test Suite)."
        ),
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

# ---------------------------------------------------------------------------
# Motor de benchmark nativo (REAL, sin dependencias externas)
# ---------------------------------------------------------------------------
# Este es el motor que se usa por defecto: mide CPU/RAM/disco de verdad
# (ver native_benchmark.py), sin necesitar instalar nada aparte de
# requirements.txt. "Llegar y ejecutar": pip install -r requirements.txt
# && python main.py ya te da resultados reales de TU equipo.
#
# Cada categoría corre VARIAS veces y se reporta la MEDIANA (no el
# promedio) para que un solo pico de ruido del sistema no arruine el
# resultado, y se descarta la primera corrida como "warm-up". Esto es
# más pesado (tarda más) a propósito: la idea es bajar la variabilidad
# entre corridas de la app (antes ~15%) a cambio de unos segundos más.
import os as _os

# CPU: se corren varias "ráfagas" cortas de hashes SHA-256 en paralelo
# y se toma la mediana de hashes/seg entre ellas.
NATIVE_CPU_BURST_SEC = 1.0      # duración de cada ráfaga
NATIVE_CPU_TRIALS = 5           # cuántas ráfagas (se descarta la 1ra)

# RAM: mismo principio, con el test de copia de memoria.
NATIVE_RAM_TEST_MB = 96
NATIVE_RAM_TEST_ITERATIONS = 10
NATIVE_RAM_TRIALS = 5           # cuántas corridas (se descarta la 1ra)

# Disco: archivo más grande (más estable) y varias corridas, mediana.
# Entre escritura y lectura se le pide al SO que libere el caché de
# página de ese archivo (en Linux, vía posix_fadvise) para que la
# lectura mida disco real y no RAM cacheada.
NATIVE_DISK_TEST_MB = 192
NATIVE_DISK_TRIALS = 3

# Factor de escala para convertir cada métrica cruda (hashes/seg,
# MB/s de RAM, MB/s de disco) a un score entero "estilo videojuego"
# comparable con las gamas de benchmark_analyzer_config.py. Son valores
# de partida calibrados contra hardware típico — ajústalos si quieres
# que tus números calcen con equipos que ya conozcas.
NATIVE_SCORE_SCALE = {
    "cpu": 0.02,
    "ram": 0.5,
    "disk": 4.0,
}

# ---------------------------------------------------------------------------
# Integración opcional con Phoronix Test Suite (PTS) — AVANZADO
# ---------------------------------------------------------------------------
# https://github.com/phoronix-test-suite/phoronix-test-suite
#
# Por defecto la app NO necesita esto: usa el motor nativo de arriba.
# Esta integración queda disponible para quien SÍ quiera correr
# test-profiles reales de OpenBenchmarking.org (PTS es la app PHP que,
# por dentro, usa "phodevi" para detectar CPU/GPU/RAM/disco). Requiere
# instalar PTS + PHP-CLI aparte (ver install_pts.sh y el README).
#
# Actívalo con USE_PTS=1 (variable de entorno) o poniendo USE_PTS=True
# aquí abajo. Si está activado pero PTS no está instalado, la app cae
# automáticamente al motor nativo (no se rompe).
USE_PTS = _os.environ.get("USE_PTS", "0") == "1"

# Ruta al ejecutable de phoronix-test-suite. Si queda vacío, se busca
# automáticamente en el PATH y en ubicaciones típicas de instalación
# (ver pts_integration.find_executable()). Puedes forzar una ruta
# específica aquí, o exportar la variable de entorno PTS_EXECUTABLE
# antes de correr main.py.
PTS_EXECUTABLE = _os.environ.get("PTS_EXECUTABLE", "")

# Carpeta donde PTS guarda los resultados de cada corrida (estándar de
# PTS, normalmente no hace falta cambiarlo).
PTS_RESULTS_DIR = _os.path.expanduser("~/.phoronix-test-suite/test-results")

# Prefijo usado para nombrar cada corrida de resultados que dispara
# esta app (para poder identificarlas fácil dentro de PTS_RESULTS_DIR).
PTS_RESULT_IDENTIFIER_PREFIX = "benchmark_gui"

# Tiempo máximo (segundos) que se espera a que termine un test-profile
# de PTS antes de darlo por fallido. Algunos tests son largos y/o
# necesitan descargarse la primera vez.
PTS_TEST_TIMEOUT_SEC = 1800  # 30 minutos

# Mapea cada categoría (misma key que en CUSTOM_TESTS / RESULT_CATEGORIES)
# al test-profile de PTS que se debe correr para esa categoría. Puedes
# cambiar estos por cualquier test-profile válido de OpenBenchmarking.org
# (busca más en https://openbenchmarking.org/tests). Si una categoría
# queda en None, se omite (no se corre ni se muestra en resultados).
PTS_TEST_PROFILES = {
    "cpu": "pts/compress-7zip",
    "gpu": "pts/glmark2",
    "ram": "pts/ramspeed",
    "disk": "pts/fio",
    "browser": None,  # PTS no trae un test de navegador "de fábrica"
}

# Factor de escala para convertir el resultado crudo de cada test PTS
# (que viene en unidades muy distintas entre sí: MB/s, FPS, segundos,
# MIPS, etc.) a un score entero "estilo videojuego" comparable con el
# resto de la app. Son valores de partida — ajústalos calibrando contra
# hardware que ya conozcas (ver benchmark_analyzer_config.py para cómo
# se pesan luego en el score global).
PTS_SCORE_SCALE = {
    "cpu": 5,
    "gpu": 10,
    "ram": 1,
    "disk": 2,
}

# Si True: cuando USE_PTS está activo pero PTS no está instalado (o un
# test individual falla), la app cae de vuelta al motor nativo (datos
# reales de CPU/RAM/disco medidos en el momento, ver native_benchmark.py)
# en vez de mostrar un error. Ponlo en False si prefieres que falle
# explícitamente cuando PTS no esté disponible.
PTS_FALLBACK_TO_SIMULATION = True
