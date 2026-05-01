import pytest, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .conftest import slow_type, slow_click, wait_for_login_to_disappear

@pytest.mark.functional
class TestUsuarios:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_crear_usuario(self, browser):
        driver = browser
        self._login(driver)
        slow_click(driver, By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Usuarios')]")
        time.sleep(0.4)

        slow_click(driver, By.XPATH, "//button[contains(text(),'+ Nuevo usuario')]")
        time.sleep(0.5)

        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "modal-usuario"))
        )

        slow_type(driver, By.ID, "f-u-nombre", "Nuevo Usuario Test", 50)
        slow_type(driver, By.ID, "f-u-email", "nuevo@test.com", 50)
        slow_type(driver, By.ID, "f-u-pass", "password123", 50)

        # Cambiar rol a "veterinario"
        Select(driver.find_element(By.ID, "f-u-rol")).select_by_visible_text("Veterinario")
        time.sleep(0.15)

        registrar_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='modal-usuario']//div[contains(@class,'modal-footer')]//button[contains(text(),'Registrar')]"))
        )
        slow_click(driver, By.XPATH, "//div[@id='modal-usuario']//div[contains(@class,'modal-footer')]//button[contains(text(),'Registrar')]")
        time.sleep(0.6)

        assert "Usuario registrado" in driver.find_element(By.ID, "toast").text
        tabla = driver.find_element(By.ID, "tabla-usuarios")
        assert "Nuevo Usuario Test" in tabla.text
