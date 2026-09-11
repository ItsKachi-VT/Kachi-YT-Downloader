@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: =========================
:: Kachi Downloader - Instalador Windows
:: =========================

TITLE Kachi Downloader - Instalador
COLOR 0B

set "ROOT=%~dp0"
set "VENV_DIR=%ROOT%.venv"
set "REQUIREMENTS=%ROOT%requirements.txt"
set "APP=%ROOT%app.py"

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [1/4] Python no encontrado. Intentando instalarlo con Winget...
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo ERROR: No se pudo instalar Python automaticamemte.
        echo Instala Python 3.12 desde: https://www.python.org/downloads/windows/
        pause
        exit /b 1
    )
    set "PYTHON_CMD=py"
)

echo [1/4] Validando entorno Python...
call %PYTHON_CMD% --version >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python existe pero no se pudo ejecutar correctamente.
    echo Verifica que Python este instalado correctamente y vuelve a intentarlo.
    pause
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [2/4] Creando entorno virtual...
    call %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo [2/4] El entorno virtual ya existe.
)

echo [3/4] Instalando dependencias...
call "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Fallo al actualizar pip.
    pause
    exit /b 1
)

call "%VENV_DIR%\Scripts\python.exe" -m pip install -r "%REQUIREMENTS%"
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    echo Revisa tu conexion a internet o intenta instalar manualmente con:
    echo   %VENV_DIR%\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "%APP%" (
    echo ERROR: No se encontro app.py en esta carpeta.
    pause
    exit /b 1
)

echo [4/4] Iniciando Kachi Downloader...
start "Kachi Downloader" "%VENV_DIR%\Scripts\python.exe" "%APP%"

if errorlevel 1 (
    echo ERROR: La aplicacion no pudo iniciarse.
    pause
    exit /b 1
)

echo Instalacion completada.
exit /b 0