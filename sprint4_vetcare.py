"""
╔══════════════════════════════════════════════════════════════════╗
║         CLÍNICA VETERINARIA VETCARE - SPRINT 4                  ║
║  Módulos: Facturación, Reportes, Usuarios/Roles, Panel Gerente  ║
║  Equipo: Iván Nazareno, Fernanda Mena, Santiago Pineda          ║
╚══════════════════════════════════════════════════════════════════╝

HU010 - Generar facturas por servicios veterinarios
HU011 - Generar reportes administrativos
HU012 - Consultar estadísticas del sistema (Panel Gerente)
+    - Gestión de usuarios y roles (autenticación)
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import date, datetime
from functools import wraps

DB_PATH = "vetcare.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ─────────────────────────────────────────
#  TABLAS SPRINT 4
# ─────────────────────────────────────────

def ampliar_bd_sprint4():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            correo      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol         TEXT NOT NULL DEFAULT 'recepcionista',
            activo      INTEGER DEFAULT 1,
            token_recuperacion TEXT,
            token_expira TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS servicios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            descripcion TEXT,
            precio      REAL NOT NULL,
            activo      INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS facturas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            numero          TEXT UNIQUE NOT NULL,
            dueno_id        INTEGER NOT NULL REFERENCES duenos(id),
            mascota_id      INTEGER REFERENCES mascotas(id),
            fecha           TEXT NOT NULL,
            subtotal        REAL DEFAULT 0,
            iva             REAL DEFAULT 0,
            total           REAL DEFAULT 0,
            metodo_pago     TEXT DEFAULT 'Efectivo',
            estado          TEXT DEFAULT 'Pendiente',
            observaciones   TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS detalle_factura (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_id      INTEGER NOT NULL REFERENCES facturas(id),
            tipo            TEXT NOT NULL,  -- servicio | producto
            descripcion     TEXT NOT NULL,
            cantidad        INTEGER DEFAULT 1,
            precio_unitario REAL NOT NULL,
            subtotal        REAL NOT NULL
        );
    """)
    conn.commit()
    conn.close()
    print("✅ BD extendida para Sprint 4 (Facturación/Reportes/Usuarios).")


# ─────────────────────────────────────────
#  GESTIÓN DE USUARIOS Y ROLES
# ─────────────────────────────────────────

ROLES = {"admin", "veterinario", "recepcionista", "gerente", "soporte"}

