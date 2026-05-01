"""
CLÍNICA VETERINARIA VETCARE - SPRINT 1
Módulos: Gestión de Pacientes, Historial Clínico, Citas
"""

import sqlite3
from datetime import datetime, date

DB_PATH = "vetcare.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def inicializar_bd():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS duenos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
            telefono TEXT, correo TEXT, direccion TEXT, created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS mascotas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
            especie TEXT NOT NULL, raza TEXT, edad REAL, peso REAL,
            dueno_id INTEGER NOT NULL REFERENCES duenos(id), created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS veterinarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
            especialidad TEXT, activo INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, mascota_id INTEGER NOT NULL REFERENCES mascotas(id),
            veterinario_id INTEGER NOT NULL REFERENCES veterinarios(id), fecha TEXT NOT NULL,
            hora TEXT NOT NULL, motivo TEXT, estado TEXT DEFAULT 'Pendiente', created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS historial_clinico (
            id INTEGER PRIMARY KEY AUTOINCREMENT, mascota_id INTEGER NOT NULL REFERENCES mascotas(id),
            veterinario_id INTEGER NOT NULL REFERENCES veterinarios(id), fecha TEXT NOT NULL,
            diagnostico TEXT, tratamiento TEXT, observaciones TEXT, created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS vacunas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, mascota_id INTEGER NOT NULL REFERENCES mascotas(id),
            tipo_vacuna TEXT NOT NULL, fecha_aplicacion TEXT NOT NULL,
            proxima_dosis TEXT, veterinario_id INTEGER REFERENCES veterinarios(id)
        );
    """)
    conn.commit()
    conn.close()
    print("✅ BD inicializada")

class GestionPacientes:
    def registrar_dueno(self, nombre, telefono="", correo="", direccion=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO duenos (nombre, telefono, correo, direccion) VALUES (?,?,?,?)",
                    (nombre, telefono, correo, direccion))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Dueño '{nombre}' ID: {id_}")
        return id_

    def registrar_mascota(self, nombre, especie, dueno_id, raza="", edad=0.0, peso=0.0):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM duenos WHERE id = ?", (dueno_id,))
        if not cur.fetchone():
            conn.close()
            print(f"❌ Dueño ID {dueno_id} no existe")
            return -1
        cur.execute("INSERT INTO mascotas (nombre, especie, raza, edad, peso, dueno_id) VALUES (?,?,?,?,?,?)",
                    (nombre, especie, raza, edad, peso, dueno_id))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Mascota '{nombre}' ID: {id_}")
        return id_

    def listar_mascotas(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.nombre, m.especie, d.nombre AS dueno
            FROM mascotas m JOIN duenos d ON m.dueno_id = d.id ORDER BY m.nombre
        """)
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

    def buscar_mascota(self, termino):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.nombre AS mascota, d.nombre AS dueno
            FROM mascotas m JOIN duenos d ON m.dueno_id = d.id
            WHERE m.nombre LIKE ? OR d.nombre LIKE ?
        """, (f"%{termino}%", f"%{termino}%"))
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

class HistorialClinico:
    def registrar_consulta(self, mascota_id, veterinario_id, diagnostico, tratamiento, observaciones=""):
        conn = get_connection()
        cur = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d")
        cur.execute("""
            INSERT INTO historial_clinico (mascota_id, veterinario_id, fecha, diagnostico, tratamiento, observaciones)
            VALUES (?,?,?,?,?,?)
        """, (mascota_id, veterinario_id, fecha, diagnostico, tratamiento, observaciones))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Consulta ID: {id_}")
        return id_

    def consultar_historial(self, mascota_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT h.fecha, h.diagnostico, h.tratamiento, v.nombre AS veterinario
            FROM historial_clinico h JOIN veterinarios v ON h.veterinario_id = v.id
            WHERE h.mascota_id = ? ORDER BY h.fecha DESC
        """, (mascota_id,))
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

    def registrar_vacuna(self, mascota_id, veterinario_id, tipo_vacuna, proxima_dosis=""):
        conn = get_connection()
        cur = conn.cursor()
        fecha = date.today().isoformat()
        cur.execute("""
            INSERT INTO vacunas (mascota_id, tipo_vacuna, fecha_aplicacion, proxima_dosis, veterinario_id)
            VALUES (?,?,?,?,?)
        """, (mascota_id, tipo_vacuna, fecha, proxima_dosis, veterinario_id))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Vacuna '{tipo_vacuna}' ID: {id_}")
        return id_

