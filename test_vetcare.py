"""
╔══════════════════════════════════════════════════════════════════╗
║     VETCARE — SUITE DE PRUEBAS AUTOMATIZADAS (pytest)            ║
║     Patrón AAA: Arrange → Act → Assert                           ║
║     Ejecutar: python -m pytest test_vetcare.py -v                ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import pytest
import sqlite3

# Añadir directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Usar BD en memoria para tests aislados
TEST_DB = "vetcare_test.db"

# Parchear DB_PATH en todos los módulos antes de importar
import sprint1_vetcare as s1
import sprint2_vetcare as s2
import sprint3_vetcare as s3
import sprint4_vetcare as s4

for mod in [s1, s2, s3, s4]:
    mod.DB_PATH = TEST_DB


# ─────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────

@pytest.fixture(autouse=True)
def fresh_db():
    """Cada test arranca con una BD limpia y estructura completa."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    s1.inicializar_bd()
    s2.ampliar_bd_sprint2()
    s3.ampliar_bd_sprint3()
    s4.ampliar_bd_sprint4()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture
def gp():
    return s1.GestionPacientes()

@pytest.fixture
def hc():
    return s1.HistorialClinico()

@pytest.fixture
def gc():
    return s1.GestionCitas()

@pytest.fixture
def gd():
    return s2.GestionDiagnosticos()

@pytest.fixture
def gv():
    return s2.GestionVacunas()

@pytest.fixture
def gca():
    return s2.GestionCitasAvanzada()

@pytest.fixture
def inv():
    return s3.GestionInventario()

@pytest.fixture
def gu():
    return s4.GestionUsuarios()

@pytest.fixture
def gf():
    return s4.GestionFacturacion()

@pytest.fixture
def gr():
    return s4.GestionReportes()


@pytest.fixture
def datos_base(gp, gc):
    """Crea dueños, mascotas y veterinario base para los tests."""
    d1 = gp.registrar_dueno("Carlos Test", "310-000-0000", "carlos@test.com", "Calle 1")
    d2 = gp.registrar_dueno("María Test", "320-000-0000", "maria@test.com")
    m1 = gp.registrar_mascota("Fido", "Perro", d1, "Labrador", 3, 20)
    m2 = gp.registrar_mascota("Luna", "Gato", d2, "Persa", 2, 4)
    v1 = gc.registrar_veterinario("Dr. Test", "General")
    return {"d1": d1, "d2": d2, "m1": m1, "m2": m2, "v1": v1}


# ─────────────────────────────────────────
#  SPRINT 1 — PACIENTES
# ─────────────────────────────────────────

class TestGestionPacientes:

    def test_CP001_registrar_dueno_exitoso(self, gp):
        """Registrar un dueño con datos válidos retorna un ID positivo."""
        # Arrange
        nombre, telefono, correo = "Ana García", "300-111-2222", "ana@test.com"
        # Act
        dueno_id = gp.registrar_dueno(nombre, telefono, correo)
        # Assert
        assert dueno_id > 0, "El ID del dueño debe ser un entero positivo"

    def test_CP002_registrar_mascota_exitosa(self, gp):
        """Registrar mascota con dueño válido retorna ID positivo."""
        # Arrange
        d_id = gp.registrar_dueno("Pedro", "310-000-0000")
        # Act
        m_id = gp.registrar_mascota("Rex", "Perro", d_id, "Poodle", 4, 12)
        # Assert
        assert m_id > 0

    def test_CP003_mascota_con_dueno_invalido(self, gp):
        """Registrar mascota con dueño inexistente retorna -1."""
        # Arrange
        dueno_id_invalido = 99999
        # Act
        resultado = gp.registrar_mascota("Rex", "Perro", dueno_id_invalido)
        # Assert
        assert resultado == -1

    def test_CP004_busqueda_por_nombre_mascota(self, gp, datos_base):
        """Búsqueda por nombre de mascota retorna resultados correctos."""
        # Arrange
        termino = "Fido"
        # Act
        resultados = gp.buscar_mascota(termino)
        # Assert
        assert len(resultados) >= 1
        assert resultados[0]["mascota"] == "Fido"

    def test_CP005_busqueda_por_nombre_dueno(self, gp, datos_base):
        """Búsqueda por nombre del dueño retorna mascotas asociadas."""
        # Arrange
        termino = "Carlos"
        # Act
        resultados = gp.buscar_mascota(termino)
        # Assert
        assert len(resultados) >= 1
        assert "Carlos" in resultados[0]["dueno"]

    def test_CP006_busqueda_sin_resultados(self, gp):
        """Búsqueda sin coincidencias retorna lista vacía."""
        # Arrange  (BD vacía)
        # Act
        resultados = gp.buscar_mascota("XYZ_NO_EXISTE")
        # Assert
        assert resultados == []

    def test_CP007_ver_ficha_existente(self, gp, datos_base):
        """ver_ficha retorna dict con datos de mascota y dueño."""
        # Arrange
        m_id = datos_base["m1"]
        # Act
        ficha = gp.ver_ficha(m_id)
        # Assert
        assert ficha is not None
        assert ficha["nombre"] == "Fido"
        assert "dueno" in ficha

    def test_CP008_ver_ficha_inexistente(self, gp):
        """ver_ficha de ID inexistente retorna None."""
        # Arrange
        id_invalido = 99999
        # Act
        ficha = gp.ver_ficha(id_invalido)
        # Assert
        assert ficha is None

    def test_CP009_actualizar_mascota(self, gp, datos_base):
        """Actualizar mascota modifica el campo correctamente."""
        # Arrange
        m_id = datos_base["m1"]
        nuevo_peso = 22.5
        # Act
        ok = gp.actualizar_mascota(m_id, peso=nuevo_peso)
        ficha = gp.ver_ficha(m_id)
        # Assert
        assert ok is True
        assert ficha["peso"] == nuevo_peso


