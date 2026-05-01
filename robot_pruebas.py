#!/usr/bin/env python3
"""
ROBOT DE PRUEBAS AUTOMATIZADAS - VETCARE
Ejecuta todas las pruebas sin intervención humana
"""

import subprocess
import sys
import os
import time
from datetime import datetime

class RobotPruebasVetCare:
    def __init__(self):
        self.resultados = {
            "aprobadas": 0,
            "falladas": 0,
            "total": 0,
            "tiempo_ejecucion": 0
        }
    
    def ejecutar_comando(self, comando, descripcion):
        """Ejecuta un comando y retorna el resultado"""
        print(f"\n🔄 {descripcion}...")
        inicio = time.time()
        
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True
        )
        
        fin = time.time()
        return resultado, fin - inicio
    
    def ejecutar_pruebas(self):
        """Ejecuta todas las suites de prueba"""
        
        print("=" * 60)
        print("🐾 ROBOT DE PRUEBAS AUTOMATIZADAS - VETCARE")
        print(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        pruebas = [
            ("pytest tests/test_unitarias.py -v --tb=short", "Pruebas Unitarias"),
            ("pytest tests/test_integracion.py -v --tb=short", "Pruebas de Integración"),
            ("pytest tests/test_reportes.py -v --tb=short", "Pruebas de Reportes"),
        ]
        
        tiempo_total = 0
        
        for comando, descripcion in pruebas:
            resultado, tiempo = self.ejecutar_comando(comando, descripcion)
            tiempo_total += tiempo
            
            if resultado.returncode == 0:
                print(f"✅ {descripcion} completadas en {tiempo:.2f} segundos")
                self.resultados["aprobadas"] += 1
            else:
                print(f"❌ {descripcion} fallaron en {tiempo:.2f} segundos")
                self.resultados["falladas"] += 1
                print(resultado.stdout)
                print(resultado.stderr)
            
            self.resultados["total"] += 1
        
        self.resultados["tiempo_ejecucion"] = tiempo_total
        
        # Ejecutar cobertura
        print("\n📊 Generando reporte de cobertura...")
        subprocess.run("pytest tests/ --cov=. --cov-report=html --cov-report=term", shell=True)
        
        self.mostrar_resumen()
    
    def mostrar_resumen(self):
        """Muestra el resumen final de pruebas"""
        print("\n" + "=" * 60)
        print("📋 RESUMEN FINAL DEL ROBOT")
        print("=" * 60)
        print(f"✅ Pruebas aprobadas: {self.resultados['aprobadas']}")
        print(f"❌ Pruebas falladas: {self.resultados['falladas']}")
        print(f"📊 Total pruebas: {self.resultados['total']}")
        print(f"⏱️  Tiempo total: {self.resultados['tiempo_ejecucion']:.2f} segundos")
        
        if self.resultados['falladas'] == 0:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            print("✅ El sistema está funcionando correctamente")
        else:
            print(f"\n⚠️  Atención: {self.resultados['falladas']} pruebas fallaron")
            print("🔧 Revisar los errores mostrados arriba")
        
        print("=" * 60)
        print("📁 Reporte de cobertura generado en: htmlcov/index.html")
        print("🤖 Robot finalizado automáticamente")

if __name__ == "__main__":
    robot = RobotPruebasVetCare()
    robot.ejecutar_pruebas()
    
    # Esperar 5 segundos antes de cerrar automáticamente
    print("\n🔄 Cerrando robot en 5 segundos...")
    time.sleep(5)