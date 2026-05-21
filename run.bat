@echo off
REM ============================================================
REM  Polybilling - Arrancar la aplicacion
REM ============================================================
cd /d "%~dp0"

if not exist venv (
    echo ERROR: no existe la carpeta venv. Ejecuta primero setup.bat
    pause
    exit /b 1
)

echo Verificando que las bases de datos esten corriendo...
docker compose up -d >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo  ERROR: Docker Desktop no esta corriendo.
    echo  Abre Docker Desktop y espera a que diga "Engine running",
    echo  luego vuelve a ejecutar run.bat.
    echo ============================================================
    pause
    exit /b 1
)

powershell -NoProfile -Command "if (-not (Test-NetConnection 127.0.0.1 -Port 3306 -InformationLevel Quiet)) { exit 1 }"
if errorlevel 1 (
    echo.
    echo ============================================================
    echo  AVISO: MySQL local no responde en el puerto 3306.
    echo  Abre Laragon (Start All) o inicia tu servidor MySQL,
    echo  luego vuelve a ejecutar run.bat.
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Aplicacion en  http://localhost:8000
echo  Cierra esta ventana o Ctrl+C para detener la app
echo ============================================================
echo.

call venv\Scripts\python.exe run.py
pause
