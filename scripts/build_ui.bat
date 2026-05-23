@echo off
REM build_ui.bat - Converte o arquivo .ui do Qt Designer para um módulo Python.
REM
REM Uso:
REM   scripts\build_ui.bat
REM
REM Execute da raiz do projeto ou de qualquer lugar (o script resolve o caminho).

setlocal enabledelayedexpansion

REM Resolve o diretório do projeto (pasta pai de scripts\)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

set "UI_FILE=%PROJECT_DIR%\zpl_viewer.ui"
set "OUTPUT_DIR=%PROJECT_DIR%\lib"
set "OUTPUT_FILE=%OUTPUT_DIR%\ui_zpl_viewer.py"

REM Verifica se o arquivo .ui existe
if not exist "%UI_FILE%" (
    echo Erro: Arquivo .ui nao encontrado em '%UI_FILE%'.
    exit /b 1
)

REM Cria o diretório de saída se não existir
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Localiza o pyside6-uic
set "UIC="
if exist "%PROJECT_DIR%\.venv\Scripts\pyside6-uic.exe" (
    set "UIC=%PROJECT_DIR%\.venv\Scripts\pyside6-uic.exe"
) else (
    where pyside6-uic >nul 2>&1
    if !errorlevel! equ 0 (
        set "UIC=pyside6-uic"
    ) else (
        echo Erro: 'pyside6-uic' nao encontrado. Ative o .venv ou instale o PySide6.
        exit /b 1
    )
)

"%UIC%" "%UI_FILE%" -o "%OUTPUT_FILE%"

if %errorlevel% equ 0 (
    echo OK: UI gerada com sucesso: %OUTPUT_FILE%
) else (
    echo Erro: Falha ao gerar a UI.
    exit /b %errorlevel%
)
