"""
╔══════════════════════════════════════════════════════════════════╗
║         CLÍNICA VETERINARIA VETCARE - SPRINT 2                   ║
║  Módulos: Diagnósticos, Tratamientos, Vacunas, Modificar Citas   ║
║  Equipo: Iván Nazareno, Fernanda Mena, Santiago Pineda           ║
╚══════════════════════════════════════════════════════════════════╝

HU004 - Registrar diagnósticos y tratamientos (Veterinario)
HU005 - Registrar vacunas aplicadas
HU006 - Modificar o cancelar citas (Recepcionista)

NOTA: Este sprint extiende la BD del Sprint 1.
    Ejecutar primero sprint1_vetcare.py para crear la BD base.
"""

import sqlite3
from datetime import datetime, date

DB_PATH = "vetcare.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ─────────────────────────────────────────
#  EXTENSIÓN DE TABLAS PARA SPRINT 2
# ─────────────────────────────────────────

def ampliar_bd_sprint2():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS tratamientos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            historial_id    INTEGER REFERENCES historial_clinico(id),
            mascota_id      INTEGER NOT NULL REFERENCES mascotas(id),
            medicamento     TEXT NOT NULL,
            dosis           TEXT,
            frecuencia      TEXT,
            fecha_inicio    TEXT,
            fecha_fin       TEXT,
            estado          TEXT DEFAULT 'En curso',
            observaciones   TEXT
        );

        CREATE TABLE IF NOT EXISTS cirugias (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            mascota_id      INTEGER NOT NULL REFERENCES mascotas(id),
            veterinario_id  INTEGER NOT NULL REFERENCES veterinarios(id),
            fecha           TEXT NOT NULL,
            procedimiento   TEXT NOT NULL,
            anestesia       TEXT,
            duracion_min    INTEGER,
            observaciones   TEXT,
            estado          TEXT DEFAULT 'Realizada'
        );

        CREATE TABLE IF NOT EXISTS postoperatorio (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            cirugia_id      INTEGER NOT NULL REFERENCES cirugias(id),
            fecha           TEXT NOT NULL,
            evolucion       TEXT,
            tratamiento     TEXT,
            notificado_dueno INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()
    print("✅ BD extendida para Sprint 2.")


# ─────────────────────────────────────────
#  HU004 - DIAGNÓSTICOS Y TRATAMIENTOS
# ─────────────────────────────────────────

class GestionDiagnosticos:
    """
    Solo veterinarios pueden registrar/editar diagnósticos.
    El rol se valida antes de llamar estos métodos (ver capa de autenticación, Sprint 4).
    """

    def registrar_diagnostico(self, mascota_id: int, veterinario_id: int,
                            diagnostico: str, tratamiento_texto: str,
                            observaciones: str = "") -> int:
        """Guarda una entrada en historial_clinico."""
        conn = get_connection()
        cur = conn.cursor()

        fecha = date.today().isoformat()
        cur.execute("""
            INSERT INTO historial_clinico
                (mascota_id, veterinario_id, fecha, diagnostico, tratamiento, observaciones)
            VALUES (?,?,?,?,?,?)
        """, (mascota_id, veterinario_id, fecha, diagnostico,
            tratamiento_texto, observaciones))
        conn.commit()
        hist_id = cur.lastrowid
        conn.close()
        print(f"✅ Diagnóstico registrado (historial ID {hist_id}).")
        return hist_id

    def registrar_tratamiento(self, mascota_id: int, historial_id: int,
                            medicamento: str, dosis: str,
                            frecuencia: str, fecha_inicio: str,
                            fecha_fin: str, observaciones: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tratamientos
                (historial_id, mascota_id, medicamento, dosis, frecuencia,
                fecha_inicio, fecha_fin, observaciones)
            VALUES (?,?,?,?,?,?,?,?)
        """, (historial_id, mascota_id, medicamento, dosis, frecuencia,
            fecha_inicio, fecha_fin, observaciones))
        conn.commit()
        trat_id = cur.lastrowid
        conn.close()
        print(f"✅ Tratamiento '{medicamento}' registrado (ID {trat_id}).")
        return trat_id

    def actualizar_estado_tratamiento(self, tratamiento_id: int,
                                    nuevo_estado: str) -> bool:
        estados_validos = {"En curso", "Completado", "Suspendido"}
        if nuevo_estado not in estados_validos:
            print(f"❌ Estado inválido. Opciones: {estados_validos}")
            return False
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tratamientos SET estado = ? WHERE id = ?",
            (nuevo_estado, tratamiento_id)
        )
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Tratamiento ID {tratamiento_id} → {nuevo_estado}.")
        return ok

    def consultar_tratamientos(self, mascota_id: int) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id, t.medicamento, t.dosis, t.frecuencia,
                t.fecha_inicio, t.fecha_fin, t.estado, t.observaciones
            FROM tratamientos t
            WHERE t.mascota_id = ?
            ORDER BY t.fecha_inicio DESC
        """, (mascota_id,))
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    def evolucion_mascota(self, mascota_id: int) -> list:
        """Historial completo: diagnósticos + tratamientos."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT h.fecha, h.diagnostico, h.tratamiento, h.observaciones,
                v.nombre AS veterinario,
                GROUP_CONCAT(t.medicamento || ' (' || t.dosis || ')', ' | ') AS medicamentos
            FROM historial_clinico h
            JOIN veterinarios v ON h.veterinario_id = v.id
            LEFT JOIN tratamientos t ON t.historial_id = h.id
            WHERE h.mascota_id = ?
            GROUP BY h.id
            ORDER BY h.fecha DESC
        """, (mascota_id,))
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados


