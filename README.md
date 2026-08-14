# CPU - Benchmark

Herramienta para **evaluar el rendimiento real de computadores donados** y clasificarlos automáticamente en gamas, de modo que cada equipo recuperado se destine a la tarea educativa que efectivamente puede sostener.

Proyecto del **Equipo 6 — HaCAiThon 2026** (CAi Ingeniería UC), construido sobre la iniciativa CPU de reacondicionamiento y donación de PCs.

---

## El problema

Cuando llega un lote de PCs donados, decidir qué hacer con cada uno (¿se dona?, ¿se desarma por piezas?, ¿qué distro liviana le instalo?) se hace hoy "a ojo", mirando specs. Pero las specs mienten: dos equipos con el mismo i3 rinden distinto según el disco, la RAM y el estado real del hardware.

La solución de este proyecto es **medir, no leer specs**: correr un benchmark real sobre el equipo, calcular un score ponderado y clasificarlo en una gama con una recomendación de uso concreta.

---

## Arquitectura

El repositorio agrupa cuatro componentes que hoy viven en carpetas separadas:

| Componente | Carpeta | Stack | Rol |
|---|---|---|---|
| **Motor de benchmark (NO FUNCIONAL)** | `benchmark/` | Python + Phoronix Test Suite | Corre las pruebas reales sobre el hardware |
| **Interfaz gráfica y Benchmark (FUNCIONAL)** | `interfaz_grafica/` | Python + PySide6 (Qt) + Benchmark (FUNCIONAL) | App de escritorio que dispara el benchmark y muestra resultados |
| **Backend / API** | `backend/` | Node.js + Express 5 + Sequelize + PostgreSQL | Autenticación e inventario centralizado de equipos |
| **Sitio web** | `frontend/` | HTML + CSS + JS vanilla | Landing pública, login e inventario |

### Flujo previsto

```
[PC donado]
     |
     v
GUI (PySide6)  --dispara-->  Phoronix Test Suite  --resultados-->  analyzer
     |                                                                  |
     |                                          score global + gama <---+
     v
API REST (Express)  -->  PostgreSQL  -->  inventario web (equipos.html)
```

---

## Componentes en detalle

### 1. Motor de benchmark (`benchmark/initial.py`)

Automatiza **Phoronix Test Suite (PTS)** desde Python, sin interacción manual y sin depender de internet en tiempo de ejecución.

Qué hace el script, en orden:

1. Clona PTS desde GitHub si no existe localmente.
2. Inicializa la configuración de PTS y acepta el *user agreement* de forma no interactiva.
3. Parcha `pts_test_run_options.php` para que PTS tome las opciones por defecto de cada test en vez de quedarse esperando input.
4. Escribe la sección `BatchMode` de `~/.phoronix-test-suite/user-config.xml` directamente (en lugar de usar `batch-setup` interactivo), activando `SaveResults` y desactivando prompts, navegador y subida de resultados.
5. Instala y corre los tests vía `batch-install` / `batch-run`, pasando `TEST_RESULTS_NAME`, `TEST_RESULTS_IDENTIFIER` y `PRESET_OPTIONS` como variables de entorno.

**Tests elegidos** — el set mínimo representativo para cargas de ofimática y navegación en hardware antiguo:

| Test | Mide |
|---|---|
| `pts/stress-ng` | CPU |
| `pts/stream` | Ancho de banda de RAM |
| `pts/fio` | Disco (lectura aleatoria 4K) |

**Requisitos:** Linux, `git`, `php`, y las dependencias de compilación que PTS pide para cada perfil de test.

```bash
cd benchmark/
python3 initial.py
```

> El `.gitignore` ya excluye `phoronix-test-suite/`, `test-results/`, `installed-tests/` y demás artefactos que PTS genera en runtime.

---

### 2. Interfaz gráfica (`interfaz_grafica/`)

App de escritorio en PySide6, diseñada para que un técnico corra el benchmark sin tocar la terminal.

```bash
pip install PySide6
python main.py
```

**Arquitectura por capas** — cada archivo tiene una responsabilidad única:

