"""
CLÍNICA VETERINARIA VETCARE - SPRINT 4
Módulos: Facturación, Reportes, Usuarios/Roles, Panel Gerente
"""

import sqlite3
import hashlib
from datetime import date

DB_PATH = "vetcare.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def ampliar_bd_sprint4():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'recepcionista', activo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
            precio REAL NOT NULL, activo INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, numero TEXT UNIQUE NOT NULL,
            dueno_id INTEGER NOT NULL REFERENCES duenos(id), mascota_id INTEGER REFERENCES mascotas(id),
            fecha TEXT NOT NULL, subtotal REAL DEFAULT 0, iva REAL DEFAULT 0,
            total REAL DEFAULT 0, metodo_pago TEXT DEFAULT 'Efectivo',
            estado TEXT DEFAULT 'Pendiente'
        );
        CREATE TABLE IF NOT EXISTS detalle_factura (
            id INTEGER PRIMARY KEY AUTOINCREMENT, factura_id INTEGER NOT NULL REFERENCES facturas(id),
            descripcion TEXT NOT NULL, cantidad INTEGER DEFAULT 1,
            precio_unitario REAL NOT NULL, subtotal REAL NOT NULL
        );
    """)
    conn.commit()
    conn.close()
    print("✅ BD extendida Sprint 4")

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

class GestionUsuarios:
    def registrar_usuario(self, nombre, correo, password, rol):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO usuarios (nombre, correo, password_hash, rol) VALUES (?,?,?,?)",
                        (nombre, correo, hash_password(password), rol))
            conn.commit()
            id_ = cur.lastrowid
            conn.close()
            print(f"✅ Usuario '{nombre}' ID: {id_}, rol: {rol}")
            return id_
        except sqlite3.IntegrityError:
            conn.close()
            print(f"❌ Correo '{correo}' ya existe")
            return -1

    def autenticar(self, correo, password):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, rol FROM usuarios WHERE correo = ? AND password_hash = ? AND activo = 1",
                    (correo, hash_password(password)))
        user = cur.fetchone()
        conn.close()
        if user:
            print(f"✅ Bienvenido {user['nombre']} ({user['rol']})")
            return dict(user)
        print("❌ Credenciales incorrectas")
        return None

    def listar_usuarios(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, correo, rol FROM usuarios")
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return res

class GestionFacturacion:
    def _next_numero(self):
        conn = get_connection()
        total = conn.execute("SELECT COUNT(*) FROM facturas").fetchone()[0]
        conn.close()
        return f"VET-{date.today().year}-{str(total + 1).zfill(5)}"

    def crear_factura(self, dueno_id, mascota_id, metodo_pago="Efectivo"):
        numero = self._next_numero()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO facturas (numero, dueno_id, mascota_id, fecha, metodo_pago) VALUES (?,?,?,?,?)",
                    (numero, dueno_id, mascota_id, date.today().isoformat(), metodo_pago))
        conn.commit()
        id_ = cur.lastrowid
        conn.close()
        print(f"✅ Factura {numero} creada")
        return id_

    def agregar_item(self, factura_id, descripcion, precio_unitario, cantidad=1):
        subtotal = precio_unitario * cantidad
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO detalle_factura (factura_id, descripcion, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
                    (factura_id, descripcion, cantidad, precio_unitario, subtotal))
        # Recalcular totales
        total_neto = conn.execute("SELECT COALESCE(SUM(subtotal),0) FROM detalle_factura WHERE factura_id = ?", (factura_id,)).fetchone()[0]
        iva = total_neto * 0.19
        total = total_neto + iva
        cur.execute("UPDATE facturas SET subtotal = ?, iva = ?, total = ? WHERE id = ?",
                    (total_neto, iva, total, factura_id))
        conn.commit()
        conn.close()
        return True

    def registrar_pago(self, factura_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE facturas SET estado = 'Pagada' WHERE id = ? AND estado = 'Pendiente'", (factura_id,))
        ok = cur.rowcount > 0
        conn.commit()
        conn.close()
        if ok:
            print(f"✅ Pago registrado")
        return ok

    def ver_factura(self, factura_id):
        conn = get_connection()
        f = conn.execute("SELECT * FROM facturas WHERE id = ?", (factura_id,)).fetchone()
        if not f:
            return None
        items = [dict(r) for r in conn.execute("SELECT descripcion, cantidad, precio_unitario, subtotal FROM detalle_factura WHERE factura_id = ?", (factura_id,))]
        conn.close()
        return dict(f) | {"items": items}

class GestionReportes:
    def panel_gerente(self):
        conn = get_connection()
        hoy = date.today().isoformat()
        mes_actual = date.today().replace(day=1).isoformat()
        
        total_pacientes = conn.execute("SELECT COUNT(*) FROM mascotas").fetchone()[0]
        citas_hoy = conn.execute("SELECT COUNT(*) FROM citas WHERE fecha = ?", (hoy,)).fetchone()[0]
        ingresos_mes = conn.execute("SELECT COALESCE(SUM(total),0) FROM facturas WHERE estado='Pagada' AND fecha >= ?", (mes_actual,)).fetchone()[0]
        stock_bajo = conn.execute("SELECT COUNT(*) FROM productos WHERE activo=1 AND stock_actual <= stock_minimo").fetchone()[0]
        
        conn.close()
        return {"total_pacientes": total_pacientes, "citas_hoy": citas_hoy,
                "ingresos_mes": round(ingresos_mes, 2), "productos_stock_bajo": stock_bajo}

def imprimir_tabla(registros, titulo=""):
    if titulo:
        print(f"\n{'─'*50}\n  {titulo}\n{'─'*50}")
    if not registros:
        print("  (Sin registros)")
        return
    for r in registros:
        print(f"  {', '.join(f'{k}: {v}' for k, v in r.items())}")

def imprimir_panel(kpis):
    print("\n" + "═"*50)
    print("  📊 PANEL GERENTE")
    print("═"*50)
    print(f"  Pacientes: {kpis['total_pacientes']}")
    print(f"  Citas hoy: {kpis['citas_hoy']}")
    print(f"  Ingresos mes: ${kpis['ingresos_mes']:,.0f}")
    print(f"  Stock bajo: {kpis['productos_stock_bajo']} productos")

def demo_sprint4():
    print("\n" + "═"*50 + "\n  VETCARE - SPRINT 4\n" + "═"*50)
    ampliar_bd_sprint4()
    
    gu = GestionUsuarios()
    gf = GestionFacturacion()
    gr = GestionReportes()
    
    # Solo crear usuarios si no existen
    conn = get_connection()
    vacio = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0
    conn.close()
    
    if vacio:
        gu.registrar_usuario("Admin", "admin@vetcare.co", "admin123", "admin")
        gu.registrar_usuario("Recepcionista", "recepcion@vetcare.co", "recep123", "recepcionista")
    
    # Autenticación demo
    usuario = gu.autenticar("admin@vetcare.co", "admin123")
    
    # Factura demo (si hay datos)
    conn = get_connection()
    dueno = conn.execute("SELECT id FROM duenos LIMIT 1").fetchone()
    mascota = conn.execute("SELECT id FROM mascotas LIMIT 1").fetchone()
    conn.close()
    
    if dueno and mascota:
        factura_id = gf.crear_factura(dueno["id"], mascota["id"], "Tarjeta")
        gf.agregar_item(factura_id, "Consulta General", 50000)
        gf.agregar_item(factura_id, "Vacuna Rabia", 35000)
        gf.registrar_pago(factura_id)
        
        factura = gf.ver_factura(factura_id)
        if factura:
            print(f"\n  FACTURA #{factura['numero']}: ${factura['total']:,.0f}")
    
    imprimir_tabla(gu.listar_usuarios(), "USUARIOS")
    imprimir_panel(gr.panel_gerente())
    print("\n✅ Sprint 4 listo")
    print("✅ SISTEMA COMPLETO")

if __name__ == "__main__":
    demo_sprint4()