# ─────────────────────────────────────────
#  HU005 - VACUNAS
# ─────────────────────────────────────────

class GestionVacunas:
    """Control de vacunación y alertas de próxima dosis."""

    def registrar_vacuna(self, mascota_id: int, veterinario_id: int,
                        tipo_vacuna: str, proxima_dosis: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()
        fecha = date.today().isoformat()
        cur.execute("""
            INSERT INTO vacunas
                (mascota_id, tipo_vacuna, fecha_aplicacion, proxima_dosis, veterinario_id)
            VALUES (?,?,?,?,?)
        """, (mascota_id, tipo_vacuna, fecha, proxima_dosis, veterinario_id))
        conn.commit()
        vid = cur.lastrowid
        conn.close()
        print(f"✅ Vacuna '{tipo_vacuna}' registrada (ID {vid}). Próxima: {proxima_dosis or 'N/A'}")
        return vid

    def vacunas_proximas(self, dias: int = 30) -> list:
        """Mascotas con vacuna próxima dentro de N días."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.nombre AS mascota, m.especie, d.nombre AS dueno,
                d.correo, d.telefono, v.tipo_vacuna, v.proxima_dosis
            FROM vacunas v
            JOIN mascotas m ON v.mascota_id = m.id
            JOIN duenos d ON m.dueno_id = d.id
            WHERE v.proxima_dosis IS NOT NULL
            AND v.proxima_dosis != ''
            AND julianday(v.proxima_dosis) - julianday('now') BETWEEN 0 AND ?
            ORDER BY v.proxima_dosis
        """, (dias,))
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    def historial_vacunas(self, mascota_id: int) -> list:
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
#  HU006 - MODIFICAR/CANCELAR CITAS
# ─────────────────────────────────────────

