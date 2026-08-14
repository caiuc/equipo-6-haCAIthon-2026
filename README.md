# Benchmark Ligero — Interfaz GUI (PySide6)

App de escritorio que mide el rendimiento real de tu equipo (CPU, RAM y
disco) y lo clasifica en una gama (Donación / Baja / Media / Alta).

## Ejecutar (llegar y ejecutar, sin instalar nada más)
```bash
pip install -r requirements.txt
python main.py
```
Eso es todo. Al tocar **"Correr Benchmark"** la app mide, en el
momento, sobre **tu equipo real**:

- **CPU** — hashes SHA-256 por segundo, en paralelo entre núcleos.
- **RAM** — ancho de banda real de memoria (MB/s), copiando bloques
  grandes.
- **Disco** — velocidad real de escritura y lectura (MB/s), con un
  archivo temporal de verdad (se borra solo al terminar).

No son datos simulados ni aleatorios: son mediciones reales tomadas en
el momento, con Python puro + librería estándar (ver
`native_benchmark.py`). No hace falta instalar PHP, PTS, ni nada fuera
de `requirements.txt`.

Cada categoría corre **varias veces** (5 ráfagas de CPU, 5 corridas de
RAM, 3 de disco) y se reporta la **mediana**, descartando la primera
corrida como calentamiento — el benchmark completo tarda unos
**8-10 segundos** en vez de 2-3, a propósito: es el precio de que la
diferencia entre una corrida y otra baje de ~15% a ~2-5% en vez de
tener un solo número que puede salir alto o bajo por ruido del
sistema. Puedes ajustar cuántas corridas hace cada categoría en
`config.py` (`NATIVE_CPU_TRIALS`, `NATIVE_RAM_TRIALS`,
`NATIVE_DISK_TRIALS`).

`psutil` (en `requirements.txt`) es opcional: mejora un poco la
detección de RAM/disco, pero si no está instalada la app igual
funciona con los fallbacks de la librería estándar.

**Diagnóstico rápido**, sin abrir la GUI:
```bash
python native_benchmark.py
```
Corre el mismo benchmark real y lo imprime por consola.

### GPU
El motor nativo no incluye un test de GPU real (requeriría drivers y
librerías gráficas específicas de cada sistema operativo, lo que iría
en contra de "llegar y ejecutar"). El checkbox de GPU en Opciones
queda ahí para el día que se conecte un test real; mientras tanto, si
lo seleccionas, la app avisa que lo omite — no inventa un número.

## Opcional / avanzado: Phoronix Test Suite (PTS)

Si en algún momento quieres benchmarks estandarizados y comparables
con [OpenBenchmarking.org](https://openbenchmarking.org/tests)
(incluye tests de GPU reales, por ejemplo), la app puede correr
**Phoronix Test Suite** (https://github.com/phoronix-test-suite/phoronix-test-suite)
por debajo — el proyecto al que pertenece **phodevi**
(`pts-core/objects/phodevi`), el módulo que PTS usa internamente para
detectar CPU/GPU/RAM/disco. Esto es opcional y NO hace falta para usar
la app normalmente.

**1) Instala PTS:**

Opción A — script incluido (Linux, recomendado):
```bash
chmod +x install_pts.sh
./install_pts.sh
```
Clona el repo completo de PTS, instala PHP-CLI si falta, y deja el
ejecutable listo.

Opción B — manual / otras plataformas:
```bash
git clone https://github.com/phoronix-test-suite/phoronix-test-suite.git
cd phoronix-test-suite
./phoronix-test-suite system-info   # prueba rápida (usa phodevi)
```
Luego asegúrate de que `phoronix-test-suite` quede en tu `PATH`, o
apunta la app directamente a la ruta del ejecutable con
`PTS_EXECUTABLE` (variable de entorno o en `config.py`).

Requiere PHP-CLI instalado (PTS es una app en PHP) y conexión a
internet la primera vez que corres cada test — PTS descarga el
test-profile desde OpenBenchmarking.org.

**2) Actívalo:**
```bash
export USE_PTS=1
python main.py
```
(o pon `USE_PTS = True` directamente en `config.py`). Si PTS no está
instalado, la app cae automáticamente al motor nativo — nunca se
rompe.

