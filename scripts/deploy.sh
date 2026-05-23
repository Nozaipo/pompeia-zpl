#!/usr/bin/env bash
#
# deploy.sh - Compila o projeto em um executável .exe via PyInstaller.
#
# Uso:
#   ./scripts/deploy.sh
#
# O executável será gerado em: dist/zpl_viewer.exe

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$PROJECT_DIR/build"
SPEC_FILE="$PROJECT_DIR/zpl_viewer.spec"
MAIN_SCRIPT="$PROJECT_DIR/zpl_viewer.py"
ICON_FILE="$PROJECT_DIR/lib/logo.ico"

echo "=== Build UI ==="
"$SCRIPT_DIR/build_ui.sh"

echo ""
echo "=== PyInstaller ==="

# Verifica se o pyinstaller está disponível
if [ -f "$PROJECT_DIR/.venv/bin/pyinstaller" ]; then
    PYINSTALLER="$PROJECT_DIR/.venv/bin/pyinstaller"
elif command -v pyinstaller &> /dev/null; then
    PYINSTALLER="pyinstaller"
else
    echo "Erro: 'pyinstaller' não encontrado. Instale com: pip install pyinstaller"
    exit 1
fi

# Monta comando base
CMD=("$PYINSTALLER" "--onedir" "--clean" "--windowed" "--name" "zpl_viewer" "--distpath" "$DIST_DIR" "--workpath" "$BUILD_DIR")

# Adiciona o ícone se existir
if [ -f "$ICON_FILE" ]; then
    CMD+=("--icon" "$ICON_FILE")
fi

# Adiciona dados adicionais (arquivos que devem ser incluídos no bundle)
CMD+=("--add-data" "lib/ui_zpl_viewer.py:lib")
CMD+=("--add-data" "lib/logo.py:lib")
CMD+=("--add-data" "lib/__init__.py:lib")

CMD+=("$MAIN_SCRIPT")

# Limpa build anterior (opcional, evita cache corrompido)
rm -rf "$BUILD_DIR"
rm -f "$SPEC_FILE"

"${CMD[@]}"

echo ""
echo "✔ Deploy concluído!"
echo "  Executável: $DIST_DIR/zpl_viewer.exe"
