"""
native_benchmark.py
====================
Motor de benchmark REAL, autocontenido (Python puro + librería
estándar, `psutil` opcional). No depende de Phoronix Test Suite ni de
PHP — "llegar y ejecutar": pip install -r requirements.txt && python
main.py ya mide TU equipo de verdad.

Metodología para que los resultados sean ESTABLES entre corridas
(bajar la variabilidad típica de ~15% a ~3-5%):

  - Cada categoría corre VARIAS veces (config.NATIVE_*_TRIALS) y se
    reporta la MEDIANA, no el promedio: un solo pico de ruido del
    sistema (otro proceso, pausa de GC, throttling térmico momentáneo)
    no arruina el resultado.
  - Se descarta la primera corrida de CPU y RAM como "warm-up"
    (interpretación de bytecode, caché de CPU L1/L2 frío, etc.).
  - El recolector de basura de Python se desactiva durante cada
    medición para que una pausa de GC no meta ruido en el tiempo.
  - En el test de disco, después de escribir se le pide al SO que
    libere el caché de página de ese archivo (posix_fadvise en Linux,
    no requiere privilegios de root) antes de leer, para medir
    velocidad de disco real y no RAM cacheada — la causa más común de
    resultados de disco inconsistentes entre corridas.

Esto es intencionalmente más pesado (tarda más) que una corrida única:
la idea es cambiar unos segundos extra por resultados reproducibles.
"""

from __future__ import annotations

import gc
import hashlib
import os
import platform
import statistics
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

import config

try:
    import psutil
except ImportError:  # psutil es opcional: si no está, usamos fallbacks.
    psutil = None


# Categorías que este motor SÍ sabe medir de verdad.
AVAILABLE_CATEGORIES = ("cpu", "ram", "disk")


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _cpu_count() -> int:
    """Núcleos REALMENTE asignados a este proceso (respeta límites de
    cgroups/contenedores/afinidad), no solo los físicos del host."""
    if hasattr(os, "sched_getaffinity"):
        try:
            return len(os.sched_getaffinity(0))
        except OSError:
            pass
    return os.cpu_count() or 1


def _median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else 0.0


def _run(cmd, timeout=4):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


# ---------------------------------------------------------------------------
# Detección de hardware (best-effort, multiplataforma, nunca lanza excepción)
# ---------------------------------------------------------------------------

def detect_cpu_name() -> str:
    system = platform.system()
    name = ""

    if system == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    if line.lower().startswith("model name"):
                        name = line.split(":", 1)[1].strip()
                        break
        except OSError:
            pass
    elif system == "Darwin":
        name = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
    elif system == "Windows":
        out = _run(["wmic", "cpu", "get", "name"])
        lines = [ln.strip() for ln in out.splitlines() if ln.strip() and "Name" not in ln]
        if lines:
            name = lines[0]

    if not name:
        name = platform.processor() or platform.uname().processor or "CPU"

    return f"{name} ({_cpu_count()} núcleos)"


