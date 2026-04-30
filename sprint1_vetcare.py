"""
╔══════════════════════════════════════════════════════════════════╗
║         CLÍNICA VETERINARIA VETCARE - SPRINT 1                   ║
║  Módulos: Gestión de Pacientes, Historial Clínico, Citas         ║
║  Equipo: Iván Nazareno, Fernanda Mena, Santiago Pineda           ║
╚══════════════════════════════════════════════════════════════════╝

HU001 - Registro de mascotas y dueños
HU002 - Consulta de historial clínico
HU003 - Agendamiento de citas
"""

import sqlite3
import os
from datetime import datetime, date

# ─────────────────────────────────────────
#  BASE DE DATOS
# ─────────────────────────────────────────

DB_PATH = "vetcare.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_bd():
    """Crea todas las tablas si no existen."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS duenos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            telefono    TEXT,
            correo      TEXT,
            direccion   TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS mascotas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            especie     TEXT NOT NULL,
            raza        TEXT,
            edad        REAL,
            peso        REAL,
            dueno_id    INTEGER NOT NULL REFERENCES duenos(id),
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS veterinarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            especialidad TEXT,
            activo      INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS citas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            mascota_id      INTEGER NOT NULL REFERENCES mascotas(id),
            veterinario_id  INTEGER NOT NULL REFERENCES veterinarios(id),
            fecha           TEXT NOT NULL,
            hora            TEXT NOT NULL,
            motivo          TEXT,
            estado          TEXT DEFAULT 'Pendiente',
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS historial_clinico (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            mascota_id      INTEGER NOT NULL REFERENCES mascotas(id),
            veterinario_id  INTEGER NOT NULL REFERENCES veterinarios(id),
            fecha           TEXT NOT NULL,
            diagnostico     TEXT,
            tratamiento     TEXT,
            observaciones   TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS vacunas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            mascota_id      INTEGER NOT NULL REFERENCES mascotas(id),
            tipo_vacuna     TEXT NOT NULL,
            fecha_aplicacion TEXT NOT NULL,
            proxima_dosis   TEXT,
            veterinario_id  INTEGER REFERENCES veterinarios(id)
        );
    """)

    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente.")


# ─────────────────────────────────────────
#  MÓDULO 1: GESTIÓN DE PACIENTES (HU001)
# ─────────────────────────────────────────

