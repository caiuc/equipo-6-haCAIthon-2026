"""
pts_integration.py
===================
Capa de integración con Phoronix Test Suite (PTS):

    https://github.com/phoronix-test-suite/phoronix-test-suite

Este módulo NO reimplementa detección de hardware ni motores de
benchmark propios: en su lugar, ejecuta el binario `phoronix-test-suite`
como subproceso (tal como se ejecutaría desde la terminal) y parsea su
salida / sus resultados en XML.

¿Por qué así y no importando `phodevi` directamente?
-----------------------------------------------------
`phodevi` (Phoronix Device Interface, el módulo al que apunta el enlace
que nos diste: pts-core/objects/phodevi) es un conjunto de clases PHP
que viven DENTRO de pts-core y que PTS usa internamente para detectar
CPU, GPU, RAM, disco, red, etc. No es una librería standalone que se
pueda "importar" desde Python: solo funciona como parte de la
aplicación completa de Phoronix Test Suite.

La forma soportada y estable de acceder a esa detección de hardware
(y de disparar benchmarks reales) desde otro lenguaje es invocar el
propio CLI `phoronix-test-suite`, que expone justamente lo que
`phodevi` calcula:

  - `phoronix-test-suite system-info`   -> usa phodevi para reportar
    CPU, GPU, RAM, disco, motherboard, SO, kernel, etc.
  - `phoronix-test-suite batch-benchmark <test-profile>` -> corre un
    test real descargado de OpenBenchmarking.org y genera un XML de
    resultados (composite.xml) en
    ~/.phoronix-test-suite/test-results/<identifier>/composite.xml

Este módulo envuelve ambos comandos y expone funciones simples en
Python para que `benchmark_logic.py` no tenga que preocuparse de
subprocess, XML ni de si PTS está instalado o no.

Requisitos en el sistema (no en este repo, PTS es una app aparte):
  - PHP (phoronix-test-suite es una app PHP)
  - phoronix-test-suite instalado y en el PATH (o configurado vía
    config.PTS_EXECUTABLE / variable de entorno PTS_EXECUTABLE)
  - Conexión a internet la primera vez que se corre cada test-profile
    (PTS descarga el test desde OpenBenchmarking.org)

Ver install_pts.sh y el README para instrucciones de instalación.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

import config

# ---------------------------------------------------------------------------
# Ubicación del ejecutable
# ---------------------------------------------------------------------------

# Rutas típicas donde suele instalarse phoronix-test-suite si no quedó
# en el PATH (instalación manual desde el repo, por ejemplo).
_COMMON_PATHS = [
    "/usr/bin/phoronix-test-suite",
    "/usr/local/bin/phoronix-test-suite",
    os.path.expanduser("~/phoronix-test-suite/phoronix-test-suite"),
    os.path.expanduser("~/.local/bin/phoronix-test-suite"),
]


def find_executable() -> str | None:
    """
    Busca el ejecutable de phoronix-test-suite, en este orden:

      1) config.PTS_EXECUTABLE (o variable de entorno PTS_EXECUTABLE,
         que config.py ya lee).
      2) El PATH del sistema (`which phoronix-test-suite`).
      3) Ubicaciones típicas de instalación manual.

    Retorna la ruta al ejecutable, o None si no se encontró.
    """
    configured = getattr(config, "PTS_EXECUTABLE", "") or ""
    if configured and os.path.isfile(configured) and os.access(configured, os.X_OK):
        return configured

    found = shutil.which("phoronix-test-suite")
    if found:
        return found

    for candidate in _COMMON_PATHS:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None


def is_available() -> bool:
    """True si encontramos un ejecutable de phoronix-test-suite utilizable."""
    return find_executable() is not None


# ---------------------------------------------------------------------------
# Detección de hardware (usa phodevi por debajo, vía `system-info`)
# ---------------------------------------------------------------------------

_SYSTEM_INFO_PATTERNS = {
    "cpu_name": r"Processor:\s*([^,\n]+)",
    "gpu_name": r"Graphics:\s*([^,\n]+)",
    "ram_name": r"Memory:\s*([^,\n]+)",
    "disk_name": r"Disk:\s*([^,\n]+)",
    "motherboard_name": r"Motherboard:\s*([^,\n]+)",
    "os_name": r"OS:\s*([^,\n]+)",
    "kernel_name": r"Kernel:\s*([^,\n]+)",
}

_VERSION_PATTERN = r"Phoronix Test Suite\s+v?([\d.]+)"


def get_system_info(timeout: int = 60) -> dict:
    """
    Ejecuta `phoronix-test-suite system-info` (que usa phodevi
    internamente) y parsea el hardware detectado a un dict:

        {
            "cpu_name": "AMD Ryzen 7 5800X @ 3.80GHz (8 Cores)",
            "gpu_name": "NVIDIA GeForce RTX 3070",
            "ram_name": "16GB",
            "disk_name": "1000GB Samsung SSD 970",
            "pts_version": "10.8.4",
            ...
        }

    Si PTS no está disponible o falla, retorna un dict vacío (nunca
    lanza excepción) — quien llame decide qué hacer con datos vacíos.
    """
    executable = find_executable()
    if not executable:
        return {}

    try:
        proc = subprocess.run(
            [executable, "system-info"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, OSError):
        return {}

    return _parse_system_info(proc.stdout or "")


def _parse_system_info(text: str) -> dict:
    info = {}
    for key, pattern in _SYSTEM_INFO_PATTERNS.items():
        match = re.search(pattern, text)
        if match:
            info[key] = match.group(1).strip()

    version_match = re.search(_VERSION_PATTERN, text)
    if version_match:
        info["pts_version"] = version_match.group(1)

    return info


# ---------------------------------------------------------------------------
# Configuración de "batch mode" (para que PTS corra sin pedir input)
# ---------------------------------------------------------------------------

_BATCH_CONFIG_XML = """<?xml version="1.0"?>
<PhoronixTestSuite>
  <BatchMode>
    <SaveResults>TRUE</SaveResults>
    <OpenBrowser>FALSE</OpenBrowser>
    <UploadResults>FALSE</UploadResults>
    <PromptForTestIdentifier>FALSE</PromptForTestIdentifier>
    <PromptForTestDescription>FALSE</PromptForTestDescription>
    <PromptSaveName>FALSE</PromptSaveName>
    <RunAllTestCombinations>TRUE</RunAllTestCombinations>
    <Configured>TRUE</Configured>
  </BatchMode>
