# Importamos las librerias
import json
import subprocess
import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET


# Descargamos la suite de benchmark

repo_url = 'https://github.com/phoronix-test-suite/phoronix-test-suite.git'

# Constantes para la ejecucion del test

PTS_DIR = Path("phoronix-test-suite")
PTS_LOCATION = str(Path("phoronix-test-suite") / "phoronix-test-suite")
TEST_RUN = ['pts/stream', 'pts/fio', 'pts/stress-ng']

print(f"Iniciando la descarga de la suite Phoronix Test Suite")

if not PTS_DIR.exists():
    try:
        # Ejecutamos el git clone 
        
        resultados = subprocess.run(
            ["git", "clone", repo_url],
            check=True,
            capture_output=True,
            text=True
        )  
        print("CPU: Repositorio descargado con éxito")

    except subprocess.CalledProcessError as e:
        print(f'Detalle del error: \n{e.stderr}')

    except FileNotFoundError:
        print('CPU: Dependencia necesaria, no esta git instalado')

# Instalamos los test

def test_install(test_install: list) -> None:
    terminal = [
        PTS_LOCATION,
        "install",
        *test_install
    ]

    subprocess.run(terminal, stdin=subprocess.DEVNULL, check=True)

test_install(TEST_RUN)

# FIxs de Claude, no dio el tiempo

PTS_BIN = str(Path("phoronix-test-suite") / "phoronix-test-suite")
CONFIG  = Path.home() / ".phoronix-test-suite" / "user-config.xml"
TESTS   = ["pts/stream", "pts/fio", "pts/stress-ng"]

BATCH = {
    "SaveResults":              "TRUE",
    "OpenBrowser":              "FALSE",
    "UploadResults":            "FALSE",
    "PromptForTestIdentifier":  "FALSE",
    "PromptForTestDescription": "FALSE",
    "PromptSaveName":           "FALSE",
    "RunAllTestCombinations":   "FALSE",
    "Configured":               "TRUE",
}

def inicializar_config() -> None:
    """Primera corrida: genera la config por defecto y pasa el user agreement."""
    subprocess.run([PTS_BIN, "version"], input="Y\nN\n", text=True, timeout=120)
    if not CONFIG.exists():
        raise RuntimeError(f"PTS no generó {CONFIG}")

def parchar_pts() -> None:
    archivo = PTS_DIR / "pts-core" / "objects" / "pts_test_run_options.php"
    codigo = archivo.read_text()
    roto  = "$bench_choice = array_keys($option_names);"
    sano  = "$bench_choice = strval($o->get_option_default());"
    if roto in codigo:
        archivo.write_text(codigo.replace(roto, sano))
        print("PTS parchado")

parchar_pts()

def forzar_batch_mode() -> None:
    arbol = ET.parse(CONFIG)
    batch = arbol.getroot().find("./Options/BatchMode")
    for clave, valor in BATCH.items():
        nodo = batch.find(clave)
        if nodo is None:
            nodo = ET.SubElement(batch, clave)
        nodo.text = valor
    arbol.write(CONFIG, encoding="utf-8", xml_declaration=True)

def entorno_pts(identificador: str, nombre: str) -> dict:
    env = os.environ.copy()
    env.update({
        "TEST_RESULTS_NAME":       nombre,
        "TEST_RESULTS_IDENTIFIER": identificador,
        "PTS_SILENT_MODE":         "1",
        # completa con lo que sacaste del grep:
        "PRESET_OPTIONS": "stream.run-type=Copy; fio.mode=...; fio.blocksize=...",
    })
    return env

def correr_test(test: str, identificador: str, timeout: int = 3600) -> None:
    nombre = f"{identificador}_{test.split('/')[-1]}"
    subprocess.run(
        [PTS_BIN, "batch-run", test],
        env=entorno_pts(identificador, nombre),
        stdin=subprocess.DEVNULL,
        timeout=timeout,
        check=True,
    )

inicializar_config()
forzar_batch_mode()
subprocess.run([PTS_BIN, "batch-install", *TESTS],
               stdin=subprocess.DEVNULL, timeout=3600, check=True)

for t in TESTS:
    correr_test(t, "PC_TEST")