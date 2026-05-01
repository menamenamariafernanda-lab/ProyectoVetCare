import pytest
from sprint4_vetcare import GestionUsuarios

@pytest.mark.unit
class TestGestionUsuarios:
    def test_crear_usuario_exitoso(self, test_db):
        gu = GestionUsuarios()
        uid = gu.registrar_usuario("Ana", "ana@vetcare.com", "pass123", "admin")
        assert uid > 0, "El ID del usuario debe ser positivo"

    def test_autenticar_usuario_correcto(self, test_db):
        gu = GestionUsuarios()
        gu.registrar_usuario("Luis", "luis@vetcare.com", "segura", "veterinario")
        user = gu.autenticar("luis@vetcare.com", "segura")
        assert user is not None, "La autenticación debe devolver un usuario"
        assert user["nombre"] == "Luis"
        assert user["rol"] == "veterinario"

    def test_autenticar_password_incorrecta(self, test_db):
        gu = GestionUsuarios()
        gu.registrar_usuario("Marta", "marta@vetcare.com", "clave", "admin")
        result = gu.autenticar("marta@vetcare.com", "equivocada")
        assert result is None, "Debe fallar con contraseña incorrecta"

    def test_autenticar_usuario_inexistente(self, test_db):
        gu = GestionUsuarios()
        result = gu.autenticar("nadie@vetcare.com", "cualquiera")
        assert result is None

    def test_listar_usuarios(self, test_db):
        gu = GestionUsuarios()
        gu.registrar_usuario("U1", "u1@vetcare.com", "p1", "admin")
        gu.registrar_usuario("U2", "u2@vetcare.com", "p2", "seguridad")
        usuarios = gu.listar_usuarios()
        assert len(usuarios) == 2
        # Verificar que los nombres estén presentes
        nombres = {u["nombre"] for u in usuarios}
        assert nombres == {"U1", "U2"}