class GestionPacientes:
    """Registro y consulta de mascotas y sus dueños."""

    def registrar_dueno(self, nombre: str, telefono: str = "",
                        correo: str = "", direccion: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO duenos (nombre, telefono, correo, direccion) VALUES (?,?,?,?)",
            (nombre, telefono, correo, direccion)
        )
        conn.commit()
        dueno_id = cur.lastrowid
        conn.close()
        print(f"✅ Dueño '{nombre}' registrado con ID {dueno_id}.")
        return dueno_id

    def registrar_mascota(self, nombre: str, especie: str, dueno_id: int,
                        raza: str = "", edad: float = 0.0,
                        peso: float = 0.0) -> int:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar que el dueño exista
        cur.execute("SELECT id FROM duenos WHERE id = ?", (dueno_id,))
        if not cur.fetchone():
            conn.close()
            print(f"❌ Error: No existe un dueño con ID {dueno_id}.")
            return -1

        cur.execute(
            "INSERT INTO mascotas (nombre, especie, raza, edad, peso, dueno_id) VALUES (?,?,?,?,?,?)",
            (nombre, especie, raza, edad, peso, dueno_id)
        )
        conn.commit()
        mascota_id = cur.lastrowid
        conn.close()
        print(f"✅ Mascota '{nombre}' registrada con ID {mascota_id}.")
        return mascota_id

    def actualizar_mascota(self, mascota_id: int, **kwargs) -> bool:
        campos_permitidos = {"nombre", "especie", "raza", "edad", "peso"}
        campos = {k: v for k, v in kwargs.items() if k in campos_permitidos}
        if not campos:
            print("⚠️  No hay campos válidos para actualizar.")
            return False

        set_clause = ", ".join(f"{k} = ?" for k in campos)
        valores = list(campos.values()) + [mascota_id]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"UPDATE mascotas SET {set_clause} WHERE id = ?", valores)
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Mascota ID {mascota_id} actualizada.")
        else:
            print(f"❌ Mascota ID {mascota_id} no encontrada.")
        return ok

    def eliminar_mascota(self, mascota_id: int) -> bool:
        """Elimina una mascota por ID. No se puede eliminar si tiene citas activas."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) AS total FROM citas WHERE mascota_id = ? AND estado NOT IN ('Cancelada','Completada')",
            (mascota_id,)
        )
        if cur.fetchone()["total"] > 0:
            conn.close()
            print(f"❌ No se puede eliminar: la mascota ID {mascota_id} tiene citas activas.")
            return False
        cur.execute("DELETE FROM mascotas WHERE id = ?", (mascota_id,))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Mascota ID {mascota_id} eliminada.")
        else:
            print(f"❌ Mascota ID {mascota_id} no encontrada.")
        return ok

    def eliminar_dueno(self, dueno_id: int) -> bool:
        """Elimina un dueño por ID. No se puede eliminar si tiene mascotas registradas."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM mascotas WHERE dueno_id = ?", (dueno_id,))
        if cur.fetchone()["total"] > 0:
            conn.close()
            print(f"❌ No se puede eliminar: el dueño ID {dueno_id} tiene mascotas registradas.")
            return False
        cur.execute("DELETE FROM duenos WHERE id = ?", (dueno_id,))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Dueño ID {dueno_id} eliminado.")
        else:
            print(f"❌ Dueño ID {dueno_id} no encontrado.")
        return ok

    def buscar_mascota(self, termino: str) -> list:
        """Búsqueda por nombre de mascota, especie o nombre del dueño."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.nombre AS mascota, m.especie, m.raza, m.edad, m.peso,
                d.nombre AS dueno, d.telefono, d.correo
            FROM mascotas m
            JOIN duenos d ON m.dueno_id = d.id
            WHERE m.nombre LIKE ? OR m.especie LIKE ? OR d.nombre LIKE ?
        """, (f"%{termino}%", f"%{termino}%", f"%{termino}%"))
        resultados = [dict(row) for row in cur.fetchall()]
        conn.close()
        return resultados

    def ver_ficha(self, mascota_id: int) -> dict | None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.*, d.nombre AS dueno, d.telefono, d.correo, d.direccion
            FROM mascotas m
            JOIN duenos d ON m.dueno_id = d.id
            WHERE m.id = ?
        """, (mascota_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def listar_mascotas(self) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.nombre, m.especie, m.raza, m.edad, m.peso,
                d.nombre AS dueno
            FROM mascotas m JOIN duenos d ON m.dueno_id = d.id
            ORDER BY m.nombre
        """)
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados


# ─────────────────────────────────────────
#  MÓDULO 2: HISTORIAL CLÍNICO (HU002)
# ─────────────────────────────────────────

class HistorialClinico:
    """Solo los veterinarios pueden registrar y editar diagnósticos."""

    def registrar_consulta(self, mascota_id: int, veterinario_id: int,
                        diagnostico: str, tratamiento: str,
                        observaciones: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar existencia de mascota y veterinario
        cur.execute("SELECT id FROM mascotas WHERE id = ?", (mascota_id,))
        if not cur.fetchone():
            conn.close()
            print(f"❌ Mascota ID {mascota_id} no encontrada.")
            return -1
        cur.execute("SELECT id FROM veterinarios WHERE id = ?", (veterinario_id,))
        if not cur.fetchone():
            conn.close()
            print(f"❌ Veterinario ID {veterinario_id} no encontrado.")
            return -1

        fecha = datetime.now().strftime("%Y-%m-%d")
        cur.execute("""
            INSERT INTO historial_clinico
                (mascota_id, veterinario_id, fecha, diagnostico, tratamiento, observaciones)
            VALUES (?,?,?,?,?,?)
        """, (mascota_id, veterinario_id, fecha, diagnostico, tratamiento, observaciones))
        conn.commit()
        hist_id = cur.lastrowid
        conn.close()
        print(f"✅ Consulta registrada con ID {hist_id}.")
        return hist_id

    def consultar_historial(self, mascota_id: int) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT h.id, h.fecha, h.diagnostico, h.tratamiento, h.observaciones,
                v.nombre AS veterinario
            FROM historial_clinico h
            JOIN veterinarios v ON h.veterinario_id = v.id
            WHERE h.mascota_id = ?
            ORDER BY h.fecha DESC
        """, (mascota_id,))
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    def eliminar_consulta(self, historial_id: int) -> bool:
        """Elimina un registro del historial clínico por ID."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM historial_clinico WHERE id = ?", (historial_id,))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Consulta ID {historial_id} eliminada del historial.")
        else:
            print(f"❌ Consulta ID {historial_id} no encontrada.")
        return ok

    def eliminar_vacuna(self, vacuna_id: int) -> bool:
        """Elimina un registro de vacuna por ID."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM vacunas WHERE id = ?", (vacuna_id,))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Vacuna ID {vacuna_id} eliminada.")
        else:
            print(f"❌ Vacuna ID {vacuna_id} no encontrada.")
        return ok

    def registrar_vacuna(self, mascota_id: int, veterinario_id: int,
                        tipo_vacuna: str, proxima_dosis: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()
        fecha = date.today().isoformat()
        cur.execute("""
            INSERT INTO vacunas (mascota_id, tipo_vacuna, fecha_aplicacion,
                                proxima_dosis, veterinario_id)
            VALUES (?,?,?,?,?)
        """, (mascota_id, tipo_vacuna, fecha, proxima_dosis, veterinario_id))
        conn.commit()
        vid = cur.lastrowid
        conn.close()
        print(f"✅ Vacuna '{tipo_vacuna}' registrada con ID {vid}.")
        return vid

    def consultar_vacunas(self, mascota_id: int) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT v.id, v.tipo_vacuna, v.fecha_aplicacion, v.proxima_dosis,
                vet.nombre AS veterinario
            FROM vacunas v
            LEFT JOIN veterinarios vet ON v.veterinario_id = vet.id
            WHERE v.mascota_id = ?
            ORDER BY v.fecha_aplicacion DESC
        """, (mascota_id,))
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados


# ─────────────────────────────────────────
#  MÓDULO 3: GESTIÓN DE CITAS (HU003)
# ─────────────────────────────────────────

class GestionCitas:
    """Agendamiento sin duplicación de horarios."""

    def registrar_veterinario(self, nombre: str,
                            especialidad: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO veterinarios (nombre, especialidad) VALUES (?,?)",
            (nombre, especialidad)
        )
        conn.commit()
        vid = cur.lastrowid
        conn.close()
        print(f"✅ Veterinario '{nombre}' registrado con ID {vid}.")
        return vid

    def agendar_cita(self, mascota_id: int, veterinario_id: int,
                    fecha: str, hora: str, motivo: str = "") -> int:
        """Valida que no exista otro turno del mismo veterinario en fecha/hora."""
        conn = get_connection()
        cur = conn.cursor()

        # Verificar duplicado
        cur.execute("""
            SELECT id FROM citas
            WHERE veterinario_id = ? AND fecha = ? AND hora = ?
            AND estado != 'Cancelada'
        """, (veterinario_id, fecha, hora))
        if cur.fetchone():
            conn.close()
            print(f"❌ El veterinario ya tiene una cita el {fecha} a las {hora}.")
            return -1

        cur.execute("""
            INSERT INTO citas (mascota_id, veterinario_id, fecha, hora, motivo)
            VALUES (?,?,?,?,?)
        """, (mascota_id, veterinario_id, fecha, hora, motivo))
        conn.commit()
        cita_id = cur.lastrowid
        conn.close()
        print(f"✅ Cita agendada con ID {cita_id} para el {fecha} a las {hora}.")
        return cita_id

    def cancelar_cita(self, cita_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE citas SET estado = 'Cancelada' WHERE id = ?", (cita_id,)
        )
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Cita ID {cita_id} cancelada.")
        else:
            print(f"❌ Cita ID {cita_id} no encontrada.")
        return ok

    def reprogramar_cita(self, cita_id: int, nueva_fecha: str,
                        nueva_hora: str) -> bool:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener veterinario de la cita
        cur.execute(
            "SELECT veterinario_id FROM citas WHERE id = ?", (cita_id,)
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            print(f"❌ Cita ID {cita_id} no encontrada.")
            return False

        # Verificar que el nuevo horario esté libre
        cur.execute("""
            SELECT id FROM citas
            WHERE veterinario_id = ? AND fecha = ? AND hora = ?
            AND estado != 'Cancelada' AND id != ?
        """, (row["veterinario_id"], nueva_fecha, nueva_hora, cita_id))
        if cur.fetchone():
            conn.close()
            print(f"❌ El veterinario ya tiene cita el {nueva_fecha} a las {nueva_hora}.")
            return False

        cur.execute("""
            UPDATE citas SET fecha = ?, hora = ?, estado = 'Reprogramada'
            WHERE id = ?
        """, (nueva_fecha, nueva_hora, cita_id))
        conn.commit()
        conn.close()
        print(f"✅ Cita ID {cita_id} reprogramada para {nueva_fecha} {nueva_hora}.")
        return True

    def agenda_del_dia(self, fecha: str) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.hora, m.nombre AS mascota, m.especie,
                d.nombre AS dueno, d.telefono,
                v.nombre AS veterinario, c.motivo, c.estado
            FROM citas c
            JOIN mascotas m ON c.mascota_id = m.id
            JOIN duenos d ON m.dueno_id = d.id
            JOIN veterinarios v ON c.veterinario_id = v.id
            WHERE c.fecha = ?
            ORDER BY c.hora
        """, (fecha,))
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    def buscar_citas(self, fecha: str = "", veterinario_id: int = 0,
                    estado: str = "") -> list:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            SELECT c.id, c.fecha, c.hora, c.motivo, c.estado,
                m.nombre AS mascota, v.nombre AS veterinario
            FROM citas c
            JOIN mascotas m ON c.mascota_id = m.id
            JOIN veterinarios v ON c.veterinario_id = v.id
            WHERE 1=1
        """
        params = []
        if fecha:
            query += " AND c.fecha = ?"
            params.append(fecha)
        if veterinario_id:
            query += " AND c.veterinario_id = ?"
            params.append(veterinario_id)
        if estado:
            query += " AND c.estado = ?"
            params.append(estado)
        query += " ORDER BY c.fecha, c.hora"
        cur.execute(query, params)
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados


# ─────────────────────────────────────────
#  HELPERS DE PRESENTACIÓN
# ─────────────────────────────────────────

def imprimir_tabla(registros: list, titulo: str = ""):
    if titulo:
        print(f"\n{'─'*60}")
        print(f"  {titulo}")
        print(f"{'─'*60}")
    if not registros:
        print("  (Sin registros)")
        return
    headers = list(registros[0].keys())
    widths = [max(len(str(h)), max(len(str(r.get(h, ""))) for r in registros)) for h in headers]
    fmt = "  " + "  │  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("  " + "─┼─".join("─" * w for w in widths))
    for r in registros:
        print(fmt.format(*[str(r.get(h, "")) for h in headers]))


# ─────────────────────────────────────────
#  DEMO / PRUEBA
# ─────────────────────────────────────────

def demo_sprint1():
    print("\n" + "═"*60)
    print("  VETCARE - SPRINT 1 DEMO")
    print("═"*60)

    inicializar_bd()

    gp = GestionPacientes()
    hc = HistorialClinico()
    gc = GestionCitas()

    # Datos de prueba
    d1 = gp.registrar_dueno("Carlos Ramírez", "311-555-1234", "cramirez@email.com", "Calle 5 #12")
    d2 = gp.registrar_dueno("María López", "320-777-9999", "mlopez@email.com")

    m1 = gp.registrar_mascota("Firulais", "Perro", d1, "Labrador", 3, 20.5)
    m2 = gp.registrar_mascota("Michi", "Gato", d2, "Siamés", 1.5, 4.2)

    v1 = gc.registrar_veterinario("Dr. Andrés Torres", "Medicina General")
    v2 = gc.registrar_veterinario("Dra. Paula Ríos", "Cirugía")

    # Citas
    gc.agendar_cita(m1, v1, "2026-04-20", "09:00", "Revisión anual")
    gc.agendar_cita(m2, v1, "2026-04-20", "10:00", "Vacuna")
    gc.agendar_cita(m1, v1, "2026-04-20", "09:00", "Duplicado - debe fallar")

    # Historial
    hc.registrar_consulta(m1, v1, "Otitis leve", "Gotas óticas 5 días", "Revisar en 1 semana")
    hc.registrar_vacuna(m1, v1, "Rabia", "2027-04-20")
    hc.registrar_vacuna(m2, v1, "Triple felina", "2027-04-20")

    # Mostrar resultados
    imprimir_tabla(gp.listar_mascotas(), "MASCOTAS REGISTRADAS")
    imprimir_tabla(gc.agenda_del_dia("2026-04-20"), "AGENDA 2026-04-20")
    imprimir_tabla(hc.consultar_historial(m1), f"HISTORIAL CLÍNICO - Mascota ID {m1}")
    imprimir_tabla(hc.consultar_vacunas(m1), f"VACUNAS - Mascota ID {m1}")

    # Búsqueda
    resultados = gp.buscar_mascota("Carlos")
    imprimir_tabla(resultados, "BÚSQUEDA: 'Carlos'")

    print("\n✅ Sprint 1 completado.\n")


if __name__ == "__main__":
    # Limpiar BD anterior para demo limpia
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    demo_sprint1()