```
main.py                      Punto de entrada (QApplication)

  Presentación
  ├── main_window.py         Ventana principal: botón split (CPU Bench | Opciones)
  │                          + botón "Correr Benchmark"
  ├── options_window.py      Selección de tests personalizados (checkboxes
  │                          generados automáticamente desde config.CUSTOM_TESTS)
  ├── results_window.py      Score total + tarjeta por categoría
  ├── running_dialog.py      Diálogo "Ejecutando..." con barra de progreso
  ├── circuit_background.py  Decoración: líneas de circuito en las esquinas
  └── theme.py               Paleta de colores y QSS de todos los widgets

  Configuración
  ├── config.py                     Textos, tamaños, URLs, lista de tests y categorías
  └── benchmark_analyzer_config.py  Pesos del score y umbrales de las gamas

  Lógica
  ├── benchmark_controller.py  Orquestador: lanza el worker, muestra el diálogo
  │                            de progreso y despliega resultados
  ├── workers.py               QThreads para no congelar la UI
  ├── benchmark_logic.py       Motor de benchmark (hoy placeholder)
  └── benchmark_analyzer.py    Calcula el score global y clasifica en gama
```

La separación clave: `main_window.py` y `options_window.py` **no saben nada** de threads ni de benchmarks. Solo llaman a `BenchmarkController`. Si mañana cambia cómo se ejecuta el benchmark, se toca un solo archivo.

**Contrato de datos.** Todo el flujo se comunica con un dict de forma fija:

```python
{
    "score": int,                                    # opcional; si falta, se estima
    "cpu_score": int,     "cpu_name": str,
    "gpu_score": int,     "gpu_name": str,
    "ram_score": int,     "ram_name": str,
    "disk_score": int,    "disk_name": str,
    "browser_score": int,
}
```

---

### 3. Modelo de evaluación (`benchmark_analyzer.py`)

**Score global.** Si el dict de resultados no trae un `score` ya calculado, se estima ponderando las categorías según `SCORE_WEIGHTS`:

| Categoría | Peso |
|---|---|
| CPU | 0.40 |
| GPU | 0.20 |
| Disco | 0.20 |
| RAM | 0.10 |
| Navegador | 0.10 |

**Clasificación por gamas.** Es una **escala continua**: cada gama define solo un `score_min`, y el techo de una gama es implícitamente el piso de la siguiente. Esto garantiza que *todo* equipo cae en alguna gama — no existe zona gris "sin clasificar".

| Gama | `score_min` | Uso recomendado |
|---|---|---|
| Apto para Donación | 0 | Obsoleto para uso normal: reciclaje, piezas, o texto sin multitarea |
| Gama Baja | 2 500 | Ofimática básica y navegación |
| Gama Media | 9 000 | Uso general fluido, programación ligera, multitarea |
| Gama Alta | 40 000 | Modelado 3D, edición de video, VMs |

Cada gama incluye además `reference_metrics` (valores orientativos de `cpu_score`, `disk_score`, `ram_score`) que sirven **solo como contexto informativo** — la decisión se toma únicamente con `score_min`.

Ambas tablas son constantes editables en `benchmark_analyzer_config.py`: ajustar el modelo de evaluación no requiere tocar la lógica.

---

### 4. Backend / API (`backend/`)

API REST en Express 5 con Sequelize sobre PostgreSQL.

**Modelos**

- `User` — `name`, `email` (único), `password`. Hasheo con bcrypt vía hooks `beforeCreate` / `beforeUpdate`.
- `Computer` — `name`, `owner`, `type`, `processor`, `ramType`, `ramCapacity`, `storageType`, `storageCapacity`, `graphics`, `comment`.

