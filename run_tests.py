#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas automatizadas
Ejecutar: python run_tests.py
"""

import sys
import subprocess
import os


def run_tests():
    """Ejecuta todas las pruebas con diferentes opciones"""
    
    print("=" * 60)
    print("🐾 EJECUTANDO PRUEBAS AUTOMATIZADAS - VETCARE")
    print("=" * 60)
    
    tests_passed = True
    
    # 1. Ejecutar pruebas unitarias
    print("\n📋 1. Pruebas Unitarias")
    print("-" * 40)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_unitarias.py", "-v", "--tb=short"],
        capture_output=False
    )
    if result.returncode != 0:
        tests_passed = False
    
    # 2. Ejecutar pruebas de reportes
    print("\n📊 2. Pruebas de Reportes")
    print("-" * 40)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_reportes.py", "-v", "--tb=short"],
        capture_output=False
    )
    if result.returncode != 0:
        tests_passed = False
    
    # 3. Ejecutar pruebas de integración
    print("\n🔗 3. Pruebas de Integración")
    print("-" * 40)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_integracion.py", "-v", "--tb=short"],
        capture_output=False
    )
    if result.returncode != 0:
        tests_passed = False
    
    # 4. Ejecutar todas las pruebas con cobertura
    print("\n📈 4. Pruebas con Cobertura de Código")
    print("-" * 40)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--cov=.", "--cov-report=term", "--cov-report=html"],
        capture_output=False
    )
    
    # Resumen final
    print("\n" + "=" * 60)
    if tests_passed:
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("📁 Reporte de cobertura generado en: htmlcov/index.html")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON - Revisar resultados arriba")
    print("=" * 60)
    
    return 0 if tests_passed else 1


if __name__ == "__main__":
    sys.exit(run_tests())