# Benchmark Ligero — Interfaz GUI (PySide6)

## Requisitos
```bash
pip install PySide6
```

## Ejecutar
```bash
python main.py
```

## Estructura del proyecto

```
config.py            -> Todos los textos, tamaños, URL y lista de tests personalizados.
                         Es lo primero que deberías editar para personalizar la app.

theme.py              -> Todo el estilo visual: colores, degradado de fondo, fuentes
                         y QSS de cada tipo de widget (botones, tarjetas, checkboxes...).
                         Edita este archivo para cambiar la paleta de colores de toda la app.

circuit_background.py -> Widget decorativo que dibuja las líneas de "circuito" en las
                         esquinas de la ventana (puramente estético).

benchmark_logic.py    -> La lógica real del benchmark (hoy son placeholders con time.sleep).
                         Reemplaza el contenido de run_full_benchmark() y
                         run_custom_tests() con tu código real.

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

### Conectar el benchmark real
Edita `benchmark_logic.py`:
- `run_full_benchmark()` -> lo que corre el botón principal "Correr Benchmark".
  Debe devolver un dict con este formato exacto para que `results_window.py`
  lo muestre correctamente:
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
  Si tu función real ya devuelve este formato, solo tienes que reemplazar
  el `return` placeholder por la llamada a tu función.
- `run_custom_tests(selected_keys)` -> lo que corre desde Opciones, según los
  tests que el usuario marcó (usa `key` de cada test en `CUSTOM_TESTS`).

Ambas funciones aceptan un `progress_callback` opcional para reportar avance
en tiempo real en la ventana de "ejecutando benchmark".

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