def detect_ram_name() -> str:
    total_bytes = None
    if psutil is not None:
        try:
            total_bytes = psutil.virtual_memory().total
        except Exception:
            total_bytes = None

    if total_bytes is None and platform.system() == "Linux":
        try:
            with open("/proc/meminfo", encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        total_bytes = kb * 1024
                        break
        except (OSError, ValueError):
            total_bytes = None

    if total_bytes:
        total_gb = total_bytes / (1024 ** 3)
        return f"{total_gb:.1f} GB RAM"
    return "RAM del sistema"


def detect_disk_name() -> str:
    path = tempfile.gettempdir()
    try:
        if psutil is not None:
            usage = psutil.disk_usage(path)
            return f"Disco del sistema ({usage.total / (1024 ** 3):.0f} GB)"
    except Exception:
        pass
    return "Disco del sistema"


# ---------------------------------------------------------------------------
# CPU: hashes SHA-256/seg, en paralelo, mediana de varias ráfagas
# ---------------------------------------------------------------------------

def _cpu_worker(deadline: float) -> int:
    """Calcula hashes SHA-256 hasta `deadline` (perf_counter). hashlib
    libera el GIL durante el cómputo en C, así que varios hilos sí
    aprovechan varios núcleos aquí."""
    data = os.urandom(4096)
    digest = hashlib.sha256
    count = 0
    while time.perf_counter() < deadline:
        digest(data).digest()
        count += 1
    return count


def _cpu_burst(duration: float, workers: int) -> float:
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        deadline = time.perf_counter() + duration
        with ThreadPoolExecutor(max_workers=workers) as pool:
            counts = list(pool.map(lambda _: _cpu_worker(deadline), range(workers)))
    finally:
        if gc_was_enabled:
            gc.enable()
    return sum(counts) / duration


def _bench_cpu(progress_callback=None) -> tuple[int, str]:
    burst = getattr(config, "NATIVE_CPU_BURST_SEC", 1.0)
    trials = max(2, getattr(config, "NATIVE_CPU_TRIALS", 5))
    workers = _cpu_count()

    if progress_callback:
        total_sec = burst * trials
        progress_callback(
            f"CPU: {trials} ráfagas de hashes SHA-256 en paralelo "
            f"({workers} hilos, ~{total_sec:.1f}s totales) para un resultado estable..."
        )

    samples = []
    for i in range(trials):
        rate = _cpu_burst(burst, workers)
        samples.append(rate)
        if progress_callback:
            progress_callback(f"CPU: ráfaga {i + 1}/{trials} -> {rate:,.0f} hashes/seg")

    # Se descarta la primera ráfaga (warm-up: caché de CPU frío,
    # interpretación de bytecode) y se toma la mediana del resto.
    stable_samples = samples[1:] if len(samples) > 1 else samples
    hashes_per_sec = _median(stable_samples)

    scale = config.NATIVE_SCORE_SCALE.get("cpu", 0.02)
    score = int(round(hashes_per_sec * scale))
    return score, detect_cpu_name()


# ---------------------------------------------------------------------------
# RAM: ancho de banda real de memoria (MB/s), mediana de varias corridas
# ---------------------------------------------------------------------------

def _ram_trial(src: bytearray, dst: bytearray, iterations: int, block_mb: int) -> float:
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        start = time.perf_counter()
        for _ in range(iterations):
            dst[:] = src
        elapsed = time.perf_counter() - start
    finally:
        if gc_was_enabled:
            gc.enable()
    total_mb = block_mb * iterations
    return total_mb / elapsed if elapsed > 0 else 0.0


def _bench_ram(progress_callback=None) -> tuple[int, str]:
    block_mb = getattr(config, "NATIVE_RAM_TEST_MB", 96)
    iterations = getattr(config, "NATIVE_RAM_TEST_ITERATIONS", 10)
    trials = max(2, getattr(config, "NATIVE_RAM_TRIALS", 5))
    size = block_mb * 1024 * 1024

    if progress_callback:
        progress_callback(
            f"RAM: {trials} corridas de {block_mb}MB x{iterations} copias "
            f"para un resultado estable..."
        )

    src = bytearray(os.urandom(size))
    dst = bytearray(size)

    samples = []
    for i in range(trials):
        rate = _ram_trial(src, dst, iterations, block_mb)
        samples.append(rate)
        if progress_callback:
            progress_callback(f"RAM: corrida {i + 1}/{trials} -> {rate:,.0f} MB/s")

    stable_samples = samples[1:] if len(samples) > 1 else samples
    mb_per_sec = _median(stable_samples)

    scale = config.NATIVE_SCORE_SCALE.get("ram", 0.5)
    score = int(round(mb_per_sec * scale))
    return score, detect_ram_name()


# ---------------------------------------------------------------------------
# Disco: velocidad real de escritura/lectura (MB/s), mediana de varias
# corridas, forzando liberar el caché de página entre escritura y lectura
# ---------------------------------------------------------------------------

def _drop_page_cache(fh) -> None:
    """Le pide al SO que descarte el caché de página de este archivo
    (no requiere privilegios de root). Sin esto, la lectura justo
    después de escribir mide velocidad de RAM, no de disco — la causa
    más común de resultados de disco inconsistentes entre corridas."""
    if hasattr(os, "posix_fadvise") and hasattr(os, "POSIX_FADV_DONTNEED"):
        try:
            os.posix_fadvise(fh.fileno(), 0, 0, os.POSIX_FADV_DONTNEED)
        except OSError:
            pass


def _disk_trial(path: str, chunk: bytes, total_mb: int) -> tuple[float, float]:
    chunk_mb = len(chunk) / (1024 * 1024)

    start = time.perf_counter()
    written_mb = 0.0
    with open(path, "wb") as fh:
        while written_mb < total_mb:
            fh.write(chunk)
            written_mb += chunk_mb
        fh.flush()
        os.fsync(fh.fileno())
        _drop_page_cache(fh)
    write_elapsed = time.perf_counter() - start
    write_mbps = written_mb / write_elapsed if write_elapsed > 0 else 0.0

    start = time.perf_counter()
    read_mb = 0.0
    with open(path, "rb") as fh:
        _drop_page_cache(fh)
        while True:
            data = fh.read(4 * 1024 * 1024)
            if not data:
                break
            read_mb += len(data) / (1024 * 1024)
    read_elapsed = time.perf_counter() - start
    read_mbps = read_mb / read_elapsed if read_elapsed > 0 else 0.0

    return write_mbps, read_mbps


def _bench_disk(progress_callback=None) -> tuple[int, str]:
    total_mb = getattr(config, "NATIVE_DISK_TEST_MB", 192)
    trials = max(1, getattr(config, "NATIVE_DISK_TRIALS", 3))
    chunk = os.urandom(4 * 1024 * 1024)  # 4MB, reutilizado

    path = os.path.join(tempfile.gettempdir(), "benchmark_gui_disk_test.tmp")

    if progress_callback:
        progress_callback(
            f"Disco: {trials} corridas de {total_mb}MB (escritura+lectura real, "
            f"sin caché de página) para un resultado estable..."
        )

    write_samples, read_samples = [], []
    try:
        for i in range(trials):
            write_mbps, read_mbps = _disk_trial(path, chunk, total_mb)
            write_samples.append(write_mbps)
            read_samples.append(read_mbps)
            if progress_callback:
                progress_callback(
                    f"Disco: corrida {i + 1}/{trials} -> "
                    f"escritura {write_mbps:,.0f} MB/s, lectura {read_mbps:,.0f} MB/s"
                )
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

    write_mbps = _median(write_samples)
    read_mbps = _median(read_samples)
    # El menor de los dos es la estimación conservadora y honesta del
    # throughput sostenido real del disco.
    effective_mbps = min(write_mbps, read_mbps) if read_mbps > 0 else write_mbps

    scale = config.NATIVE_SCORE_SCALE.get("disk", 4.0)
    score = int(round(effective_mbps * scale))
    return score, detect_disk_name()


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

_BENCH_FUNCS = {
    "cpu": _bench_cpu,
    "ram": _bench_ram,
    "disk": _bench_disk,
}


def run_benchmark(categories, progress_callback=None) -> dict:
    """
    Corre mediciones reales (varias corridas, mediana) para cada
    categoría pedida y devuelve el dict con el mismo formato que
    espera results_window.py:

        {"score": int, "cpu_score": ..., "cpu_name": ..., ...}

    Categorías no soportadas (p.ej. "gpu", "browser") se omiten con un
    aviso por progress_callback, en vez de inventar un valor.
    """
    results = {}
    total = 0
    counted = 0

    for key in categories:
        bench_func = _BENCH_FUNCS.get(key)
        if bench_func is None:
            if progress_callback:
                progress_callback(
                    f"{key.upper()}: no hay test nativo real disponible todavía "
                    f"(se omite, no se inventa un dato)."
                )
            continue

        score, hw_name = bench_func(progress_callback=progress_callback)
        results[f"{key}_score"] = score
        if hw_name:
            results[f"{key}_name"] = hw_name
        total += score
        counted += 1

    if counted:
        results["score"] = total

    return results


# ---------------------------------------------------------------------------
# Diagnóstico rápido desde la línea de comandos:
#   python native_benchmark.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    def _print_progress(msg):
        print(f"  {msg}")

    print("Corriendo benchmark nativo real (CPU, RAM, disco)...")
    result = run_benchmark(list(AVAILABLE_CATEGORIES), progress_callback=_print_progress)
    print()
    for key, value in result.items():
        print(f"{key}: {value}")