</PhoronixTestSuite>
"""


def ensure_batch_config() -> None:
    """
    Si el usuario nunca corrió `phoronix-test-suite batch-setup`,
    escribe una configuración de batch-mode razonable (no interactiva,
    sin subir resultados a OpenBenchmarking.org) para que
    `batch-benchmark` pueda correr sin bloquearse esperando input.

    Si ya existe un user-config.xml, esta función NO lo toca — se
    respeta la configuración que el usuario ya tenga.
    """
    config_path = os.path.expanduser("~/.phoronix-test-suite/user-config.xml")
    if os.path.exists(config_path):
        return

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as fh:
        fh.write(_BATCH_CONFIG_XML)


# ---------------------------------------------------------------------------
# Ejecutar un benchmark real y leer su resultado
# ---------------------------------------------------------------------------

class PTSBenchmarkError(RuntimeError):
    """Error al ejecutar o parsear un benchmark de Phoronix Test Suite."""


def run_category_benchmark(
    category_key: str,
    test_profile: str,
    hw_info: dict,
    progress_callback=None,
) -> tuple[int, str]:
    """
    Corre un test-profile real de PTS (por ejemplo "pts/compress-7zip")
    y devuelve (score_normalizado, nombre_de_hardware) para esa
    categoría.

    category_key: la key de la categoría ("cpu", "gpu", "ram", "disk").
        Se usa para buscar el factor de escala en config.PTS_SCORE_SCALE
        y el nombre de hardware en hw_info (p.ej. "cpu_name").
    test_profile: identificador del test en OpenBenchmarking.org,
        p.ej. "pts/compress-7zip". Ver config.PTS_TEST_PROFILES.
    hw_info: dict ya obtenido con get_system_info().
    progress_callback: función opcional para reportar avance en texto.
    """
    executable = find_executable()
    if not executable:
        raise PTSBenchmarkError(
            "No se encontró el ejecutable 'phoronix-test-suite'. "
            "Instálalo (ver install_pts.sh / README) o configura "
            "PTS_EXECUTABLE en config.py."
        )

    ensure_batch_config()

    identifier = f"{config.PTS_RESULT_IDENTIFIER_PREFIX}_{category_key}_{int(time.time())}"

    env = os.environ.copy()
    # PTS respeta estas variables de entorno en batch-mode para no
    # preguntar nombre/descripción de la corrida de resultados.
    env["TEST_RESULTS_NAME"] = identifier
    env["TEST_RESULTS_IDENTIFIER"] = identifier
    env["TEST_RESULTS_DESCRIPTION"] = f"Corrida automatica desde benchmark_gui ({category_key})"

    cmd = [executable, "batch-benchmark", test_profile]
    timeout = getattr(config, "PTS_TEST_TIMEOUT_SEC", 1800)

    if progress_callback:
        progress_callback(
            f"Corriendo '{test_profile}' vía Phoronix Test Suite "
            f"(puede tardar varios minutos, y puede descargar el test "
            f"la primera vez)..."
        )

    try:
        proc = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise PTSBenchmarkError(
            f"El test '{test_profile}' superó el tiempo límite de {timeout}s."
        ) from exc
    except OSError as exc:
        raise PTSBenchmarkError(
            f"No se pudo ejecutar phoronix-test-suite: {exc}"
        ) from exc

    if proc.returncode != 0:
        stderr_tail = (proc.stderr or "").strip()[-800:]
        raise PTSBenchmarkError(
            f"phoronix-test-suite devolvió un error al correr "
            f"'{test_profile}' (código {proc.returncode}):\n{stderr_tail}"
        )

    composite_path = os.path.join(config.PTS_RESULTS_DIR, identifier, "composite.xml")
    if not os.path.exists(composite_path):
        composite_path = _find_composite_fallback(identifier)

    if not composite_path or not os.path.exists(composite_path):
        raise PTSBenchmarkError(
            f"'{test_profile}' corrió pero no se encontró el archivo de "
            f"resultados esperado ('{identifier}') en "
            f"{config.PTS_RESULTS_DIR}. Revisa la salida de PTS o corre "
            f"'phoronix-test-suite batch-setup' manualmente una vez."
        )

    score = _score_from_composite(composite_path, category_key)
    hw_name = hw_info.get(f"{category_key}_name", "")

    return score, hw_name


def _find_composite_fallback(identifier: str) -> str | None:
    """
    Último recurso: busca dentro de PTS_RESULTS_DIR una carpeta cuyo
    nombre contenga el identifier (algunas versiones de PTS sanitizan
    el nombre) y devuelve su composite.xml si existe.
    """
    results_dir = config.PTS_RESULTS_DIR
    if not os.path.isdir(results_dir):
        return None

    for entry in sorted(os.listdir(results_dir), reverse=True):
        if identifier in entry:
            candidate = os.path.join(results_dir, entry, "composite.xml")
            if os.path.exists(candidate):
                return candidate
    return None


def _score_from_composite(path: str, category_key: str) -> int:
    """
    Parsea composite.xml y calcula un score entero "estilo videojuego"
    a partir de los valores crudos del test (que vienen en unidades
    muy distintas: MB/s, FPS, segundos, MIPS, etc.).

    Usa <Proportion> (HIB = higher-is-better, LIB = lower-is-better)
    para saber si hay que invertir el valor antes de escalarlo, y
    config.PTS_SCORE_SCALE[category_key] como factor de calibración.
    """
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise PTSBenchmarkError(f"No se pudo leer el XML de resultados: {exc}") from exc

    root = tree.getroot()
    scale = config.PTS_SCORE_SCALE.get(category_key, 1)

    per_result_scores = []
    for result in root.iter("Result"):
        proportion = (result.findtext("Proportion") or "HIB").strip().upper()

        raw_values = []
        for entry in result.iter("Entry"):
            raw_text = entry.findtext("Value")
            if not raw_text:
                continue
            try:
                raw_values.append(float(raw_text.strip().split()[0].replace(",", "")))
            except ValueError:
                continue

        if not raw_values:
            continue

        avg_raw = sum(raw_values) / len(raw_values)

        if proportion == "LIB" and avg_raw > 0:
            # Tiempos/latencias: menor es mejor -> invertimos para que
            # "más rápido" se traduzca en "score más alto".
            per_result_scores.append((scale * 1000.0) / avg_raw)
        else:
            per_result_scores.append(avg_raw * scale)

    if not per_result_scores:
        raise PTSBenchmarkError(
            "El XML de resultados no contenía valores numéricos utilizables."
        )

    return int(round(sum(per_result_scores) / len(per_result_scores)))


# ---------------------------------------------------------------------------
# Diagnóstico rápido desde la línea de comandos:
#   python pts_integration.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    exe = find_executable()
    if not exe:
        print("✗ No se encontró 'phoronix-test-suite'.")
        print("  Instálalo con install_pts.sh o revisa el README.")
    else:
        print(f"✓ phoronix-test-suite encontrado en: {exe}")
        print("Consultando system-info (usa phodevi internamente)...")
        info = get_system_info()
        if not info:
            print("  No se pudo obtener system-info (¿PTS instalado correctamente?).")
        else:
            for key, value in info.items():
                print(f"  {key}: {value}")