PERMISOS = {
    "admin":         {"todo"},
    "gerente":       {"reportes", "facturas_consulta", "inventario_consulta", "citas_consulta"},
    "veterinario":   {"historial_escribir", "historial_leer", "citas_leer", "vacunas_escribir"},
    "recepcionista": {"citas_escribir", "citas_leer", "pacientes_leer", "facturas_escribir"},
    "soporte":       {"usuarios_admin"},
}


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class GestionUsuarios:
    """Registro, autenticación y control de acceso por rol."""

    def registrar_usuario(self, nombre: str, correo: str,
                        password: str, rol: str) -> int:
        if rol not in ROLES:
            print(f"❌ Rol inválido. Opciones: {ROLES}")
            return -1
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO usuarios (nombre, correo, password_hash, rol)
                VALUES (?,?,?,?)
            """, (nombre, correo, _hash_password(password), rol))
            conn.commit()
            uid = cur.lastrowid
            conn.close()
            print(f"✅ Usuario '{nombre}' registrado (ID {uid}, rol: {rol}).")
            print(f"📨 Email de confirmación enviado a {correo} (simulado).")
            return uid
        except sqlite3.IntegrityError:
            conn.close()
            print(f"❌ Ya existe un usuario con el correo '{correo}'.")
            return -1

    def autenticar(self, correo: str, password: str) -> dict | None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nombre, correo, rol, activo
            FROM usuarios
            WHERE correo = ? AND password_hash = ?
        """, (correo, _hash_password(password)))
        row = cur.fetchone()
        conn.close()
        if not row:
            print("❌ Credenciales incorrectas.")
            return None
        if not row["activo"]:
            print("❌ Usuario inactivo.")
            return None
        usuario = dict(row)
        print(f"✅ Acceso concedido: {usuario['nombre']} ({usuario['rol']}).")
        return usuario

    def solicitar_recuperacion(self, correo: str) -> str:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE correo = ?", (correo,))
        row = cur.fetchone()
        if not row:
            conn.close()
            print("❌ No existe usuario con ese correo.")
            return ""
        token = secrets.token_hex(16)
        # Expira en 15 minutos (simulado)
        expira = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            UPDATE usuarios
            SET token_recuperacion = ?, token_expira = ?
            WHERE correo = ?
        """, (token, expira, correo))
        conn.commit()
        conn.close()
        print(f"📨 Token de recuperación enviado a {correo} (simulado): {token[:8]}...")
        return token

    def cambiar_password(self, correo: str, token: str,
                        nueva_password: str) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM usuarios
            WHERE correo = ? AND token_recuperacion = ?
        """, (correo, token))
        row = cur.fetchone()
        if not row:
            conn.close()
            print("❌ Token inválido o expirado.")
            return False
        cur.execute("""
            UPDATE usuarios
            SET password_hash = ?, token_recuperacion = NULL, token_expira = NULL
            WHERE id = ?
        """, (_hash_password(nueva_password), row["id"]))
        conn.commit()
        conn.close()
        print("✅ Contraseña actualizada correctamente.")
        return True

    def listar_usuarios(self) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nombre, correo, rol, activo, created_at
            FROM usuarios ORDER BY nombre
        """)
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    def cambiar_rol(self, usuario_id: int, nuevo_rol: str) -> bool:
        if nuevo_rol not in ROLES:
            print(f"❌ Rol inválido: {nuevo_rol}")
            return False
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE usuarios SET rol = ? WHERE id = ?", (nuevo_rol, usuario_id)
        )
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Usuario ID {usuario_id} ahora tiene rol '{nuevo_rol}'.")
        return ok

    def desactivar_usuario(self, usuario_id: int) -> bool:
        """Desactiva un usuario por ID (eliminación lógica, no física)."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,)
        )
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Usuario ID {usuario_id} desactivado.")
        else:
            print(f"❌ Usuario ID {usuario_id} no encontrado.")
        return ok

    def tiene_permiso(self, usuario: dict, permiso: str) -> bool:
        rol = usuario.get("rol", "")
        perms = PERMISOS.get(rol, set())
        return "todo" in perms or permiso in perms


# ─────────────────────────────────────────
#  HU010 - FACTURACIÓN
# ─────────────────────────────────────────

IVA_TASA = 0.19  # 19% IVA Colombia