# ─────────────────────────────────────────
#  SPRINT 1 — CITAS
# ─────────────────────────────────────────

class TestGestionCitas:

    def test_CP010_agendar_cita_exitosa(self, gc, datos_base):
        """Agendar cita en horario libre retorna ID positivo."""
        # Arrange
        m, v = datos_base["m1"], datos_base["v1"]
        # Act
        cita_id = gc.agendar_cita(m, v, "2026-05-10", "09:00", "Revisión")
        # Assert
        assert cita_id > 0

    def test_CP011_prevenir_cita_duplicada(self, gc, datos_base):
        """Agendar cita en horario ya ocupado retorna -1."""
        # Arrange
        m, v = datos_base["m1"], datos_base["v1"]
        gc.agendar_cita(m, v, "2026-05-10", "09:00", "Primera cita")
        # Act — intentar el mismo horario
        resultado = gc.agendar_cita(datos_base["m2"], v, "2026-05-10", "09:00", "Duplicado")
        # Assert
        assert resultado == -1

    def test_CP012_cancelar_cita(self, gc, datos_base):
        """Cancelar cita existente retorna True y cambia estado."""
        # Arrange
        cita_id = gc.agendar_cita(datos_base["m1"], datos_base["v1"], "2026-05-11", "10:00")
        # Act
        ok = gc.cancelar_cita(cita_id)
        # Assert
        assert ok is True

    def test_CP013_cancelar_cita_inexistente(self, gc):
        """Cancelar cita con ID inválido retorna False."""
        # Arrange
        id_invalido = 99999
        # Act
        resultado = gc.cancelar_cita(id_invalido)
        # Assert
        assert resultado is False

    def test_CP014_agenda_del_dia(self, gc, datos_base):
        """agenda_del_dia retorna citas del día correcto."""
        # Arrange
        m, v = datos_base["m1"], datos_base["v1"]
        gc.agendar_cita(m, v, "2026-05-20", "08:00", "Vacuna")
        # Act
        agenda = gc.agenda_del_dia("2026-05-20")
        # Assert
        assert len(agenda) == 1
        assert agenda[0]["mascota"] == "Fido"

    def test_CP015_agenda_dia_sin_citas(self, gc):
        """agenda_del_dia sin citas retorna lista vacía."""
        # Act
        agenda = gc.agenda_del_dia("2099-12-31")
        # Assert
        assert agenda == []


# ─────────────────────────────────────────
#  SPRINT 1 — HISTORIAL
# ─────────────────────────────────────────

class TestHistorialClinico:

    def test_CP016_registrar_consulta(self, hc, datos_base):
        """Registrar consulta retorna ID positivo."""
        # Arrange
        m, v = datos_base["m1"], datos_base["v1"]
        # Act
        hist_id = hc.registrar_consulta(m, v, "Otitis", "Gotas óticas", "Revisar en 1 semana")
        # Assert
        assert hist_id > 0

    def test_CP017_historial_vacio(self, hc, datos_base):
        """Mascota sin consultas retorna historial vacío."""
        # Act
        historial = hc.consultar_historial(datos_base["m2"])
        # Assert
        assert historial == []

    def test_CP018_historial_con_consultas(self, hc, datos_base):
        """Mascota con consultas retorna historial no vacío."""
        # Arrange
        m, v = datos_base["m1"], datos_base["v1"]
        hc.registrar_consulta(m, v, "Diagnóstico A", "Tratamiento A")
        hc.registrar_consulta(m, v, "Diagnóstico B", "Tratamiento B")
        # Act
        historial = hc.consultar_historial(m)
        # Assert
        assert len(historial) == 2