class GestionCitasAvanzada:
    """Extensión de citas: modificar, cancelar con notificación al veterinario."""

    def modificar_cita(self, cita_id: int, nueva_fecha: str,
                    nueva_hora: str, nuevo_motivo: str = "") -> bool:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT veterinario_id, estado FROM citas WHERE id = ?", (cita_id,)
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            print(f"❌ Cita ID {cita_id} no existe.")
            return False
        if row["estado"] == "Cancelada":
            conn.close()
            print("❌ No se puede modificar una cita cancelada.")
            return False

        # Validar duplicado
        cur.execute("""
            SELECT id FROM citas
            WHERE veterinario_id = ? AND fecha = ? AND hora = ?
            AND estado NOT IN ('Cancelada') AND id != ?
        """, (row["veterinario_id"], nueva_fecha, nueva_hora, cita_id))
        if cur.fetchone():
            conn.close()
            print(f"❌ Horario {nueva_fecha} {nueva_hora} no disponible.")
            return False

        update_fields = "fecha = ?, hora = ?, estado = 'Reprogramada'"
        params = [nueva_fecha, nueva_hora]
        if nuevo_motivo:
            update_fields += ", motivo = ?"
            params.append(nuevo_motivo)
        params.append(cita_id)

        cur.execute(f"UPDATE citas SET {update_fields} WHERE id = ?", params)
        conn.commit()
        conn.close()

        self._notificar_veterinario(row["veterinario_id"], cita_id,
                                    nueva_fecha, nueva_hora)
        print(f"✅ Cita ID {cita_id} reprogramada para {nueva_fecha} {nueva_hora}.")
        return True

    def cancelar_cita(self, cita_id: int, motivo_cancelacion: str = "") -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT veterinario_id FROM citas WHERE id = ?", (cita_id,)
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            print(f"❌ Cita ID {cita_id} no existe.")
            return False

        cur.execute(
            "UPDATE citas SET estado = 'Cancelada' WHERE id = ?", (cita_id,)
        )
        conn.commit()
        conn.close()
        self._notificar_veterinario(row["veterinario_id"], cita_id,
                                    cancelada=True)
        print(f"✅ Cita ID {cita_id} cancelada. Motivo: {motivo_cancelacion or 'No especificado'}")
        return True

    def _notificar_veterinario(self, vet_id: int, cita_id: int,
                                nueva_fecha: str = "", nueva_hora: str = "",
                                cancelada: bool = False):
        """Simula notificación (en producción: envío de email/SMS)."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT nombre FROM veterinarios WHERE id = ?", (vet_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            if cancelada:
                print(f"📨 Notificación a {row['nombre']}: Cita #{cita_id} cancelada.")
            else:
                print(f"📨 Notificación a {row['nombre']}: Cita #{cita_id} → {nueva_fecha} {nueva_hora}.")

    def citas_por_mascota(self, mascota_id: int) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.fecha, c.hora, c.motivo, c.estado,
                v.nombre AS veterinario
            FROM citas c
            JOIN veterinarios v ON c.veterinario_id = v.id
            WHERE c.mascota_id = ?
            ORDER BY c.fecha DESC, c.hora DESC
        """, (mascota_id,))
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados


# ─────────────────────────────────────────
#  CIRUGÍAS Y POSTOPERATORIO (extra HU)
# ─────────────────────────────────────────

