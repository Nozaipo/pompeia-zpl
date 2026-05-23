@echo off
REM deploy.bat - Compila o projeto em um executável .exe via PyInstaller.
REM
REM Uso:
REM   scripts\deploy.bat
REM
REM O executável será gerado em: dist\zpl_viewer.exe

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

set "DIST_DIR=%PROJECT_DIR%\dist"
set "BUILD_DIR=%PROJECT_DIR%\build"
set "SPEC_FILE=%PROJECT_DIR%\zpl_viewer.spec"
set "MAIN_SCRIPT=%PROJECT_DIR%\zpl_viewer.py"
set "ICON_FILE=%PROJECT_DIR%\lib\logo.ico"

echo === Build UI ===
call "%SCRIPT_DIR%build_ui.bat"

echo.
echo === PyInstaller ===

REM Localiza o pyinstaller
set "PYINSTALLER="
if exist "%PROJECT_DIR%\.venv\Scripts\pyinstaller.exe" (
    set "PYINSTALLER=%PROJECT_DIR%\.venv\Scripts\pyinstaller.exe"
) else (
    where pyinstaller >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYINSTALLER=pyinstaller"
    ) else (
        echo Erro: 'pyinstaller' nao encontrado. Instale com: pip install pyinstaller
        exit /b 1
    )
)

REM Monta comando base
set "CMD=%PYINSTALLER% --onedir --clean --windowed --name zpl_viewer --distpath "%DIST_DIR%" --workpath "%BUILD_DIR%""

REM Adiciona o ícone se existir
if exist "%ICON_FILE%" (
    set "CMD=%CMD% --icon "%ICON_FILE%""
)

REM Adiciona dados adicionais (arquivos que devem ser incluídos no bundle)
set "CMD=%CMD% --add-data "lib\ui_zpl_viewer.py;lib""
set "CMD=%CMD% --add-data "lib\logo.py;lib""
set "CMD=%CMD% --add-data "lib\__init__.py;lib""

set "CMD=%CMD% "%MAIN_SCRIPT%""

REM Limpa build anterior (evita cache corrompido)
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%SPEC_FILE%" del "%SPEC_FILE%"

%CMD%

if !errorlevel! equ 0 (
    echo.
    echo OK: Deploy concluido!
    echo   Executavel: %DIST_DIR%\zpl_viewer.exe
) else (
    echo.
    echo Erro: Falha no deploy.
    exit /b !errorlevel!
)