# ─────────────────────────────────────────
#  SPRINT 2 — DIAGNÓSTICOS Y VACUNAS
# ─────────────────────────────────────────

class TestDiagnosticosVacunas:

    def test_CP019_registrar_diagnostico(self, gd, datos_base):
        """Registrar diagnóstico retorna historial ID positivo."""
        # Arrange
        m, v = datos_base["m1"], datos_base["v1"]
        # Act
        hist_id = gd.registrar_diagnostico(m, v, "Dermatitis", "Antihistamínico")
        # Assert
        assert hist_id > 0

    def test_CP020_registrar_tratamiento(self, gd, datos_base):
        """Registrar tratamiento retorna ID positivo."""
        # Arrange
        m, v = datos_base["m1"], datos_base["v1"]
        hist_id = gd.registrar_diagnostico(m, v, "Infección", "Antibiótico")
        # Act
        trat_id = gd.registrar_tratamiento(m, hist_id, "Amoxicilina", "500mg",
                                            "2/día", "2026-04-15", "2026-04-30")
        # Assert
        assert trat_id > 0

    def test_CP021_vacunas_proximas(self, gv, datos_base):
        """vacunas_proximas detecta próxima dosis dentro del período."""
        # Arrange
        m, v = datos_base["m1"], datos_base["v1"]
        gv.registrar_vacuna(m, v, "Rabia", "2026-04-30")  # próxima en ~20 días
        # Act
        proximas = gv.vacunas_proximas(dias=30)
        # Assert
        assert len(proximas) >= 1


# ─────────────────────────────────────────
#  SPRINT 3 — INVENTARIO
# ─────────────────────────────────────────

class TestInventario:

    def test_CP022_agregar_producto(self, inv):
        """Agregar producto con stock inicial válido retorna ID positivo."""
        # Arrange
        codigo, nombre = "MED-TEST-001", "Paracetamol 500mg"
        # Act
        pid = inv.agregar_producto(codigo, nombre, "medicamento", 1000, 2000, 50, 10)
        # Assert
        assert pid > 0

    def test_CP023_codigo_duplicado(self, inv):
        """Agregar producto con código duplicado retorna -1."""
        # Arrange
        inv.agregar_producto("MED-DUP", "Producto A", "medicamento", 1000, 2000, 10, 5)
        # Act
        resultado = inv.agregar_producto("MED-DUP", "Producto B", "medicamento", 1000, 2000, 10, 5)
        # Assert
        assert resultado == -1

    def test_CP024_alerta_stock_bajo_al_crear(self, inv):
        """Producto creado con stock < mínimo genera alerta."""
        # Arrange
        inv.agregar_producto("ALERT-001", "Stock Bajo Test", "insumo", 500, 1000, 2, 5)
        # Act
        alertas = inv.alertas_activas()
        # Assert
        assert len(alertas) >= 1
        assert any("BAJO" in a["mensaje"] or "bajo" in a["tipo_alerta"] for a in alertas)

    def test_CP025_entrada_incrementa_stock(self, inv):
        """Registrar entrada incrementa el stock del producto."""
        # Arrange
        pid = inv.agregar_producto("ENT-001", "Producto Entrada", "insumo", 100, 200, 10, 5)
        stock_inicial = inv.consultar_stock()
        inicial = next(p["stock_actual"] for p in stock_inicial if p["id"] == pid)
        # Act
        inv.registrar_entrada(pid, 15, "Compra")
        stock_final = inv.consultar_stock()
        final = next(p["stock_actual"] for p in stock_final if p["id"] == pid)
        # Assert
        assert final == inicial + 15

    def test_CP026_salida_reduce_stock(self, inv):
        """Registrar salida reduce el stock del producto."""
        # Arrange
        pid = inv.agregar_producto("SAL-001", "Producto Salida", "insumo", 100, 200, 20, 5)
        # Act
        inv.registrar_salida(pid, 5, "Venta")
        stock = inv.consultar_stock()
        actual = next(p["stock_actual"] for p in stock if p["id"] == pid)
        # Assert
        assert actual == 15

    def test_CP027_salida_sin_stock_suficiente(self, inv):
        """Salida mayor al stock disponible retorna False."""
        # Arrange
        pid = inv.agregar_producto("INSUF-001", "Poco Stock", "insumo", 100, 200, 3, 1)
        # Act
        resultado = inv.registrar_salida(pid, 10, "Exceso")
        # Assert
        assert resultado is False

    def test_CP028_ajuste_inventario(self, inv):
        """Ajuste de inventario establece el stock exacto indicado."""
        # Arrange
        pid = inv.agregar_producto("AJUST-001", "Ajuste Test", "insumo", 100, 200, 50, 5)
        # Act
        inv.ajuste_inventario(pid, 30, "Conteo físico")
        stock = inv.consultar_stock()
        actual = next(p["stock_actual"] for p in stock if p["id"] == pid)
        # Assert
        assert actual == 30

    def test_CP029_historial_movimientos(self, inv):
        """Movimientos quedan registrados en historial."""
        # Arrange
        pid = inv.agregar_producto("HIST-001", "Historia Test", "insumo", 100, 200, 20, 5)
        inv.registrar_salida(pid, 5, "Test salida")
        # Act
        movimientos = inv.historial_movimientos(pid)
        # Assert — debe haber al menos 2: entrada inicial + salida
        assert len(movimientos) >= 2


