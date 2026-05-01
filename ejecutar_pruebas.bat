@echo off
title PRUEBAS AUTOMATIZADAS - VETCARE
color 0A

echo ========================================
echo   🐾 VETCARE - PRUEBAS AUTOMATIZADAS
echo ========================================
echo.

echo [1/5] Verificando entorno...
cd /d "%~dp0"

echo [2/5] Instalando dependencias...
pip install pytest pytest-qt pytest-cov pytest-xdist --quiet

echo [3/5] Creando estructura de pruebas...
if not exist tests mkdir tests
if not exist tests\__init__.py echo. > tests\__init__.py

echo [4/5] Ejecutando pruebas...
echo.
echo ========================================
echo   📋 RESULTADOS DE LAS PRUEBAS
echo ========================================
echo.

pytest tests/ -v --tb=short --disable-warnings --cov=. --cov-report=term

echo.
echo ========================================
echo   ✅ PRUEBAS FINALIZADAS
echo ========================================
echo.
echo Presiona cualquier tecla para salir...
pause > nul