class GestionCirugias:
    def registrar_cirugia(self, mascota_id: int, veterinario_id: int,
                        procedimiento: str, fecha: str,
                        anestesia: str = "", duracion_min: int = 0,
                        observaciones: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cirugias
                (mascota_id, veterinario_id, fecha, procedimiento,
                anestesia, duracion_min, observaciones)
            VALUES (?,?,?,?,?,?,?)
        """, (mascota_id, veterinario_id, fecha, procedimiento,
            anestesia, duracion_min, observaciones))
        conn.commit()
        cid = cur.lastrowid
        conn.close()
        print(f"✅ Cirugía '{procedimiento}' registrada (ID {cid}).")
        return cid

    def registrar_postoperatorio(self, cirugia_id: int, evolucion: str,
                                tratamiento: str,
                                notificar_dueno: bool = True) -> int:
        conn = get_connection()
        cur = conn.cursor()
        fecha = date.today().isoformat()
        cur.execute("""
            INSERT INTO postoperatorio
                (cirugia_id, fecha, evolucion, tratamiento, notificado_dueno)
            VALUES (?,?,?,?,?)
        """, (cirugia_id, fecha, evolucion, tratamiento,
            1 if notificar_dueno else 0))
        conn.commit()
        pid = cur.lastrowid
        conn.close()
        if notificar_dueno:
            print(f"📨 Dueño notificado sobre evolución postoperatoria (cirugia ID {cirugia_id}).")
        print(f"✅ Registro postoperatorio ID {pid} guardado.")
        return pid


# ─────────────────────────────────────────
#  HELPERS
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
    widths = [max(len(str(h)), max((len(str(r.get(h, ""))) for r in registros), default=0)) for h in headers]
    fmt = "  " + "  │  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("  " + "─┼─".join("─" * w for w in widths))
    for r in registros:
        print(fmt.format(*[str(r.get(h, "")) for h in headers]))


# ─────────────────────────────────────────
#  DEMO SPRINT 2
# ─────────────────────────────────────────

def demo_sprint2():
    """
    Asume que ya se ejecutó sprint1_vetcare.py y la BD tiene datos base.
    Si la BD no existe, se puede correr primero:
        python sprint1_vetcare.py
    """
    print("\n" + "═"*60)
    print("  VETCARE - SPRINT 2 DEMO")
    print("═"*60)

    ampliar_bd_sprint2()

    gd = GestionDiagnosticos()
    gv = GestionVacunas()
    gca = GestionCitasAvanzada()
    gc_cx = GestionCirugias()

    # Necesitamos IDs existentes en la BD
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM mascotas LIMIT 2")
    mascotas = [r["id"] for r in cur.fetchall()]
    cur.execute("SELECT id FROM veterinarios LIMIT 1")
    vets = [r["id"] for r in cur.fetchall()]
    cur.execute("SELECT id FROM citas WHERE estado='Pendiente' LIMIT 1")
    citas = [r["id"] for r in cur.fetchall()]
    conn.close()

    if not mascotas or not vets:
        print("⚠️  Primero ejecuta sprint1_vetcare.py para generar datos base.")
        return

    m1, m2 = mascotas[0], mascotas[1] if len(mascotas) > 1 else mascotas[0]
    v1 = vets[0]

    # HU004 - Diagnósticos y tratamientos
    hist_id = gd.registrar_diagnostico(
        m1, v1,
        "Dermatitis alérgica",
        "Antihistamínico oral + shampoo medicado",
        "Evitar contacto con pasto húmedo"
    )
    gd.registrar_tratamiento(
        m1, hist_id, "Cetirizina", "5mg", "1 vez al día",
        "2026-04-15", "2026-04-30"
    )
    gd.registrar_tratamiento(
        m1, hist_id, "Shampoo Clorhedixina", "Aplicación tópica", "Cada 3 días",
        "2026-04-15", "2026-05-15", "Dejar actuar 5 min antes de enjuagar"
    )

    imprimir_tabla(gd.evolucion_mascota(m1), f"EVOLUCIÓN MÉDICA - Mascota ID {m1}")
    imprimir_tabla(gd.consultar_tratamientos(m1), f"TRATAMIENTOS - Mascota ID {m1}")

    # HU005 - Vacunas
    gv.registrar_vacuna(m1, v1, "Rabia", "2027-04-15")
    gv.registrar_vacuna(m2, v1, "Parvovirus", "2026-10-15")

    imprimir_tabla(gv.vacunas_proximas(365), "VACUNAS PRÓXIMAS (365 días)")

    # HU006 - Modificar/cancelar citas
    if citas:
        cita_id = citas[0]
        gca.modificar_cita(cita_id, "2026-04-25", "11:00", "Revisión de tratamiento")

    imprimir_tabla(gca.citas_por_mascota(m1), f"CITAS - Mascota ID {m1}")

    # Cirugías (funcionalidad extra)
    cx_id = gc_cx.registrar_cirugia(
        m2, v1, "Esterilización", "2026-04-18",
        "Anestesia general", 45, "Procedimiento rutinario"
    )
    gc_cx.registrar_postoperatorio(
        cx_id, "Paciente estable, recuperándose bien",
        "Analgésico 3 días + reposo", True
    )

    print("\n✅ Sprint 2 completado.\n")


if __name__ == "__main__":
    demo_sprint2()
