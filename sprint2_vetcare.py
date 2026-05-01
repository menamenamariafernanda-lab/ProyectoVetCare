"""
CLÍNICA VETERINARIA VETCARE - SPRINT 2
Módulos: Diagnósticos, Tratamientos, Vacunas, Modificar Citas
"""

import sqlite3
from datetime import date

DB_PATH = "vetcare.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def ampliar_bd_sprint2():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS tratamientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, historial_id INTEGER REFERENCES historial_clinico(id),
            mascota_id INTEGER NOT NULL REFERENCES mascotas(id), medicamento TEXT NOT NULL,
            dosis TEXT, frecuencia TEXT, fecha_inicio TEXT, fecha_fin TEXT,
            estado TEXT DEFAULT 'En curso', observaciones TEXT
        );
        CREATE TABLE IF NOT EXISTS cirugias (
            id INTEGER PRIMARY KEY AUTOINCREMENT, mascota_id INTEGER NOT NULL REFERENCES mascotas(id),
            veterinario_id INTEGER NOT NULL REFERENCES veterinarios(id), fecha TEXT NOT NULL,
            procedimiento TEXT NOT NULL, anestesia TEXT, duracion_min INTEGER,
            observaciones TEXT, estado TEXT DEFAULT 'Realizada'
        );
        CREATE TABLE IF NOT EXISTS postoperatorio (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cirugia_id INTEGER NOT NULL REFERENCES cirugias(id),
            fecha TEXT NOT NULL, evolucion TEXT, tratamiento TEXT, notificado_dueno INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()
    print("✅ BD extendida Sprint 2")

class GestionDiagnosticos:
    def registrar_diagnostico(self, mascota_id, veterinario_id, diagnostico, tratamiento, observaciones=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO historial_clinico (mascota_id, veterinario_id, fecha, diagnostico, tratamiento, observaciones)
            VALUES (?,?,?,?,?,?)
        """, (mascota_id, veterinario_id, date.today().isoformat(), diagnostico, tratamiento, observaciones))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Diagnóstico ID: {id_}")
        return id_

    def registrar_tratamiento(self, mascota_id, historial_id, medicamento, dosis, frecuencia, fecha_inicio, fecha_fin, observaciones=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tratamientos (historial_id, mascota_id, medicamento, dosis, frecuencia, fecha_inicio, fecha_fin, observaciones)
            VALUES (?,?,?,?,?,?,?,?)
        """, (historial_id, mascota_id, medicamento, dosis, frecuencia, fecha_inicio, fecha_fin, observaciones))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Tratamiento ID: {id_}")
        return id_

    def consultar_tratamientos(self, mascota_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, medicamento, dosis, estado FROM tratamientos WHERE mascota_id = ?", (mascota_id,))
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

class GestionVacunas:
    def registrar_vacuna(self, mascota_id, veterinario_id, tipo_vacuna, proxima_dosis=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vacunas (mascota_id, tipo_vacuna, fecha_aplicacion, proxima_dosis, veterinario_id)
            VALUES (?,?,?,?,?)
        """, (mascota_id, tipo_vacuna, date.today().isoformat(), proxima_dosis, veterinario_id))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Vacuna ID: {id_}")
        return id_

    def vacunas_proximas(self, dias=30):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.nombre AS mascota, v.tipo_vacuna, v.proxima_dosis
            FROM vacunas v JOIN mascotas m ON v.mascota_id = m.id
            WHERE v.proxima_dosis != '' AND julianday(v.proxima_dosis) - julianday('now') BETWEEN 0 AND ?
        """, (dias,))
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

class GestionCitasAvanzada:
    def modificar_cita(self, cita_id, nueva_fecha, nueva_hora, nuevo_motivo=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT veterinario_id, estado FROM citas WHERE id = ?", (cita_id,))
        cita = cur.fetchone()
        if not cita or cita["estado"] == "Cancelada":
            conn.close()
            print("❌ Cita no existe o está cancelada")
            return False
        cur.execute("SELECT id FROM citas WHERE veterinario_id = ? AND fecha = ? AND hora = ? AND id != ?",
                    (cita["veterinario_id"], nueva_fecha, nueva_hora, cita_id))
        if cur.fetchone():
            conn.close()
            print("❌ Horario ocupado")
            return False
        cur.execute("UPDATE citas SET fecha = ?, hora = ?, estado = 'Reprogramada' WHERE id = ?",
                    (nueva_fecha, nueva_hora, cita_id))
        conn.commit()
        conn.close()
        print(f"✅ Cita reprogramada para {nueva_fecha} {nueva_hora}")
        return True

    def cancelar_cita(self, cita_id, motivo=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE citas SET estado = 'Cancelada' WHERE id = ?", (cita_id,))
        ok = cur.rowcount > 0
        conn.commit()
        conn.close()
        if ok:
            print(f"✅ Cita cancelada. Motivo: {motivo or 'No especificado'}")
        return ok

def imprimir_tabla(registros, titulo=""):
    if titulo:
        print(f"\n{'─'*50}\n  {titulo}\n{'─'*50}")
    if not registros:
        print("  (Sin registros)")
        return
    for r in registros:
        print(f"  {', '.join(f'{k}: {v}' for k, v in r.items())}")

def demo_sprint2():
    print("\n" + "═"*50 + "\n  VETCARE - SPRINT 2\n" + "═"*50)
    ampliar_bd_sprint2()
    
    conn = get_connection()
    mascotas = [r["id"] for r in conn.execute("SELECT id FROM mascotas LIMIT 2")]
    veterinarios = [r["id"] for r in conn.execute("SELECT id FROM veterinarios LIMIT 1")]
    conn.close()
    
    if not mascotas or not veterinarios:
        print("⚠️ Ejecuta primero sprint1_vetcare.py")
        return
    
    gd = GestionDiagnosticos()
    gv = GestionVacunas()
    gc = GestionCitasAvanzada()
    
    # Demo
    hist_id = gd.registrar_diagnostico(mascotas[0], veterinarios[0], "Dermatitis", "Antihistamínico")
    gd.registrar_tratamiento(mascotas[0], hist_id, "Cetirizina", "5mg", "1/día", "2026-04-15", "2026-04-30")
    
    gv.registrar_vacuna(mascotas[0], veterinarios[0], "Rabia", "2027-04-15")
    
    imprimir_tabla(gd.consultar_tratamientos(mascotas[0]), "TRATAMIENTOS")
    imprimir_tabla(gv.vacunas_proximas(365), "VACUNAS PRÓXIMAS")
    
    print("\n✅ Sprint 2 listo")

if __name__ == "__main__":
    demo_sprint2()