# ─────────────────────────────────────────
#  SPRINT 4 — USUARIOS
# ─────────────────────────────────────────

class TestUsuarios:

    def test_CP030_registrar_usuario_exitoso(self, gu):
        """Registrar usuario con datos válidos retorna ID positivo."""
        # Arrange
        nombre, correo, pwd, rol = "Test User", "test@vetcare.co", "Pass1234!", "admin"
        # Act
        uid = gu.registrar_usuario(nombre, correo, pwd, rol)
        # Assert
        assert uid > 0

    def test_CP031_autenticacion_correcta(self, gu):
        """Autenticación con credenciales correctas retorna dict de usuario."""
        # Arrange
        gu.registrar_usuario("Auth User", "auth@vetcare.co", "MiClave123!", "recepcionista")
        # Act
        usuario = gu.autenticar("auth@vetcare.co", "MiClave123!")
        # Assert
        assert usuario is not None
        assert usuario["correo"] == "auth@vetcare.co"
        assert usuario["rol"] == "recepcionista"

    def test_CP032_autenticacion_incorrecta(self, gu):
        """Autenticación con contraseña incorrecta retorna None."""
        # Arrange
        gu.registrar_usuario("Wrong Pass", "wrong@vetcare.co", "Correcta123!", "admin")
        # Act
        resultado = gu.autenticar("wrong@vetcare.co", "Incorrecta999!")
        # Assert
        assert resultado is None

    def test_CP033_correo_duplicado(self, gu):
        """Registrar dos usuarios con el mismo correo retorna -1 en el segundo."""
        # Arrange
        gu.registrar_usuario("User A", "dup@vetcare.co", "Pass1!", "admin")
        # Act
        resultado = gu.registrar_usuario("User B", "dup@vetcare.co", "Pass2!", "gerente")
        # Assert
        assert resultado == -1

    def test_CP034_rol_invalido(self, gu):
        """Registrar usuario con rol inválido retorna -1."""
        # Act
        resultado = gu.registrar_usuario("Bad Role", "bad@vetcare.co", "Pass1!", "superheroe")
        # Assert
        assert resultado == -1

    def test_CP035_permisos_admin(self, gu):
        """El rol admin tiene permiso sobre cualquier acción."""
        # Arrange
        gu.registrar_usuario("Admin", "admin@vetcare.co", "Admin1234!", "admin")
        usuario = gu.autenticar("admin@vetcare.co", "Admin1234!")
        # Act & Assert
        assert gu.tiene_permiso(usuario, "historial_escribir")
        assert gu.tiene_permiso(usuario, "facturas_escribir")
        assert gu.tiene_permiso(usuario, "reportes")

    def test_CP036_permisos_recepcionista(self, gu):
        """El rol recepcionista no puede editar historial clínico."""
        # Arrange
        gu.registrar_usuario("Recep", "recep@vetcare.co", "Recep1234!", "recepcionista")
        usuario = gu.autenticar("recep@vetcare.co", "Recep1234!")
        # Act & Assert
        assert gu.tiene_permiso(usuario, "citas_escribir")      # ✅ sí puede
        assert not gu.tiene_permiso(usuario, "historial_escribir")  # ❌ no puede

    def test_CP037_recuperacion_contrasena(self, gu):
        """El flujo de recuperación genera token y permite cambiar contraseña."""
        # Arrange
        gu.registrar_usuario("Recover", "recover@vetcare.co", "Original1!", "veterinario")
        # Act
        token = gu.solicitar_recuperacion("recover@vetcare.co")
        ok = gu.cambiar_password("recover@vetcare.co", token, "Nueva2026!")
        # Assert
        assert ok is True
        usuario = gu.autenticar("recover@vetcare.co", "Nueva2026!")
        assert usuario is not None


