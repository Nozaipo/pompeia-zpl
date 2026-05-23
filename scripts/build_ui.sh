#!/usr/bin/env bash
#
# build_ui.sh - Converte o arquivo .ui do Qt Designer para um módulo Python
#               e compila o arquivo .qrc de recursos (ícone) para módulo Python.
#
# Uso:
#   ./scripts/build_ui.sh
#
# Certifique-se de estar no diretório raiz do projeto ou execute daqui mesmo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LIB_DIR="$PROJECT_DIR/lib"

UI_FILE="$LIB_DIR/zpl_viewer.ui"
QRC_FILE="$LIB_DIR/logo.qrc"

UI_OUTPUT="$LIB_DIR/ui_zpl_viewer.py"
QRC_OUTPUT="$LIB_DIR/logo.py"

mkdir -p "$LIB_DIR"

# --- Localiza pyside6-uic e pyside6-rcc ---
if [ -f "$PROJECT_DIR/.venv/bin/pyside6-uic" ]; then
    UIC="$PROJECT_DIR/.venv/bin/pyside6-uic"
    RCC="$PROJECT_DIR/.venv/bin/pyside6-rcc"
elif command -v pyside6-uic &> /dev/null; then
    UIC="pyside6-uic"
    RCC="pyside6-rcc"
else
    echo "Erro: 'pyside6-uic' não encontrado. Ative o .venv ou instale o PySide6."
    exit 1
fi

# --- Compila UI ---
if [ ! -f "$UI_FILE" ]; then
    echo "Erro: Arquivo .ui não encontrado em '$UI_FILE'."
    exit 1
fi

"$UIC" "$UI_FILE" -o "$UI_OUTPUT"
echo "✔ UI gerada: $UI_OUTPUT"

# --- Compila recursos (.qrc) ---
if [ ! -f "$QRC_FILE" ]; then
    echo "Aviso: Arquivo .qrc não encontrado em '$QRC_FILE'. Recursos não compilados."
else
    "$RCC" "$QRC_FILE" -o "$QRC_OUTPUT"
    echo "✔ Recursos compilados: $QRC_OUTPUT"
fi
