@echo off
REM ============================================================
REM  Polybilling - Instalacion inicial (ejecutar UNA sola vez)
REM ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo  Polybilling - Setup inicial
echo ============================================================
echo.
echo  ANTES DE CONTINUAR, ASEGURATE DE TENER ABIERTOS:
echo    [1] Docker Desktop  (con la ballena fija = "Engine running")
echo    [2] MySQL local     (Laragon Start All, o tu MySQL Server)
echo.
echo  Pulsa cualquier tecla cuando ambos esten corriendo...
pause >nul
echo.

REM --- 1) Verificar Python ----------------------------------------------
echo [1/7] Verificando Python 3.12...
where python >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python no esta en el PATH.
    echo   Instala Python 3.12 desde https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version

REM --- 2) Verificar Docker ----------------------------------------------
echo.
echo [2/7] Verificando Docker Desktop...
docker --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Docker no esta instalado o no esta corriendo.
    echo   Descargalo desde https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
docker --version

REM --- 3) Verificar MySQL local -----------------------------------------
echo.
echo [3/7] Verificando MySQL local (puerto 3306)...
powershell -NoProfile -Command "if (-not (Test-NetConnection 127.0.0.1 -Port 3306 -InformationLevel Quiet)) { exit 1 }"
if errorlevel 1 (
    echo.
    echo   AVISO: No se detecto MySQL local en el puerto 3306.
    echo   Necesitas tener un servidor MySQL/MariaDB corriendo. Opciones:
    echo     - Laragon       https://laragon.org/download/  (mas facil en Windows)
    echo     - MySQL Server  https://dev.mysql.com/downloads/installer/
    echo     - XAMPP         https://www.apachefriends.org/
    echo   Despues edita .env si tu MySQL usa otro usuario/password.
    echo.
    pause
)

REM --- 4) Crear venv ----------------------------------------------------
echo.
echo [4/7] Creando entorno virtual (venv)...
if not exist venv (
    python -m venv venv
) else (
    echo   venv ya existe, lo reutilizo.
)

REM --- 5) Instalar dependencias -----------------------------------------
echo.
echo [5/7] Instalando dependencias (puede tardar 1-2 minutos)...
call venv\Scripts\python.exe -m pip install --upgrade pip --quiet
call venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo   ERROR: fallo pip install. Revisa la conexion a internet.
    pause
    exit /b 1
)

REM --- 6) Levantar Cassandra, MongoDB y Neo4j en Docker -----------------
echo.
echo [6/7] Levantando Cassandra, MongoDB y Neo4j con Docker...
docker compose up -d
if errorlevel 1 (
    echo   ERROR: fallo docker compose up. Asegurate que Docker Desktop este corriendo.
    pause
    exit /b 1
)

echo.
echo   Esperando 60 segundos a que Cassandra arranque (es el mas lento)...
timeout /t 60 /nobreak >nul

REM --- 7) Cargar datos semilla en los 4 motores -------------------------
echo.
echo [7/7] Cargando datos semilla en los 4 motores...
call venv\Scripts\python.exe dbs\seed_all.py
if errorlevel 1 (
    echo   AVISO: el seed reporto algun error. Reintentalo con:
    echo     venv\Scripts\python.exe dbs\seed_all.py
)

echo.
echo ============================================================
echo  Setup terminado. Para arrancar la app: doble clic en run.bat
echo  o ejecuta:  venv\Scripts\python.exe run.py
echo  Despues abre http://localhost:8000 en tu navegador
echo ============================================================
echo.
pause