**Diagnóstico rápido de PTS**, sin abrir la GUI:
```bash
python pts_integration.py
```
Te dice si encontró el ejecutable y qué hardware detectó (vía
`system-info`, que usa phodevi por debajo).

## Cómo queda conectado (resumen técnico)

```
main_window.py / options_window.py
        │
        ▼
benchmark_controller.py  (orquesta worker + ventanas)
        │
        ▼
workers.py  (QThread, no bloquea la UI)
        │
        ▼
benchmark_logic.py  (run_full_benchmark / run_custom_tests)
        │
        ▼
native_benchmark.py  (motor por defecto, siempre real)
        │  hashlib SHA-256 en paralelo               -> CPU
        │  copia de bloques grandes en memoria        -> RAM
        │  escritura/lectura real de archivo temporal -> Disco
        ▼
   dict de resultados  →  results_window.py / benchmark_analyzer.py

  (opcional, si config.USE_PTS está activo: benchmark_logic.py intenta
   primero pts_integration.py -> subprocess `phoronix-test-suite`, y si
   no está disponible cae de vuelta al motor nativo de arriba)
```

- Qué mide cada categoría del motor nativo (CPU/RAM/Disco) está en
  `native_benchmark.py` — funciones `_bench_cpu` / `_bench_ram` /
  `_bench_disk`.
- Cómo se convierte cada métrica cruda (hashes/seg, MB/s) a un score
  comparable se controla con `config.NATIVE_SCORE_SCALE` — son valores
  de partida, cambialos calibrando contra hardware conocido.
- Si activas `config.USE_PTS` y un test de PTS falla,
  `config.PTS_FALLBACK_TO_SIMULATION` decide si la app cae al motor
  nativo para esa categoría (default) o lanza un error.

## Estructura del proyecto

```
config.py            -> Todos los textos, tamaños, URL, lista de tests
                         personalizados, la configuración del motor
                         nativo (duración de tests, factores de escala)
                         y la config opcional de Phoronix Test Suite.

native_benchmark.py   -> Motor de benchmark REAL por defecto: mide CPU
                         (hashes SHA-256/seg), RAM (MB/s copiando
                         bloques) y disco (MB/s escribiendo/leyendo un
                         archivo temporal real). Sin dependencias
                         externas más allá de requirements.txt. Corre
                         `python native_benchmark.py` para un
                         diagnóstico rápido sin abrir la GUI.

pts_integration.py    -> Puente OPCIONAL hacia Phoronix Test Suite
                         (activar con config.USE_PTS): detecta el
                         ejecutable, lee hardware (vía phodevi, con
                         `system-info`), corre benchmarks reales
                         (`batch-benchmark`) y parsea el XML de resultados.
                         Corre `python pts_integration.py` para un
                         diagnóstico rápido sin abrir la GUI.

install_pts.sh         -> Instala Phoronix Test Suite completo (clona el
                         repo, instala PHP-CLI si falta). Solo necesario
                         si activas config.USE_PTS. Ver sección de
                         instalación más abajo.

theme.py              -> Todo el estilo visual: colores, degradado de fondo, fuentes
                         y QSS de cada tipo de widget (botones, tarjetas, checkboxes...).
                         Edita este archivo para cambiar la paleta de colores de toda la app.

circuit_background.py -> Widget decorativo que dibuja las líneas de "circuito" en las
                         esquinas de la ventana (puramente estético).

benchmark_logic.py    -> Orquesta la corrida: por defecto llama a
                         native_benchmark.py (real, siempre disponible).
                         Si config.USE_PTS está activo, intenta primero
                         pts_integration.py y cae de vuelta al motor
                         nativo si PTS no está instalado o algo falla.

workers.py            -> QThreads que corren benchmark_logic.py sin congelar la UI.
                         Normalmente no necesitas tocar esto.

running_dialog.py     -> Ventana "Ejecutando benchmark..." con barra de progreso.

options_window.py     -> Ventana de Opciones (checkboxes de tests personalizados,
                          generados automáticamente desde config.CUSTOM_TESTS).

results_window.py     -> Ventana de Resultados: score total + tarjetas por
                          categoría (CPU, GPU, RAM, disco, navegador). Las
                          categorías mostradas se definen en config.RESULT_CATEGORIES.

main_window.py         -> Ventana principal: botón split (CPU Bench | Opciones)
                          + botón "Correr Benchmark".

main.py                -> Punto de entrada.
```

