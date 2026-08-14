#!/usr/bin/env bash
#
# install_pts.sh
# ================
# Instala Phoronix Test Suite (PTS) — el proyecto al que pertenece
# "phodevi" (pts-core/objects/phodevi), que es el módulo que PTS usa
# internamente para detectar CPU/GPU/RAM/disco.
#
# phodevi NO es una librería standalone: es parte interna de pts-core y
# solo funciona dentro de la aplicación completa de Phoronix Test
# Suite. Por eso este script instala PTS completo, no solo esa carpeta.
#
# Uso:
#   chmod +x install_pts.sh
#   ./install_pts.sh
#
# Requiere: git y php-cli (el script intenta instalar php-cli si falta
# y detecta apt; en otras distros instala PHP manualmente antes de
# correr esto).

set -e

INSTALL_DIR="${PTS_INSTALL_DIR:-$HOME/phoronix-test-suite}"
REPO_URL="https://github.com/phoronix-test-suite/phoronix-test-suite.git"

echo "== Instalando Phoronix Test Suite en: $INSTALL_DIR =="

# 1) Verifica/instala PHP CLI (requerido por PTS)
if ! command -v php >/dev/null 2>&1; then
    echo "PHP no encontrado."
    if command -v apt-get >/dev/null 2>&1; then
        echo "Instalando php-cli con apt-get (puede pedir tu contraseña)..."
        sudo apt-get update
        sudo apt-get install -y php-cli
    else
        echo "No se detectó apt-get. Instala PHP manualmente para tu"
        echo "distro (por ejemplo: dnf install php-cli / pacman -S php)"
        echo "y vuelve a correr este script."
        exit 1
    fi
fi

# 2) Clona (o actualiza) el repo completo de phoronix-test-suite
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Ya existe una instalación en $INSTALL_DIR, actualizando..."
    git -C "$INSTALL_DIR" pull
else
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

chmod +x "$INSTALL_DIR/phoronix-test-suite"

# 3) Deja un enlace en ~/.local/bin si existe y está en el PATH
LOCAL_BIN="$HOME/.local/bin"
if [ -d "$LOCAL_BIN" ]; then
    ln -sf "$INSTALL_DIR/phoronix-test-suite" "$LOCAL_BIN/phoronix-test-suite"
    echo "Enlace creado en $LOCAL_BIN/phoronix-test-suite"
fi

echo
echo "== Listo =="
echo "Ejecutable: $INSTALL_DIR/phoronix-test-suite"
echo
echo "Si '$LOCAL_BIN' no está en tu PATH, exporta la ruta antes de"
echo "correr main.py, por ejemplo:"
echo "  export PTS_EXECUTABLE=\"$INSTALL_DIR/phoronix-test-suite\""
echo
echo "Prueba rápida (usa phodevi internamente):"
echo "  $INSTALL_DIR/phoronix-test-suite system-info"
