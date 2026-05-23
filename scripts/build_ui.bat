@echo off
REM build_ui.bat - Converte o arquivo .ui do Qt Designer para um módulo Python
REM                e compila o arquivo .qrc de recursos (ícone) para módulo Python.
REM
REM Uso:
REM   scripts\build_ui.bat
REM
REM Execute da raiz do projeto ou de qualquer lugar (o script resolve o caminho).

setlocal enabledelayedexpansion

REM Resolve o diretório do projeto (pasta pai de scripts\)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "LIB_DIR=%PROJECT_DIR%\lib"

set "UI_FILE=%LIB_DIR%\zpl_viewer.ui"
set "QRC_FILE=%LIB_DIR%\logo.qrc"

set "UI_OUTPUT=%LIB_DIR%\ui_zpl_viewer.py"
set "QRC_OUTPUT=%LIB_DIR%\logo.py"

REM Cria o diretório de saída se não existir
if not exist "%LIB_DIR%" mkdir "%LIB_DIR%"

REM --- Localiza pyside6-uic e pyside6-rcc ---
set "UIC="
set "RCC="
if exist "%PROJECT_DIR%\.venv\Scripts\pyside6-uic.exe" (
    set "UIC=%PROJECT_DIR%\.venv\Scripts\pyside6-uic.exe"
    set "RCC=%PROJECT_DIR%\.venv\Scripts\pyside6-rcc.exe"
) else (
    where pyside6-uic >nul 2>&1
    if !errorlevel! equ 0 (
        set "UIC=pyside6-uic"
        set "RCC=pyside6-rcc"
    ) else (
        echo Erro: 'pyside6-uic' nao encontrado. Ative o .venv ou instale o PySide6.
        exit /b 1
    )
)

REM --- Compila UI ---
if not exist "%UI_FILE%" (
    echo Erro: Arquivo .ui nao encontrado em '%UI_FILE%'.
    exit /b 1
)

"%UIC%" "%UI_FILE%" -o "%UI_OUTPUT%"
if !errorlevel! equ 0 (
    echo OK: UI gerada: %UI_OUTPUT%
) else (
    echo Erro: Falha ao gerar a UI.
    exit /b !errorlevel!
)

REM --- Compila recursos (.qrc) ---
if not exist "%QRC_FILE%" (
    echo Aviso: Arquivo .qrc nao encontrado em '%QRC_FILE%'. Recursos nao compilados.
) else (
    "%RCC%" "%QRC_FILE%" -o "%QRC_OUTPUT%"
    if !errorlevel! equ 0 (
        echo OK: Recursos compilados: %QRC_OUTPUT%
    ) else (
        echo Erro: Falha ao compilar recursos.
        exit /b !errorlevel!
    )
)
