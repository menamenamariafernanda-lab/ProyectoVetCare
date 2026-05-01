"""
CLÍNICA VETERINARIA VETCARE - SPRINT 3
Módulos: Inventario de Medicamentos y Productos
"""

import sqlite3
from datetime import date

DB_PATH = "vetcare.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def ampliar_bd_sprint3():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL, categoria TEXT, precio_compra REAL DEFAULT 0,
            precio_venta REAL DEFAULT 0, stock_actual INTEGER DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5, unidad TEXT DEFAULT 'unidad',
            fecha_vencimiento TEXT, activo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT, producto_id INTEGER NOT NULL REFERENCES productos(id),
            tipo TEXT NOT NULL, cantidad INTEGER NOT NULL, motivo TEXT,
            referencia TEXT, usuario TEXT DEFAULT 'sistema', fecha TEXT DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS alertas_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT, producto_id INTEGER NOT NULL REFERENCES productos(id),
            tipo_alerta TEXT, mensaje TEXT, resuelta INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()
    print("✅ BD extendida Sprint 3")

class GestionInventario:
    def agregar_producto(self, codigo, nombre, categoria, precio_compra, precio_venta, stock_inicial, stock_minimo=5, unidad="unidad", fecha_vencimiento=""):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO productos (codigo, nombre, categoria, precio_compra, precio_venta, stock_actual, stock_minimo, unidad, fecha_vencimiento)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (codigo, nombre, categoria, precio_compra, precio_venta, stock_inicial, stock_minimo, unidad, fecha_vencimiento))
            conn.commit()
            id_ = cur.lastrowid
            self._registrar_movimiento(cur, id_, "entrada", stock_inicial, "Stock inicial", "")
            conn.commit()
            conn.close()
            print(f"✅ Producto '{nombre}' ID: {id_}")
            return id_
        except sqlite3.IntegrityError:
            conn.close()
            print(f"❌ Código '{codigo}' ya existe")
            return -1

    def _registrar_movimiento(self, cur, producto_id, tipo, cantidad, motivo, referencia, usuario="sistema"):
        cur.execute("INSERT INTO movimientos_inventario (producto_id, tipo, cantidad, motivo, referencia, usuario) VALUES (?,?,?,?,?,?)",
                    (producto_id, tipo, cantidad, motivo, referencia, usuario))

    def registrar_entrada(self, producto_id, cantidad, motivo="Compra"):
        if cantidad <= 0:
            print("❌ Cantidad debe ser positiva")
            return False
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?", (cantidad, producto_id))
        self._registrar_movimiento(cur, producto_id, "entrada", cantidad, motivo, "")
        conn.commit()
        conn.close()
        print(f"✅ Entrada de {cantidad} unidades")
        return True

    def registrar_salida(self, producto_id, cantidad, motivo="Venta"):
        if cantidad <= 0:
            return False
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT stock_actual, nombre FROM productos WHERE id = ?", (producto_id,))
        prod = cur.fetchone()
        if not prod or prod["stock_actual"] < cantidad:
            conn.close()
            print("❌ Stock insuficiente")
            return False
        cur.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?", (cantidad, producto_id))
        self._registrar_movimiento(cur, producto_id, "salida", cantidad, motivo, "")
        conn.commit()
        conn.close()
        print(f"✅ Salida de {cantidad} unidades")
        return True

    def consultar_stock(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, stock_actual, stock_minimo FROM productos WHERE activo = 1")
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

    def productos_stock_bajo(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, stock_actual, stock_minimo FROM productos WHERE activo = 1 AND stock_actual <= stock_minimo")
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

def imprimir_tabla(registros, titulo=""):
    if titulo:
        print(f"\n{'─'*50}\n  {titulo}\n{'─'*50}")
    if not registros:
        print("  (Sin registros)")
        return
    for r in registros:
        print(f"  {', '.join(f'{k}: {v}' for k, v in r.items())}")

def demo_sprint3():
    print("\n" + "═"*50 + "\n  VETCARE - SPRINT 3\n" + "═"*50)
    ampliar_bd_sprint3()
    
    inv = GestionInventario()
    
    # Solo agregar productos si no existen
    conn = get_connection()
    vacio = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0] == 0
    conn.close()
    
    if vacio:
        inv.agregar_producto("MED-001", "Amoxicilina", "medicamento", 3500, 6000, 50, 10, "caja", "2027-06-30")
        inv.agregar_producto("MED-002", "Cetirizina", "medicamento", 2000, 4000, 3, 5, "blíster", "2026-12-31")
        inv.agregar_producto("INS-001", "Jeringas 5ml", "insumo", 800, 1500, 100, 20, "caja x50")
    
    inv.registrar_entrada(2, 20, "Compra")  # Aumentar stock de Cetirizina
    inv.registrar_salida(1, 5, "Tratamiento")
    
    imprimir_tabla(inv.consultar_stock(), "INVENTARIO")
    imprimir_tabla(inv.productos_stock_bajo(), "STOCK BAJO")
    print("\n✅ Sprint 3 listo")

if __name__ == "__main__":
    demo_sprint3()