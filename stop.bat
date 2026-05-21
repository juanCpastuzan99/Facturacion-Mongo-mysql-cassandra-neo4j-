@echo off
REM ============================================================
REM  Polybilling - Detener las bases de datos
REM ============================================================
cd /d "%~dp0"

echo Deteniendo Cassandra, MongoDB, MySQL y Neo4j...
docker compose stop

echo.
echo Las bases de datos quedan apagadas pero conservan sus datos.
echo Para apagarlas y BORRAR todo:  docker compose down -v
echo.
pause