class GestionFacturacion:
    """Genera facturas electrónicas con detalle de servicios/productos."""

    def _numero_factura(self) -> str:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM facturas")
        total = cur.fetchone()["total"]
        conn.close()
        return f"VET-{date.today().year}-{str(total + 1).zfill(5)}"

    def registrar_servicio(self, nombre: str, precio: float,
                            descripcion: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO servicios (nombre, descripcion, precio)
            VALUES (?,?,?)
        """, (nombre, descripcion, precio))
        conn.commit()
        sid = cur.lastrowid
        conn.close()
        print(f"✅ Servicio '{nombre}' registrado (ID {sid}, precio: ${precio:,.0f}).")
        return sid

    def crear_factura(self, dueno_id: int, mascota_id: int,
                    metodo_pago: str = "Efectivo",
                    observaciones: str = "") -> int:
        """Crea una factura vacía. Añadir ítems con agregar_item()."""
        numero = self._numero_factura()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO facturas
                (numero, dueno_id, mascota_id, fecha, metodo_pago, observaciones)
            VALUES (?,?,?,?,?,?)
        """, (numero, dueno_id, mascota_id, date.today().isoformat(),
            metodo_pago, observaciones))
        conn.commit()
        fid = cur.lastrowid
        conn.close()
        print(f"✅ Factura {numero} creada (ID {fid}).")
        return fid

    def agregar_item(self, factura_id: int, descripcion: str,
                    precio_unitario: float, cantidad: int = 1,
                    tipo: str = "servicio") -> bool:
        subtotal_item = precio_unitario * cantidad
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO detalle_factura
                (factura_id, tipo, descripcion, cantidad, precio_unitario, subtotal)
            VALUES (?,?,?,?,?,?)
        """, (factura_id, tipo, descripcion, cantidad,
            precio_unitario, subtotal_item))
        # Recalcular totales
        cur.execute("""
            SELECT COALESCE(SUM(subtotal), 0) AS total_neto
            FROM detalle_factura WHERE factura_id = ?
        """, (factura_id,))
        total_neto = cur.fetchone()["total_neto"]
        iva = round(total_neto * IVA_TASA, 2)
        total = round(total_neto + iva, 2)
        cur.execute("""
            UPDATE facturas SET subtotal = ?, iva = ?, total = ?
            WHERE id = ?
        """, (total_neto, iva, total, factura_id))
        conn.commit()
        conn.close()
        return True

    def registrar_pago(self, factura_id: int,
                    metodo_pago: str = "Efectivo") -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE facturas SET estado = 'Pagada', metodo_pago = ?
            WHERE id = ? AND estado = 'Pendiente'
        """, (metodo_pago, factura_id))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Pago registrado para factura ID {factura_id}.")
        else:
            print(f"⚠️  Factura ID {factura_id} no encontrada o ya pagada.")
        return ok

    def ver_factura(self, factura_id: int) -> dict | None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT f.*, d.nombre AS cliente, m.nombre AS mascota
            FROM facturas f
            JOIN duenos d ON f.dueno_id = d.id
            LEFT JOIN mascotas m ON f.mascota_id = m.id
            WHERE f.id = ?
        """, (factura_id,))
        factura = cur.fetchone()
        if not factura:
            conn.close()
            return None
        cur.execute("""
            SELECT tipo, descripcion, cantidad, precio_unitario, subtotal
            FROM detalle_factura WHERE factura_id = ?
        """, (factura_id,))
        items = [dict(r) for r in cur.fetchall()]
        conn.close()
        result = dict(factura)
        result["items"] = items
        return result

    def imprimir_factura(self, factura_id: int):
        f = self.ver_factura(factura_id)
        if not f:
            print(f"❌ Factura ID {factura_id} no encontrada.")
            return
        print("\n" + "═"*55)
        print("       CLÍNICA VETERINARIA VETCARE")
        print("       NIT: 900.123.456-7")
        print("═"*55)
        print(f"  Factura N°: {f['numero']}")
        print(f"  Fecha:      {f['fecha']}")
        print(f"  Cliente:    {f['cliente']}")
        print(f"  Mascota:    {f.get('mascota', 'N/A')}")
        print(f"  Pago:       {f['metodo_pago']}  │  Estado: {f['estado']}")
        print("─"*55)
        print(f"  {'DESCRIPCIÓN':<28} {'CANT':>4} {'P.UNIT':>10} {'SUBTOTAL':>10}")
        print("─"*55)
        for item in f["items"]:
            print(f"  {item['descripcion']:<28} {item['cantidad']:>4} "
                f"${item['precio_unitario']:>9,.0f} ${item['subtotal']:>9,.0f}")
        print("─"*55)
        print(f"  {'Subtotal':>44}: ${f['subtotal']:>9,.0f}")
        print(f"  {'IVA (19%)':>44}: ${f['iva']:>9,.0f}")
        print(f"  {'TOTAL':>44}: ${f['total']:>9,.0f}")
        print("═"*55)

    def anular_factura(self, factura_id: int) -> bool:
        """Anula una factura cambiando su estado a 'Anulada'. No elimina el registro (trazabilidad contable)."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT estado FROM facturas WHERE id = ?", (factura_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            print(f"❌ Factura ID {factura_id} no encontrada.")
            return False
        if row["estado"] == "Pagada":
            conn.close()
            print(f"❌ No se puede anular la factura ID {factura_id}: ya está pagada.")
            return False
        cur.execute(
            "UPDATE facturas SET estado = 'Anulada' WHERE id = ?", (factura_id,)
        )
        conn.commit()
        conn.close()
        print(f"✅ Factura ID {factura_id} anulada.")
        return True

    def buscar_facturas(self, dueno_nombre: str = "", fecha: str = "",
                        estado: str = "") -> list:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            SELECT f.id, f.numero, d.nombre AS cliente, f.fecha,
                f.total, f.metodo_pago, f.estado
            FROM facturas f
            JOIN duenos d ON f.dueno_id = d.id
            WHERE 1=1
        """
        params = []
        if dueno_nombre:
            query += " AND d.nombre LIKE ?"
            params.append(f"%{dueno_nombre}%")
        if fecha:
            query += " AND f.fecha = ?"
            params.append(fecha)
        if estado:
            query += " AND f.estado = ?"
            params.append(estado)
        query += " ORDER BY f.fecha DESC, f.id DESC"
        cur.execute(query, params)
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados


# ─────────────────────────────────────────
#  HU011 / HU012 - REPORTES Y PANEL
# ─────────────────────────────────────────

class GestionReportes:
    """Reportes administrativos y estadísticos para el gerente."""

    def reporte_ventas(self, fecha_inicio: str, fecha_fin: str) -> dict:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT COUNT(*) AS total_facturas,
                COALESCE(SUM(total), 0) AS ingresos_totales,
                COALESCE(SUM(iva), 0) AS total_iva,
                COALESCE(AVG(total), 0) AS ticket_promedio
            FROM facturas
            WHERE estado = 'Pagada'
            AND fecha BETWEEN ? AND ?
        """, (fecha_inicio, fecha_fin))
        resumen = dict(cur.fetchone())

        cur.execute("""
            SELECT metodo_pago, COUNT(*) AS cantidad,
                COALESCE(SUM(total), 0) AS monto
            FROM facturas
            WHERE estado = 'Pagada' AND fecha BETWEEN ? AND ?
            GROUP BY metodo_pago
        """, (fecha_inicio, fecha_fin))
        por_metodo = [dict(r) for r in cur.fetchall()]
        conn.close()

        return {"periodo": f"{fecha_inicio} → {fecha_fin}",
                "resumen": resumen, "por_metodo_pago": por_metodo}

    def reporte_citas(self, fecha_inicio: str, fecha_fin: str) -> dict:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT estado, COUNT(*) AS cantidad
            FROM citas
            WHERE fecha BETWEEN ? AND ?
            GROUP BY estado
        """, (fecha_inicio, fecha_fin))
        por_estado = [dict(r) for r in cur.fetchall()]

        cur.execute("""
            SELECT v.nombre AS veterinario, COUNT(*) AS citas
            FROM citas c
            JOIN veterinarios v ON c.veterinario_id = v.id
            WHERE c.fecha BETWEEN ? AND ?
            GROUP BY c.veterinario_id
            ORDER BY citas DESC
        """, (fecha_inicio, fecha_fin))
        por_veterinario = [dict(r) for r in cur.fetchall()]

        conn.close()
        return {"periodo": f"{fecha_inicio} → {fecha_fin}",
                "por_estado": por_estado,
                "por_veterinario": por_veterinario}

    def panel_gerente(self) -> dict:
        """KPIs principales para el panel de control."""
        conn = get_connection()
        cur = conn.cursor()

        hoy = date.today().isoformat()
        mes_inicio = date.today().replace(day=1).isoformat()

        kpis = {}

        cur.execute("SELECT COUNT(*) AS n FROM mascotas")
        kpis["total_pacientes"] = cur.fetchone()["n"]

        cur.execute(
            "SELECT COUNT(*) AS n FROM citas WHERE fecha = ?", (hoy,)
        )
        kpis["citas_hoy"] = cur.fetchone()["n"]

        cur.execute("""
            SELECT COALESCE(SUM(total), 0) AS n FROM facturas
            WHERE estado = 'Pagada' AND fecha >= ?
        """, (mes_inicio,))
        kpis["ingresos_mes"] = round(cur.fetchone()["n"], 2)

        cur.execute("""
            SELECT COUNT(*) AS n FROM productos
            WHERE activo = 1 AND stock_actual <= stock_minimo
        """)
        kpis["productos_stock_bajo"] = cur.fetchone()["n"]

        cur.execute("""
            SELECT COUNT(*) AS n FROM facturas WHERE estado = 'Pendiente'
        """)
        kpis["facturas_pendientes"] = cur.fetchone()["n"]

        cur.execute("""
            SELECT m.especie, COUNT(*) AS consultas
            FROM historial_clinico h
            JOIN mascotas m ON h.mascota_id = m.id
            GROUP BY m.especie ORDER BY consultas DESC LIMIT 5
        """)
        kpis["top_especies_consultadas"] = [dict(r) for r in cur.fetchall()]

        conn.close()
        return kpis

    def exportar_json(self, datos: dict | list, nombre_archivo: str) -> str:
        """Exporta reporte como JSON (base para integración con Excel/PDF)."""
        ruta = f"/home/claude/{nombre_archivo}.json"
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ Reporte exportado: {ruta}")
        return ruta


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

def imprimir_tabla(registros: list, titulo: str = ""):
    if titulo:
        print(f"\n{'─'*70}")
        print(f"  {titulo}")
        print(f"{'─'*70}")
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


def imprimir_panel(kpis: dict):
    print("\n" + "═"*55)
    print("   📊  PANEL DE CONTROL - CLÍNICA VETCARE")
    print("═"*55)
    print(f"   👾  Total pacientes registrados : {kpis['total_pacientes']}")
    print(f"   📅  Citas programadas hoy       : {kpis['citas_hoy']}")
    print(f"   💰  Ingresos del mes            : ${kpis['ingresos_mes']:,.0f}")
    print(f"   ⚠️   Productos con stock bajo    : {kpis['productos_stock_bajo']}")
    print(f"   🧾  Facturas pendientes de pago : {kpis['facturas_pendientes']}")
    if kpis.get("top_especies_consultadas"):
        print("\n   🐾  Especies más consultadas:")
        for e in kpis["top_especies_consultadas"]:
            print(f"       • {e['especie']}: {e['consultas']} consultas")
    print("═"*55)


# ─────────────────────────────────────────
#  DEMO SPRINT 4
# ─────────────────────────────────────────

def demo_sprint4():
    print("\n" + "═"*60)
    print("  VETCARE - SPRINT 4 DEMO")
    print("═"*60)

    ampliar_bd_sprint4()

    gu = GestionUsuarios()
    gf = GestionFacturacion()
    gr = GestionReportes()

    # Usuarios
    gu.registrar_usuario("Iván Nazareno", "ivan@vetcare.co",  "Admin1234!", "admin")
    gu.registrar_usuario("Fernanda Mena", "fernanda@vetcare.co", "Vet5678!", "veterinario")
    gu.registrar_usuario("Santiago Pineda", "santiago@vetcare.co", "Rec9012!", "recepcionista")
    gu.registrar_usuario("Gerente VetCare", "gerente@vetcare.co", "Ger3456!", "gerente")

    # Autenticación
    usuario = gu.autenticar("ivan@vetcare.co", "Admin1234!")
    if usuario:
        tiene = gu.tiene_permiso(usuario, "historial_escribir")
        print(f"   Permiso 'historial_escribir': {'✅' if tiene else '❌'}")

    # Recuperación de contraseña
    token = gu.solicitar_recuperacion("fernanda@vetcare.co")
    if token:
        gu.cambiar_password("fernanda@vetcare.co", token, "NuevaVet2026!")

    imprimir_tabla(gu.listar_usuarios(), "USUARIOS DEL SISTEMA")

    # Servicios
    s1 = gf.registrar_servicio("Consulta General", 50000, "Revisión básica")
    s2 = gf.registrar_servicio("Cirugía Menor", 250000, "Procedimientos menores")
    s3 = gf.registrar_servicio("Vacunación", 35000, "Aplicación de vacuna")

    # Obtener IDs de BD
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM duenos LIMIT 2")
    duenos = [r["id"] for r in cur.fetchall()]
    cur.execute("SELECT id FROM mascotas LIMIT 2")
    mascotas_ids = [r["id"] for r in cur.fetchall()]
    conn.close()

    if not duenos:
        print("⚠️  Ejecuta primero los sprints anteriores para tener datos base.")
        return

    d1, d2 = duenos[0], duenos[1] if len(duenos) > 1 else duenos[0]
    m1, m2 = mascotas_ids[0], mascotas_ids[1] if len(mascotas_ids) > 1 else mascotas_ids[0]

    # HU010 - Facturas
    f1 = gf.crear_factura(d1, m1, "Tarjeta Crédito", "Consulta de rutina")
    gf.agregar_item(f1, "Consulta General", 50000, 1, "servicio")
    gf.agregar_item(f1, "Amoxicilina 500mg x2", 12000, 2, "producto")
    gf.registrar_pago(f1, "Tarjeta Crédito")
    gf.imprimir_factura(f1)

    f2 = gf.crear_factura(d2, m2, "Efectivo", "Vacunación triple")
    gf.agregar_item(f2, "Vacunación Triple Felina", 35000, 1, "servicio")
    gf.agregar_item(f2, "Jeringas", 1500, 2, "producto")
    gf.imprimir_factura(f2)  # pendiente de pago

    imprimir_tabla(gf.buscar_facturas(), "TODAS LAS FACTURAS")
    imprimir_tabla(gf.buscar_facturas(estado="Pendiente"), "FACTURAS PENDIENTES")

    # HU011 - Reportes
    ventas = gr.reporte_ventas("2026-01-01", "2026-12-31")
    print(f"\n{'─'*55}")
    print("  REPORTE DE VENTAS 2026")
    print(f"{'─'*55}")
    print(f"  Facturas pagadas    : {ventas['resumen']['total_facturas']}")
    print(f"  Ingresos totales    : ${ventas['resumen']['ingresos_totales']:,.0f}")
    print(f"  IVA recaudado       : ${ventas['resumen']['total_iva']:,.0f}")
    print(f"  Ticket promedio     : ${ventas['resumen']['ticket_promedio']:,.0f}")
    imprimir_tabla(ventas["por_metodo_pago"], "Por Método de Pago")

    citas_rep = gr.reporte_citas("2026-01-01", "2026-12-31")
    imprimir_tabla(citas_rep["por_estado"], "REPORTE CITAS - Por Estado")
    imprimir_tabla(citas_rep["por_veterinario"], "REPORTE CITAS - Por Veterinario")

    # HU012 - Panel Gerente
    kpis = gr.panel_gerente()
    imprimir_panel(kpis)

    # Exportar
    gr.exportar_json(ventas, "reporte_ventas_2026")
    gr.exportar_json(kpis, "panel_gerente")

    print("\n✅ Sprint 4 completado.")
    print("✅ SISTEMA VETCARE - TODOS LOS SPRINTS COMPLETADOS.\n")


if __name__ == "__main__":
    demo_sprint4()