**Endpoints** (todos bajo el prefijo `/api`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/` | — | Health check |
| `POST` | `/auth/login` | — | Login; devuelve JWT válido por 1 h |
| `POST` | `/auth/forgot-password` | — | Genera token de recuperación (15 min) |
| `GET` | `/computers` | JWT | Lista todos los equipos |
| `POST` | `/computers` | JWT | Registra un equipo nuevo |
| `PATCH` | `/computers/:id` | JWT | Edita un equipo existente |
| `POST` | `/contact` | — | Formulario de contacto |

La autenticación usa `Authorization: Bearer <token>`; el middleware `authenticate.js` verifica el JWT y adjunta el payload a `req.user`. Los errores se centralizan con el helper `createHttpError(status, message)` y un middleware de error en `app.js`.

**Variables de entorno** (`.env`)

```
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cpu_db
DB_USER=...
DB_PASS=...
JWT_SECRET=...
```

**Levantar**

```bash
cd backend/
npm install
npx sequelize-cli db:migrate
node index.js
```

---

### 5. Sitio web (`frontend/`)

Sitio estático, sin framework ni build step. Se abre directamente o se sirve con cualquier servidor estático.

| Página | Contenido |
|---|---|
| `index.html` | Landing: hero, noticias (donación a Penco, recuperación de equipos, herramienta de benchmark), utilidades, contacto y redes |
| `benchmark.html` | Descarga de la herramienta + explicación de las tres gamas de rendimiento |
| `login.html` | Formulario que hace `POST` a `/api/auth/login` y guarda el JWT en `localStorage` |
| `equipos.html` | Tabla del inventario de equipos registrados |

---

## Estado actual y pendientes

Este es un prototipo de hackathon (8 horas). Lo que falta, documentado explícitamente:

### Bloqueantes

- **La GUI no está conectada al benchmark real.** `benchmark_logic.get_benchmark_results()` devuelve datos hardcodeados (un Ryzen 7 5800X ficticio). Falta fusionar `initial.py` con `benchmark_logic.py` para que el botón "Correr Benchmark" dispare PTS de verdad y parsee sus resultados.
- **El backend no arranca.** Hay que resolver antes:
  - `routes/index.js` llama `router.use('/contact')` sin handler → Express 5 lanza excepción al iniciar.
  - `routes/contact.js` no importa `express`, no crea un `router` ni exporta nada.
  - `routes/computer.js` requiere `../middleware/authenticate`, pero la carpeta se llama `middlewares/` (plural).
  - `models/index.js` requiere `config/config.json`, pero solo existe `config/config.js`.
  - `package.json` no declara `jsonwebtoken`, `sequelize`, `pg` ni `pg-hstore`, que sí se usan en el código.
  - `models/user.js` y la migración de usuarios hacen `require('../app')` sin necesitarlo, creando un ciclo de imports.
- **El inventario web usa datos falsos.** `equipos.html` tiene la verificación de token comentada y renderiza un array `mockComputers` hardcodeado en vez de llamar a `GET /api/computers`.

### Inconsistencias de diseño a resolver

- **Dos modelos de ponderación distintos.** El diseño del benchmark con PTS apunta a disco 45 % / CPU 30 % / RAM 25 % (calibrado con un i3-2100 como piso de referencia). El código en `benchmark_analyzer_config.py` usa CPU 40 % / GPU 20 % / disco 20 % / RAM 10 % / navegador 10 %. Hay que unificar: si el proyecto es solo Linux para ofimática, GPU y navegador probablemente no deberían pesar, y el disco debería dominar.
- **Categorías sin motor detrás.** La GUI muestra GPU y navegador, pero el set de tests de PTS elegido no los mide.
- **Escala de scores sin normalizar.** Los umbrales de gamas (2 500 / 9 000 / 40 000) son valores absolutos que no corresponden a las unidades que devuelve PTS. Falta la normalización 0–100 contra el equipo de referencia.
- `PRESET_OPTIONS` en `initial.py` tiene placeholders sin completar (`fio.mode=...`, `fio.blocksize=...`).
- `CPU_BENCH_URL` en `config.py` apunta a `https://example.com/cpu-bench-info`.
- El README de `frontend/`, `backend/` y `benchmark/` sigue siendo el resumen de las bases de la hackathon, no documentación del código.
- No hay tests en ningún componente.

---

## Estructura del repositorio

```
project_cpu/
├── benchmark/          Motor de benchmark (Python + PTS)
│   └── initial.py
├── interfaz_grafica/   App de escritorio (PySide6)
├── backend/            API REST (Express + Sequelize + PostgreSQL)
│   ├── app.js, index.js
│   ├── config/, models/, migrations/
│   ├── routes/         auth, computer, contact
│   ├── middlewares/    authenticate (JWT)
│   └── error/          createHttpError
└── frontend/           Sitio estático
    ├── index.html, benchmark.html, login.html, equipos.html
    └── images/
```

---

## Licencia

MIT — © 2026 CAi UC.
