"""
╔══════════════════════════════════════════════════════════════════╗
║         CLÍNICA VETERINARIA VETCARE - SPRINT 3                   ║
║  Módulos: Inventario de Medicamentos y Productos                 ║
║  Equipo: Iván Nazareno, Fernanda Mena, Santiago Pineda           ║
╚══════════════════════════════════════════════════════════════════╝

HU007 - Gestionar inventario de medicamentos
HU008 - Actualizar precios de productos
HU009 - Registrar entradas y salidas de inventario (movimientos)
"""

import sqlite3
from datetime import date, datetime

DB_PATH = "vetcare.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ─────────────────────────────────────────
#  TABLAS DE INVENTARIO
# ─────────────────────────────────────────

def ampliar_bd_sprint3():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo          TEXT UNIQUE NOT NULL,
            nombre          TEXT NOT NULL,
            descripcion     TEXT,
            categoria       TEXT,          -- medicamento | insumo | alimento
            precio_compra   REAL DEFAULT 0,
            precio_venta    REAL DEFAULT 0,
            stock_actual    INTEGER DEFAULT 0,
            stock_minimo    INTEGER DEFAULT 5,
            unidad          TEXT DEFAULT 'unidad',
            fecha_vencimiento TEXT,
            activo          INTEGER DEFAULT 1,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id     INTEGER NOT NULL REFERENCES productos(id),
            tipo            TEXT NOT NULL,   -- entrada | salida | ajuste
            cantidad        INTEGER NOT NULL,
            motivo          TEXT,
            referencia      TEXT,            -- nro factura, cita, etc.
            usuario         TEXT DEFAULT 'sistema',
            fecha           TEXT DEFAULT (date('now')),
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS alertas_stock (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id     INTEGER NOT NULL REFERENCES productos(id),
            tipo_alerta     TEXT,           -- stock_bajo | vencimiento
            mensaje         TEXT,
            resuelta        INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()
    print("✅ BD extendida para Sprint 3 (Inventario).")


# ─────────────────────────────────────────
#  HU007 - GESTIÓN DE INVENTARIO
# ─────────────────────────────────────────

class GestionInventario:
    """Administrador controla productos, stock y alertas."""

    # ── Productos ──────────────────────────────

    def agregar_producto(self, codigo: str, nombre: str,
                        categoria: str, precio_compra: float,
                        precio_venta: float, stock_inicial: int,
                        stock_minimo: int = 5, unidad: str = "unidad",
                        descripcion: str = "",
                        fecha_vencimiento: str = "") -> int:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO productos
                    (codigo, nombre, descripcion, categoria, precio_compra,
                    precio_venta, stock_actual, stock_minimo, unidad, fecha_vencimiento)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (codigo, nombre, descripcion, categoria, precio_compra,
                precio_venta, stock_inicial, stock_minimo, unidad,
                fecha_vencimiento))
            conn.commit()
            pid = cur.lastrowid

            # Registrar entrada inicial
            self._registrar_movimiento(cur, pid, "entrada",
                                    stock_inicial, "Stock inicial", "")
            conn.commit()
            conn.close()
            print(f"✅ Producto '{nombre}' [{codigo}] registrado (ID {pid}).")
            self._verificar_alertas(pid)
            return pid
        except sqlite3.IntegrityError:
            conn.close()
            print(f"❌ Ya existe un producto con el código '{codigo}'.")
            return -1

    def editar_producto(self, producto_id: int, **kwargs) -> bool:
        campos_permitidos = {"nombre", "descripcion", "categoria",
                            "precio_compra", "precio_venta",
                            "stock_minimo", "unidad", "fecha_vencimiento",
                            "activo"}
        campos = {k: v for k, v in kwargs.items() if k in campos_permitidos}
        if not campos:
            print("⚠️  No hay campos válidos para actualizar.")
            return False
        set_clause = ", ".join(f"{k} = ?" for k in campos)
        valores = list(campos.values()) + [producto_id]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"UPDATE productos SET {set_clause} WHERE id = ?", valores)
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Producto ID {producto_id} actualizado.")
        return ok

    def eliminar_producto(self, producto_id: int) -> bool:
        """Baja lógica (activo = 0)."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE productos SET activo = 0 WHERE id = ?", (producto_id,))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Producto ID {producto_id} dado de baja.")
        return ok

    def consultar_stock(self, solo_activos: bool = True) -> list:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            SELECT id, codigo, nombre, categoria, precio_venta,
                stock_actual, stock_minimo, unidad, fecha_vencimiento,
                CASE WHEN stock_actual <= stock_minimo THEN '⚠️ BAJO' ELSE '✅ OK' END AS estado_stock
            FROM productos
        """
        if solo_activos:
            query += " WHERE activo = 1"
        query += " ORDER BY nombre"
        cur.execute(query)
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    def buscar_producto(self, termino: str) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, codigo, nombre, categoria, precio_venta,
                stock_actual, stock_minimo, unidad
            FROM productos
            WHERE activo = 1
            AND (nombre LIKE ? OR codigo LIKE ? OR categoria LIKE ?)
            ORDER BY nombre
        """, (f"%{termino}%", f"%{termino}%", f"%{termino}%"))
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    # ── HU009 - Movimientos ────────────────────

    def registrar_entrada(self, producto_id: int, cantidad: int,
                        motivo: str = "Compra", referencia: str = "",
                        usuario: str = "admin") -> bool:
        if cantidad <= 0:
            print("❌ La cantidad debe ser positiva.")
            return False
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?",
            (cantidad, producto_id)
        )
        self._registrar_movimiento(cur, producto_id, "entrada",
                                cantidad, motivo, referencia, usuario)
        conn.commit()
        conn.close()
        print(f"✅ Entrada de {cantidad} unidades al producto ID {producto_id}.")
        self._verificar_alertas(producto_id)
        return True

    def registrar_salida(self, producto_id: int, cantidad: int,
                        motivo: str = "Venta", referencia: str = "",
                        usuario: str = "admin") -> bool:
        if cantidad <= 0:
            print("❌ La cantidad debe ser positiva.")
            return False
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT stock_actual, nombre FROM productos WHERE id = ? AND activo = 1",
            (producto_id,)
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            print(f"❌ Producto ID {producto_id} no encontrado.")
            return False
        if row["stock_actual"] < cantidad:
            conn.close()
            print(f"❌ Stock insuficiente. Disponible: {row['stock_actual']}, solicitado: {cantidad}.")
            return False

        cur.execute(
            "UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?",
            (cantidad, producto_id)
        )
        self._registrar_movimiento(cur, producto_id, "salida",
                                cantidad, motivo, referencia, usuario)
        conn.commit()
        conn.close()
        print(f"✅ Salida de {cantidad} unidades del producto '{row['nombre']}'.")
        self._verificar_alertas(producto_id)
        return True

    def ajuste_inventario(self, producto_id: int, nueva_cantidad: int,
                        motivo: str = "Ajuste físico",
                        usuario: str = "admin") -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT stock_actual FROM productos WHERE id = ?", (producto_id,)
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            print(f"❌ Producto ID {producto_id} no encontrado.")
            return False
        diferencia = nueva_cantidad - row["stock_actual"]
        cur.execute(
            "UPDATE productos SET stock_actual = ? WHERE id = ?",
            (nueva_cantidad, producto_id)
        )
        tipo = "entrada" if diferencia >= 0 else "salida"
        self._registrar_movimiento(cur, producto_id, "ajuste",
                                abs(diferencia), motivo, "", usuario)
        conn.commit()
        conn.close()
        print(f"✅ Ajuste aplicado: stock ahora en {nueva_cantidad} unidades.")
        self._verificar_alertas(producto_id)
        return True

    def historial_movimientos(self, producto_id: int = 0) -> list:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            SELECT m.id, p.nombre AS producto, p.codigo, m.tipo,
                m.cantidad, m.motivo, m.referencia,
                m.usuario, m.fecha
            FROM movimientos_inventario m
            JOIN productos p ON m.producto_id = p.id
        """
        if producto_id:
            query += f" WHERE m.producto_id = {producto_id}"
        query += " ORDER BY m.created_at DESC LIMIT 50"
        cur.execute(query)
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    # ── HU008 - Actualizar precios ─────────────

    def actualizar_precio(self, producto_id: int,
                        nuevo_precio_venta: float,
                        nuevo_precio_compra: float = -1) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        if nuevo_precio_compra >= 0:
            cur.execute("""
                UPDATE productos SET precio_venta = ?, precio_compra = ?
                WHERE id = ?
            """, (nuevo_precio_venta, nuevo_precio_compra, producto_id))
        else:
            cur.execute(
                "UPDATE productos SET precio_venta = ? WHERE id = ?",
                (nuevo_precio_venta, producto_id)
            )
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Precio actualizado para producto ID {producto_id}.")
        return ok

    # ── Alertas ────────────────────────────────

    def _registrar_movimiento(self, cur, producto_id: int, tipo: str,
                            cantidad: int, motivo: str, referencia: str,
                            usuario: str = "sistema"):
        cur.execute("""
            INSERT INTO movimientos_inventario
                (producto_id, tipo, cantidad, motivo, referencia, usuario)
            VALUES (?,?,?,?,?,?)
        """, (producto_id, tipo, cantidad, motivo, referencia, usuario))

    def _verificar_alertas(self, producto_id: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT nombre, stock_actual, stock_minimo, fecha_vencimiento
            FROM productos WHERE id = ?
        """, (producto_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return

        alertas_generadas = []

        # Alerta stock bajo
        if row["stock_actual"] <= row["stock_minimo"]:
            mensaje = (f"⚠️  STOCK BAJO: '{row['nombre']}' tiene "
                    f"{row['stock_actual']} unidades (mínimo: {row['stock_minimo']}).")
            print(mensaje)
            cur.execute("""
                INSERT INTO alertas_stock (producto_id, tipo_alerta, mensaje)
                VALUES (?,?,?)
            """, (producto_id, "stock_bajo", mensaje))
            alertas_generadas.append(mensaje)

        # Alerta vencimiento próximo (30 días)
        if row["fecha_vencimiento"]:
            try:
                fv = date.fromisoformat(row["fecha_vencimiento"])
                dias = (fv - date.today()).days
                if 0 <= dias <= 30:
                    mensaje = (f"⚠️  VENCIMIENTO: '{row['nombre']}' vence "
                            f"en {dias} días ({row['fecha_vencimiento']}).")
                    print(mensaje)
                    cur.execute("""
                        INSERT INTO alertas_stock (producto_id, tipo_alerta, mensaje)
                        VALUES (?,?,?)
                    """, (producto_id, "vencimiento", mensaje))
                    alertas_generadas.append(mensaje)
                elif dias < 0:
                    mensaje = f"🚫 VENCIDO: '{row['nombre']}' venció el {row['fecha_vencimiento']}."
                    print(mensaje)
            except ValueError:
                pass

        conn.commit()
        conn.close()

    def alertas_activas(self) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.id, p.nombre AS producto, a.tipo_alerta,
                a.mensaje, a.created_at
            FROM alertas_stock a
            JOIN productos p ON a.producto_id = p.id
            WHERE a.resuelta = 0
            ORDER BY a.created_at DESC
        """)
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados

    def resolver_alerta(self, alerta_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE alertas_stock SET resuelta = 1 WHERE id = ?", (alerta_id,)
        )
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        if ok:
            print(f"✅ Alerta ID {alerta_id} marcada como resuelta.")
        return ok

    def productos_stock_bajo(self) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, codigo, nombre, categoria, stock_actual,
                stock_minimo, unidad
            FROM productos
            WHERE activo = 1 AND stock_actual <= stock_minimo
            ORDER BY stock_actual ASC
        """)
        resultados = [dict(r) for r in cur.fetchall()]
        conn.close()
        return resultados


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


# ─────────────────────────────────────────
#  DEMO SPRINT 3
# ─────────────────────────────────────────

def demo_sprint3():
    print("\n" + "═"*60)
    print("  VETCARE - SPRINT 3 DEMO")
    print("═"*60)

    ampliar_bd_sprint3()

    inv = GestionInventario()

    # HU007 - Agregar productos
    p1 = inv.agregar_producto(
        "MED-001", "Amoxicilina 500mg", "medicamento",
        3500, 6000, 50, stock_minimo=10, unidad="caja",
        descripcion="Antibiótico oral",
        fecha_vencimiento="2027-06-30"
    )
    p2 = inv.agregar_producto(
        "MED-002", "Cetirizina 10mg", "medicamento",
        2000, 4000, 3, stock_minimo=5, unidad="blíster",
        descripcion="Antihistamínico",
        fecha_vencimiento="2026-12-31"
    )
    p3 = inv.agregar_producto(
        "INS-001", "Jeringas 5ml", "insumo",
        800, 1500, 100, stock_minimo=20, unidad="caja x50"
    )
    p4 = inv.agregar_producto(
        "MED-003", "Ivermectina 1%", "medicamento",
        5000, 9000, 4, stock_minimo=5, unidad="frasco",
        fecha_vencimiento="2026-05-01"  # cerca de vencer
    )

    # HU008 - Actualizar precio
    inv.actualizar_precio(p1, 6500, 3800)

    # HU009 - Movimientos
    inv.registrar_entrada(p2, 20, "Compra urgente", "OC-2026-045", "admin")
    inv.registrar_salida(p1, 5, "Tratamiento mascota ID 1", "CITA-001", "vet_torres")
    inv.registrar_salida(p3, 10, "Uso en consultas", "CONS-2026-04", "admin")
    inv.ajuste_inventario(p3, 95, "Ajuste por conteo físico", "admin")

    # Mostrar resultados
    imprimir_tabla(inv.consultar_stock(), "INVENTARIO COMPLETO")
    imprimir_tabla(inv.productos_stock_bajo(), "PRODUCTOS CON STOCK BAJO")
    imprimir_tabla(inv.alertas_activas(), "ALERTAS ACTIVAS")
    imprimir_tabla(
        inv.historial_movimientos(), "ÚLTIMOS MOVIMIENTOS DE INVENTARIO"
    )

    # Búsqueda
    imprimir_tabla(inv.buscar_producto("med"), "BÚSQUEDA: 'med'")

    print("\n✅ Sprint 3 completado.\n")


if __name__ == "__main__":
    demo_sprint3()
