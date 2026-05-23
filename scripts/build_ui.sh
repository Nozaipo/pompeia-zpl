#!/usr/bin/env bash
#
# build_ui.sh - Converte o arquivo .ui do Qt Designer para um módulo Python.
#
# Uso:
#   ./scripts/build_ui.sh
#
# Certifique-se de estar no diretório raiz do projeto ou execute daqui mesmo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

UI_FILE="$PROJECT_DIR/zpl_viewer.ui"
OUTPUT_DIR="$PROJECT_DIR/lib"
OUTPUT_FILE="$OUTPUT_DIR/ui_zpl_viewer.py"

# Verifica se o arquivo .ui existe
if [ ! -f "$UI_FILE" ]; then
    echo "Erro: Arquivo .ui não encontrado em '$UI_FILE'."
    exit 1
fi

# Cria o diretório de saída se não existir
mkdir -p "$OUTPUT_DIR"

# Localiza o pyside6-uic (prioriza o .venv do projeto, depois o global)
if [ -f "$PROJECT_DIR/.venv/bin/pyside6-uic" ]; then
    UIC="$PROJECT_DIR/.venv/bin/pyside6-uic"
elif command -v pyside6-uic &> /dev/null; then
    UIC="pyside6-uic"
else
    echo "Erro: 'pyside6-uic' não encontrado. Ative o .venv ou instale o PySide6."
    exit 1
fi

"$UIC" "$UI_FILE" -o "$OUTPUT_FILE"

echo "✔ UI gerada com sucesso: $OUTPUT_FILE"