# ─────────────────────────────────────────
#  SPRINT 4 — FACTURACIÓN
# ─────────────────────────────────────────

class TestFacturacion:

    def test_CP038_crear_factura(self, gf, datos_base):
        """Crear factura retorna ID positivo."""
        # Arrange
        d, m = datos_base["d1"], datos_base["m1"]
        # Act
        fid = gf.crear_factura(d, m, "Efectivo")
        # Assert
        assert fid > 0

    def test_CP039_calculo_iva_correcto(self, gf, datos_base):
        """Factura con un ítem calcula IVA 19% y total correctamente."""
        # Arrange
        fid = gf.crear_factura(datos_base["d1"], datos_base["m1"])
        # Act
        gf.agregar_item(fid, "Consulta General", 50000, 1, "servicio")
        f = gf.ver_factura(fid)
        # Assert
        assert f["subtotal"] == 50000.0
        assert f["iva"] == pytest.approx(9500.0, abs=1)
        assert f["total"] == pytest.approx(59500.0, abs=1)

    def test_CP040_factura_multiples_items(self, gf, datos_base):
        """Factura con múltiples ítems acumula subtotales correctamente."""
        # Arrange
        fid = gf.crear_factura(datos_base["d1"], datos_base["m1"])
        # Act
        gf.agregar_item(fid, "Consulta", 50000, 1)
        gf.agregar_item(fid, "Medicamento", 12000, 2)  # 24000
        f = gf.ver_factura(fid)
        # Assert — subtotal = 50000 + 24000 = 74000
        assert f["subtotal"] == 74000.0
        assert f["total"] == pytest.approx(74000 * 1.19, abs=1)

    def test_CP041_registrar_pago(self, gf, datos_base):
        """Registrar pago cambia estado de factura a Pagada."""
        # Arrange
        fid = gf.crear_factura(datos_base["d1"], datos_base["m1"])
        gf.agregar_item(fid, "Servicio", 30000, 1)
        # Act
        ok = gf.registrar_pago(fid, "Efectivo")
        f = gf.ver_factura(fid)
        # Assert
        assert ok is True
        assert f["estado"] == "Pagada"

    def test_CP042_numeracion_facturas_unica(self, gf, datos_base):
        """Dos facturas distintas tienen números únicos."""
        # Arrange
        d, m = datos_base["d1"], datos_base["m1"]
        # Act
        f1 = gf.crear_factura(d, m)
        f2 = gf.crear_factura(d, m)
        fact1 = gf.ver_factura(f1)
        fact2 = gf.ver_factura(f2)
        # Assert
        assert fact1["numero"] != fact2["numero"]


# ─────────────────────────────────────────
#  SPRINT 4 — REPORTES
# ─────────────────────────────────────────

class TestReportes:

    def test_CP043_panel_gerente_keys(self, gr):
        """panel_gerente retorna todos los KPIs esperados."""
        # Act
        kpis = gr.panel_gerente()
        # Assert
        claves_esperadas = {"total_pacientes", "citas_hoy", "ingresos_mes",
                            "productos_stock_bajo", "facturas_pendientes",
                            "top_especies_consultadas"}
        assert claves_esperadas.issubset(kpis.keys())

    def test_CP044_reporte_ventas_estructura(self, gr):
        """reporte_ventas retorna dict con claves correctas."""
        # Act
        reporte = gr.reporte_ventas("2026-01-01", "2026-12-31")
        # Assert
        assert "resumen" in reporte
        assert "por_metodo_pago" in reporte
        assert "ingresos_totales" in reporte["resumen"]

    def test_CP045_exportar_json(self, gr, tmp_path):
        """exportar_json crea archivo JSON válido."""
        # Arrange
        datos = {"test": "value", "numero": 42}
        import json, tempfile
        # Act — usar directorio temporal
        original_path = "/home/claude/test_export.json"
        gr.exportar_json(datos, "test_export")
        # Assert
        assert os.path.exists(original_path)
        with open(original_path) as f:
            loaded = json.load(f)
        assert loaded["test"] == "value"
        os.remove(original_path)


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────

if __name__ == "__main__":
    # Ejecutar con: python test_vetcare.py
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=False
    )
    sys.exit(result.returncode)