## Cómo modificar cosas comunes

### Cambiar textos, título o tamaño de ventana
Edita `config.py`.

### Cambiar colores, degradado de fondo o estilo de botones
Edita `theme.py`. Todas las variables de color están al inicio del archivo
(`COLOR_BG_TOP`, `COLOR_ACCENT`, `COLOR_PRIMARY_BTN_BG`, etc.) — cambia esos
valores hex y se propaga a toda la app automáticamente.

### Quitar o ajustar las líneas de circuito decorativas
En `main_window.py`, dentro de `_build_ui()`, se crean dos `CircuitCorner`
(`circuit_top`, `circuit_bottom`). Puedes eliminar esas líneas, cambiar la
esquina (`corner="top-right"`, `"bottom-left"`, etc.) o ajustar `opacity`.

### Cambiar la URL que abre "CPU Bench"
Edita `CPU_BENCH_URL` en `config.py`.

### Agregar/quitar un test personalizado (en Opciones)
Agrega o quita un diccionario en `CUSTOM_TESTS` dentro de `config.py`:
```python
CUSTOM_TESTS = [
    {"key": "cpu", "label": "CPU", "description": "..."},
    {"key": "mi_test", "label": "Mi Test", "description": "..."},
]
```
El checkbox correspondiente aparece automáticamente en la ventana de Opciones.

### El benchmark real (motor nativo por defecto)
`benchmark_logic.py` ya no es un placeholder: `run_full_benchmark()` y
`run_custom_tests(selected_keys)` llaman a `native_benchmark.py`, que
mide CPU/RAM/disco reales de tu equipo y devuelve el dict con el
formato que espera `results_window.py`:
```python
{
    "score": 8734,               # score total
    "cpu_score": 4210, "cpu_name": "AMD Ryzen 7 5800X",
    "gpu_score": 6120, "gpu_name": "NVIDIA RTX 3070",
    "ram_score": 3890, "ram_name": "16 GB DDR4 3200MHz",
    "disk_score": 5310, "disk_name": "NVMe SSD 512GB",
    "browser_score": 2980,       # sin "_name": es válido omitirlo
}
```
La categoría "gpu" (y "browser") se omiten automáticamente si pides
esas keys y el motor activo no sabe medirlas de verdad — no se inventa
un valor (ver `native_benchmark.AVAILABLE_CATEGORIES`).

Si en algún momento quieres reemplazar el motor nativo por otro
(propio, o PTS activándolo con `config.USE_PTS`), el único contrato que
hay que respetar es ese dict — puedes cambiar el cuerpo de
`get_benchmark_results()` en `benchmark_logic.py` por tu propia
llamada, sin tocar `workers.py` ni las ventanas.

Ambas funciones (`run_full_benchmark` / `run_custom_tests`) aceptan un
`progress_callback` opcional para reportar avance en tiempo real en la
ventana de "ejecutando benchmark" (ya conectado: verás mensajes como
"Ejecutando test de CPU (pts/compress-7zip)...").

### Agregar o quitar categorías en la pantalla de Resultados
Edita `RESULT_CATEGORIES` en `config.py`. Cada entrada necesita un `key`
que coincida con las claves `{key}_score` / `{key}_name` que devuelve
`benchmark_logic.run_full_benchmark()`. Si una categoría no viene en el
resultado, la fila simplemente no se muestra (no hace falta que todas las
categorías estén siempre presentes).

### Cambiar qué se hace al terminar el benchmark
El resultado del botón principal ahora abre `results_window.py`
automáticamente. Los tests personalizados de Opciones siguen mostrando un
`QMessageBox` simple (puedes cambiarlo por `ResultsWindow` también si
quieres el mismo formato ahí).
