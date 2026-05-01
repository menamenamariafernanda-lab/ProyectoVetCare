"""
Pruebas unitarias - Validación de funciones específicas
"""
import pytest
from sprint4_vetcare import hash_password, GestionUsuarios, GestionFacturacion


class TestHashPassword:
    """Pruebas para la función hash_password"""
    
    def test_hash_es_diferente_original(self):
        """Verifica que el hash no sea igual al texto original"""
        password = "miPassword123"
        hashed = hash_password(password)
        assert hashed != password
    
    def test_hash_longitud_fija(self):
        """El hash SHA256 debe tener 64 caracteres"""
        hashed = hash_password("cualquierPassword")
        assert len(hashed) == 64
    
    def test_hash_consistente(self):
        """Mismo password debe generar mismo hash"""
        pwd = "passwordConsistente"
        hash1 = hash_password(pwd)
        hash2 = hash_password(pwd)
        assert hash1 == hash2
    
    def test_hash_diferente_para_diferentes_passwords(self):
        """Passwords diferentes deben generar hashes diferentes"""
        hash1 = hash_password("pass123")
        hash2 = hash_password("pass456")
        assert hash1 != hash2
    
    def test_hash_con_password_vacio(self):
        """Manejo de password vacío"""
        hashed = hash_password("")
        assert isinstance(hashed, str)
        assert len(hashed) == 64


class TestGestionUsuariosUnitario:
    """Pruebas unitarias para GestionUsuarios"""
    
    def test_registrar_usuario_exitoso(self, gestion_usuarios, datos_prueba_usuarios, temp_db):
        """Registro exitoso de nuevo usuario"""
        data = datos_prueba_usuarios[0]
        user_id = gestion_usuarios.registrar_usuario(
            data["nombre"], data["correo"], data["password"], data["rol"]
        )
        assert user_id > 0
    
    def test_registrar_usuario_duplicado_falla(self, gestion_usuarios, temp_db):
        """No se debe poder registrar mismo correo dos veces"""
        # Primer registro
        gestion_usuarios.registrar_usuario("Usuario1", "duplicado@test.com", "pass1", "recepcionista")
        
        # Segundo registro con mismo correo (debe fallar)
        user_id = gestion_usuarios.registrar_usuario("Usuario2", "duplicado@test.com", "pass2", "recepcionista")
        assert user_id == -1
    
    def test_autenticar_credenciales_correctas(self, gestion_usuarios, temp_db):
        """Autenticación exitosa con credenciales correctas"""
        # Registrar usuario
        gestion_usuarios.registrar_usuario("Auth Test", "auth@test.com", "secreto123", "admin")
        
        # Autenticar
        user = gestion_usuarios.autenticar("auth@test.com", "secreto123")
        assert user is not None
        assert user["nombre"] == "Auth Test"
        assert user["rol"] == "admin"
    
    def test_autenticar_credenciales_incorrectas(self, gestion_usuarios, temp_db):
        """Autenticación falla con credenciales incorrectas"""
        # Registrar usuario
        gestion_usuarios.registrar_usuario("Bad Auth", "badauth@test.com", "passwordOK", "recepcionista")
        
        # Intentar con password incorrecto
        user = gestion_usuarios.autenticar("badauth@test.com", "passwordWRONG")
        assert user is None
    
    def test_autenticar_usuario_inexistente(self, gestion_usuarios):
        """Usuario que no existe no puede autenticarse"""
        user = gestion_usuarios.autenticar("noexiste@test.com", "cualquierPass")
        assert user is None
    
    def test_listar_usuarios_estructura_correcta(self, gestion_usuarios, temp_db):
        """La lista de usuarios debe tener la estructura correcta"""
        # Registrar algunos usuarios
        gestion_usuarios.registrar_usuario("Lista1", "lista1@test.com", "pass", "recepcionista")
        gestion_usuarios.registrar_usuario("Lista2", "lista2@test.com", "pass", "veterinario")
        
        usuarios = gestion_usuarios.listar_usuarios()
        
        assert isinstance(usuarios, list)
        if usuarios:
            assert "id" in usuarios[0]
            assert "nombre" in usuarios[0]
            assert "correo" in usuarios[0]
            assert "rol" in usuarios[0]


class TestGestionFacturacionUnitario:
    """Pruebas unitarias para GestionFacturacion"""
    
    def test_crear_factura_genera_numero(self, gestion_facturacion, temp_db):
        """La factura debe tener un número único"""
        factura_id = gestion_facturacion.crear_factura(1, 1, "Efectivo")
        assert factura_id > 0
        
        factura = gestion_facturacion.ver_factura(factura_id)
        assert factura is not None
        assert "numero" in factura
        assert factura["numero"].startswith("VET-")
    
    def test_agregar_item_calcula_subtotal(self, gestion_facturacion, temp_db):
        """Agregar items debe calcular correctamente subtotal e IVA"""
        factura_id = gestion_facturacion.crear_factura(1, 1, "Efectivo")
        
        # Agregar item de $50,000
        gestion_facturacion.agregar_item(factura_id, "Consulta", 50000, 1)
        
        factura = gestion_facturacion.ver_factura(factura_id)
        
        assert factura["subtotal"] == 50000
        assert factura["iva"] == 50000 * 0.19  # 9,500
        assert factura["total"] == 50000 * 1.19  # 59,500
    
    def test_agregar_multiples_items(self, gestion_facturacion, temp_db):
        """Múltiples items deben sumar correctamente"""
        factura_id = gestion_facturacion.crear_factura(1, 1, "Efectivo")
        
        gestion_facturacion.agregar_item(factura_id, "Consulta", 50000, 1)
        gestion_facturacion.agregar_item(factura_id, "Vacuna", 35000, 1)
        gestion_facturacion.agregar_item(factura_id, "Medicamento", 20000, 2)
        
        factura = gestion_facturacion.ver_factura(factura_id)
        
        subtotal_esperado = 50000 + 35000 + (20000 * 2)  # 125,000
        assert factura["subtotal"] == subtotal_esperado
    
    def test_registrar_pago_cambia_estado(self, gestion_facturacion, temp_db):
        """Registrar pago debe cambiar estado a 'Pagada'"""
        factura_id = gestion_facturacion.crear_factura(1, 1, "Efectivo")
        gestion_facturacion.agregar_item(factura_id, "Servicio Test", 10000, 1)
        
        # Verificar estado inicial
        factura = gestion_facturacion.ver_factura(factura_id)
        assert factura["estado"] == "Pendiente"
        
        # Registrar pago
        resultado = gestion_facturacion.registrar_pago(factura_id)
        assert resultado is True
        
        # Verificar estado actualizado
        factura = gestion_facturacion.ver_factura(factura_id)
        assert factura["estado"] == "Pagada"
    
    def test_ver_factura_retorna_items(self, gestion_facturacion, temp_db):
        """ver_factura debe incluir la lista de items"""
        factura_id = gestion_facturacion.crear_factura(1, 1, "Efectivo")
        gestion_facturacion.agregar_item(factura_id, "Item 1", 10000, 1)
        gestion_facturacion.agregar_item(factura_id, "Item 2", 20000, 2)
        
        factura = gestion_facturacion.ver_factura(factura_id)
        
        assert "items" in factura
        assert isinstance(factura["items"], list)
        assert len(factura["items"]) == 2