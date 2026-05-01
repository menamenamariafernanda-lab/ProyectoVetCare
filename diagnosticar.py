"""
DIAGNÓSTICO RÁPIDO - VETCARE
Ejecutar para identificar problemas
"""

import sys
import os
import traceback

print("=" * 60)
print("🔍 DIAGNÓSTICO DEL SISTEMA VETCARE")
print("=" * 60)

# 1. Verificar archivo principal
print("\n[1] Verificando archivo principal...")
try:
    import sprint4_vetcare
    print("✅ sprint4_vetcare.py encontrado")
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# 2. Verificar base de datos
print("\n[2] Verificando base de datos...")
try:
    from sprint4_vetcare import get_connection, ampliar_bd_sprint4
    ampliar_bd_sprint4()
    conn = get_connection()
    print("✅ Conexión a BD exitosa")
    conn.close()
except Exception as e:
    print(f"❌ Error en BD: {e}")

# 3. Verificar clases principales
print("\n[3] Verificando clases principales...")
try:
    from sprint4_vetcare import GestionUsuarios, GestionFacturacion, GestionReportes
    gu = GestionUsuarios()
    print("✅ GestionUsuarios OK")
    gf = GestionFacturacion()
    print("✅ GestionFacturacion OK")
    gr = GestionReportes()
    print("✅ GestionReportes OK")
except Exception as e:
    print(f"❌ Error en clases: {e}")
    traceback.print_exc()

# 4. Verificar estructura de tablas
print("\n[4] Verificando tablas en BD...")
try:
    conn = get_connection()
    tablas = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"📊 Tablas encontradas: {[t['name'] for t in tablas]}")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")

# 5. Verificar datos de prueba
print("\n[5] Verificando datos de prueba...")
try:
    conn = get_connection()
    duenos = conn.execute("SELECT COUNT(*) FROM duenos").fetchone()[0]
    mascotas = conn.execute("SELECT COUNT(*) FROM mascotas").fetchone()[0]
    print(f"✅ Dueños: {duenos}, Mascotas: {mascotas}")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("📋 Diagnóstico completado")
print("=" * 60)