class GestionCitas:
    def registrar_veterinario(self, nombre, especialidad=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO veterinarios (nombre, especialidad) VALUES (?,?)", (nombre, especialidad))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Veterinario '{nombre}' ID: {id_}")
        return id_

    def agendar_cita(self, mascota_id, veterinario_id, fecha, hora, motivo=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM citas WHERE veterinario_id = ? AND fecha = ? AND hora = ? AND estado != 'Cancelada'
        """, (veterinario_id, fecha, hora))
        if cur.fetchone():
            conn.close()
            print(f"❌ Horario ocupado")
            return -1
        cur.execute("INSERT INTO citas (mascota_id, veterinario_id, fecha, hora, motivo) VALUES (?,?,?,?,?)",
                    (mascota_id, veterinario_id, fecha, hora, motivo))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Cita ID: {id_} para {fecha} {hora}")
        return id_

    def agenda_del_dia(self, fecha):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.hora, m.nombre AS mascota, v.nombre AS veterinario, c.estado
            FROM citas c JOIN mascotas m ON c.mascota_id = m.id
            JOIN veterinarios v ON c.veterinario_id = v.id WHERE c.fecha = ? ORDER BY c.hora
        """, (fecha,))
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

def imprimir_tabla(registros, titulo=""):
    if titulo:
        print(f"\n{'─'*50}\n  {titulo}\n{'─'*50}")
    if not registros:
        print("  (Sin registros)")
        return
    headers = list(registros[0].keys())
    for r in registros:
        print(f"  {', '.join(f'{k}: {v}' for k, v in r.items())}")

def cargar_datos_iniciales():
    conn = get_connection()
    vacia = conn.execute("SELECT COUNT(*) FROM duenos").fetchone()[0] == 0
    conn.close()
    
    if not vacia:
        print("📦 Datos ya existen, omitiendo carga inicial")
        return
    
    print("📦 Cargando datos iniciales...")
    gp = GestionPacientes()
    hc = HistorialClinico()
    gc = GestionCitas()
    
    d1 = gp.registrar_dueno("Carlos Ramírez", "311-555-1234", "cramirez@email.com")
    d2 = gp.registrar_dueno("María López", "320-777-9999", "mlopez@email.com")
    
    m1 = gp.registrar_mascota("Firulais", "Perro", d1, "Labrador", 3, 20.5)
    m2 = gp.registrar_mascota("Michi", "Gato", d2, "Siamés", 1.5, 4.2)
    
    v1 = gc.registrar_veterinario("Dr. Andrés Torres", "Medicina General")
    v2 = gc.registrar_veterinario("Dra. Paula Ríos", "Cirugía")
    
    gc.agendar_cita(m1, v1, "2026-04-20", "09:00", "Revisión anual")
    gc.agendar_cita(m2, v1, "2026-04-20", "10:00", "Vacuna")
    
    hc.registrar_consulta(m1, v1, "Otitis leve", "Gotas óticas", "Revisar en 1 semana")
    hc.registrar_vacuna(m1, v1, "Rabia", "2027-04-20")
    hc.registrar_vacuna(m2, v1, "Triple felina", "2027-04-20")

def demo_sprint1():
    print("\n" + "═"*50 + "\n  VETCARE - SPRINT 1\n" + "═"*50)
    inicializar_bd()
    cargar_datos_iniciales()
    
    gp = GestionPacientes()
    imprimir_tabla(gp.listar_mascotas(), "MASCOTAS")
    imprimir_tabla(gp.buscar_mascota("Carlos"), "BÚSQUEDA: Carlos")
    print("\n✅ Sprint 1 listo")

if __name__ == "__main__":
    demo_sprint1()